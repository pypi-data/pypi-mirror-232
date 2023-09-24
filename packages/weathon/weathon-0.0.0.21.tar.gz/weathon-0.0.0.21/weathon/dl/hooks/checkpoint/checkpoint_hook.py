import os
import os.path as osp
import random
import time
from typing import Optional

import numpy as np
import torch

from weathon.dl.base import BaseHook
from weathon.dl.hooks.checkpoint.checkpoint_processor import CheckpointProcessor
from weathon.dl.registry import HOOKS
from weathon.dl.utils.constants import Priority, ModelFile, LogKeys
from weathon.dl.utils.constants import Hooks
from weathon.dl.utils.logger import get_logger
from weathon.dl.utils.torch_utils import is_master


class CheckpointStrategy:
    by_epoch = 'by_epoch'
    by_step = 'by_step'
    no = 'no'


@HOOKS.register_module(module_name=Hooks.CheckpointHook)
class CheckpointHook(BaseHook):
    """Save checkpoints periodically.

    Args:
        save_strategy(str): The strategy to save checkpoint, can be `by_epoch`, `by_step` or `no`
        interval (int): The frequency to save model. If `by_epoch=True`,
            it means the number of epochs, else means the number of iterations
        save_dir (str): The directory to save checkpoints. If is None, use `trainers.work_dir`
        output_dir (str): The absolute path to save the output files for inference. If it's not specified,
            the default dir is `{sub_dir}/output`.
        save_last (bool): Whether to save the last checkpoint. Default: True.
        max_checkpoint_num (int): The max number of checkpoint files, default None which means never delete anything.
            If the number exceeding the limit, earlier checkpoints will be deleted first.
        kwargs:
            by_epoch (bool): Same with `save_strategy`, but has a higher priority, legacy argument.
            output_sub_dir (str): The folder under the `save_dir` to save the output checkpoint for inference.
                This argument is kept to fit the existing configs.
    """

    PRIORITY = Priority.LOW

    EVAL_RESULT_FILE = 'eval_result.txt'

    def __init__(self,
                 save_strategy: Optional[str] = CheckpointStrategy.by_epoch,
                 interval: Optional[int] = 0,
                 save_dir: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 save_last: Optional[bool] = True,
                 max_checkpoint_num: Optional[int] = None,
                 **kwargs):
        self.interval = interval
        self.save_dir = save_dir
        if 'by_epoch' in kwargs:
            self.save_strategy = CheckpointStrategy.by_epoch if kwargs['by_epoch'] else CheckpointStrategy.by_step
        else:
            self.save_strategy = save_strategy
        if 'output_sub_dir' in kwargs:
            self.output_sub_dir = kwargs['output_sub_dir']
            self.output_dir = None
        else:
            self.output_sub_dir = None
            self.output_dir = output_dir
        self.save_last = save_last
        self.rng_state = None
        self.tag = -1
        self.is_model_id = None
        self.max_checkpoint_num = max(int(max_checkpoint_num), 1) if max_checkpoint_num else None
        self.history_checkpoints = []
        self.processor = CheckpointProcessor()

    def set_processor(self, processor):
        """
        The checkpoint hook accepts a processors to finish the actual saving/deleting action.
        """
        self.processor = processor

    def before_run(self, trainer):
        """
        确定模型保存目录
        """
        self.tag = -1
        if not self.save_dir:
            self.save_dir = trainer.work_dir
        if not self.output_dir:
            self.output_dir = osp.join(self.save_dir, self.output_sub_dir if self.output_sub_dir else ModelFile.TRAIN_OUTPUT_DIR)

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)

        self.logger = trainer.logger if hasattr(trainer, 'logger') else get_logger()

        if is_master():
            output_dir = self.output_dir
            # only global master prepares the output folder
            self.processor.prepare_output(trainer, output_dir)
            self.logger.info(f'Checkpoints will be saved to {self.save_dir}')

    def generate_prefix(self, trainer, save_strategy):
        if save_strategy == CheckpointStrategy.by_epoch:
            return f'{LogKeys.EPOCH}_{trainer.epoch + 1}'
        else:
            return f'{LogKeys.ITER}_{trainer.iter + 1}'

    def _do_save(self, trainer, save_strategy):
        # prefix like 'epoch-1' or 'iter-1'
        prefix = self.generate_prefix(trainer, save_strategy)
        if self.processor.should_save_on_rank(trainer):
            if is_master():
                if save_strategy == CheckpointStrategy.by_epoch:
                    self.logger.info(f'Saving checkpoint at {trainer.epoch + 1} epoch')
                else:
                    self.logger.info(f'Saving checkpoint at {trainer.iter + 1} iter')
            self._save_checkpoint(trainer, prefix)

    def after_train_epoch(self, trainer):
        if self.save_strategy != CheckpointStrategy.by_epoch:
            return

        if self._should_save(trainer):
            self._do_save(trainer, CheckpointStrategy.by_epoch)

    def after_train_iter(self, trainer):
        if self.save_strategy != CheckpointStrategy.by_step:
            return

        if self._should_save(trainer):
            self._do_save(trainer, CheckpointStrategy.by_step)

    def save_evaluate_results(self, trainer):
        with open(os.path.join(self.output_dir, self.EVAL_RESULT_FILE), 'a') as f:
            f.write(f'{trainer.epoch}-{str(trainer.metric_values)}\n')

    def _save_checkpoint(self, trainer, prefix):
        """Save checkpoint files and remove obsolete ones
        """
        checkpoint_path_prefix = os.path.join(self.save_dir, prefix)
        meta = self._create_training_state(trainer)
        self.processor.save_checkpoints(trainer, checkpoint_path_prefix,self.output_dir, meta)
        self.save_evaluate_results(trainer)
        self.history_checkpoints.append(checkpoint_path_prefix)
        self._remove_obsolete_checkpoints(trainer)
        return prefix

    def _remove_obsolete_checkpoints(self, trainer):

        if self.max_checkpoint_num is not None and len(self.history_checkpoints) > self.max_checkpoint_num:
            history_checkpoints = [ckpt for ckpt in self.history_checkpoints]
            self.history_checkpoints.clear()
            for i, checkpoint_path_prefix in enumerate(history_checkpoints):
                if i < len(history_checkpoints) - self.max_checkpoint_num:
                    self.logger.info(f'deleting checkpoint: {checkpoint_path_prefix}')
                    self.processor.remove_checkpoints(trainer, checkpoint_path_prefix=checkpoint_path_prefix)
                else:
                    self.history_checkpoints.append(checkpoint_path_prefix)

    def _should_save(self, trainer):
        if self.save_strategy == CheckpointStrategy.by_epoch:
            check_last = self.is_last_epoch
            check_frequency = self.every_n_epochs
        elif self.save_strategy == CheckpointStrategy.by_step:
            check_last = self.is_last_iter
            check_frequency = self.every_n_iters
        else:
            return False

        if check_frequency(trainer, self.interval) or (self.save_last and check_last(trainer)):
            return True
        return False

    def _create_training_state(self, trainer):
        self.rng_state = {
            'random': random.getstate(),
            'numpy': np.random.get_state(),
            'cpu': torch.random.get_rng_state(),
            'cuda': torch.cuda.get_rng_state_all(),
        }

        # keep epoch/iter/inner_iter/random_state
        meta = {
            'epoch': trainer.epoch,
            'iter': trainer.iter + 1,
            'inner_iter': trainer.inner_iter + 1,
            'rng_state': self.rng_state,
        }

        # keep hooks state
        i = 0
        for hook in trainer.hooks:
            if hasattr(hook, 'state_dict') and getattr(hook, '_should_save', True):
                meta[f'{hook.__class__}-{i}'] = hook.state_dict()
                i += 1

        return meta


