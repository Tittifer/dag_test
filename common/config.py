import configparser
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from common.paths import CONF_DIR


@dataclass(frozen=True)
class ApiConfig:
    host: str
    timeout: float


@dataclass(frozen=True)
class MysqlConfig:
    enabled: bool
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass(frozen=True)
class RedisConfig:
    enabled: bool
    host: str
    port: int
    password: str
    db: int


class Config:
    def __init__(self, config_file: Optional[Path] = None, base_url: Optional[str] = None):
        self.config_file = config_file or CONF_DIR / "config.ini"
        self.parser = configparser.ConfigParser()
        read_files = self.parser.read(self.config_file, encoding="utf-8")
        if not read_files:
            raise FileNotFoundError(f"config file not found: {self.config_file}")
        self._base_url = base_url or os.getenv("DAG_API_HOST")

    @property
    def api(self) -> ApiConfig:
        host = self._base_url or self.parser.get("api", "host")
        return ApiConfig(
            host=host.rstrip("/"),
            timeout=self.parser.getfloat("api", "timeout", fallback=10.0),
        )

    @property
    def mysql(self) -> MysqlConfig:
        return MysqlConfig(
            enabled=self.parser.getboolean("mysql", "enabled", fallback=False),
            host=self.parser.get("mysql", "host", fallback="localhost"),
            port=self.parser.getint("mysql", "port", fallback=3306),
            database=self.parser.get("mysql", "database", fallback="dag_docker_sim"),
            username=self.parser.get("mysql", "username", fallback="root"),
            password=self.parser.get("mysql", "password", fallback=""),
        )

    @property
    def redis(self) -> RedisConfig:
        return RedisConfig(
            enabled=self.parser.getboolean("redis", "enabled", fallback=False),
            host=self.parser.get("redis", "host", fallback="localhost"),
            port=self.parser.getint("redis", "port", fallback=6379),
            password=self.parser.get("redis", "password", fallback=""),
            db=self.parser.getint("redis", "db", fallback=0),
        )

    def get(self, section: str, option: str, fallback: Optional[str] = None) -> Optional[str]:
        return self.parser.get(section, option, fallback=fallback)

