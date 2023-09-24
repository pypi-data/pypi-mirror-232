import os
import os.path as osp
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import partial
from typing import Any, Dict, Union, Optional, List, Callable
from collections import OrderedDict
from dataclasses import fields
from packaging import version

import torch
from torch import nn
from torch.nn import DataParallel

from weathon.dl.registry import build_backbone, build_model
from weathon.dl.utils.checkpoint import save_checkpoint, save_configuration, save_pretrained
from weathon.dl.utils.config.config import ConfigDict, Config
from weathon.dl.utils.constants import ModelFile, Tasks
from weathon.dl.utils.device import verify_device
from weathon.dl.utils.fileio.file_utils import func_receive_dict_inputs
from weathon.dl.utils.logger import get_logger
from weathon.dl.utils.nlp.distributed import DistributedDataParallel

logger = get_logger()


class BaseHead(ABC):
    """The head base class is for the tasks head method definition

    """

    def __init__(self, **kwargs):
        self.config = ConfigDict(kwargs)

    @abstractmethod
    def forward(self, *args, **kwargs) -> Dict[str, Any]:
        """
        This method will use the output from backbone model to do any
        downstream tasks. Receive The output from backbone model.

        Returns (Dict[str, Any]): The output from downstream task.
        """
        pass

    @abstractmethod
    def compute_loss(self, *args, **kwargs) -> Dict[str, Any]:
        """
        compute loss for head during the finetuning.

        Returns (Dict[str, Any]): The loss dict
        """
        pass


