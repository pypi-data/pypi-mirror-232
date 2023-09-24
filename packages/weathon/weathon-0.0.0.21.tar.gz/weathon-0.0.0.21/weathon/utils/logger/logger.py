import logging
init_loggers = {}

from weathon.utils.dist import is_worker_master

def get_logger(log_name: str = None,  log_level: int = logging.INFO):
    """ Get logging logger
    Args:
        log_level: Logging level.
    """
    logger_name = __name__.split('.')[0] if not log_name else log_name
    logger = logging.getLogger(logger_name)
    if logger_name in init_loggers:
        return logger

    log_level = log_level if is_worker_master() else logging.ERROR
    logger.setLevel(log_level)
    init_loggers[logger_name] = True
    return logger
