from abc import ABC
from dataclasses import dataclass
from typing import Optional, List, Callable

from weathon.quantization.datamodel.bar import BarData
from weathon.quantization.datamodel.tick import TickData
from weathon.quantization.datamodel.request import HistoryRequest


@dataclass
class DataFeedConfig:
    name: str = ""
    username: str = ""
    password: str = ""


class BaseDatafeed(ABC):
    """
    Abstract datafeed class for connecting to different datafeed.
    """

    def init(self, output: Callable = print) -> bool:
        """
        Initialize datafeed service connection.
        """
        pass

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """
        Query history bar data.
        """
        pass

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """
        Query history tick data.
        """
        pass
