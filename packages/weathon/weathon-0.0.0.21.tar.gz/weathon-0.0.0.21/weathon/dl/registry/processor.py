from weathon.dl.registry.registry import Registry, build_from_cfg
from weathon.dl.utils.config.config import ConfigDict

PREPROCESSORS = Registry('preprocessors')

POSTPROCESSORS = Registry('postprocessors')


def build_preprocessor(cfg: ConfigDict, task_name: str = None, default_args: dict = None):
    """ build preprocessor given model config dict

    Args:
        cfg (:obj:`ConfigDict`): config dict for model object.
        task_name (str, optional):  application field name, refer to
            :obj:`Fields` for more details
        default_args (dict, optional): Default initialization arguments.
    """
    return build_from_cfg(cfg, PREPROCESSORS, group_key=task_name, default_args=default_args)


def build_postprocessor(cfg: ConfigDict, task_name: str, default_args: dict = None):
    return build_from_cfg(cfg, POSTPROCESSORS, group_key=task_name, default_args=default_args)
