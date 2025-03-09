import redis.asyncio as redis
import json
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation
from app.utils.logger_config import LOGGER


class RedisChatHandler:
    @staticmethod
    async def store_message_in_redis(channel_id, message):
        """Store a message in Redis for the given channel."""
        try:

            redis_client = await RedisManager.get_redis_client()
            await redis_client.rpush(channel_id, str(message))
            # print(f"Message successfully stored in Redis for channel: {channel_id}")
        except redis.exceptions.RedisError as e:
            LOGGER.error(
                "Redis error occurred while storing message in channel %s: %s",
                channel_id,
                str(e),
                exc_info=True,
            )
        except Exception as e:
            LOGGER.error(
                "An unexpected error occurred while storing message in Redis: %s",
                str(e),
                exc_info=True,
            )

    @staticmethod
    async def move_chat_to_mongo(channel_id):
        """Move all chat messages from Redis to MongoDB
        when either of the user leaves the channel."""
        try:
            redis_client = await RedisManager.get_redis_client()

            messages = await redis_client.lrange(channel_id, 0, -1)
            if not messages:
                return
            # print("mes =====================", messages)
            decoded_messages = [json.loads(message) for message in messages]

            # print("medecoded_messagess =====================", decoded_messages)
            await Conversation.bulk_insert_chat(decoded_messages)

            await redis_client.delete(channel_id)

        except Exception as e:
            LOGGER.error(
                "An error occurred while saving chat in MongoDB for channel %s: %s",
                channel_id,
                str(e),
                exc_info=True,
            )
