import asyncio
from app.services.redis_client import RedisManager
from typing import Dict, Any
from app.services.metrics import REDIS_CHANNELS_ACTIVE, REDIS_CHANNELS_TOTAL
from app.utils.logger_config import LOGGER


class RedisWebSocketManager:
    """Manages WebSocket connections with Redis Pub/Sub for real-time messaging."""

    active_listeners: Dict[str, Any] = dict()

    @staticmethod
    async def subscribe_and_listen(group: str, connected_websockets: list):
        """Subscribes to a Redis channel and listens for messages,
        broadcasting to connected WebSockets."""

        if group in RedisWebSocketManager.active_listeners:
            print(f"Listener already running for group {group}")
            return

        REDIS_CHANNELS_ACTIVE.inc()
        REDIS_CHANNELS_TOTAL.inc()
        redis_client = await RedisManager.get_pubsub_client()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(group)
        RedisWebSocketManager.active_listeners[group] = pubsub
        print(f"Subscribed to {group}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    print(f"Received: {message} to {group}")

                    # await asyncio.gather(
                    #     *[conn.send_text(data) for conn in connected_websockets]
                    # )

                    await asyncio.gather(
                        *(conn.send_text(data) for conn in connected_websockets)
                    )

                if not connected_websockets:
                    break
        except asyncio.CancelledError:
            LOGGER.info("Listener for group %s stopped.", group)

        except Exception as e:
            LOGGER.error(
                "Error in listener for group %s: %s", group, str(e), exc_info=True
            )
        finally:
            REDIS_CHANNELS_ACTIVE.dec()
            
            await pubsub.unsubscribe(group)
            await redis_client.close()
            RedisWebSocketManager.active_listeners.pop(group, None)
            LOGGER.info("Unsubscribed from group %s", group)

    @staticmethod
    async def publish_message(group: str, message: str):
        """Publishes a message to a Redis channel."""
        try:

            redis_client = await RedisManager.get_pubsub_client()
            await redis_client.publish(group, message)
            print(f"Published: {message} to {group}")
            # await redis_client.close()
        except Exception as e:
            LOGGER.error(
                "Failed to publish message to group %s: %s",
                group,
                str(e),
                exc_info=True,
            )
            # print(f"failed to public messafe {str(e)}")
