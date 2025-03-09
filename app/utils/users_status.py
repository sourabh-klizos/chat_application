# from app.services.redis_client import remove_user_online_status
from app.utils.online_user_manager import OnlineUserManager
from app.utils.logger_config import LOGGER


async def set_user_offline(
    websocket_connections: dict, websocket_id: str, user_id: str
) -> None:
    """Removes a user's WebSocket connection and updates their status."""

    try:

        await OnlineUserManager.remove_user_online_status(user_id)

        if websocket_id in websocket_connections:
            del websocket_connections[websocket_id]
    except Exception as e:
        LOGGER.error(
            "Error occurred while setting user %s offline: %s",
            user_id,
            str(e),
            exc_info=True,
        )
