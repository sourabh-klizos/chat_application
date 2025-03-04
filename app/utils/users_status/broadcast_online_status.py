# from app.services.redis_client import get_all_online_users
from app.utils.online_user_manager import OnlineUserManager

import asyncio
import json


async def update_online_status(websocket_connections: dict) -> None:

    try:

        online_users = await OnlineUserManager.get_all_online_users()

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
    except Exception as e:  # noqa
        pass
