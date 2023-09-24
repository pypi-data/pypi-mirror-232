import sys
from dataclasses import dataclass
from tzlocal import get_localzone_name
from playhouse.shortcuts import ReconnectMixin

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo, available_timezones  # noqa
else:
    from backports.zoneinfo import ZoneInfo, available_timezones  # noqa

from peewee import MySQLDatabase

DB_TZ = ZoneInfo(get_localzone_name())


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    """带有重连混入的MySQL数据库类"""
    pass


@dataclass
class DatabaseConfig:
    timezone = get_localzone_name()
    database: str = ""
    host: str = ""
    port: int = 0
    user: str = ""
    password: str = ""


# mysql
@dataclass
class MariadbConfig(DatabaseConfig):
    database: str = "quantdb"
    host: str = "192.168.0.193"
    port: int = 3306
    user: str = "quant"
    password: str = "o6yaU0JdikCHWI7E"

    def __post_init__(self):
        self.db = ReconnectMySQLDatabase(database=self.database,
                                         user=self.user,
                                         password=self.password,
                                         host=self.host,
                                         port=self.port)


@dataclass
class Vnpydb(MariadbConfig):
    database = 'vnpydb'
    user = 'vnpy'
    password = 'ZDtVFUYrGosoGtVV'


# redis
@dataclass
class Redis(DatabaseConfig):
    database: str = "redis"
    host: str = "192.168.0.193"
    port: str = 6379
    user: str = ""
    password: str = ""
