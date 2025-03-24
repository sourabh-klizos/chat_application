# from app.services.redis_client import get_all_online_users
from app.utils.online_user_manager import OnlineUserManager

import asyncio
import json



async def update_online_status(websocket_connections: dict) -> None:
    """
    Broadcasts the updated list of online users to all active WebSocket connections.

    Fetches online users, formats the data, and sends it to connected clients.
    """
    try:

        online_users = await OnlineUserManager.get_all_online_users()
        print("update_online_status", online_users)

        if online_users:
            sockets_ids = [
                user_socket_id["websocket_id"]
                for user_socket_id in online_users.values()
            ]
            active_online_users = [
                user_data["data"] for user_data in online_users.values()
            ]

            online_users_data = json.dumps(active_online_users)

            tasks = [
                websocket_connections[socket_id].send_text(online_users_data)
                for socket_id in sockets_ids
                if socket_id in websocket_connections
            ]

            if tasks:
                await asyncio.gather(*tasks)

        print("No active websocket connections to send data.")
    except Exception as e:
        print(f"Error updating online status: {e}")
