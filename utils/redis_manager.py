import redis.asyncio as redis
from typing import Optional
import config

class RedisPool:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True,
            max_connections=10
        )
        self._conn: Optional[redis.Redis] = None

    async def __aenter__(self) -> redis.Redis:
        self._conn = redis.Redis(connection_pool=self.pool)
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            await self._conn.close()
            self._conn = None