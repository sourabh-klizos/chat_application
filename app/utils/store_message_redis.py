import redis.asyncio as redis
import json
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation
from app.utils.logger_config import LOGGER
import asyncio


class RedisChatHandler:


    @staticmethod
    async def store_message_in_redis(channel_id, message): #old one
        """Store a message in a Redis Stream instead of a list."""
        try:
            redis_client = await RedisManager.get_redis_client()
            chat_stream = "chat_stream"

            message_data = {
                "channel": channel_id,
                "message": message
            }

            await redis_client.xadd(chat_stream, message_data)

        except Exception  as e:
            LOGGER.error(f"Redis error: {str(e)}", exc_info=True)


    




    @staticmethod
    async def move_chat_to_mongo():
        """Background task to move messages from Redis to MongoDB."""
        print("""Background task to move messages from Redis to MongoDB.""")
        try:
            redis_client = await RedisManager.get_redis_client()
            chat_stream = "chat_stream"

            while True:
                messages = await redis_client.xrange(chat_stream, "-", "+", count=500)
                print("bg messages ============================", messages)
                
                if messages:
                    print("inside msg")
        

                    decoded_messages = list()

                    for message_id,  message in messages:
                        print(message.get('message'))
                        decoded_messages.append(json.loads(message.get('message')))
                        await redis_client.xdel(chat_stream, message_id)


                    print(decoded_messages, " decoded_messages, ==================================")

                    if decoded_messages:
                        await Conversation.bulk_insert_chat(decoded_messages)
                        LOGGER.info(
                        "Messages Moved to Mongo DB "
                        )

                await asyncio.sleep(3)
        except Exception as e:
            await asyncio.sleep(2)
            LOGGER.error(f"Error in move_chat_to_mongo: {e}", exc_info=True)



