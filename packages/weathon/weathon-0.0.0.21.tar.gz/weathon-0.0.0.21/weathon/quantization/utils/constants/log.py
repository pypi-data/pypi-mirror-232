from dataclasses import dataclass
from logging import CRITICAL, Formatter

from weathon.utils.logger import formatter


@dataclass
class LogStatus:
    name: str = 'weathon quant'
    activate: bool = True
    level: int = CRITICAL
    console: bool = True
    file: bool = True
    formatter:Formatter = formatter