class BaseModel(ABC):
    """Base model interface.
    """

    def __init__(self, model_dir, *args, **kwargs):
        self.model_dir = model_dir
        device_name = kwargs.get('device', 'gpu')
        verify_device(device_name)
        self._device_name = device_name

    def __call__(self, inputs) -> Dict[str, Any]:
        return self.postprocess(self.forward(inputs))

    @abstractmethod
    def forward(self,inputs) -> Dict[str, Any]:
        """
        Run the forward pass for a model.

        Returns:
            Dict[str, Any]: output from the model forward pass
        """
        pass

    def postprocess(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """ Model specific postprocess and convert model output to
        standard model outputs.

        Args:
            inputs:  input data

        Return:
            dict of results:  a dict containing outputs of model, each
                output should have the standard output name.
        """
        return outputs

    @classmethod
    def _instantiate(cls, **kwargs):
        """ Define the instantiation method of a model,default method is by
            calling the constructor. Note that in the case of no loading model
            process in constructor of a task model, a load_model method is
            added, and thus this method is overloaded
        """
        return cls(**kwargs)

    @classmethod
    def from_pretrained(cls, local_model_dir: str, cfg_dict: Config = None, device: str = None,
                        **kwargs: object) -> object:
        """Instantiate a model from local directory 

        Args:
            model_path(str): A model dir to be loaded
            cfg_dict(Config, `optional`): An optional model config. If provided, it will replace the config read out of the `model_name_or_path`
            device(str, `optional`): The device to load the model.
            **kwargs:
                task(str, `optional`): The `Tasks` enumeration value to replace the task value
                read out of config in the `model_name_or_path`. This is useful when the model to be loaded is not
                equal to the model saved.
                For example, load a `backbone` into a `text-classification` model.
                Other kwargs will be directly fed into the `model` key, to replace the default configs.
        Returns:
            A model instance.

        """

        logger.info(f'initialize model from {local_model_dir}')

        cfg = cfg_dict if cfg_dict else Config.from_file(osp.join(local_model_dir, ModelFile.CONFIGURATION_YAML))
        task_name = cfg.task
        if 'task' in kwargs:
            task_name = kwargs.pop('task')

        model_cfg = cfg.model
        if hasattr(model_cfg, 'model_type') and not hasattr(model_cfg, 'type'):
            model_cfg.type = model_cfg.model_type
        model_cfg.model_dir = local_model_dir

        for k, v in kwargs.items():
            model_cfg[k] = v
        if device is not None:
            model_cfg.device = device
        if task_name is Tasks.backbone:
            model_cfg.init_backbone = True
            model = build_backbone(model_cfg)
        else:
            model = build_model(model_cfg, task_name=task_name)

        # dynamically add pipeline info to model for pipeline inference
        if hasattr(cfg, 'pipeline'):
            model.pipeline = cfg.pipeline

        if not hasattr(model, 'cfg'):
            model.cfg = cfg

        model_cfg.pop('model_dir', None)
        model.name = model.type
        model.model_dir = local_model_dir
        return model

    def save_pretrained(self,
                        target_folder: Union[str, os.PathLike],
                        save_checkpoint_names: Union[str, List[str]] = None,
                        config: Optional[dict] = None,
                        **kwargs):
        """
        将训练的模型,配置文件,以及其他相关文件保存到一个目录中,以便可以重新加载

        Args:
            target_folder (Union[str, os.PathLike]):
            Directory to which to save. Will be created if it doesn't exist.

            save_checkpoint_names (Union[str, List[str]]):
            The checkpoint names to be saved in the target_folder

            config (Optional[dict], optional):
            The config for the configuration.json, might not be identical with model.config
        """
        raise NotImplementedError('save_pretrained method need to be implemented by the subclass.')


class TorchHead(BaseHead, torch.nn.Module):
    """ Base head interface for pytorch

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        torch.nn.Module.__init__(self)

    def forward(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def compute_loss(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError


class TorchModel(BaseModel, torch.nn.Module):
    """ Base model interface for pytorch

    """

    def __init__(self, model_dir=None, *args, **kwargs):
        super().__init__(model_dir, *args, **kwargs)
        torch.nn.Module.__init__(self)

    # def __call__(self, *args, **kwargs) -> Dict[str, Any]:
    #     # Adapting a model with only one dict arg, and the arg name must be input or inputs
    #     if func_receive_dict_inputs(self.forward):
    #         return self.postprocess(self.forward(args[0], **kwargs))
    #     else:
    #         return self.postprocess(self.forward(*args, **kwargs))

    def _load_pretrained(self, net, load_path, strict=True, param_key='params'):
        if isinstance(net, (DataParallel, DistributedDataParallel)):
            net = net.module
        load_net = torch.load(load_path, map_location=lambda storage, loc: storage)
        if param_key is not None:
            if param_key not in load_net and 'params' in load_net:
                param_key = 'params'
                logger.info(f'Loading: {param_key} does not exist, use params.')
            if param_key in load_net:
                load_net = load_net[param_key]
        logger.info(f'Loading {net.__class__.__name__} model from {load_path}, with param key: [{param_key}].')
        # remove unnecessary 'module.'
        for k, v in deepcopy(load_net).items():
            if k.startswith('module.'):
                load_net[k[7:]] = v
                load_net.pop(k)
        net.load_state_dict(load_net, strict=strict)
        logger.info('load model done.')
        return net

    def print_state_dict(self):
        pass

    def forward(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def post_init(self):
        """
        A method executed at the end of each model initialization, to execute code that needs the model's
        modules properly initialized (such as weight initialization).
        """
        self.init_weights()

    def init_weights(self):
        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize the weights"""
        if isinstance(module, nn.Linear):
            # Slightly different from the TF version which uses truncated_normal for initialization
            # cf https://github.com/pytorch/pytorch/pull/5617
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def save_pretrained(self,
                        target_folder: Union[str, os.PathLike],
                        save_checkpoint_names: Union[str, List[str]] = None,
                        save_function: Callable = partial(save_checkpoint, with_meta=False),
                        config: Optional[dict] = None,
                        save_config_function: Callable = save_configuration,
                        **kwargs):
        """save the pretrained model, its configuration and other related files to a directory,
            so that it can be re-loaded

        Args:
            target_folder (Union[str, os.PathLike]):
            Directory to which to save. Will be created if it doesn't exist.

            save_checkpoint_names (Union[str, List[str]]):
            The checkpoint names to be saved in the target_folder

            save_function (Callable, optional):
            The function to use to save the state dictionary.

            config (Optional[dict], optional):
            The config for the configuration.json, might not be identical with model.config

            save_config_function (Callble, optional):
            The function to use to save the configuration.

        """
        if config is None and hasattr(self, 'cfg'):
            config = self.cfg

        save_pretrained(self, target_folder, save_checkpoint_names, save_function, **kwargs)

        if config is not None:
            save_config_function(target_folder, config)

    def compile(self, **kwargs):
        """Compile torch model with torch>=2.0

        Args:
            kwargs:
                backend: The backend param of torch.compile
                mode: The mode param of torch.compile
        """

        if version.parse(torch.__version__) >= version.parse('2.0.0.dev'):
            return torch.compile(self, **kwargs)
        else:
            logger.warning(
                f'Torch compiling needs torch version >= 2.0.0, your torch version is : {torch.__version__},'
                f' returns original model')
            return self


# ################################# Output #################################

class BaseOutput(list):

    def __post_init__(self):
        self.reconstruct()
        self.post_init = True

    def reconstruct(self):
        # Low performance, but low frequency.
        self.clear()
        for idx, key in enumerate(self.keys()):
            self.append(getattr(self, key))

    def __getitem__(self, item):
        if isinstance(item, str):
            if hasattr(self, item):
                return getattr(self, item)
        elif isinstance(item, (int, slice)):
            return super().__getitem__(item)
        raise IndexError(f'No Index {item} found in the dataclass.')

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key in [f.name for f in fields(self)]:
                if key not in self.keys():
                    super().__setattr__(key, value)
                    self.reconstruct()
                elif id(getattr(self, key)) != id(value):
                    super().__setattr__(key, value)
                    super().__setitem__(self.keys().index(key), value)
            else:
                super().__setattr__(key, value)
        elif isinstance(key, int):
            super().__setitem__(key, value)
            key_name = self.keys()[key]
            super().__setattr__(key_name, value)

    def __setattr__(self, key, value):
        if getattr(self, 'post_init', False):
            return self.__setitem__(key, value)
        else:
            return super().__setattr__(key, value)

    def keys(self):
        return [f.name for f in fields(self) if getattr(self, f.name) is not None]


