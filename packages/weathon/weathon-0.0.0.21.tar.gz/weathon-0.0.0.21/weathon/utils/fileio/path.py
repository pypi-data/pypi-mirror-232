from pathlib import Path
from typing import Tuple, Union

from .file_utils import ensure_directory
from weathon.utils.logger import get_logger

logger = get_logger()


def get_path(path_name: Union[str, Path], force_create: bool = False) -> Tuple[Path, Path]:
    """
    如果当前运行环境下有该文件夹，就使用该文件夹。如果不存在，就在home目录下新建该文件夹

    """
    if not path_name:
        raise ValueError("path must be exist")

    cwd: Path = Path.cwd()
    curr_path: Path = cwd.joinpath(path_name)

    # If .quant folder exists in current working directory,
    # then use it as trader running path.
    if curr_path.exists():
        return cwd, curr_path

    logger.warning(f'{curr_path} is not exist and will mkdir at {curr_path}')
    if force_create:
        curr_path.mkdir()
        return cwd, curr_path

    # Otherwise use home path of system.
    home_path: Path = Path.home()
    default_path: Path = home_path.joinpath(path_name)

    logger.warning(f'{curr_path} is not exist and will mkdir at {default_path}')

    # Create .quant folder under home path if not exist.
    ensure_directory(default_path)
    return home_path, default_path


def get_folder_path(father_path: Path, folder_name: str) -> Path:
    ensure_directory(father_path)
    folder_path = father_path.joinpath(folder_name)
    ensure_directory(folder_path)
    return folder_path


def get_file_path(file_path: Path, file_name: str) -> Path:
    ensure_directory(file_path)
    file_path = file_path.joinpath(file_name)
    return file_path
