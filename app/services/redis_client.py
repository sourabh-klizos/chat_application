import os
import redis.asyncio as redis
from typing import Optional
import json


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_CHANNEL = "chat"


redis_pool: Optional[redis.ConnectionPool] = None

redis_client_pubsub: Optional[redis.Redis] = None


async def get_redis_client():
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True
        )

    return redis.Redis(connection_pool=redis_pool)


async def get_redis_client_pubsub():
    global redis_client_pubsub
    if redis_client_pubsub is None:
        redis_client_pubsub = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return redis_client_pubsub


# async def get_redis_pubsub_client():
#     return redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)


# async def subscribe_to_channel(channel: str):
#     client = await get_redis_client()

#     pubsub = client.pubsub()

#     await pubsub.subscribe(channel)

#     async for message in pubsub.listen():
#         if message["type"] == "message":
#             # await message_handler(message["data"])
#             await print(message)


async def set_online_users(user_id: str, websocket_id, user_data: dict):
    client = await get_redis_client()

    online_users = await client.get("online_users")

    if online_users is None:
        online_users_dict = dict()
    else:
        online_users_dict = json.loads(online_users)

    user_data = {"websocket_id": websocket_id, "data": user_data}
    online_users_dict[user_id] = user_data

    await client.set("online_users", json.dumps(online_users_dict))


async def get_all_online_users():
    client = await get_redis_client()

    online_users = await client.get("online_users")
    online_users_list = json.loads(online_users)
    return online_users_list


async def remove_user_online_status(user_id: str) -> None:
    client = await get_redis_client()

    online_users = await client.get("online_users")

    if online_users is None:
        return

    online_users_dict = json.loads(online_users)

    if user_id not in online_users_dict:
        return

    removed_user = online_users_dict.pop(user_id)

    await client.set("online_users", json.dumps(online_users_dict))
