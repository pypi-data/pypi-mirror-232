import random
from typing import Optional

import numpy as np
import torch
from packaging import version

from weathon import __version__
from weathon.dl.base import BaseHook
from weathon.dl.hooks.checkpoint.checkpoint_processor import CheckpointProcessor
from weathon.dl.registry import HOOKS
from weathon.dl.utils.constants import Priority
from weathon.dl.utils.constants import Hooks
from weathon.dl.utils.logger import get_logger


@HOOKS.register_module(module_name=Hooks.LoadCheckpointHook)
class LoadCheckpointHook(BaseHook):
    """
    在训练或评估的时候加载模型 checkpoint 文件
    This hook does not need to be configured or saved in the config file.
    User should use it by:
    >>> trainers.train('some-checkpoint', load_all_state=True)
    or
    >>> trainers.evaluate('some-checkpoint')
    instead.

    Args:
        checkpoint_file (str): The checkpoint file to be loaded.
        load_all_state (bool): Load all states(optimizer, epoch, lr_scheduler, random_state, etc.) when loading old
            training state file or not. The model's state dict will only be loaded if False.
        strict (bool): If strict, any unmatched keys will cause an error.
    """

    PRIORITY = Priority.HIGH

    _should_save = False

    # From 1.3.1 version we split one pth file to two files: trainers state pth file/model state pth file.
    _TWO_PTH_FILE_VERSION = '1.3.1'

    def __init__(
        self,
        checkpoint_file: Optional[str] = None,
        load_all_state: Optional[bool] = True,
        strict: Optional[bool] = False,
    ):
        self.checkpoint_file = checkpoint_file
        self.rng_state = None
        self.need_load_rng_state = False
        self.load_all_state = load_all_state
        self.strict = strict
        self.processor = CheckpointProcessor()

    def before_run(self, trainer):
        if not hasattr(trainer, 'logger'):
            self.logger = get_logger()
        else:
            self.logger = trainer.logger

        if self.checkpoint_file is not None:
            meta = self.load_checkpoint(self.checkpoint_file, trainer,self.load_all_state, self.strict)
            self.rng_state = meta.get('rng_state')
            self.need_load_rng_state = self.load_all_state

    def before_train_iter(self, trainer):
        if self.need_load_rng_state:
            if self.rng_state is not None:
                random.setstate(self.rng_state['random'])
                np.random.set_state(self.rng_state['numpy'])
                torch.random.set_rng_state(self.rng_state['cpu'])
                if torch.cuda.is_available():
                    torch.cuda.random.set_rng_state_all(self.rng_state['cuda'])
                self.need_load_rng_state = False
            else:
                self.logger.info( # TODO
                    'Random state cannot be found in checkpoint file, this may cause a random data order or model initialization.'
                )

    @staticmethod
    def _restore_training_state(trainer, meta):
        trainer._epoch = meta.get('epoch', trainer._epoch)
        trainer._iter = meta.get('iter', trainer._iter)
        trainer._inner_iter = meta.get('inner_iter', trainer._inner_iter)

        i = 0
        for hook in trainer.hooks:
            if hasattr(hook, 'load_state_dict') and getattr(hook, '_should_save', True):
                key = f'{hook.__class__}-{i}'
                if key in meta:
                    hook.load_state_dict(meta.get(key, {}))
                else:
                    trainer.logger.warning(f'The state_dict of hook {hook.__class__} at index {i} is not found in the checkpoint file.')
                i += 1

    @classmethod
    def load_checkpoint(cls,
                        filename,
                        trainer,
                        load_all_state=True,
                        strict=False):
        """A static method to load checkpoint files.

        Args:
            filename(str): An absolute model bin file(pth or bin) or a dir path with a file prefix(like epoch_1).
            trainer(`EpochBasedTrainer`): The trainers instance.
            load_all_state(`bool`): Load all states including the trainers states.
            strict(`bool`): Load module state dict strictly.

        Returns:
            A dict containing the train states saved by `_create_training_state`
        """
        meta = cls().processor.load_checkpoints(filename, trainer,load_all_state, strict)
        if load_all_state:
            cls._restore_training_state(trainer, meta)

        if meta is not None:
            _version = meta.get('weathon', __version__)
            if _version is not None and version.parse(_version) < version.parse(LoadCheckpointHook._TWO_PTH_FILE_VERSION):
                trainer.logger.warning(
                    'The unique pth file is split into a model file and '
                    f'a trainers file since version {LoadCheckpointHook._TWO_PTH_FILE_VERSION},'
                    'consider re-training your model or '
                    'using a converting script to split the single pth file into two.'
                )
            trainer.logger.info(
                f'Checkpoint {filename} saving time: {meta.get("time")}, weathon version: {_version}'
            )
        return meta
