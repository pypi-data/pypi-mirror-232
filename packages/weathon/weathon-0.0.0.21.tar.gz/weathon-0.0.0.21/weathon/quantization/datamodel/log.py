from dataclasses import dataclass
from datetime import datetime
from logging import INFO

from weathon.quantization.base.data import BaseData


@dataclass
class LogData(BaseData):
    """
    Log data is used for recording log messages on GUI or in log files.
    """

    msg: str
    level: int = INFO

    def __post_init__(self) -> None:
        """"""
        self.time: datetime = datetime.now()

