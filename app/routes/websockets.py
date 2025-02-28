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
from app.services.redis_client import (
    set_online_users,
    get_all_online_users,
    remove_user_online_status,
    get_redis_client_pubsub,
)
from pymongo.errors import PyMongoError
from datetime import datetime
from app.database.db import get_db
from pymongo.collection import Collection
from bson import ObjectId
from app.utils.convert_bson_id_str import convert_objectids_list, convert_objectid
import json
from app.services.redis_client import redis_pool


ws_routes = APIRouter(prefix="/ws")


active_connections: Dict[str, List] = dict()


async def handle_incoming_message(group: str, message: str):
    if group in active_connections:
        await asyncio.gather(
            *[conn.send_text(message) for conn in active_connections[group]]
        )


websocket_connections = {}


@ws_routes.websocket("/status/{user_id}")
async def user_status(websocket: WebSocket, user_id: str, db=Depends(get_db)):
    bson_id = ObjectId(user_id)
    user_collection: Collection = db["users"]
    await websocket.accept()
    websocket_id = str(id(websocket))
    websocket_connections[websocket_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()

            json_data = json.loads(data)

            if json_data["type"] == "user_left":

                user_to_remove = json_data["user_id"]

                await remove_user_online_status(user_to_remove)

                if websocket_id in websocket_connections:
                    del websocket_connections[websocket_id]




            if (
                json_data["type"] != "user_left"
                or json_data["type"] == "get_online_users"
            ):

                user_details = await user_collection.find_one(
                    {"_id": bson_id}, {"username": 1}
                )

                user_details_dict = await convert_objectid(user_details)

                await set_online_users(user_id, websocket_id, user_details_dict)

            online_users = await get_all_online_users()

            sockets_ids = list()
            for key, _ in online_users.items():
                sockets_ids.append(online_users[key]["websocket_id"])

            online_users_data = [online_users[data]["data"] for data in online_users]

            tasks = list()

            for socket_id in sockets_ids:
                if websocket_connections.get(socket_id):
                    tasks.append(
                        websocket_connections[socket_id].send_text(
                            f"{json.dumps(online_users_data)}"
                        )
                    )

            if tasks:
                await asyncio.gather(*tasks)
            else:
                print("No active websocket connections to send data.")

    except WebSocketDisconnect:
        await remove_user_online_status(user_id)
        if websocket_id in websocket_connections:
            del websocket_connections[websocket_id]

        online_users = await get_all_online_users()


        sockets_ids = list()
        for key, _ in online_users.items():
            sockets_ids.append(online_users[key]["websocket_id"])

        online_users_data = [online_users[data]["data"] for data in online_users]

        tasks = list()

        for socket_id in sockets_ids:
            if websocket_connections.get(socket_id):
                tasks.append(
                    websocket_connections[socket_id].send_text(
                        f"{json.dumps(online_users_data)}"
                    )
                )

        if tasks:
            await asyncio.gather(*tasks)
        else:
            print("No active websocket connections to send data.")


        


async def message_handler(message_data):
    # Process the message data
    print(f"Received message: {message_data.decode('utf-8')}")

    
# from fastapi import WebSocket, WebSocketDisconnect, Depends
# import asyncio
# import json
# from datetime import datetime
# from pymongo.collection import Collection
# from pymongo.errors import PyMongoError

# active_connections = {}

@ws_routes.websocket("/{i}/{other}")
async def websocket_endpoint(
    websocket: WebSocket, i: str, other: str, db=Depends(get_db)
):
    print("======================================================")
    
    chat_collection: Collection = db["chats"]
    
    # Determine the group from the provided parameters
    group = None
    if (i and other) and (other != "null"):
        group: str = i + other
        group = "".join(sorted(group))

    await websocket.accept()

    # Get Redis Pub/Sub client
    client = await get_redis_client_pubsub()
    pubsub = client.pubsub()
    channel = f"chat:{group}"
    
    # Subscribe to the channel
    await pubsub.subscribe(channel)

    # This function listens for messages from Redis and sends them to all connected clients in the group
    async def listen_for_messages(pubsub, group):
        async for message in pubsub.listen():
            if message["type"] == "message":
                # Decode the Redis message data
                redis_data = message["data"].decode()  # Redis message is in bytes, decode it
                print(f"Received Redis message: {redis_data}")
                print("="*50)

                # Ensure the group exists in active_connections
                if group in active_connections:
                    # Forward the Redis message to all WebSocket clients in the group
                    await asyncio.gather(
                        *[conn.send_text(redis_data) for conn in active_connections[group]]
                    )
                else:
                    print(f"Group '{group}' does not have any active connections.")
        # Run the Redis message listener in the background

    listener_task = asyncio.create_task(listen_for_messages(pubsub, group))

    # Track WebSocket connections per group
    if group not in active_connections:
        active_connections[group] = []
    active_connections[group].append(websocket)

    try:
        while True:
            # Wait for a new message from the WebSocket client
            data = await websocket.receive_text()
            json_data = json.loads(data)
            
            # Insert the message into the MongoDB collection
            try:
                await chat_collection.insert_one(
                    {
                        "sender_id": json_data["sender_id"],
                        "receiver_id": json_data["receiver_id"],
                        "text": json_data["text"],
                        "created_at": datetime.now(),
                    }
                )
            except PyMongoError as e:
                print(f"An error occurred while inserting the document: {e}")

            # Publish the message to the Redis channel
            await client.publish(channel, json.dumps(data))

            # Send the message to all other WebSocket clients in the group
            await asyncio.gather(
                *[conn.send_text(data) for conn in active_connections[group]]
            )

    except WebSocketDisconnect:
        # Handle WebSocket disconnection: remove the client and unsubscribe from Redis if necessary
        active_connections[group].remove(websocket)
        if not active_connections[group]:  # Unsubscribe from Redis if no active connections left
            await pubsub.unsubscribe(channel)

    except Exception as e:
        # General error handling
        print(f"Unexpected error: {str(e)}")

    finally:
        # Cleanup: ensure the listener task is canceled and Redis unsubscribe is called
        listener_task.cancel()
        await pubsub.unsubscribe(channel)
        print(f"Unsubscribed from Redis channel: {channel}")
