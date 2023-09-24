from torch import nn
from weathon.dl.registry import PARALLEL


def is_parallel(module):
    """Check if a module is wrapped by parallel object.

    The following modules are regarded as parallel object:
     - torch.nn.parallel.DataParallel
     - torch.nn.parallel.distributed.DistributedDataParallel
    You may add you own parallel object by registering it to `modelscope.parallel.PARALLEL`.

    Args:
        module (nn.Module): The module to be checked.

    Returns:
        bool: True if the is wrapped by parallel object.
    """
    module_wrappers = []
    for group, module_dict in PARALLEL.modules.items():
        module_wrappers.extend(list(module_dict.values()))

    return isinstance(module, tuple(module_wrappers))


def parallelize(model, distributed, local_rank):
    if distributed:
        return nn.parallel.DistributedDataParallel(model,device_ids=[local_rank],output_device=[local_rank],find_unused_parameters=True)
    else:
        return nn.DataParallel(model)