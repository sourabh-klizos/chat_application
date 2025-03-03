import os
import redis.asyncio as redis
from typing import Optional
import json
import asyncio
from dotenv import load_dotenv
from app.config import Settings

# load_dotenv(".env")

# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT")

REDIS_HOST = Settings.REDIS_HOST
REDIS_PORT = Settings.REDIS_PORT


print("redis env========================================",REDIS_HOST ,REDIS_PORT )

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





async def set_online_users(user_id: str, websocket_id, user_data: dict):

    client = await RedisManager.get_redis_client()

    online_users = await client.get("online_users")

    if online_users is None:
        online_users_dict = dict()
    else:
        online_users_dict = json.loads(online_users)

    user_data = {"websocket_id": websocket_id, "data": user_data}
    online_users_dict[user_id] = user_data

    await client.set("online_users", json.dumps(online_users_dict))


async def get_all_online_users():

    client = await RedisManager.get_redis_client()

    online_users = await client.get("online_users")
    if online_users is None:
        return
    online_users_list = json.loads(online_users)
    return online_users_list


async def remove_user_online_status(user_id: str) -> None:

    client = await RedisManager.get_redis_client()

    online_users = await client.get("online_users")

    if online_users is None:
        return

    online_users_dict = json.loads(online_users)

    if user_id not in online_users_dict:
        return

    removed_user = online_users_dict.pop(user_id)

    await client.set("online_users", json.dumps(online_users_dict))





