import os
import json
import time
import numpy as np
from tqdm import tqdm
from pathlib import Path
from copy import deepcopy, copy
from functools import partial
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Union, List, Mapping, Tuple

import torch
from torch import nn
from torch import distributed as dist
from torch.nn import DataParallel
from torch.utils.data import DataLoader, Dataset, DistributedSampler, default_collate

from weathon.dl.base import BaseMetric
from weathon.dl.base.loss import BaseLoss
from weathon.dl.base.model import TorchModel, BaseModel,BaseOutput
from weathon.dl.base.processor import BaseProcessor
from weathon.dl.base.hook import BaseHook
from weathon.dl.base.dataset import TorchCustomDataset
from weathon.dl.registry.registry import build_from_cfg, default_group

from weathon.dl.utils.logger import LogBuffer
from weathon.dl.utils.logger import get_logger
from weathon.dl.registry import (
    HOOKS,
    build_model,
    build_metric,
    build_optimizer,
    build_lr_scheduler,
    build_custom_dataset,
    build_preprocessor,
    build_parallel,
    build_custom_datacollator, TRAINERS
)
from weathon.dl.utils.data_utils import to_device
from weathon.dl.utils.device import create_device
from weathon.dl.utils.fileio.file_utils import func_receive_dict_inputs
from weathon.utils.fileio import ensure_directory
from weathon.dl.utils.fileio.format.json_utils import JSONIteratorEncoder
from weathon.dl.utils.config.config import Config, ConfigDict
from weathon.dl.utils.constants import ModeKeys, TrainerStages, Priority, get_priority, DEFAULT_HOOKS_CONFIG, \
    HOOK_KEY_CHAIN_MAP, DistributedParallelType, LogKeys, Tasks, Datasets
from weathon.dl.utils.torch_utils import set_random_seed, is_master, init_dist, get_dist_info, is_dist, get_local_rank
from weathon.dl.registry.loss import build_loss
from weathon.dl.utils.trainer_utils import worker_init_fn


# logger = get_logger()


