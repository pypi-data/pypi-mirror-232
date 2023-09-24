import logging
from logging import Logger, Formatter, FileHandler, StreamHandler

from pathlib import Path
from typing import Union, Dict

from weathon.utils.dist import is_worker_master

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handlers: Dict[str, FileHandler] = {}


def add_file_handler(logger: Logger, log_file: Union[str, Path], file_mode: str, log_level: Union[str, int],
                     formatter: Formatter = formatter) -> None:
    if is_worker_master() and log_file is not None:
        file_handler = FileHandler(log_file, file_mode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)


def add_console_handler(logger: Logger, log_level: Union[str, int], formatter: Formatter = formatter) -> None:
    """
    Add console output of log.
    """
    # handle duplicate logs to the console
    # Starting in 1.8.0, PyTorch DDP attaches a StreamHandler <stderr> (NOTSET) to the root logger.
    # As logger.propagate is True by default, this root level handler causes logging messages from rank>0 processes to
    # unexpectedly show up on the console, creating much unwanted clutter.
    # To fix this issue, we set the root logger's StreamHandler, if any, to log at the ERROR level.
    log_level = log_level if is_worker_master() else logging.ERROR

    console_handler = StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def add_null_handler(logger: Logger) -> None:
    null_handler: logging.NullHandler = logging.NullHandler()
    logger.addHandler(null_handler)


def get_file_logger_handler(filename: str) -> FileHandler:
    handler: FileHandler = file_handlers.get(filename, None)
    if not handler:
        handler = FileHandler(filename)
        file_handlers[filename] = handler
    return handler


def get_file_logger(filename: str) -> Logger:
    logger: Logger = logging.getLogger(filename)
    handler: FileHandler = get_file_logger_handler(filename)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger