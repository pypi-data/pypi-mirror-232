from datetime import timedelta, datetime
from typing import Dict, List, Optional, Callable
from copy import deepcopy

import pandas as pd
from pandas import DataFrame
import tushare as ts
from tushare.pro.client import DataApi

from weathon.quantization.base import BaseDatafeed
from weathon.quantization.datamodel import HistoryRequest, BarData
from weathon.quantization.utils.constants import Interval, Exchange, TuShareConfig
from weathon.utils.numeric import round_to
from weathon.utils.constants import CHINA_TZ


class TushareDatafeed(BaseDatafeed):
    """TuShare数据服务接口"""

    def __init__(self):
        """"""
        self.inited: bool = False
        self.config = TuShareConfig()

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        if self.inited:
            return True

        if not self.config.token:
            output("Tushare数据服务初始化失败：token为空！")
            return False

        ts.set_token(self.config.token)
        self.pro: Optional[DataApi] = ts.pro_api()
        self.inited = True

        return True

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询k线数据"""
        if not self.inited:
            self.init(output)

        symbol: str = req.symbol
        exchange: Exchange = req.exchange
        interval: Interval = req.interval
        start: datetime = req.start.strftime("%Y-%m-%d %H:%M:%S")
        end: datetime = req.end.strftime("%Y-%m-%d %H:%M:%S")

        ts_symbol: str = self.config.to_tushare_symbol(symbol, exchange)
        if not ts_symbol:
            return None

        asset: str = self.config.to_tushare_asset(symbol, exchange)
        if not asset:
            return None

        ts_interval: str = self.config.interval.get(interval)
        if not ts_interval:
            return None

        adjustment: timedelta = self.config.interval_adjustment[interval]

        try:
            d1: DataFrame = ts.pro_bar(
                ts_code=ts_symbol,
                start_date=start,
                end_date=end,
                asset=asset,
                freq=ts_interval
            )
        except IOError as ex:
            output(f"发生输入/输出错误：{ex}")
            return []

        df: DataFrame = deepcopy(d1)

        while True:
            if len(d1) != 8000:
                break
            tmp_end: str = d1["trade_time"].values[-1]

            d1 = ts.pro_bar(
                ts_code=ts_symbol,
                start_date=start,
                end_date=tmp_end,
                asset=asset,
                freq=ts_interval
            )
            df = pd.concat([df[:-1], d1])

        bar_keys: List[datetime] = []
        bar_dict: Dict[datetime, BarData] = {}
        data: List[BarData] = []

        # 处理原始数据中的NaN值
        df.fillna(0, inplace=True)

        if df is not None:
            for ix, row in df.iterrows():   # ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
                if row["open"] is None:
                    continue

                if interval.value == "d":
                    dt: str = row["trade_date"]
                    dt: datetime = datetime.strptime(dt, "%Y%m%d")
                else:
                    dt: str = row["trade_time"]
                    dt: datetime = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") - adjustment

                dt = dt.replace(tzinfo=CHINA_TZ)

                turnover = row.get("amount", 0)
                if turnover is None:
                    turnover = 0

                open_interest = row.get("oi", 0)
                if open_interest is None:
                    open_interest = 0

                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=round_to(row["open"], 0.000001),
                    high_price=round_to(row["high"], 0.000001),
                    low_price=round_to(row["low"], 0.000001),
                    close_price=round_to(row["close"], 0.000001),
                    volume=row["vol"],
                    turnover=turnover,
                    open_interest=open_interest,
                    gateway_name="TuShare"
                )

                bar_dict[dt] = bar

        bar_keys: list = bar_dict.keys()
        bar_keys = sorted(bar_keys, reverse=False)
        for i in bar_keys:
            data.append(bar_dict[i])

        return data
