from typing import Any, Dict, List

from common.config import Config


class MysqlClient:
    def __init__(self, config: Config | None = None):
        self.config = (config or Config()).mysql

    def query_all(self, sql: str) -> List[Dict[str, Any]]:
        if not self.config.enabled:
            raise RuntimeError("mysql assertion requested, but [mysql].enabled=false")
        import pymysql

        connection = pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            database=self.config.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return list(cursor.fetchall())
        finally:
            connection.close()


class RedisClient:
    def __init__(self, config: Config | None = None):
        self.config = (config or Config()).redis

    def exists(self, key: str) -> bool:
        if not self.config.enabled:
            raise RuntimeError("redis assertion requested, but [redis].enabled=false")
        import redis

        client = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            password=self.config.password or None,
            db=self.config.db,
            decode_responses=True,
        )
        return bool(client.exists(key))

