from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

from weathon.quantization.datamodel import TradeData, TickData
from weathon.quantization.datamodel.leg import LegData
from weathon.quantization.utils.constants import Direction, Exchange
from weathon.utils.constants import LOCAL_TZ
from weathon.utils.numeric import floor_to, round_to, ceil_to


@dataclass
class SpreadItem:
    """价差数据容器"""

    name: str
    bid_volume: int
    bid_price: float
    ask_price: float
    ask_volume: int
    net_pos: int
    datetime: datetime
    price_formula: str
    trading_formula: str



class SpreadData:
    """"""

    def __init__(
        self,
        name: str,
        legs: List[LegData],
        variable_symbols: Dict[str, str],
        variable_directions: Dict[str, int],
        price_formula: str,
        trading_multipliers: Dict[str, int],
        active_symbol: str,
        min_volume: float,
        compile_formula: bool = True
    ) -> None:
        """"""
        self.name: str = name
        self.compile_formula: bool = compile_formula

        self.legs: Dict[str, LegData] = {}
        self.active_leg: LegData = None
        self.passive_legs: List[LegData] = []

        self.min_volume: float = min_volume
        self.pricetick: float = 0

        # For calculating spread pos and sending orders
        self.trading_multipliers: Dict[str, int] = trading_multipliers

        self.price_formula: str = ""
        self.trading_formula: str = ""

        for leg in legs:
            self.legs[leg.vt_symbol] = leg
            if leg.vt_symbol == active_symbol:
                self.active_leg = leg
            else:
                self.passive_legs.append(leg)

            trading_multiplier: int = self.trading_multipliers[leg.vt_symbol]
            if trading_multiplier > 0:
                self.trading_formula += f"+{trading_multiplier}*{leg.vt_symbol}"
            else:
                self.trading_formula += f"{trading_multiplier}*{leg.vt_symbol}"

            if not self.pricetick:
                self.pricetick = leg.pricetick
            else:
                self.pricetick = min(self.pricetick, leg.pricetick)

        # Spread data
        self.bid_price: float = 0
        self.ask_price: float = 0
        self.bid_volume: float = 0
        self.ask_volume: float = 0

        self.long_pos: int = 0
        self.short_pos: int = 0
        self.net_pos: int = 0

        self.datetime: datetime = None

        self.leg_pos: defaultdict = defaultdict(int)

        # 价差计算公式相关
        self.variable_symbols: dict = variable_symbols
        self.variable_directions: dict = variable_directions
        self.price_formula = price_formula

        # 实盘时编译公式，加速计算
        if compile_formula:
            self.price_code: str = compile(price_formula, __name__, "eval")
        # 回测时不编译公式，从而支持多进程优化
        else:
            self.price_code: str = price_formula

        self.variable_legs: Dict[str, LegData] = {}
        for variable, vt_symbol in variable_symbols.items():
            leg: LegData = self.legs[vt_symbol]
            self.variable_legs[variable] = leg

    def calculate_price(self) -> bool:
        """
        计算价差盘口

        1. 如果各条腿价格均有效，则计算成功，返回True
        2. 反之只要有一条腿的价格无效，则计算失败，返回False
        """
        self.clear_price()

        # Go through all legs to calculate price
        bid_data: dict = {}
        ask_data: dict = {}
        volume_inited: bool = False

        for variable, leg in self.variable_legs.items():
            # Filter not all leg price data has been received
            if not leg.bid_volume or not leg.ask_volume:
                self.clear_price()
                return False

            # Generate price dict for calculating spread bid/ask
            variable_direction: int = self.variable_directions[variable]
            if variable_direction > 0:
                bid_data[variable] = leg.bid_price
                ask_data[variable] = leg.ask_price
            else:
                bid_data[variable] = leg.ask_price
                ask_data[variable] = leg.bid_price

            # Calculate volume
            trading_multiplier: int = self.trading_multipliers[leg.vt_symbol]
            if not trading_multiplier:
                continue

            leg_bid_volume: float = leg.bid_volume
            leg_ask_volume: float = leg.ask_volume

            if trading_multiplier > 0:
                adjusted_bid_volume: float = floor_to(
                    leg_bid_volume / trading_multiplier,
                    self.min_volume
                )
                adjusted_ask_volume: float = floor_to(
                    leg_ask_volume / trading_multiplier,
                    self.min_volume
                )
            else:
                adjusted_bid_volume: float = floor_to(
                    leg_ask_volume / abs(trading_multiplier),
                    self.min_volume
                )
                adjusted_ask_volume: float = floor_to(
                    leg_bid_volume / abs(trading_multiplier),
                    self.min_volume
                )

            # For the first leg, just initialize
            if not volume_inited:
                self.bid_volume = adjusted_bid_volume
                self.ask_volume = adjusted_ask_volume
                volume_inited = True
            # For following legs, use min value of each leg quoting volume
            else:
                self.bid_volume = min(self.bid_volume, adjusted_bid_volume)
                self.ask_volume = min(self.ask_volume, adjusted_ask_volume)

        # Calculate spread price
        self.bid_price = self.parse_formula(self.price_code, bid_data)
        self.ask_price = self.parse_formula(self.price_code, ask_data)

        # Round price to pricetick
        if self.pricetick:
            self.bid_price = round_to(self.bid_price, self.pricetick)
            self.ask_price = round_to(self.ask_price, self.pricetick)

        # Update calculate time
        self.datetime = datetime.now(LOCAL_TZ)

        return True

    def update_trade(self, trade: TradeData) -> None:
        """更新委托成交"""
        if trade.direction == Direction.LONG:
            self.leg_pos[trade.vt_symbol] += trade.volume
        else:
            self.leg_pos[trade.vt_symbol] -= trade.volume

    def calculate_pos(self) -> None:
        """"""
        long_pos = 0
        short_pos = 0

        for n, leg in enumerate(self.legs.values()):
            leg_long_pos = 0
            leg_short_pos = 0

            trading_multiplier: int = self.trading_multipliers[leg.vt_symbol]
            if not trading_multiplier:
                continue

            net_pos = self.leg_pos[leg.vt_symbol]
            adjusted_net_pos = net_pos / trading_multiplier

            if adjusted_net_pos > 0:
                adjusted_net_pos = floor_to(adjusted_net_pos, self.min_volume)
                leg_long_pos = adjusted_net_pos
            else:
                adjusted_net_pos = ceil_to(adjusted_net_pos, self.min_volume)
                leg_short_pos = abs(adjusted_net_pos)

            if not n:
                long_pos = leg_long_pos
                short_pos = leg_short_pos
            else:
                long_pos = min(long_pos, leg_long_pos)
                short_pos = min(short_pos, leg_short_pos)

        self.long_pos = long_pos
        self.short_pos = short_pos
        self.net_pos = long_pos - short_pos

    def clear_price(self) -> None:
        """"""
        self.bid_price = 0
        self.ask_price = 0
        self.bid_volume = 0
        self.ask_volume = 0

    def calculate_leg_volume(self, vt_symbol: str, spread_volume: float) -> float:
        """"""
        leg: LegData = self.legs[vt_symbol]
        trading_multiplier: int = self.trading_multipliers[leg.vt_symbol]
        leg_volume: float = spread_volume * trading_multiplier
        return leg_volume

    def calculate_spread_volume(self, vt_symbol: str, leg_volume: float) -> float:
        """"""
        leg: LegData = self.legs[vt_symbol]
        trading_multiplier: int = self.trading_multipliers[leg.vt_symbol]
        spread_volume: float = leg_volume / trading_multiplier

        if spread_volume > 0:
            spread_volume = floor_to(spread_volume, self.min_volume)
        else:
            spread_volume = ceil_to(spread_volume, self.min_volume)

        return spread_volume

    def to_tick(self) -> None:
        """"""
        tick: TickData = TickData(
            symbol=self.name,
            exchange=Exchange.LOCAL,
            datetime=self.datetime,
            name=self.name,
            last_price=(self.bid_price + self.ask_price) / 2,
            bid_price_1=self.bid_price,
            ask_price_1=self.ask_price,
            bid_volume_1=self.bid_volume,
            ask_volume_1=self.ask_volume,
            gateway_name="SPREAD"
        )
        return tick

    def get_leg_size(self, vt_symbol: str) -> float:
        """"""
        leg: LegData = self.legs[vt_symbol]
        return leg.size

    def parse_formula(self, formula: str, data: Dict[str, float]) -> Any:
        """"""
        locals().update(data)
        value = eval(formula)
        return value

    def get_item(self) -> None:
        """获取数据对象"""
        item: SpreadItem = SpreadItem(
            name=self.name,
            bid_volume=self.bid_volume,
            bid_price=self.bid_price,
            ask_price=self.ask_price,
            ask_volume=self.ask_volume,
            net_pos=self.net_pos,
            datetime=self.datetime,
            price_formula=self.price_formula,
            trading_formula=self.trading_formula,
        )
        return item

