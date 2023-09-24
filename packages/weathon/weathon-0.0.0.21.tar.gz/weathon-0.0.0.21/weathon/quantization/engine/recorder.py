import sys
from threading import Thread
from queue import Queue, Empty
from copy import copy
from collections import defaultdict
from typing import Any, Dict, List, Optional

from weathon.quantization.base.database import BaseDatabase
from weathon.quantization.base.engine import Event, EventEngine, BaseEngine, MainEngine
from weathon.quantization.datamodel import SubscribeRequest, TickData, BarData, ContractData, Exchange
from weathon.quantization.datamodel.spread import SpreadData
from weathon.quantization.utils.bar_generator import BarGenerator

from weathon.quantization.utils.constants import EVENT_RECORDER_UPDATE, EVENT_RECORDER_LOG, EVENT_RECORDER_EXCEPTION, \
    EVENT_TIMER, EVENT_TICK, EVENT_CONTRACT
from weathon.quantization.utils.database.sqlite import SqliteDatabase
from weathon.utils.constants import DEFAULT_QUANT_HOME


class RecorderEngine(BaseEngine):
    """
    For running data recorder.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        self.app_name = "DataRecorder"
        setting_filename: str = "data_recorder_setting.json"

        super().__init__(main_engine, event_engine, self.app_name)

        self.queue: Queue = Queue()
        self.thread: Thread = Thread(target=self.run)
        self.active: bool = False

        self.tick_recordings: Dict[str, Dict] = {}
        self.bar_recordings: Dict[str, Dict] = {}
        self.bar_generators: Dict[str, BarGenerator] = {}

        self.timer_count: int = 0
        self.timer_interval: int = 10

        self.ticks: Dict[str, List[TickData]] = defaultdict(list)
        self.bars: Dict[str, List[BarData]] = defaultdict(list)

        self.database: BaseDatabase = SqliteDatabase()

        # self.load_setting()
        self.register_event()
        self.start()
        self.put_event()

    def load_setting(self) -> None:
        """"""
        setting: dict = load_json(self.setting_filename)
        self.tick_recordings = setting.get("tick", {})
        self.bar_recordings = setting.get("bar", {})

    def save_setting(self) -> None:
        """"""
        setting: dict = {
            "tick": self.tick_recordings,
            "bar": self.bar_recordings
        }
        save_json(self.setting_filename, setting)

    def run(self) -> None:
        """"""
        while self.active:
            try:
                task: Any = self.queue.get(timeout=1)
                task_type, data = task

                if task_type == "tick":
                    self.database.save_tick_data(data, stream=True)
                elif task_type == "bar":
                    self.database.save_bar_data(data, stream=True)

            except Empty:
                continue

            except Exception:
                self.active = False

                info = sys.exc_info()
                event: Event = Event(EVENT_RECORDER_EXCEPTION, info)
                self.event_engine.put(event)

    def close(self) -> None:
        """"""
        self.active = False

        if self.thread.is_alive():
            self.thread.join()

    def start(self) -> None:
        """"""
        self.active = True
        self.thread.start()

    def add_bar_recording(self, qt_symbol: str) -> None:
        """"""
        if qt_symbol in self.bar_recordings:
            self.write_log(f"已在K线记录列表中：{qt_symbol}")
            return

        if Exchange.LOCAL.value not in qt_symbol:
            contract: Optional[ContractData] = self.main_engine.get_contract(qt_symbol)
            if not contract:
                self.write_log(f"找不到合约：{qt_symbol}")
                return

            self.bar_recordings[qt_symbol] = {
                "symbol": contract.symbol,
                "exchange": contract.exchange.value,
                "gateway_name": contract.gateway_name
            }

            self.subscribe(contract)
        else:
            self.bar_recordings[qt_symbol] = {}

        self.save_setting()
        self.put_event()

        self.write_log(f"添加K线记录成功：{qt_symbol}")

    def add_tick_recording(self, qt_symbol: str) -> None:
        """"""
        if qt_symbol in self.tick_recordings:
            self.write_log(f"已在Tick记录列表中：{qt_symbol}")
            return

        # For normal contract
        if Exchange.LOCAL.value not in qt_symbol:
            contract: Optional[ContractData] = self.main_engine.get_contract(qt_symbol)
            if not contract:
                self.write_log(f"找不到合约：{qt_symbol}")
                return

            self.tick_recordings[qt_symbol] = {
                "symbol": contract.symbol,
                "exchange": contract.exchange.value,
                "gateway_name": contract.gateway_name
            }

            self.subscribe(contract)
        # No need to subscribe for spread data
        else:
            self.tick_recordings[qt_symbol] = {}

        self.save_setting()
        self.put_event()

        self.write_log(f"添加Tick记录成功：{qt_symbol}")

    def remove_bar_recording(self, qt_symbol: str) -> None:
        """"""
        if qt_symbol not in self.bar_recordings:
            self.write_log(f"不在K线记录列表中：{qt_symbol}")
            return

        self.bar_recordings.pop(qt_symbol)
        self.save_setting()
        self.put_event()

        self.write_log(f"移除K线记录成功：{qt_symbol}")

    def remove_tick_recording(self, qt_symbol: str) -> None:
        """"""
        if qt_symbol not in self.tick_recordings:
            self.write_log(f"不在Tick记录列表中：{qt_symbol}")
            return

        self.tick_recordings.pop(qt_symbol)
        self.save_setting()
        self.put_event()

        self.write_log(f"移除Tick记录成功：{qt_symbol}")

    def register_event(self, EVENT_SPREAD_DATA=None) -> None:
        """"""
        self.event_engine.register(EVENT_TIMER, self.process_timer_event)
        self.event_engine.register(EVENT_TICK, self.process_tick_event)
        self.event_engine.register(EVENT_CONTRACT, self.process_contract_event)
        self.event_engine.register(EVENT_SPREAD_DATA, self.process_spread_event)

    def update_tick(self, tick: TickData) -> None:
        """"""
        if tick.qt_symbol in self.tick_recordings:
            self.record_tick(copy(tick))

        if tick.qt_symbol in self.bar_recordings:
            bg: BarGenerator = self.get_bar_generator(tick.qt_symbol)
            bg.update_tick(copy(tick))

    def process_timer_event(self, event: Event) -> None:
        """"""
        self.timer_count += 1
        if self.timer_count < self.timer_interval:
            return
        self.timer_count = 0

        for bars in self.bars.values():
            self.queue.put(("bar", bars))
        self.bars.clear()

        for ticks in self.ticks.values():
            self.queue.put(("tick", ticks))
        self.ticks.clear()

    def process_tick_event(self, event: Event) -> None:
        """"""
        tick: TickData = event.data
        self.update_tick(tick)

    def process_contract_event(self, event: Event) -> None:
        """"""
        contract: ContractData = event.data
        qt_symbol: str = contract.qt_symbol

        if (qt_symbol in self.tick_recordings or qt_symbol in self.bar_recordings):
            self.subscribe(contract)

    def process_spread_event(self, event: Event) -> None:
        """"""
        spread: SpreadData = event.data
        tick: TickData = spread.to_tick()

        # Filter not inited spread data
        if tick.datetime:
            self.update_tick(tick)

    def write_log(self, msg: str) -> None:
        """"""
        event: Event = Event(
            EVENT_RECORDER_LOG,
            msg
        )
        self.event_engine.put(event)

    def put_event(self) -> None:
        """"""
        tick_symbols: List[str] = list(self.tick_recordings.keys())
        tick_symbols.sort()

        bar_symbols: List[str] = list(self.bar_recordings.keys())
        bar_symbols.sort()

        data: dict = {
            "tick": tick_symbols,
            "bar": bar_symbols
        }

        event: Event = Event(
            EVENT_RECORDER_UPDATE,
            data
        )
        self.event_engine.put(event)

    def record_tick(self, tick: TickData) -> None:
        """"""
        self.ticks[tick.qt_symbol].append(tick)

    def record_bar(self, bar: BarData) -> None:
        """"""
        self.bars[bar.qt_symbol].append(bar)

    def get_bar_generator(self, qt_symbol: str) -> BarGenerator:
        """"""
        bg: Optional[BarGenerator] = self.bar_generators.get(qt_symbol, None)

        if not bg:
            bg = BarGenerator(self.record_bar)
            self.bar_generators[qt_symbol] = bg

        return bg

    def subscribe(self, contract: ContractData) -> None:
        """"""
        req: SubscribeRequest = SubscribeRequest(
            symbol=contract.symbol,
            exchange=contract.exchange
        )
        self.main_engine.subscribe(req, contract.gateway_name)
