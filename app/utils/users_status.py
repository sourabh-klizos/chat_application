# from app.services.redis_client import remove_user_online_status
from app.utils.online_user_manager import OnlineUserManager


async def set_user_offline(
    websocket_connections: dict, websocket_id: str, user_id: str
) -> None:
    """Removes a user's WebSocket connection and updates their status."""

    try:

        await OnlineUserManager.remove_user_online_status(user_id)

        if websocket_id in websocket_connections:
            del websocket_connections[websocket_id]
    except Exception as e:  # noqa
        pass