class BaseTrainer(ABC):
    """ 训练器基类, 不可被实例化
    训练器基类定义一些必要的接口, 提供默认的实现方法, 比如解析配置文件和命令行参数.
    """

    def __init__(self, cfg_file: Union[str, Path], arg_parse_fn: Optional[Callable] = None):
        """ Trainer basic init, should be called in derived class

        Args:
            cfg_file: 配置文件路径.
            arg_parse_fn: Same as ``parse_fn`` in :obj:`Config.to_args`.
        """
        self.cfg = Config.from_file(cfg_file)
        if arg_parse_fn:
            self.args = self.cfg.to_args(arg_parse_fn)
        else:
            self.args = None

        self.launcher = self.cfg.get("launcher", None)
        self.distribute = self.cfg.get("distribute", "dp")
        self.device_ids = self.cfg.get("device_ids", [])



        # The parallel_groups field will be initialized in the hooks' after_init stage.
        self.parallel_groups = {}

        self.log_buffer = LogBuffer()
        self.visualization_buffer = LogBuffer()
        self.timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        # 训练工作目录
        self.work_dir = self.cfg.safe_get("train.work_dir", "./work_dir")
        ensure_directory(self.work_dir)

        # logger
        log_file = os.path.join(self.work_dir, '{}.log'.format(self.timestamp))
        log_level = self.cfg.get('log_level', 'INFO').upper()
        self.logger = get_logger(log_file=log_file, log_level=log_level)

        # for DP
        self._prepare_device_dp()

    @abstractmethod
    def train(self, *args, **kwargs):
        """ 训练处过程
        训练过程的处理应该根据特定任务和模型进行具体实现, 相关参数应该在"__init__"函数中初始化,在该函数中应用
        """
        raise NotImplementedError("train method is not implement !")

    @abstractmethod
    def evaluate(self, checkpoint_path: str, *args, **kwargs) -> Dict[str, float]:
        """ 评估过程
        评估过程的处理应该根据特定任务和模型进行具体实现, 相关参数应该在"__init__"函数中初始化,在该函数中应用
        """
        pass

    @property
    def dp_group(self):
        """
        Get the data parallel group.
        """
        return self.parallel_groups[DistributedParallelType.DP]

    @property
    def tp_group(self):
        """
        Get the tensor parallel group.
        """
        return self.parallel_groups[DistributedParallelType.TP]

    @property
    def pp_group(self):
        """
        Get the pipeline parallel group.
        """
        return self.parallel_groups[DistributedParallelType.PP]

    def is_dp_group_available(self):
        """
        Get whether the data parallel group is initialized.
        """
        return DistributedParallelType.DP in self.parallel_groups

    def is_tp_group_available(self):
        """
        Get whether the tensor parallel group is initialized.
        """
        return DistributedParallelType.TP in self.parallel_groups

    def is_pp_group_available(self):
        """
        Get whether the pipeline parallel group is initialized.
        """
        return DistributedParallelType.PP in self.parallel_groups

    def to_parallel(self, model) -> Union[nn.Module, TorchModel]:
        # config format to reserve custom ddp
        if self.cfg.get('parallel', None):
            dp_cfg = deepcopy(self.cfg['parallel'])
            dp_cfg.update(dict(module=model, device_ids=[torch.cuda.current_device()]))
            return build_parallel(dp_cfg)
        dp_cfg = dict(type='DistributedDataParallel', module=model, find_unused_parameters=True,
                      device_ids=[torch.cuda.current_device()], process_group=self.dp_group)
        return build_parallel(dp_cfg)

    def unwrap_module(self, model) -> Union[nn.Module, TorchModel]:
        """Unwrap the model until it's a naked nn.Module."""
        if hasattr(model, 'module'):
            return self.unwrap_module(model.module)
        else:
            assert isinstance(model, torch.nn.Module), "model is not instance torch.nn.Module"
            return model

    def merge_default_hooks_into_cfg(self):
        """将默认配置与输入配置合并
        """
        if self.launcher is not None and not self.cfg.safe_get('train.hooks.DDPHook') \
                and self.distribute.lower() == 'ddp':
            # A logic to fit the current code
            # Put a DDPHook in if launcher is provided.
            if 'hooks' not in self.cfg.train:
                self.cfg.train['hooks'] = ConfigDict([])
            self.cfg.train['hooks'].append({
                'type': 'DDPHook',
                'launcher': self.launcher
            })
        #  如果"BestCkptSaverHook"存在于输入配置,该函数将弹出默认的"CheckpointHook"
        self.cfg.merge_from_dict(DEFAULT_HOOKS_CONFIG, force=False)

    def update_cfg(self) -> Config:
        def _hook_split(hook: Dict) -> Tuple[str, Dict]:
            hook = hook.copy()
            return hook.pop('type'), hook

        if 'hooks' not in self.cfg.train:
            return self.cfg
        key_chain_map = {}
        for hook in self.cfg.train.hooks:
            if not hook:
                continue
            key, value = _hook_split(hook)
            if key not in HOOK_KEY_CHAIN_MAP:
                continue
            key_chain_map[HOOK_KEY_CHAIN_MAP[key]] = value
            hook.clear()
        self.cfg.train.hooks = list(filter(bool, self.cfg.train.hooks))
        self.cfg.merge_from_dict(key_chain_map)
        # return cfg

    def merge_hooks(self) -> List[Dict]:

        def _check_basic_hook(cfg: Config, key_chain: str, hook_type: str) -> bool:
            if cfg.safe_get(key_chain) is None:
                return False
            hooks = list(
                filter(lambda hook: hook['type'] == hook_type,
                       getattr(cfg.train, 'hooks', [])))
            assert len(hooks) == 0, f'The key_chain {key_chain} and the traditional hook ' \
                                    f'cannot exist at the same time, ' \
                                    f'please delete {hook_type} in the configuration file.'
            return True

        def _key_chain_to_hook(cfg: Config, key_chain: str,
                               hook_type: str) -> Optional[Dict]:
            if not _check_basic_hook(cfg, key_chain, hook_type):
                return None
            hook_params: Dict = cfg.safe_get(key_chain)
            hook = {'type': hook_type}
            hook.update(hook_params)
            return hook

        hooks = getattr(self.cfg.train, 'hooks', []).copy()
        for hook_type, key_chain in HOOK_KEY_CHAIN_MAP.items():
            hook = _key_chain_to_hook(self.cfg, key_chain, hook_type)
            if hook is not None:
                hooks.append(hook)
        return hooks

    def get_device(self, device=None):
        """Get the device information.

        Args:
            device: The input device info.

        Returns:
            device_name: The final device name.
        """
        device_name = device if device is not None else 'gpu'
        if is_dist():
            local_rank = get_local_rank()
            device_name = f'cuda:{local_rank}'

        return create_device(device_name)

    # def _save_checkpoint(self, epoch, save_best=False):
    #     """
    #     Saving checkpoints
    #
    #     :param epoch: current epoch number
    #     :param log: logging information of the epoch
    #     :param save_best: if True, rename the saved checkpoint to 'model_best.pth'
    #     """
    #     arch = type(self.model).__name__
    #     state = {
    #         'arch': arch,
    #         'epoch': epoch,
    #         'state_dict': self.model.state_dict(),
    #         'optimizer': self.optimizer.state_dict(),
    #         'monitor_best': self.mnt_best,
    #         'config': self.config
    #     }
    #     filename = str(self.checkpoint_dir / 'checkpoint-epoch{}.pth'.format(epoch))
    #     torch.save(state, filename)
    #     logger.info("Saving checkpoint: {} ...".format(filename))
    #
    #     if save_best:
    #         self.best_path = str(self.checkpoint_dir / 'model_best.pth')
    #         logger.info("Saving current best: {} ...".format(self.best_path))
    #         torch.save(state, self.best_path)
    # def _resume_checkpoint(self, resume_path):
    #     """
    #     Resume from saved checkpoints
    #
    #     :param resume_path: Checkpoint path to be resumed
    #     """
    #     resume_path = str(resume_path)
    #     logger.info("Loading checkpoint: {} ...".format(resume_path))
    #     checkpoint = torch.load(resume_path)
    #     # self.start_epoch = checkpoint['epoch']
    #     # self.mnt_best = checkpoint['monitor_best']
    #
    #     # load architecture params from checkpoint.
    #     # if checkpoint['config']['model'] != self.config['model']:
    #     #     self.logger.warning("Warning: Architecture configuration given in config file is different from that of "
    #     #                         "checkpoint. This may yield an exception while state_dict is being loaded.")
    #     self.model.load_state_dict(checkpoint['state_dict'])
    #
    #     # load optimizer state from checkpoint only when optimizer type is not changed.
    #     if checkpoint['config']['optimizer']['type'] != self.config['optimizer']['type']:
    #         self.logger.warning("Warning: Optimizer type given in config file is different from that of checkpoint. "
    #                             "Optimizer parameters not being resumed.")
    #     else:
    #         self.optimizer.load_state_dict(checkpoint['optimizer'])
    #
    #     self.logger.info("Checkpoint loaded. Resume training from epoch {}".format(self.start_epoch))


