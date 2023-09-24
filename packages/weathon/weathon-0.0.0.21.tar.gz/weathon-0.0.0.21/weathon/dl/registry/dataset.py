from weathon.dl.utils.config.config import ConfigDict
from weathon.dl.registry.registry import build_from_cfg, Registry

CUSTOM_DATASETS = Registry('custom_datasets')

CUSTOM_DATA_COLLATORS = Registry("custom_data_collator")


def build_custom_dataset(cfg: ConfigDict, task_name: str, default_args: dict = None):
    """给定模型配置文件 以及 任务名称 构建用户自定义数据集
    """
    return build_from_cfg(cfg, CUSTOM_DATASETS, group_key=task_name, default_args=default_args)


def build_custom_datacollator(cfg: ConfigDict, task_name: str, default_args: dict = None):
    return build_from_cfg(cfg, CUSTOM_DATA_COLLATORS, group_key=task_name, default_args=default_args)