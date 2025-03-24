import redis.asyncio as redis
from typing import Optional
from redis.asyncio import Redis
from app.utils.logger_config import LOGGER
from app.config import Settings


REDIS_HOST = Settings.REDIS_HOST
REDIS_PORT = Settings.REDIS_PORT





class RedisManager:
    _redis_pool: Optional[redis.ConnectionPool] = None

    @staticmethod
    async def get_redis_client():
        """Get a Redis client instance with a connection pool."""
        try:
            if RedisManager._redis_pool is None:
                RedisManager._redis_pool = redis.ConnectionPool.from_url(
                    f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True,
                    max_connections=5000
                )
                LOGGER.info(
                    "Created new Redis connection pool at %s:%s", REDIS_HOST, REDIS_PORT
                )

            LOGGER.info("Returning Redis client instance from connection pool")
            return redis.Redis(connection_pool=RedisManager._redis_pool)

        except Exception as e:
            LOGGER.error(
                "Error occurred while getting Redis client: %s", str(e), exc_info=True
            )
            raise



    @staticmethod
    async def get_pubsub_client():
        """Get an async Redis client for pub/sub using the connection pool."""
        try:
            return await RedisManager.get_redis_client()
        except Exception as e:
            LOGGER.error("Error occurred while getting Redis pub/sub client: %s", str(e), exc_info=True)
            raise



    
