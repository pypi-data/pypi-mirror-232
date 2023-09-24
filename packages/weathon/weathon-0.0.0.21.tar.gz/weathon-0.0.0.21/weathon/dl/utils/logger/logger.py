import importlib
import logging
from typing import Optional

init_loggers = {}

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_logger(log_file: Optional[str] = None, log_level: int = logging.INFO, file_mode: str = 'w'):
    """ Get logging logger

    Args:
        log_file: 日志文件,如果指定,文件处理器将会被加到logger对象中.
        log_level: Logging level.
        file_mode: 如果"log_file"不为空,指定打开日志文件的模式,默认为"w".
    """

    logger_name = __name__.split('.')[0]
    logger = logging.getLogger(logger_name)

    if logger_name in init_loggers:
        add_file_handler_if_needed(logger, log_file, file_mode, log_level)
        return logger

    # handle duplicate logs to the console
    # Starting in 1.8.0, PyTorch DDP attaches a StreamHandler <stderr> (NOTSET)
    # to the root logger. As logger.propagate is True by default, this root
    # level handler causes logging messages from rank>0 processes to
    # unexpectedly show up on the console, creating much unwanted clutter.
    # To fix this issue, we set the root logger's StreamHandler, if any, to log
    # at the ERROR level.
    for handler in logger.root.handlers:
        if type(handler) is logging.StreamHandler:
            handler.setLevel(logging.ERROR)

    stream_handler = logging.StreamHandler()
    handlers = [stream_handler]

    if importlib.util.find_spec('torch') is not None:
        from weathon.dl.utils.torch_utils import is_master
        is_worker0 = is_master()
    else:
        is_worker0 = True

    if is_worker0 and log_file is not None:
        file_handler = logging.FileHandler(log_file, file_mode)
        handlers.append(file_handler)

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    if is_worker0:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.ERROR)

    init_loggers[logger_name] = True

    return logger


def add_file_handler_if_needed(logger, log_file, file_mode, log_level):
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return

    if importlib.util.find_spec('torch') is not None:
        from weathon.dl.utils.torch_utils import is_master
        is_worker0 = is_master()
    else:
        is_worker0 = True

    if is_worker0 and log_file is not None:
        file_handler = logging.FileHandler(log_file, file_mode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
