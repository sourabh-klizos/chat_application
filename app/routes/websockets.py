from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from typing import List, Dict
import asyncio
from pymongo.errors import PyMongoError
from datetime import datetime
from app.database.db import get_db
from pymongo.collection import Collection
from bson import ObjectId
import json


from app.utils.users_status.set_user_offline import set_user_offline
from app.utils.users_status.set_users_online import set_users_status_online
from app.utils.users_status.broadcast_online_status import update_online_status
from app.utils.create_unique_group import ChatGroup
from app.utils.chat_conversations import Conversation
from app.utils.get_current_logged_in_user import get_current_user_id


ws_routes = APIRouter(prefix="/ws")


active_connections: Dict[str, List] = dict()


async def handle_incoming_message(group: str, message: str):
    if group in active_connections:
        await asyncio.gather(
            *[conn.send_text(message) for conn in active_connections[group]]
        )


websocket_connections = {}


@ws_routes.websocket("/status/")
async def user_status(websocket: WebSocket, token: str = Query(...)):

    user_id = await get_current_user_id(token)
    await websocket.accept()
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

    except WebSocketDisconnect:

        await set_user_offline(
            websocket_connections=websocket_connections,
            websocket_id=websocket_id,
            user_id=user_id,
        )

        await update_online_status(websocket_connections=websocket_connections)


async def message_handler(message_data):
    # Process the message data
    print(f"Received message: {message_data.decode('utf-8')}")


@ws_routes.websocket("/{other}/")
async def websocket_endpoint(websocket: WebSocket, other: str, token: str = Query(...)):

    current_user = await get_current_user_id(token)

    group = await ChatGroup.create_unique_group(current_user, other)
    await websocket.accept()

    if group not in active_connections:
        active_connections[group] = []
    active_connections[group].append(websocket)

    try:
        while True:

            data = await websocket.receive_text()
            try:

                await Conversation.insert_chat(data)

            except PyMongoError as e:
                print(f"An error occurred while inserting the document: {e}")

            await asyncio.gather(
                *[conn.send_text(data) for conn in active_connections[group]]
            )

    except WebSocketDisconnect:
        active_connections[group].remove(websocket)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
