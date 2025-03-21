from fastapi import (
    APIRouter,
    # Query,
    WebSocket,
    WebSocketDisconnect,
)
from typing import List, Dict
import asyncio

import json
import time
from app.utils.logger_config import LOGGER
from app.utils.users_status.set_users_online import set_users_status_online
from app.utils.users_status.set_user_offline import set_user_offline

# from app.utils.online_user_manager import OnlineUserManager
# from app.services.redis_client import RedisManager
from app.utils.users_status.broadcast_online_status import update_online_status
from app.utils.create_unique_group import ChatGroup

# from app.utils.chat_conversations import Conversation

# from app.utils.get_current_logged_in_user import get_current_user_id
from app.utils.pub_sub import RedisWebSocketManager
from app.services.metrics import (
    WS_CONNECTIONS_ACTIVE,
    WS_CONNECTIONS_TOTAL,
    WS_MESSAGES,
    MESSAGE_PROCESSING_TIME,
    WS_CONNECTIONS_DISC,
)
from app.utils.store_message_redis import RedisChatHandler


ws_routes = APIRouter(prefix="/ws")


active_connections: Dict[str, List] = dict()


websocket_connections: Dict[str, WebSocket] = dict()


@ws_routes.websocket("/status/{user_id}/")
async def user_status(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint to track and update user online status in real time,
    handling connections, status changes, and disconnections.
    """

    await websocket.accept()

    WS_CONNECTIONS_ACTIVE.inc()
    WS_CONNECTIONS_TOTAL.inc()

    websocket_id = str(id(websocket))
    websocket_connections[websocket_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()

            json_data = json.loads(data)

            if json_data["type"] == "user_left":

                await set_user_offline(
                    websocket_connections=websocket_connections,
                    websocket_id=websocket_id,
                    user_id=user_id,
                )

            if (
                json_data["type"]
                != "user_left"
                # or json_data["type"] == "get_online_users"
            ):
                await set_users_status_online(
                    websocket_id=websocket_id, user_id=user_id
                )

            await update_online_status(websocket_connections=websocket_connections)

    except Exception as e:
        LOGGER.error(
            "WebSocket error: user_id=%s, error=%s", user_id, str(e), exc_info=True
        )

    finally:
        WS_CONNECTIONS_ACTIVE.dec()

        await set_user_offline(
            websocket_connections=websocket_connections,
            websocket_id=websocket_id,
            user_id=user_id,
        )

        websocket_connections.pop(websocket_id, None)
        LOGGER.info(
            "WebSocket connection closed: user_id=%s, websocket_id=%s",
            user_id,
            websocket_id,
        )




# message_queue = asyncio.Queue()


# async def message_worker():
#     """Background worker to process messages from the queue."""
#     while True:
#         group, data = await message_queue.get()  # Get the next message
#         await RedisChatHandler.store_message_in_redis(group, data)  # Store in Redis
#         message_queue.task_done()  # Mark as done

# Start multiple workers (adjust the number based on load)


# asyncio.create_task(message_worker())

# for _ in range(5):  # 5 parallel workers
#     asyncio.create_task(message_worker())




@ws_routes.websocket("/{current_user}/{other}/")
async def websocket_chat(websocket: WebSocket, other: str, current_user: str):
    """
    WebSocket endpoint for real-time chat between two users.

    Handles connections, message broadcasting, and disconnections,
    leveraging Redis for pub/sub.
    """

    current_user = current_user

    group = await ChatGroup.create_unique_group(current_user, other)
    await websocket.accept()

    WS_CONNECTIONS_ACTIVE.inc()
    WS_CONNECTIONS_TOTAL.inc()

    if group not in active_connections:
        active_connections[group] = []
        listener_task = asyncio.create_task(
            RedisWebSocketManager.subscribe_and_listen(group, active_connections[group])
        )

    active_connections[group].append(websocket)

    try:
        while True:
            # start_time = time.time()
            data = await websocket.receive_text()

            WS_MESSAGES.inc()

            # await message_queue.put((group, data))


            asyncio.create_task(RedisChatHandler.store_message_in_redis(group, data))

            # await RedisWebSocketManager.publish_message(group, data)

            asyncio.create_task(
                RedisWebSocketManager.publish_message(group, data)
            )
            
            # latency = time.time() - start_time

            # MESSAGE_PROCESSING_TIME.observe(latency)

    except WebSocketDisconnect:
        # if websocket in active_connections[group]:
        #     active_connections[group].remove(websocket)
        pass

    except Exception as e:
        LOGGER.error(
            "Unexpected error in WebSocket: group=%s, error=%s",
            group,
            str(e),
            exc_info=True,
        )

    finally:
        LOGGER.info("Entering finally block")
        WS_CONNECTIONS_DISC.dec()

        WS_CONNECTIONS_ACTIVE.dec()

        try:
            # asyncio.create_task(RedisChatHandler.move_chat_to_mongo(group))
            LOGGER.info("Moving chat from Redis to MongoDB for group=%s", group)

        except Exception as e:
            LOGGER.error("Error moving chat to MongoDB: %s", str(e), exc_info=True)

        if websocket in active_connections[group]:
            active_connections[group].remove(websocket)

        if len(active_connections[group]) == 0 and "listener_task" in locals():
            listener_task.cancel()
            del active_connections[group]
            LOGGER.info(
                "Removed WebSocket group and cancelled Redis listener: group=%s", group
            )