#@TRAINERS.register_module(group_key=Tasks.ocr_detection, module_name=Datasets.icdar2015_ocr_detection)
class ConfigTrainer(BaseTrainer):
    def __init__(self, cfg_file: Union[str, Path], arg_parse_fn: Optional[Callable] = None, **kwargs):
        super().__init__(cfg_file, arg_parse_fn)

        # 根据 cfg_modify_fn 重建 self.cfg
        cfg_modify_fn = kwargs.get("cfg_modify_fn", None)
        self.cfg = cfg_modify_fn(self.cfg) if cfg_modify_fn else self.cfg

        self._seed = kwargs.get("seed", self.cfg.get("seed", 123))
        set_random_seed(self._seed)
        self._mode = ModeKeys.TRAIN
        self._hooks: List[BaseHook] = []
        self._epoch = 0
        self._iter = 0
        self._inner_iter = 0
        self._stop_training = False
        self._metric_values = None
        self._compile = kwargs.get("compile", self.cfg.get("compile", False))
        self._max_epochs = kwargs.get("max_epochs", self.cfg.safe_get("train.max_epochs", 2))
        self._train_iters_per_epoch = kwargs.get('train_iters_per_epoch',
                                                 self.cfg.safe_get('train.train_iters_per_epoch',
                                                                   np.iinfo(np.int32).max))
        self._eval_iters_per_epoch = kwargs.get('val_iters_per_epoch',
                                                self.cfg.safe_get('evaluation.val_iters_per_epoch',
                                                                  np.iinfo(np.int32).max))
        self.use_fp16 = kwargs.get("use_fp16", self.cfg.get("use_fp16", False))

        # 训练组件
        # data
        self.train_preprocessor = self.build_preprocessor(self.cfg.preprocessor.train, mode=ModeKeys.TRAIN)
        self.eval_preprocessor = self.build_preprocessor(self.cfg.preprocessor.eval, mode=ModeKeys.EVAL)

        self.train_dataset = self.build_dataset(self.cfg.dataset.train, preprocessor=self.train_preprocessor)
        self.eval_dataset = self.build_dataset(self.cfg.dataset.eval, preprocessor=self.eval_preprocessor)

        # model
        self.model = self.build_model(self.cfg.model)

        # dp
        if self.device.type == 'cuda' and len(self.device_ids) > 1:
            self.model = DataParallel(self.model, device_ids=self.device_ids)
        self.model.to(self.device)
        # optimizer
        self.optimizer = self.build_optimizer(self.cfg.optimizer)
        # lr scheduler
        self.lr_scheduler = self.build_lr_scheduler(self.cfg.lr_scheduler)

        # metrics for evaluation
        self.metric_classes = self.build_metric_classes(self.cfg.metrics)

        # hooks
        # 1 合并默认hook配置与cfg到hook配置合并
        self.merge_default_hooks_into_cfg()
        # 2 将hook更新到cfg到属性参数中
        self.update_cfg()
        # 3 从cfg中提取出hook并实例化hook
        hooks = self.merge_hooks()
        self.register_hook_from_cfg(hooks)

        self.invoke_hook(TrainerStages.after_init)

        # _dist represents for if dp is initialized and its world_size > 1
        self._dist = self.is_dp_group_available() and dist.get_world_size(self.dp_group) > 1
        self.print_cfg()

    @property
    def dist(self):
        return self._dist

    @property
    def seed(self):
        return self._seed

    @property
    def mode(self):
        return self._mode

    @property
    def hooks(self) -> List[BaseHook]:
        return self._hooks

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def iter(self) -> int:
        return self._iter

    @property
    def inner_iter(self) -> int:
        return self._inner_iter

    @property
    def max_epochs(self):
        return self._max_epochs

    @property
    def max_iters(self):
        """int: Maximum training iterations."""
        return self._max_epochs * self.iters_per_epoch

    def _prepare_device_dp(self):
        """
        setup GPU device if available
        """

        n_gpu = torch.cuda.device_count()
        n_gpu_use = len(self.device_ids)

        if n_gpu_use > 0 and n_gpu == 0:
            self.logger.warning("Warning: There\'s no GPU available on this machine,"
                                "training will be performed on CPU.")
            n_gpu_use = 0
        if n_gpu_use > n_gpu:
            self.logger.warning("Warning: The number of GPU\'s configured to use is {}, but only {} are available "
                                "on this machine.".format(n_gpu_use, n_gpu))
            n_gpu_use = n_gpu
        self.device = torch.device('cuda:{}'.format(self.device_ids[0]) if n_gpu_use > 0 else 'cpu')

    @property
    def iters_per_epoch(self):
        def _get_data_len(dataloader):
            try:
                return len(dataloader)
            except Exception as e:
                self.logger.error(e)
                raise ValueError(
                    'Please implement ``__len__`` method for your dataset, '
                    'or add `train_iters_per_epoch` and `train_iters_per_epoch` '
                    'to your configuration file or kwargs')

        # train_iters_per_epoch or eval_iters_per_epoch should be little or equal dataloader length
        if self.mode == ModeKeys.TRAIN:
            return min(self._train_iters_per_epoch, _get_data_len(self.train_dataloader))
        elif self.mode == ModeKeys.EVAL:
            return min(self._eval_iters_per_epoch, _get_data_len(self.eval_dataloader))

    @property
    def metric_values(self):
        return self._metric_values

    def init_dist(self, launcher=None):
        """Init dist and returns the dist information.

        Args:
            launcher: The launcher info.

        Returns:
            _dist: If world_size is greater than 1.
        """
        if launcher is not None:
            init_dist(launcher)

        _, world_size = get_dist_info()
        _dist = world_size > 1
        return _dist

    def print_cfg(self):
        if is_master():
            cfg = deepcopy(self.cfg)
            cfg.train.work_dir = self.work_dir
            self.logger.info('==========================Training Config Start==========================')
            self.logger.info(json.dumps(cfg._cfg_dict, indent=4, cls=JSONIteratorEncoder))
            self.logger.info('===========================Training Config End===========================')

    def get_hook_info(self) -> str:
        # Get hooks info in each stage
        stage_hook_map: Dict[str, list] = {stage: [] for stage in BaseHook.stages}
        for hook in self.hooks:
            try:
                priority = Priority(hook.PRIORITY).name  # type: ignore
            except Exception:
                priority = Priority.NORMAL  # type: ignore
            classname = hook.__class__.__name__
            hook_info = f'({priority:<12}) {classname:<35}'
            if hasattr(hook, 'get_triggered_stages'):
                for trigger_stage in hook.get_triggered_stages():
                    stage_hook_map[trigger_stage].append(hook_info)

        stage_hook_infos = []
        for stage in BaseHook.stages:
            hook_infos = stage_hook_map[stage]
            if len(hook_infos) > 0:
                info = f'Stage: {stage}:\n    '
                info += '\n    '.join(hook_infos)
                info += '\n -------------------- '
                stage_hook_infos.append(info)
        stage_hook_infos = '\n'.join(stage_hook_infos)
        return stage_hook_infos

    def print_hook_info(self):
        if is_master() and not getattr(self, '_hook_info_printed', False):
            self.logger.info(self.get_hook_info())
            self._hook_info_printed = True

    def get_hook(self, cls):
        return [h for h in self._hooks if h.__class__ == cls]

    def visualization(self, batch_result, dataset, **kwargs):
        """ visualization function for evaluation results.

        Examples:
            >>> # draw list of images as numpy array
            >>> images = draw_images(num_of_visualization)

            >>> # set displayed name for each image
            >>> filenames = get_image_display_names()
            >>> vis_results = {'images': images, 'filenames' : filenames}

            >>> # visualization results will be displayed in group named eva_vis
            >>> self.visualization_buffer.output['eval_vis'] = vis_results

        Args:
            results (list(dict)):  a list of result dict.
            dataset (Dataset): torch dataset object to access original data.
        """
        raise NotImplementedError('visualization for evaluation will be supported in the future')

    def register_hook(self, hook: BaseHook) -> None:
        """Register a hook into the hook list.

        The hook will be inserted into a priority queue, with the specified
        priority (See :class:`Priority` for details of priorities).
        For hooks with the same priority, they will be triggered in the same
        order as they are registered.

        Args:
            hook (:obj:`Hook`): The hook to be registered.
        """
        # insert the hook to a sorted list
        inserted = False
        for i in range(len(self._hooks) - 1, -1, -1):
            p = hook.PRIORITY if hasattr(hook, 'PRIORITY') else Priority.NORMAL
            p_i = self._hooks[i].PRIORITY if hasattr(self._hooks[i], 'PRIORITY') else Priority.NORMAL

            if get_priority(p) > get_priority(p_i):
                self._hooks.insert(i + 1, hook)
                inserted = True
                break
        if not inserted:
            self._hooks.insert(0, hook)

    def register_hook_from_cfg(self, hook_cfg: List) -> List:
        """Register a hook from its cfg.

        Args:
            hook_cfg (dict): Hook config. It should have at least keys 'type'
              and 'priority' indicating its type and priority.

        Note:
            The specific hook class to register should not use 'type' and
            'priority' arguments during initialization.

        Returns:
            A list of instances of registered hooks.
        """
        hook_cfg = hook_cfg.copy()
        assert isinstance(hook_cfg, list), "hook config type must be list"
        hooks = []
        for cfg_i in hook_cfg:
            hook = build_from_cfg(cfg_i, HOOKS)
            self.register_hook(hook)
            hooks.append(hook)
        return hooks

    def invoke_hook(self, fn_name: str) -> None:
        """Call all hooks.

        Args:
            fn_name (str): The function name in each hook to be called, such as
                "before_train_epoch".
        """
        for hook in self.hooks:
            if hasattr(hook, fn_name):
                getattr(hook, fn_name)(self)

    def build_preprocessor(self, preprocessor_cfg: ConfigDict, mode: str = ModeKeys.TRAIN) -> BaseProcessor:
        """构建数据预处理器
        """
        preprocessor = build_preprocessor(preprocessor_cfg, task_name=preprocessor_cfg.task)
        preprocessor.mode = mode
        return preprocessor

    def build_dataset(self, dataset_cfg: ConfigDict, **kwargs) -> TorchCustomDataset:
        dataset = build_custom_dataset(dataset_cfg, task_name=dataset_cfg.task, default_args=kwargs)
        dataset.trainer = self
        return dataset

    def build_model(self, model_cfg: ConfigDict, **kwargs) -> BaseModel:
        model = build_model(model_cfg, task_name=model_cfg.task, default_args=kwargs)
        if not isinstance(model, nn.Module) and hasattr(model, 'model'):
            return model.model
        elif isinstance(model, nn.Module):
            return model

    def build_optimizer_hook(self, optimizer_cfg: ConfigDict, **kwargs):
        optim_options = optimizer_cfg.pop('options', {})
        optim_hook = self.cfg.train.get('optimizer_hook', {})
        if optim_hook:
            self.register_hook_from_cfg([optim_hook])

        if optim_hook.get('type') in ('TorchAMPOptimizerHook', 'ApexAMPOptimizerHook'):
            self.use_fp16 = False
        if not optim_hook or optim_hook.get('type') in ('TorchAMPOptimizerHook', 'ApexAMPOptimizerHook'):
            optim_hook.pop('type', None)
            optim_options = {**optim_options, **optim_hook}

        if optim_options is not None:
            self.register_hook_from_cfg([dict(type='OptimizerHook', **optim_options)])
        if self.use_fp16:
            self.register_hook_from_cfg([dict(type='TorchAMPOptimizerHook', **optim_options)])

    def build_optimizer(self, optimizer_cfg: ConfigDict, **kwargs):
        self.build_optimizer_hook(optimizer_cfg)
        try:
            return build_optimizer(self.unwrap_module(self.model), cfg=optimizer_cfg, default_args=kwargs)
        except KeyError as e:
            self.logger.error(
                f"Build optimizer error, the optimizer {optimizer_cfg} is a torch native component, "
                f'please check if your torch with version: {torch.__version__} matches the config.'
            )
            raise e

    def build_lr_scheduler_hook(self, lr_scheduler_cfg: Config, **kwargs):
        lr_options = lr_scheduler_cfg.pop('options', {})
        lr_hook = self.cfg.train.get('lr_scheduler_hook', {})
        if lr_hook:
            self.register_hook_from_cfg([lr_hook])

        if not lr_hook or lr_hook.get('type') == 'PlateauLrSchedulerHook':
            lr_hook.pop('type', None)
            lr_options = {**lr_options, **lr_hook}

        if lr_options:
            self.register_hook_from_cfg([dict(type='LrSchedulerHook', **lr_options)])

    def build_lr_scheduler(self, lr_scheduler_cfg: ConfigDict, **kwargs):
        self.build_lr_scheduler_hook(lr_scheduler_cfg)
        assert self.optimizer is not None, "self.optimizer should not be None"
        try:
            return build_lr_scheduler(cfg=lr_scheduler_cfg, default_args={'optimizer': self.optimizer, **kwargs})
        except KeyError as e:
            self.logger.error(
                f'Build lr_scheduler error, the lr_scheduler {lr_scheduler_cfg} is a torch native component, '
                f'please check if your torch with version: {torch.__version__} matches the config.'
            )
            raise e

    def build_metric_classes(self, metrics_cfg: Union[List, Dict], **kwargs) -> List[BaseMetric]:
        task_name = metrics_cfg.get("task", default_group) if isinstance(metrics_cfg, Dict) else default_group
        metric_fns = [build_metric(metric_cfg, task_name=task_name, default_args=kwargs) for metric_cfg in metrics_cfg]
        return metric_fns

    def build_loss_fn(self, loss_cfg: Config, **kwargs) -> BaseLoss:
        loss_fn = build_loss(loss_cfg, task_name=loss_cfg.task, default_args=kwargs)
        return loss_fn


    def build_data_collator(self,data_collator_cfg:ConfigDict, **kwargs):
        if not data_collator_cfg:
            return default_collate
        try:
            data_collator = build_custom_datacollator(data_collator_cfg, task_name=data_collator_cfg.task, default_args=kwargs)
        except TypeError:
            return default_collate
        return data_collator



    def build_dataloader(self, dataset: TorchCustomDataset, dataloader_cfg: ConfigDict, mode: str = ModeKeys.TRAIN,
                         **kwargs):
        rank = 0
        world_size = 1
        if self.is_dp_group_available():
            rank = torch.distributed.get_rank(self.dp_group)
            world_size = torch.distributed.get_world_size(self.dp_group)

        sampler = kwargs.pop('sampler', None)
        batch_size = kwargs.get("batch_size", dataloader_cfg.get("batch_size_per_gpu", 8))
        num_workers = kwargs.get("num_workers", dataloader_cfg.get("workers_per_gpu", 0))
        drop_last = kwargs.get("drop_last", dataloader_cfg.get("drop_last", False))
        shuffle = kwargs.get("shuffle", dataloader_cfg.get("shuffle", (mode == ModeKeys.TRAIN)))
        pin_memory = kwargs.get("pin_memory", dataloader_cfg.get("pin_memory", False))

        if sampler is None and self.dist and not isinstance(dataset, torch.utils.data.IterableDataset):
            sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=shuffle)
        else:
            sampler = None

        init_fn = partial(worker_init_fn, num_workers=num_workers, rank=rank, seed=self.seed) if self.seed else None
        collate_fn = self.build_data_collator(dataloader_cfg.get("collator", None))

        dataloader = DataLoader(dataset=dataset,
                                batch_size=batch_size,
                                shuffle=shuffle,
                                sampler=sampler,
                                num_workers=num_workers,
                                collate_fn=collate_fn,
                                pin_memory=pin_memory,
                                drop_last=drop_last,
                                worker_init_fn=init_fn,
                                )

        return dataloader

    def set_checkpoint_file_to_hook(self, checkpoint_path, load_all_state, strict):
        if checkpoint_path is not None:
            from weathon.dl.hooks import LoadCheckpointHook
            load_ckpt_hooks = list(filter(lambda hook: isinstance(hook, LoadCheckpointHook), self.hooks))
            if len(load_ckpt_hooks) == 0:
                load_ckpt_hook = LoadCheckpointHook()
                self.register_hook(load_ckpt_hook)
                load_ckpt_hooks.append(load_ckpt_hook)
            load_ckpt_hooks[0].checkpoint_file = checkpoint_path
            load_ckpt_hooks[0].load_all_state = load_all_state
            load_ckpt_hooks[0].strict = strict

    def train(self, *args, **kwargs):
        checkpoint_path = kwargs.get("checkpoint_path", self.cfg.safe_get("train.checkpoint.path", None))
        load_all_state = kwargs.get("load_all_state", self.cfg.safe_get("train.checkpoint.load_all_state",False))
        strict = kwargs.get("strict", self.cfg.safe_get("train.checkpoint.strict",False))
        self.train_dataloader = self.build_dataloader(self.train_dataset, self.cfg.safe_get("train.dataloader"),
                                                      ModeKeys.TRAIN)
        self._mode = ModeKeys.TRAIN
        self.data_loader = self.train_dataloader
        self.print_hook_info()
        self.set_checkpoint_file_to_hook(checkpoint_path, load_all_state, strict)
        self.train_loop(self.train_dataloader)

    def train_loop(self, dataloader):
        self.invoke_hook(TrainerStages.before_run)
        self.model.train()
        for _ in range(self._epoch, self._max_epochs):
            self.invoke_hook(TrainerStages.before_train_epoch)
            for batch_idx, data_batch in enumerate(dataloader):
                if batch_idx < self.inner_iter:  # 用于checkpoint
                    continue
                data_batch = to_device(data_batch, self.device)
                self.data_batch = data_batch
                self._inner_iter = batch_idx
                self.invoke_hook(TrainerStages.before_train_iter)
                self.train_outputs = self.train_step(self.model, data_batch)
                self.invoke_hook(TrainerStages.after_train_iter)

                del self.data_batch
                self._iter += 1
                self._mode = ModeKeys.TRAIN

                if batch_idx >= self.iters_per_epoch:
                    break
            self.invoke_hook(TrainerStages.after_train_epoch)
            self._inner_iter = 0
            self._epoch += 1
            if self._stop_training:
                break
        self.invoke_hook(TrainerStages.after_run)

    def train_step(self, model: Union[TorchModel, nn.Module], inputs):
        model.train()
        self._mode = ModeKeys.TRAIN
        train_outputs = model(inputs)

        if isinstance(train_outputs, BaseOutput):
            train_outputs = train_outputs.to_dict()
        if not isinstance(train_outputs, dict):
            raise TypeError('"model.forward()" must return a dict')

        # add model output info to log
        if 'log_vars' not in train_outputs:
            default_keys_pattern = ['loss']
            match_keys = set([])
            for key_p in default_keys_pattern:
                match_keys.update([key for key in train_outputs.keys() if key_p in key])

            log_vars = {}
            for key in match_keys:
                value = train_outputs.get(key, None)
                if value is not None:
                    log_vars.update({key: value.mean().item()})
            self.log_buffer.update(log_vars)
        else:
            self.log_buffer.update(train_outputs['log_vars'])

        return train_outputs

    def evaluation_step(self, model, inputs):
        model.eval()
        self._mode = ModeKeys.EVAL
        with torch.no_grad():
            result = self.unwrap_module(model)(inputs)
        return result

    def evaluation_loop(self, dataloader):
        vis_closure = None

        if hasattr(self.cfg.evaluation, "visualization"):
            vis_cfg = self.cfg.evaluation.visualization
            vis_closure = partial(self.visualization, dataset=self.eval_dataset, **vis_cfg)

        self.invoke_hook(TrainerStages.before_val)
        with tqdm(total=self.iters_per_epoch, desc="evaluation iterations") as pbar:
            for batch_idx, batch_data in enumerate(dataloader):
                batch_data = to_device(batch_data, self.device)
                self.invoke_hook(TrainerStages.before_val_iter)
                self.eval_outputs = self.evaluation_step(self.model, batch_data)
                for metric_cls in self.metric_classes or []:
                    metric_cls.add(self.eval_outputs, batch_data)
                if vis_closure:
                    vis_closure(self.eval_outputs)

                self.invoke_hook(TrainerStages.after_val_iter)

                if batch_idx >= self.iters_per_epoch:
                    break
                pbar.update()

        self.invoke_hook(TrainerStages.after_val)

        metric_values = {}
        if is_master():
            for metric_cls in self.metric_classes:
                metric_values.update(metric_cls.evaluate())

        return metric_values

    def evaluate(self, *args, **kwargs) -> Dict[str, float]:
        self._mode = ModeKeys.EVAL
        self.print_hook_info()
        checkpoint_path = kwargs.get("checkpoint_path", None)
        strict = kwargs.get("strict", None)
        if checkpoint_path is not None:
            from weathon.dl.hooks import LoadCheckpointHook
            LoadCheckpointHook.load_checkpoint(checkpoint_path, self, strict=strict)
        self.eval_dataloader = self.build_dataloader(self.eval_dataset, self.cfg.safe_get("evaluation.dataloader"),
                                                     ModeKeys.EVAL)
        self.data_loader = self.eval_dataloader
        for metric_cls in self.metric_classes:
            metric_cls.trainer = self
        metric_values = self.evaluation_loop(self.eval_dataloader)
        self._metric_values = metric_values
        return metric_values

    def predict(self, inputs: Union[List, Dict]) -> Dict:
        return self._predict_batch(inputs) if isinstance(inputs, List) else self._predict_item(inputs)

    def _predict_item(self, inputs: Dict) -> Dict:
        pass

    def _predict_batch(self, inputs: List) -> Dict:
        pass
