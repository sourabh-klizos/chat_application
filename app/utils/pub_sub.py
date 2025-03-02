import asyncio
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation




class RedisWebSocketManager:
    @staticmethod
    async def subscribe_and_listen(group: str, connected_websockets: list):
        redis_client = await RedisManager.get_pubsub_client()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(group)
        print(f"Subscribed to {group}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    print(f"Received: {message['data']}")
                    print("=======================================")
                    print(connected_websockets)
                    data = message['data']

                    await Conversation.insert_chat(data)

                    await asyncio.gather(
                        *[conn.send_text(data) for conn in connected_websockets]
                    )
        except asyncio.CancelledError:
            print("Listener stopped.")
        finally:
            await pubsub.unsubscribe(group)
            # await redis_client.close()

    @staticmethod
    async def publish_message(group: str, message: str):
        redis_client = await RedisManager.get_pubsub_client()
        await redis_client.publish(group, message)
        print(f"Published: {message} to {group}")
        await redis_client.close()
