from abc import ABC


class BaseEngine(ABC):
    """
    Abstract class for implementing a function engine.
    """

    def __init__( self, main_engine: 'MainEngine', event_engine: 'EventEngine', engine_name: str, **kwargs) -> None:
        """"""
        self.main_engine: 'MainEngine' = main_engine
        self.event_engine: 'EventEngine' = event_engine
        self.engine_name: str = engine_name

    def close(self) -> None:
        """"""
        pass