@HOOKS.register_module(module_name=Hooks.BestCkptSaverHook)
class BestCkptSaverHook(CheckpointHook):
    """
    Save best checkpoints hook.

    Args:
        metric_key (str): Metric key to compare rule for best score.
        save_best(bool): Save the best checkpoint, if set to False, this hook will have no effect.
        rule (str): Comparison rule for best score. Support "max" and "min". If rule is "max", the checkpoint
            at the maximum `metric_key` will be saved, If rule is "min", the checkpoint at the minimum `metric_key`
            will be saved.
        save_file_name: The manual specified saving file name.
        restore_best (bool): Whether to restore the best checkpoint after training.
        max_checkpoint_num (int): The max number of checkpoint files, default None which means never delete anything.
            If the number exceeding the limit, checkpoints with worse metric will be deleted, which is judged by the
            `rule` and `metric_key` arguments.

    The `BestCkptSaverHook` class accepts `output_sub_dir` and `output_dir` argument as its super class do.
    If neither of them are passed, the default value is `{save_dir}/output_best`.

    This class will not accept the `interval` or `save_strategy` or `by_epoch` argument, because the saving interval
    will follow the `EvaluationHook`.
    """

    PRIORITY = Priority.LOW
    rule_map = {'max': lambda x, y: x > y, 'min': lambda x, y: x < y}

    def __init__(self,
                 metric_key: str,
                 save_best: Optional[bool] = True,
                 rule: Optional[str] = 'max',
                 save_file_name: Optional[str] = None,
                 restore_best: Optional[bool] = False,
                 max_checkpoint_num: Optional[int] = 1,
                 **kwargs):
        assert rule in ['max', 'min'], 'Only support "max" or "min" rule now.'
        output_kwargs = {}
        if 'output_sub_dir' not in kwargs and 'output_dir' not in kwargs:
            output_kwargs['output_sub_dir'] = ModelFile.TRAIN_BEST_OUTPUT_DIR
        kwargs.pop('interval', None)
        kwargs.pop('save_strategy', None)
        super().__init__(
            max_checkpoint_num=max_checkpoint_num,
            **kwargs,
            **output_kwargs,
        )
        self.save_best = save_best
        self.metric_key = metric_key
        self.rule = rule
        self._best_metric = None
        self._best_ckpt_file = None
        self.save_file_name = save_file_name
        self.restore_best = restore_best
        self.history_checkpoints = set()

    def after_train_epoch(self, trainer):
        from weathon.dl.hooks import EvaluationHook
        eval_hook = trainer.get_hook(EvaluationHook)
        if len(eval_hook) == 0:
            self.logger.error(
                'Trying to save the best checkpoint, but there is no evaluation, skipping.'
            )

        if eval_hook[0].last_eval_tag == (
                'epoch', trainer.epoch) and self._should_save(trainer):
            self._do_save(trainer, 'by_epoch')

    def after_train_iter(self, trainer):
        from weathon.dl.hooks import EvaluationHook
        eval_hook = trainer.get_hook(EvaluationHook)
        if len(eval_hook) == 0:
            self.logger.error(
                'Trying to save the best checkpoint, but there is no evaluation, skipping.'
            )

        if eval_hook[0].last_eval_tag == (
                'iter', trainer.iter) and self._should_save(trainer):
            self._do_save(trainer, 'by_step')

    def _should_save(self, trainer):
        return self.save_best and self._is_best_metric(trainer.metric_values)

    def _is_best_metric(self, metric_values):
        if metric_values is None:
            return False

        if self.metric_key not in metric_values:
            raise ValueError(
                f'Not find metric_key: {self.metric_key} in {metric_values}')

        if self._best_metric is None:
            self._best_metric = metric_values[self.metric_key]
            return True
        else:
            compare_fn = self.rule_map[self.rule]
            if compare_fn(metric_values[self.metric_key], self._best_metric):
                self._best_metric = metric_values[self.metric_key]
                return True
        return False

    def generate_prefix(self, trainer, save_strategy):
        if save_strategy == CheckpointStrategy.by_epoch:
            return f'best_{LogKeys.EPOCH}{trainer.epoch + 1}_{self.metric_key}{self._best_metric}'
        else:
            return f'best_{LogKeys.ITER}{trainer.iter + 1}_{self.metric_key}{self._best_metric}'

    def _save_checkpoint(self, trainer, prefix):
        checkpoint_path_prefix = self.save_file_name
        if checkpoint_path_prefix is None:
            checkpoint_path_prefix = os.path.join(self.save_dir, prefix)
        else:
            checkpoint_path_prefix = os.path.join(self.save_dir,
                                                  checkpoint_path_prefix)

        self._best_ckpt_file = checkpoint_path_prefix
        meta = self._create_training_state(trainer)
        self.processor.save_checkpoints(trainer, checkpoint_path_prefix,
                                        self.output_dir, meta)
        self.save_evaluate_results(trainer)
        self.history_checkpoints.add(checkpoint_path_prefix)
        self._remove_obsolete_checkpoints(trainer)
        return prefix

    def _remove_obsolete_checkpoints(self, trainer):

        def extract_metric_from_filename(name1):
            metric1 = float(name1.split(self.metric_key)[1])
            if self.rule == 'max':
                return -metric1
            else:
                return metric1

        if self.max_checkpoint_num is not None and \
                len(self.history_checkpoints) > self.max_checkpoint_num:
            history_checkpoints = sorted(
                self.history_checkpoints, key=extract_metric_from_filename)
            self.history_checkpoints.clear()
            for i, checkpoint_path_prefix in enumerate(history_checkpoints):
                if i < self.max_checkpoint_num:
                    self.history_checkpoints.add(checkpoint_path_prefix)
                else:
                    self.logger.info(
                        f'deleting checkpoint: {checkpoint_path_prefix}')
                    self.processor.remove_checkpoints(
                        trainer, checkpoint_path_prefix=checkpoint_path_prefix)

    def state_dict(self):
        return {
            'best_metric': self._best_metric,
        }

    def load_state_dict(self, state_dict):
        if state_dict is not None and len(state_dict) > 0:
            self._best_metric = state_dict.get('best_metric')
        else:
            self.logger.warning(
                'The state_dict is not available, the best metric value will be affected.'
            )

    def after_run(self, trainer):
        if self.restore_best:
            # If restore_best is True, will call the LoadCheckpointHook to load the best checkpoint
            # for later evaluation or prediction.
            from weathon.dl.hooks import LoadCheckpointHook
            LoadCheckpointHook.load_checkpoint(self._best_ckpt_file, trainer)
