from datetime import timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from weathon.quantization.base.datafeed import DataFeedConfig

from .trade_enums import Interval, Exchange


@dataclass
class TuShareConfig(DataFeedConfig):
    name: str = "tushare"
    username: str = "token"
    token: str = "0eba9ee1b8e99cc21a50189f614eb617fb2fa2e1a898d5e69cf4594f"

    def __post_init__(self):
        # 数据频率映射
        self.interval: Dict[Interval, str] = {
            Interval.MINUTE: "1min",
            Interval.HOUR: "60min",
            Interval.DAILY: "D",
        }
        # 交易所映射
        self.exchange: Dict[Exchange, str] = {
            Exchange.CFFEX: "CFX",
            Exchange.SHFE: "SHF",
            Exchange.CZCE: "ZCE",
            Exchange.DCE: "DCE",
            Exchange.INE: "INE",
            Exchange.SSE: "SH",
            Exchange.SZSE: "SZ",
        }
        # 时间调整映射
        self.interval_adjustment: Dict[Interval, timedelta] = {
            Interval.MINUTE: timedelta(minutes=1),
            Interval.HOUR: timedelta(hours=1),
            Interval.DAILY: timedelta()
        }

        # 股票支持列表
        self.support_stock_exchanges: List[Exchange] = [Exchange.SSE, Exchange.SZSE, Exchange.BSE, ]
        # 期货支持列表
        self.support_future_exchanges: List[Exchange] = [Exchange.CFFEX, Exchange.SHFE, Exchange.CZCE, Exchange.DCE, Exchange.INE, ]

    def to_tushare_symbol(self, symbol, exchange) -> Optional[str]:
        """将交易所代码转换为tushare代码"""
        tushare_symbol = None
        # 股票
        if exchange in self.support_stock_exchanges:  # 交易所在股票列表中
            tushare_symbol:str = f"{symbol}.{self.exchange[exchange]}"
        
        # 期货
        if exchange in self.support_future_exchanges:
            if exchange is not Exchange.CZCE:
                tushare_symbol: str = f"{symbol}.{self.exchange[exchange]}".upper()
            else:
                idx = [x.isdigit() for x in symbol].index(True)
                product, year, month = symbol[:idx], symbol[idx], symbol[idx + 1:]
                year = '1' + year if year == '9' else '2' + year
                tushare_symbol: str = f"{product}{year}{month}.ZCE".upper()

        return tushare_symbol

    def to_tushare_asset(self, symbol, exchange) -> Optional[str]:
        """生成tushare资产类别"""
        asset = None
        # 股票
        if exchange in self.support_stock_exchanges:
            if (exchange is Exchange.SSE and symbol[0] == "6") or (exchange is Exchange.SZSE and symbol[0] == "0" ) or symbol[0] == "3":
                asset:str = "E"
            else:
                asset: str = "I"
        # 期货
        if exchange in self.support_future_exchanges:
            asset: str = "FT"
        
        return asset


@dataclass
class UDataConfig(DataFeedConfig):
    name: str = "U Data"
    username: str = "16621660628"
    password: str = "lizhen@199359"
    token: str = "jWCRKZDyqB5uLYykY-pCwLwwt3t1sQO1wcob91EgfNhpXuULCMbB2wRnWzyF4J4X"


@dataclass
class BaoStockConfig(DataFeedConfig):
    name: str = "bao stock"
    username: str = "16621660628"
    password: str = "lizhen@199359"
    token: str = "jWCRKZDyqB5uLYykY-pCwLwwt3t1sQO1wcob91EgfNhpXuULCMbB2wRnWzyF4J4X"
