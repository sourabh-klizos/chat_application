import redis.asyncio as redis
import json
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation
from app.utils.logger_config import LOGGER
import asyncio


class RedisChatHandler:

    queue = asyncio.Queue()
    batch_size = 200




######################################################

    @classmethod
    async def store_message_in_redis(cls, channel_id, message):
        """Store a message in a Redis Stream."""
        try:
            await cls.queue.put({"channel": channel_id, "message": message})
            print(f"Message added to queue. Current size: {cls.queue.qsize()}")

            # Process messages only if batch size is reached
            if cls.queue.qsize() >= cls.batch_size:
                await cls.process_messages()

        except Exception as e:
            print("Error in store_message_in_redis:", str(e))

    @classmethod
    async def process_messages(cls):
        """Fetch messages from the queue and store them in Redis."""
        try:
            redis_client = await RedisManager.get_redis_client()
            chat_stream = "chat_stream"

            messages = [await cls.queue.get() for _ in range(cls.batch_size)]
            
            async with redis_client.pipeline() as pipe:
                for msg in messages:
                    pipe.xadd(chat_stream, msg)
                await pipe.execute()

            
            await RedisChatHandler.move_chat_to_mongo("worker_a")

            print(f"Stored {cls.batch_size} messages in Redis")

        except Exception as e:
            print("Error in process_messages:", str(e))

        



    @staticmethod
    async def move_chat_to_mongo(worker_name: str):
        """Background task to move messages from Redis to MongoDB."""
        print("Background task to move messages from Redis to MongoDB.")
        
        try:
            redis_client = await RedisManager.get_redis_client()
            chat_stream = "chat_stream"
            consumer_group = "chat_group"

            # Ensure the consumer group exists
            try:
                await redis_client.xgroup_create(chat_stream, consumer_group, id="0", mkstream=True)
            except Exception as e:
                if "BUSYGROUP" in str(e):
                    print(f"[{worker_name}] Consumer group already exists.")
                else:
                    raise  # Re-raise the exception if it's something else

            # while True:
            messages = await redis_client.xreadgroup(
                groupname=consumer_group,
                consumername=worker_name,
                streams={chat_stream: ">"},
                count=200,
                block=1000  # Wait up to 1 second for new messages
            )

            if messages:
                print(f"bg messages [{worker_name}]:", messages)

                decoded_messages = [
                    json.loads(msg[1]['message']) for stream, msgs in messages for msg in msgs
                ]

                message_ids = [
                    msg[0] for stream, msgs in messages for msg in msgs
                ]

                if decoded_messages:
                    await Conversation.bulk_insert_chat(decoded_messages)
                    LOGGER.info(f"[{worker_name}] Messages moved to MongoDB.")

                    # Acknowledge messages in the consumer group
                    await redis_client.xack(chat_stream, consumer_group, *message_ids)

                    await redis_client.xdel(chat_stream, *message_ids)
                    # LOGGER.info(f"[{worker_name}] Deleted messages from Redis stream.")


                # await asyncio.sleep(1)  # Adjust based on performance needs

        except Exception as e:
            await asyncio.sleep(2)
            LOGGER.error(f"Error in move_chat_to_mongo: {e}", exc_info=True)


