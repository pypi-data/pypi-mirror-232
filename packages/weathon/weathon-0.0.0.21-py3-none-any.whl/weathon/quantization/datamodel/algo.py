from dataclasses import dataclass

from weathon.quantization.utils.constants import Direction, Status


@dataclass
class AlgoItem:
    """算法数据容器"""

    algoid: str
    spread_name: str
    direction: Direction
    price: float
    payup: int
    volume: float
    traded_volume: float
    traded_price: float
    interval: int
    count: int
    status: Status