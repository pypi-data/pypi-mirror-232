from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List
from peewee import Model,SqliteDatabase 
from pathlib import Path
from weathon.utils.fileio.file_utils import ensure_directory
from weathon.quantization.utils.constants import Interval, Exchange

file_dir = Path.home().joinpath("data", "quantization")
db_file = ensure_directory(file_dir) / "database.db"
db = SqliteDatabase(str(db_file))
class BaseDBDataModel(Model):
    

    class Meta:

        database = db
        # indexes: tuple = ((("symbol", "exchange", "interval"), True),)


class BaseDatabase(ABC):
    """
    Abstract database class for connecting to different database.
    """

    def _db_init(self):
        """
            init db object
        """
        pass

    @abstractmethod
    def save_bar_data(self, bars: List["BarData"], stream: bool = False) -> bool:
        """
        Save bar data into database.
        """
        pass

    @abstractmethod
    def save_tick_data(self, ticks: List["TickData"], stream: bool = False) -> bool:
        """
        Save tick data into database.
        """
        pass

    @abstractmethod
    def load_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ) -> List["BarData"]:
        """
        Load bar data from database.
        """
        pass

    @abstractmethod
    def load_tick_data(
            self,
            symbol: str,
            exchange: Exchange,
            start: datetime,
            end: datetime
    ) -> List["TickData"]:
        """
        Load tick data from database.
        """
        pass

    @abstractmethod
    def delete_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval
    ) -> int:
        """
        Delete all bar data with given symbol + exchange + interval.
        """
        pass

    @abstractmethod
    def delete_tick_data(
            self,
            symbol: str,
            exchange: Exchange
    ) -> int:
        """
        Delete all tick data with given symbol + exchange.
        """
        pass

    @abstractmethod
    def get_bar_overview(self) -> List["BarMeta"]:
        """
        Return bar data avaible in database.
        """
        pass

    @abstractmethod
    def get_tick_overview(self) -> List["TickMeta"]:
        """
        Return tick data avaible in database.
        """
        pass
