from collections import defaultdict
from datetime import datetime
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

from weathon.quantization.utils.constants import EVENT_TIMER



class Event:
    """
    Event object consists of a type string which is used
    by event engine for distributing event, and a data
    object which contains the real data.
    """

    def __init__(self, type: str, data: Any = None) -> None:
        """"""
        self.type: str = type
        self.data: Any = data


# Defines handler function to be used in event engine.
HandlerType: callable = Callable[[Event], None]


class EventEngine:
    """
    事件驱动：当某个新的事件被推送到程序中时（如API推送新的行情、成交），程序立即调用和这个事件相对应的处理函数进行相关的操作。

    事件驱动引擎管理不同事件的事件监听函数并执行所有和事件驱动相关的操作
    Event engine distributes event object based on its type
    to those handlers registered.

    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    """

    def __init__(self, interval: int = 1) -> None:
        """
        Timer event is generated every 1 second by default, if
        interval not specified.
        """
        # TODO:事件可以设置优先级（优先队列）
        self._interval: int = interval
        self._queue: Queue = Queue()  # 事件队列
        self._active: bool = False  # 事件引擎开关
        self._thread: Thread = Thread(target=self._run)  # 事件处理线程
        self._timer: Thread = Thread(target=self._run_timer)  # 计时器
        self._handlers: defaultdict = defaultdict(list)  # 事件处理函数字典
        self._general_handlers: List = []

    def _run(self) -> None:
        """
        事件处理线程连续运行用
        Get event from queue and then process it.
        """
        while self._active:
            try:
                # 获取事件的阻塞时间设为1秒：如果队列有值返回对应事件，如果没有值，就停顿1s
                event: Event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """
        处理事件，调用注册在引擎中的监听函数。

        首先将事件分发给注册的事件处理器，然后将事件分发给那些监听所有类型的通用处理程序
        """
        # 检查是否存在对该事件进行监听的处理函数
        if event.type in self._handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """
        计时器固定事件间隔触发后，向事件队列中存入计时器事件
        Sleep by interval second(s) and then generate a timer event.
        """
        while self._active:
            sleep(self._interval)
            event: Event = Event(type=EVENT_TIMER,data=self._interval)
            self.put(event)

    def start(self) -> None:
        """
        启动引擎
        Start event engine to process events and generate timer events.
        """
        # 将引擎设为启动
        self._active = True
        # 启动事件处理线程
        self._thread.start()
        # 启动计时器，计时器事件间隔默认设定为1秒
        self._timer.start()

    def stop(self) -> None:
        """
        停止引擎
        Stop event engine.
        """
        # 将引擎设为停止
        self._active = False
        # 停止计时器
        self._timer.join()
        # 等待事件处理线程退出
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        向事件队列中存入新的事件
        Put an event object into event queue.
        """
        self._queue.put(event)

    def register(self, type: str, handler: HandlerType) -> None:
        """
        向引擎中注册监听函数
        Register a new handler function for a specific event type. Every
        function can only be registered once for each event type.
        """
        # 获取该事件类型对应的处理函数列表
        handler_list: list = self._handlers[type]
        # 要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        向引擎中注销监听函数
        Unregister an existing handler function from event engine.
        """
        # 获取该事件类型对应的处理函数列表
        handler_list: list = self._handlers[type]
        # 如果该函数存在于列表中，则移除
        if handler in handler_list:
            handler_list.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """
        Register a new handler function for all event types. Every
        function can only be registered once for each event type.
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """
        Unregister an existing general handler function.
        """
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)



def test():
    """测试函数"""
    def simpletest(event:Event):
        print(u'处理每秒触发的计时器事件：%s' % str(datetime.now()))

    ee = EventEngine()
    ee.register(EVENT_TIMER, simpletest)
    ee.start()

if __name__ == '__main__':
    test()