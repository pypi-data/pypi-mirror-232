from dataclasses import dataclass
from datetime import datetime

from peewee import Model, AutoField, CharField, IntegerField, DoubleField, DateTimeField, MySQLDatabase
from weathon.quantization.base.database import BaseDBDataModel
from weathon.quantization.base.data import BaseData
from weathon.quantization.utils.constants import Exchange
# from weathon.quantization.utils.database.database import Mariadb

# db = Mariadb().db


class DateTimeMillisecondField(DateTimeField):
    """支持毫秒的日期时间戳字段"""

    def get_modifiers(self):
        """毫秒支持"""
        return [3]


@dataclass
class TickMeta:
    """
    meta of tick data stored in database.
    """

    symbol: str = ""
    exchange: Exchange = None
    count: int = 0
    start: datetime = None
    end: datetime = None


@dataclass
class TickData(BaseData):
    """
    Tick data contains information about:
        * last trade in market
        * orderbook snapshot
        * intraday market statistics.
    """

    symbol: str
    exchange: Exchange
    datetime: datetime

    name: str = ""
    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    last_price: float = 0
    last_volume: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    pre_close: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    localtime: datetime = None

    def __post_init__(self) -> None:
        """"""
        self.qt_symbol: str = f"{self.symbol}.{self.exchange.value}"



class DBTickData(BaseDBDataModel):
    """TICK数据表映射对象"""

    id: AutoField = AutoField()

    symbol: str = CharField()                               # 合约代码
    exchange: str = CharField()                             # 合约所在交易所
    datetime: datetime = DateTimeMillisecondField()         # Tick所属时间

    name: str = CharField()
    volume: float = DoubleField()
    turnover: float = DoubleField()
    open_interest: float = DoubleField()                    # 合约持仓量
    last_price: float = DoubleField()                       # 合约最新成交价
    last_volume: float = DoubleField()                      # 合约最新成交量
    limit_up: float = DoubleField()                         # 合约涨停价 
    limit_down: float = DoubleField()                       # 合约跌停价

    open_price: float = DoubleField()
    high_price: float = DoubleField()
    low_price: float = DoubleField()
    pre_close: float = DoubleField()


    bid_price_1: float = DoubleField()                      # 买一价
    bid_price_2: float = DoubleField(null=True)             # 买二价
    bid_price_3: float = DoubleField(null=True)             # 买三价
    bid_price_4: float = DoubleField(null=True)             # 买四价
    bid_price_5: float = DoubleField(null=True)             # 买五价

    ask_price_1: float = DoubleField()                      # 卖一价
    ask_price_2: float = DoubleField(null=True)             # 卖二价
    ask_price_3: float = DoubleField(null=True)             # 卖三价
    ask_price_4: float = DoubleField(null=True)             # 卖四价
    ask_price_5: float = DoubleField(null=True)             # 卖五价

    bid_volume_1: float = DoubleField()                     # 买一量
    bid_volume_2: float = DoubleField(null=True)            # 买二量
    bid_volume_3: float = DoubleField(null=True)            # 买三量
    bid_volume_4: float = DoubleField(null=True)            # 买四量
    bid_volume_5: float = DoubleField(null=True)            # 买五量

    ask_volume_1: float = DoubleField()                     # 卖一量
    ask_volume_2: float = DoubleField(null=True)            # 卖二量
    ask_volume_3: float = DoubleField(null=True)            # 卖三量
    ask_volume_4: float = DoubleField(null=True)            # 卖四量
    ask_volume_5: float = DoubleField(null=True)            # 卖五量

    localtime: datetime = DateTimeMillisecondField(null=True)



class DBTickOverview(BaseDBDataModel):
    """Tick汇总数据表映射对象"""

    id: AutoField = AutoField()

    symbol: str = CharField()
    exchange: str = CharField()
    count: int = IntegerField()
    start: datetime = DateTimeField()
    end: datetime = DateTimeField()

