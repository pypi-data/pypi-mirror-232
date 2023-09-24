from weathon.dl.base import BaseHook
from weathon.dl.registry import HOOKS
from weathon.dl.utils.constants import Priority, DistributedParallelType
from weathon.dl.utils.constants import Hooks
from weathon.dl.utils.device import create_device
from weathon.dl.utils.torch_utils import get_local_rank, init_dist


@HOOKS.register_module(module_name=Hooks.DDPHook)
class DDPHook(BaseHook):

    PRIORITY = Priority.LOW

    def __init__(self, launcher):
        """The DDP Hook for data parallel

        Args:
            launcher(str, required): The launcher info, can be 'pytorch' or 'mpi' or 'slurm'
        """
        assert launcher is not None
        self.launcher = launcher
        self.wrapped = False
        # TODO support single GPU evaluate & multi GPU train

    def after_init(self, trainer):
        init_dist(self.launcher)
        local_rank = get_local_rank()
        trainer.device = create_device(f'cuda:{local_rank}')
        trainer.model.to(trainer.device)
        trainer.parallel_groups[DistributedParallelType.DP] = None

    def before_run(self, trainer):
        self.wrap_module(trainer)

    def before_val(self, trainer):
        self.wrap_module(trainer)

    def before_train_epoch(self, trainer):
        trainer.train_dataloader.sampler.set_epoch(trainer.epoch)

    def before_val_epoch(self, trainer):
        trainer.eval_dataloader.sampler.set_epoch(trainer.epoch)



    def wrap_module(self, trainer):
        if not self.wrapped:
            trainer.model = trainer.to_parallel(trainer.model)
            self.wrapped = True
