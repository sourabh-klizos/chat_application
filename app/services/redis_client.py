import redis.asyncio as redis
from typing import Optional

# import json


from app.config import Settings


# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT")

REDIS_HOST = Settings.REDIS_HOST
REDIS_PORT = Settings.REDIS_PORT


class RedisManager:
    _redis_pool: Optional[redis.ConnectionPool] = None

    @staticmethod
    async def get_redis_client():
        """Get a Redis client instance with a connection pool."""
        if RedisManager._redis_pool is None:
            RedisManager._redis_pool = redis.ConnectionPool.from_url(
                f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
            )

        return redis.Redis(connection_pool=RedisManager._redis_pool)

    @staticmethod
    async def get_pubsub_client():
        """Get a Redis client for pub/sub."""
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
