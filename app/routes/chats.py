from fastapi import APIRouter, HTTPException, status, Depends

from app.utils.get_current_logged_in_user import get_current_user_id
from app.utils.logger_config import LOGGER
from app.utils.chat_conversations import Conversation
from app.services.metrics import MONGO_DB_CONNECTIONS
from app.utils.create_unique_group import ChatGroup
from app.services.redis_client import RedisManager
import json


async def get_latest_chat_from_redis(current_user_id: str, other_id: str):
    group = await ChatGroup.create_unique_group(current_user_id, other_id)
    redis_client = await RedisManager.get_redis_client()

    chat_id = f"chat:{group}"
    print(f"Fetching chat for group: {chat_id}")  # More informative log

    messages = await redis_client.lrange(chat_id, 0, -1)

    if not messages:
        return []

    # Decode messages safely, handling potential JSON errors
    decoded_messages = []
    for message in messages:
        try:
            decoded_messages.append(json.loads(message))
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON message: {message}")

    return decoded_messages




chat_routes = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@chat_routes.get(
    "/history/{other_user_id}",
    status_code=status.HTTP_200_OK,
)
async def get_chat_history(
    other_user_id: str, current_user=Depends(get_current_user_id)
):
    """Retrieves chat history between the current user and another user."""
    try:

        latest_messages = await get_latest_chat_from_redis(current_user,other_user_id )
        print("----------------------------------latest",latest_messages)


        chat_history = await Conversation.get_chat_history(current_user, other_user_id)

        if latest_messages:
            chat_history.extend(latest_messages)
        MONGO_DB_CONNECTIONS.inc()
        return chat_history

    except HTTPException as http_error:
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail,
        )

    except Exception as e:
        LOGGER.critical("Unexpected error during fetching chats: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving chat history.",
        )
