from pathlib import Path

from weathon.quantization.base import BaseApp
from weathon.quantization.engine.recorder import RecorderEngine
from weathon.quantization.utils.constants.app_name import DATA_RECORDER_NAME


class DataRecorderApp(BaseApp):
    """"""

    app_name: str = DATA_RECORDER_NAME
    app_module: str = __module__
    app_path: Path = Path(__file__).parent
    display_name: str = "行情记录"
    engine_class: RecorderEngine = RecorderEngine
    widget_name: str = "RecorderManager"
    icon_name: str = str(app_path.joinpath("ui", "recorder.ico"))