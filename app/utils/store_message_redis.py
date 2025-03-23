import redis.asyncio as redis
import json
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation
from app.utils.logger_config import LOGGER
import asyncio


class RedisChatHandler:

    queue = asyncio.Queue()
    batch_size = 2000


    @classmethod
    async def store_message_in_redis(cls, channel_id, message):
        """Store a message in a Redis Stream instead of a list."""

        try:


            await cls.queue.put({"channel": channel_id, "message": message})

            if cls.queue.qsize() >= cls.batch_size:
                messages = [await cls.queue.get() for _ in range(cls.batch_size)]
                
                async with cls.redis_client.pipeline() as pipe:
                    for msg in messages:
                        pipe.xadd(cls.stream_key, msg)
                    await pipe.execute()

                print(f"Stored {cls.batch_size} messages in Redis")

        
            return 
        except Exception as e:
            print("error in store_message_in_redis ", str(e))
    
        



        # try:
        #     redis_client = await RedisManager.get_redis_client()
        #     chat_stream = "chat_stream"

        #     message_data = {
        #         "channel": channel_id,
        #         "message": message
        #     }

        #     await redis_client.xadd(chat_stream, message_data)

        # except redis.exceptions.RedisError as e:
        #     LOGGER.error(f"Redis error: {str(e)}", exc_info=True)


    # @staticmethod
    # async def store_message_in_redis(channel_id, message):
    #     """Store a message in a Redis Stream instead of a list."""
    #     try:
    #         redis_client = await RedisManager.get_redis_client()
    #         chat_stream = "chat_stream"

    #         message_data = {
    #             "channel": channel_id,
    #             "message": message
    #         }

    #         await redis_client.xadd(chat_stream, message_data)

    #     except redis.exceptions.RedisError as e:
    #         LOGGER.error(f"Redis error: {str(e)}", exc_info=True)


    



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
                    # decoded_messages = [
                    #     json.loads(msg[1][b"message"]) for msg in messages
                    # ]

                    decoded_messages = list()

                    for message_id,  message in messages:
                        print(message.get('message'))
                        decoded_messages.append(json.loads(message.get('message')))
                        await redis_client.xdel(chat_stream, message_id)


                    print(decoded_messages, " decoded_messages, ==================================")

                    await Conversation.bulk_insert_chat(decoded_messages)
                    LOGGER.info(
                    "Messages Moved to Mongo DB ================================ "
                    )

                    # for msg_id, _ in messages:
                    #     await redis_client.xdel(chat_stream, msg_id)

                await asyncio.sleep(2)
        except Exception as e:
            await asyncio.sleep(2)
            LOGGER.error(f"Error in move_chat_to_mongo: {e}", exc_info=True)












    # @staticmethod
    # async def store_message_in_redis(channel_id, message):
    #     """Store a message in Redis for the given channel."""
    #     try:
    #         chat_id = f"chat:{channel_id}"
    #         redis_client = await RedisManager.get_redis_client()
    #         await redis_client.rpush(chat_id, str(message))

    #         # print(f"Message successfully stored in Redis for channel: {channel_id}")
    #     except redis.exceptions.RedisError as e:
    #         LOGGER.error(
    #             "Redis error occurred while storing message in channel %s: %s",
    #             chat_id,
    #             str(e),
    #             exc_info=True,
    #         )
    #     except Exception as e:
    #         LOGGER.error(
    #             "An unexpected error occurred while storing message in Redis: %s",
    #             str(e),
    #             exc_info=True,
    #         )

    # @staticmethod
    # async def move_chat_to_mongo(channel_id):
    #     """Move all chat messages from Redis to MongoDB
    #     when either of the user leaves the channel."""
    #     try:
    #         redis_client = await RedisManager.get_redis_client()
    #         chat_id = f"chat:{channel_id}"

    #         messages = await redis_client.lrange(chat_id, 0, -1)
    #         if not messages:
    #             return
    #         # print("mes =====================", messages)
    #         # decoded_messages = [json.loads(message) for message in messages]
    #         decoded_messages = tuple(json.loads(message) for message in messages)

    #         # print("medecoded_messagess =====================", decoded_messages)
    #         await Conversation.bulk_insert_chat(decoded_messages)

    #         await redis_client.delete(chat_id)

    #     except Exception as e:
    #         LOGGER.error(
    #             "An error occurred while saving chat in MongoDB for channel %s: %s",
    #             chat_id,
    #             str(e),
    #             exc_info=True,
    #         )



    # @staticmethod
    # async def store_message_in_redis(channel_id, message):
    #     """Store a message in a Redis Stream instead of a list."""
    #     try:
    #         redis_client = await RedisManager.get_redis_client()
    #         chat_stream = f"chat_stream"

    #         await redis_client.xadd(chat_stream, {"channel": channel_id, "message": message})

    #     except redis.exceptions.RedisError as e:
    #         LOGGER.error("Redis error: %s", str(e), exc_info=True)
