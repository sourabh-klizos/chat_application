# from app.services.redis_client import remove_user_online_status
from app.utils.online_user_manager import OnlineUserManager


async def set_user_offline(
    websocket_connections: dict, websocket_id: str, user_id: str
) -> None:

    try:

        await OnlineUserManager.remove_user_online_status(user_id)

        # if websocket_id in websocket_connections:
        #     del websocket_connections[websocket_id]
    except Exception as e:
        print(f"An error occurred: {e}")
