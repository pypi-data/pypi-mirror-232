from pathlib import Path
# home
HOME_PATH = Path.home()

## weathon
DEFAULT_WEATHON_HOME = HOME_PATH.joinpath(".weathon")

### quant
DEFAULT_QUANT_HOME = DEFAULT_WEATHON_HOME.joinpath(".quant")
DEFAULT_QUANT_LOG = DEFAULT_QUANT_HOME.joinpath("log")


