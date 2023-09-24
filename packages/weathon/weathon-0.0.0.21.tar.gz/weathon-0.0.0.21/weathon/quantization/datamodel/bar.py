from dataclasses import dataclass
from datetime import datetime

from peewee import Model, AutoField, CharField, DateTimeField, DoubleField, IntegerField, MySQLDatabase

from weathon.quantization.base.data import BaseData
from weathon.quantization.base.database import BaseDBDataModel
from weathon.quantization.utils.constants import Exchange, Interval
# from weathon.quantization.utils.database import Mariadb

# db = Mariadb().db



@dataclass
class BarMeta:
    """
    meta of bar data stored in database.
    """

    symbol: str = ""
    exchange: Exchange = None
    interval: Interval = None
    count: int = 0
    start: datetime = None
    end: datetime = None



@dataclass
class BarData(BaseData):
    """
    Candlestick bar data of a certain trading period.
    """

    symbol: str
    exchange: Exchange
    datetime: datetime

    interval: Interval = None
    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0

    def __post_init__(self) -> None:
        """"""
        self.qt_symbol: str = f"{self.symbol}.{self.exchange.value}"



class DBBarOverview(BaseDBDataModel):
    """K线汇总数据表映射对象"""

    id: AutoField = AutoField()

    symbol: str = CharField()
    exchange: str = CharField()
    interval: str = CharField()
    count: int = IntegerField()
    start: datetime = DateTimeField()
    end: datetime = DateTimeField()



class DBBarData(BaseDBDataModel):
    """K线数据表映射对象"""

    id: AutoField = AutoField()

    symbol: str = CharField()               # 合约代码
    exchange: str = CharField()             # 合约所在交易所
    dt: datetime = DateTimeField()          # 当前1分K线所属时间
    interval: str = CharField()

    volume: float = DoubleField()           # 当前1分钟成交量
    turnover: float = DoubleField()
    open_interest: float = DoubleField()    # 持仓量
    open_price: float = DoubleField()       # 当前1分K线开盘价
    high_price: float = DoubleField()       # 当前1分K线最高价
    low_price: float = DoubleField()        # 当前1分K线最低价
    close_price: float = DoubleField()      # 当前1分K线收盘价


