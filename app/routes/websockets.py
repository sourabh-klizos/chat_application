from fastapi import (
    APIRouter,
    # Query,
    WebSocket,
    WebSocketDisconnect,
)
from typing import List, Dict
import asyncio

import json
import traceback
import time

from app.utils.users_status.set_users_online import set_users_status_online
from app.utils.users_status.set_user_offline import set_user_offline

# from app.utils.online_user_manager import OnlineUserManager
# from app.services.redis_client import RedisManager
from app.utils.users_status.broadcast_online_status import update_online_status
from app.utils.create_unique_group import ChatGroup
from app.utils.chat_conversations import Conversation

# from app.utils.get_current_logged_in_user import get_current_user_id
from app.utils.pub_sub import RedisWebSocketManager
from app.services.metrics import (
    WS_CONNECTIONS_ACTIVE,
    WS_CONNECTIONS_TOTAL,
    WS_MESSAGES,
    MESSAGE_PROCESSING_TIME,
)
from app.utils.store_message_redis import RedisChatHandler


ws_routes = APIRouter(prefix="/ws")


active_connections: Dict[str, List] = dict()


async def handle_incoming_message(group: str, message: str):
    if group in active_connections:
        await asyncio.gather(
            *[conn.send_text(message) for conn in active_connections[group]]
        )


websocket_connections: Dict[str, WebSocket] = dict()


@ws_routes.websocket("/status/{user_id}/")
async def user_status(websocket: WebSocket, user_id: str):

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
                json_data["type"] != "user_left"
                or json_data["type"] == "get_online_users"
            ):
                await set_users_status_online(
                    websocket_id=websocket_id, user_id=user_id
                )

            await update_online_status(websocket_connections=websocket_connections)

    except Exception as e:
        print("Error", str(e))

    finally:
        WS_CONNECTIONS_ACTIVE.dec()
        await set_user_offline(
            websocket_connections=websocket_connections,
            websocket_id=websocket_id,
            user_id=user_id,
        )

        websocket_connections.pop(websocket_id, None)


@ws_routes.websocket("/{current_user}/{other}/")
async def websocket_chat(websocket: WebSocket, other: str, current_user: str):
    #  token: str = Query(...)
    # current_user = await get_current_user_id(token)
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
            start_time = time.time()
            data = await websocket.receive_text()

            WS_MESSAGES.inc()

            # await RedisChatHandler.store_message_in_redis(group, data)

            if len(active_connections[group]) == 1:
                asyncio.create_task(Conversation.insert_chat(data))
            else:
                await RedisChatHandler.store_message_in_redis(group, data)

            # await Conversation.insert_chat(data)

            # asyncio.create_task(
            #     Conversation.insert_chat(data)
            # )

            await RedisWebSocketManager.publish_message(group, data)
            latency = time.time() - start_time

            MESSAGE_PROCESSING_TIME.observe(latency)

    except WebSocketDisconnect:
        print("ws -===============================================exp")
        # await websocket.close(code=1000)
        # WS_CONNECTIONS_ACTIVE.dec()
        # await RedisChatHandler.move_chat_to_mongo(group)

        # if websocket in active_connections[group]:
        #     active_connections[group].remove(websocket)

        # if websocket in active_connections[group]:
        #     if len(active_connections[group]) == 0:
        #         listener_task.cancel()
        #         del active_connections[group]
        pass

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.format_exc()

    finally:
        print("ws -===============================================exp print finally")
        WS_CONNECTIONS_ACTIVE.dec()
        # await move_chat_to_mongo(group)

        asyncio.create_task(RedisChatHandler.move_chat_to_mongo(group))
        # await RedisChatHandler.move_chat_to_mongo(group)

        if websocket in active_connections[group]:
            active_connections[group].remove(websocket)

        if len(active_connections[group]) == 0 and "listener_task" in locals():
            listener_task.cancel()
            del active_connections[group]
