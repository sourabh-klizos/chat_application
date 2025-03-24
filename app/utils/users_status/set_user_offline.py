# from app.services.redis_client import remove_user_online_status
from app.utils.online_user_manager import OnlineUserManager


async def set_user_offline(
    websocket_connections: dict, websocket_id: str, user_id: str
) -> None:
    """
    Marks a user as offline by removing their online status.

    Removes the user from the online users list in the database.
    """

    try:

        await OnlineUserManager.remove_user_online_status(user_id)

    except Exception as e:
        print(f"An error occurred: {e}")
