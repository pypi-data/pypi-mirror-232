import numpy as np
from functools import partial
import torch
from torch.utils.data import DataLoader
from packaging import version
from weathon.dl.base.model import TorchModel, BaseModel,BaseOutput
from typing import Union
from torch import nn

from weathon.dl.base import TorchCustomDataset
from weathon.dl.base.trainer import ConfigTrainer
from weathon.dl.registry import TRAINERS
from weathon.dl.utils.config.config import ConfigDict
from weathon.dl.utils.constants import Tasks, ModeKeys, Datasets, TrainerStages,LogKeys
from weathon.dl.utils.dataset.collate_fns.cv.ocr_collate_fn import DetCollectFN
from weathon.dl.registry import LR_SCHEDULER,build_lr_scheduler
from weathon.dl.utils.trainer_utils import worker_init_fn
from weathon.dl.utils.data_utils import to_device


from torch.optim import lr_scheduler

if version.parse(torch.__version__) < version.parse('2.0.0.dev'):
    from torch.optim.lr_scheduler import _LRScheduler
else:
    from torch.optim.lr_scheduler import LRScheduler as _LRScheduler



@LR_SCHEDULER.register_module(module_name='DBLrScheduler')
class DBLrScheduler(_LRScheduler):

    def __init__(self, optimizer, base_lr, last_epoch=-1, total_epochs=1200, factor=0.9,  warmup_epochs=0, warmup_factor=1.0 / 3, verbose=False):
        self.base_lr = base_lr
        self.total_epochs = total_epochs
        self.factor = factor
        self.warmup_epochs = warmup_epochs
        self.warmup_factor = warmup_factor
        super().__init__(optimizer,last_epoch, verbose )

    def get_lr(self):
        if self.last_epoch < self.warmup_epochs:
            alpha = float(self.last_epoch) / self.warmup_epochs
            rate = self.warmup_factor * (1 - alpha) + alpha
        else:
            rate = np.power(1.0 - self.last_epoch / float(self.total_epochs + 1), self.factor)
        
        lr = rate * self.base_lr

        lr_list = []
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
            lr_list.append(param_group['lr'])
        return  lr_list


def adjust_learning_rate(optimizer, base_lr, iter, all_iters, factor, warmup_iters=0, warmup_factor=1.0 / 3):
    """
    带 warmup 的学习率衰减
    :param optimizer: 优化器
    :param base_lr: 开始的学习率
    :param iter: 当前迭代次数
    :param all_iters: 总的迭代次数
    :param factor: 学习率衰减系数
    :param warmup_iters: warmup 迭代数
    :param warmup_factor: warmup 系数
    :return:
    """
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    if iter < warmup_iters:
        alpha = float(iter) / warmup_iters
        rate = warmup_factor * (1 - alpha) + alpha
    else:
        rate = np.power(1.0 - iter / float(all_iters + 1), factor)
    lr = rate * base_lr
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr





@TRAINERS.register_module(group_key=Tasks.ocr_detection, module_name=Datasets.icdar2015_ocr_detection)
class OcrDetectionTrainer(ConfigTrainer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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

                self.log_buffer.output[LogKeys.LR] = adjust_learning_rate(self.optimizer, self.cfg.safe_get("lr_scheduler.base_lr", 0.0007), self.iter, self.iters_per_epoch * self.max_epochs, 0.9, self.iters_per_epoch * 3)
                
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

    def build_lr_scheduler(self, lr_scheduler_cfg: ConfigDict, **kwargs):
        pass
        # assert self.optimizer is not None, "self.optimizer should not be None"
        # try:
        #     return build_lr_scheduler(cfg=lr_scheduler_cfg, default_args={'optimizer': self.optimizer, **kwargs})
        # except KeyError as e:
        #     self.logger.error(
        #         f'Build lr_scheduler error, the lr_scheduler {lr_scheduler_cfg} is a torch native component, '
        #         f'please check if your torch with version: {torch.__version__} matches the config.'
        #     )
        #     raise e

