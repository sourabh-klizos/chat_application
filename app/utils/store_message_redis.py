import redis.asyncio as redis
import json
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation


class RedisChatHandler:
    @staticmethod
    async def store_message_in_redis(channel_id, message):
        """Store a message in Redis for the given channel."""
        try:
            r = await RedisManager.get_redis_client()
            await r.lpush(channel_id, str(message))
            print(f"Message successfully stored in Redis for channel: {channel_id}")
        except redis.exceptions.RedisError as e:
            print(f"Redis error occurred while storing message: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    async def move_chat_to_mongo(channel_id):
        """Move all chat messages from Redis to MongoDB
        when the user leaves the channel."""
        try:
            r = await RedisManager.get_redis_client()

            messages = await r.lrange(channel_id, 0, -1)

            decoded_messages = [json.loads(message) for message in messages]

            await Conversation.bulk_insert_chat(decoded_messages)

            await r.delete(channel_id)

        except Exception as e:
            print(f"An error occurred: while saving chat in mongodb {e}")
