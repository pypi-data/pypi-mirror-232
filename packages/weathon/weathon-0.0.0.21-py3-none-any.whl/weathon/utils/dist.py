import importlib


def is_worker_master() -> bool:
    if importlib.util.find_spec('torch') is not None:
        from weathon.dl.utils.torch_utils import is_master
        is_master = is_master()
    else:
        is_master = True

    return is_master
