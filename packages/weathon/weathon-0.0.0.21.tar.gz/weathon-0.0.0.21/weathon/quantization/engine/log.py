from datetime import datetime

from weathon.quantization.base.engine import BaseEngine, MainEngine, EventEngine, Event
from weathon.quantization.datamodel import LogData
from weathon.quantization.utils.constants import EVENT_LOG
from weathon.quantization.utils.constants.log import LogStatus
from weathon.utils.fileio.path import get_path, get_folder_path
from weathon.utils.logger import get_logger, add_null_handler, add_console_handler, add_file_handler

cwd, quant_path = get_path(".quant", force_create=True)

# 功能引擎


class LogEngine(BaseEngine):
    """
    Processes log event and output with logging module.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine, acivate: bool = True) -> None:
        """"""
        super(LogEngine, self).__init__(main_engine, event_engine, "log")
        self.log_status = LogStatus(activate=acivate)

        if not self.log_status.activate:
            return

        self.logger = get_logger("weathon quant")
        self.level: int = self.log_status.level
        self.formatter = self.log_status.formatter
        self.logger.setLevel(self.level)
        self.register_event()

    def _init_log_handler(self):
        add_null_handler(self.logger)

        # console log
        if self.log_status.console:
            add_console_handler(self.logger, log_level=self.level)

        # file log
        if self.log_status.file:
            today_date = datetime.now().strftime("%Y%m%d")
            filename = f'quant_{today_date}.log'
            log_path = get_folder_path(quant_path, 'log')
            log_file = log_path.joinpath(filename)
            self.logger.info(f'log file will be generated at {log_file}')

            add_file_handler(self.logger, log_file=log_file, file_mode='a', log_level=self.level,
                             formatter=self.formatter)

    def register_event(self) -> None:
        """"""
        self.event_engine.register(EVENT_LOG, self.process_log_event)

    def process_log_event(self, event: Event) -> None:
        """
        Process log event.
        """
        log: LogData = event.data
        self.logger.log(log.level, log.msg)
