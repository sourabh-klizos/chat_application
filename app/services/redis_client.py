import redis.asyncio as redis
from typing import Optional

# import json
from app.utils.logger_config import LOGGER


from app.config import Settings


# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT")

REDIS_HOST = Settings.REDIS_HOST
REDIS_PORT = Settings.REDIS_PORT


# class RedisManager:
#     _redis_pool: Optional[redis.ConnectionPool] = None

#     @staticmethod
#     async def get_redis_client():
#         """Get a Redis client instance with a connection pool."""
#         if RedisManager._redis_pool is None:
#             RedisManager._redis_pool = redis.ConnectionPool.from_url(
#                 f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
#             )
#             LOGGER.info("Created new Redis connection pool at %s:%s", REDIS_HOST, REDIS_PORT)
            
#         LOGGER.info("Returning Redis client instance from connection pool")
#         return redis.Redis(connection_pool=RedisManager._redis_pool)

#     @staticmethod
#     async def get_pubsub_client():
#         """Get a Redis client for pub/sub."""
#         return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)



class RedisManager:
    _redis_pool: Optional[redis.ConnectionPool] = None

    @staticmethod
    async def get_redis_client():
        """Get a Redis client instance with a connection pool."""
        try:
            if RedisManager._redis_pool is None:
                RedisManager._redis_pool = redis.ConnectionPool.from_url(
                    f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
                )
                LOGGER.info("Created new Redis connection pool at %s:%s", REDIS_HOST, REDIS_PORT)

            LOGGER.info("Returning Redis client instance from connection pool")
            return redis.Redis(connection_pool=RedisManager._redis_pool)
        
        except Exception as e:
            LOGGER.error("Error occurred while getting Redis client: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_pubsub_client():
        """Get a Redis client for pub/sub."""
        try:
            LOGGER.info("Creating new Redis pub/sub client at %s:%s", REDIS_HOST, REDIS_PORT)
            return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        
        except Exception as e:
            LOGGER.error("Error occurred while getting Redis pub/sub client: %s", str(e), exc_info=True)
            raise
