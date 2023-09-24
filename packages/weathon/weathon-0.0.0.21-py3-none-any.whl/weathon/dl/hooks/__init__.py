from typing import TYPE_CHECKING

from weathon.dl.utils.import_utils import LazyImportModule

if TYPE_CHECKING:
    from .early_stop_hook import EarlyStopHook
    from .compression import SparsityHook
    from .evaluation_hook import EvaluationHook
    from .iter_timer_hook import IterTimerHook
    from .logger import TensorboardHook, TextLoggerHook
    from .lr_scheduler_hook import LrSchedulerHook
    from .optimizer import (ApexAMPOptimizerHook, NoneOptimizerHook,
                            OptimizerHook, TorchAMPOptimizerHook)
    from .checkpoint import CheckpointHook, LoadCheckpointHook, BestCkptSaverHook
    from .distributed.ddp_hook import DDPHook
    from .distributed.deepspeed_hook import DeepspeedHook
    from .distributed.megatron_hook import MegatronHook

else:
    _import_structure = {
        'checkpoint_hook':
        ['BestCkptSaverHook', 'CheckpointHook', 'LoadCheckpointHook'],
        'compression': ['SparsityHook'],
        'evaluation_hook': ['EvaluationHook'],
        'iter_timer_hook': ['IterTimerHook'],
        'logger': ['TensorboardHook', 'TextLoggerHook'],
        'lr_scheduler_hook': ['LrSchedulerHook', 'NoneLrSchedulerHook'],
        'optimizer': [
            'ApexAMPOptimizerHook', 'NoneOptimizerHook', 'OptimizerHook',
            'TorchAMPOptimizerHook'
        ],
        'checkpoint':
        ['CheckpointHook', 'LoadCheckpointHook', 'BestCkptSaverHook'],
        'distributed.ddp_hook': ['DDPHook'],
        'distributed.deepspeed_hook': ['DeepspeedHook'],
        'distributed.megatron_hook': ['MegatronHook'],
    }

    import sys

    sys.modules[__name__] = LazyImportModule(
        __name__,
        globals()['__file__'],
        _import_structure,
        module_spec=__spec__,
        extra_objects={},
    )
