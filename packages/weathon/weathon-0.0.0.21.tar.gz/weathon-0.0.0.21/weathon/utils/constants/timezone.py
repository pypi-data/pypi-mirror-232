import sys
from tzlocal import get_localzone_name

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo, available_timezones              # noqa
else:
    from backports.zoneinfo import ZoneInfo, available_timezones    # noqa


# 中国上海时区
SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")

CHINA_TZ = SHANGHAI_TZ

LOCAL_TZ = ZoneInfo(get_localzone_name())

DB_TZ = ZoneInfo(get_localzone_name())