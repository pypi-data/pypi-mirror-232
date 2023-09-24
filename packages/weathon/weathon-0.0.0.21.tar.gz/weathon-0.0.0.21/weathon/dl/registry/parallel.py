from typing import Union, Dict
from torch.nn.parallel.distributed import DistributedDataParallel

from weathon.dl.registry.registry import Registry, build_from_cfg
from weathon.dl.utils.config.config import ConfigDict

PARALLEL = Registry('parallel')
PARALLEL.register_module(module_name='DistributedDataParallel', module_cls=DistributedDataParallel)


def build_parallel(cfg: Union[Dict, ConfigDict], default_args: dict = None):
    """ build parallel

    Args:
        cfg (:obj:`ConfigDict`): config dict for parallel object.
        default_args (dict, optional): Default initialization arguments.
    """
    return build_from_cfg(cfg, PARALLEL, default_args=default_args)
