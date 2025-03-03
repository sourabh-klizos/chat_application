import asyncio
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation




# class RedisWebSocketManager:
#     @staticmethod
#     async def subscribe_and_listen(group: str, connected_websockets: list):
#         redis_client = await RedisManager.get_pubsub_client()
#         pubsub = redis_client.pubsub()
#         await pubsub.subscribe(group)
#         print(f"Subscribed to {group}")

#         try:
#             async for message in pubsub.listen():

#                 if message["type"] == "message":
#                     data = message['data']
#                     print(f"Received: {message} to {group}")

#                     # await Conversation.insert_chat(data)

#                     await asyncio.gather(
#                         *[conn.send_text(data) for conn in connected_websockets]
#                     )

#                 if not connected_websockets: # if no user in connected list break
#                     break
#         except asyncio.CancelledError:
#             print("Listener stopped.")
#         finally:
#             await pubsub.unsubscribe(group)
#             # await redis_client.close()

#     @staticmethod
#     async def publish_message(group: str, message: str):
#         # await Conversation.insert_chat(message)
#         redis_client = await RedisManager.get_pubsub_client()
#         await redis_client.publish(group, message)
#         print(f"Published: {message} to {group}")
#         await redis_client.close()










import asyncio
from app.services.redis_client import RedisManager
from app.utils.chat_conversations import Conversation


class RedisWebSocketManager:
    active_listeners = {}

    @staticmethod
    async def subscribe_and_listen(group: str, connected_websockets: list):
        if group in RedisWebSocketManager.active_listeners:
            print(f"Listener already running for group {group}")
            return

        redis_client = await RedisManager.get_pubsub_client()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(group)
        RedisWebSocketManager.active_listeners[group] = pubsub 
        print(f"Subscribed to {group}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message['data']
                    print(f"Received: {message} to {group}")

                   
                    await asyncio.gather(
                        *[conn.send_text(data) for conn in connected_websockets]
                    )

                if not connected_websockets:
                    break
        except asyncio.CancelledError:
            print(f"Listener for {group} stopped.")
        finally:
            await pubsub.unsubscribe(group)
            RedisWebSocketManager.active_listeners.pop(group, None)
  

    @staticmethod
    async def publish_message(group: str, message: str):
        redis_client = await RedisManager.get_pubsub_client()
        await redis_client.publish(group, message)
        print(f"Published: {message} to {group}")
        await redis_client.close()