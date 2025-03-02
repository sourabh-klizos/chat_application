from app.services.redis_client import remove_user_online_status


async def set_user_offline(
    websocket_connections: dict, websocket_id: str, user_id: str
) -> None:

    try:

        await remove_user_online_status(user_id)

        if websocket_id in websocket_connections:
            del websocket_connections[websocket_id]
    except Exception as e:
        pass
