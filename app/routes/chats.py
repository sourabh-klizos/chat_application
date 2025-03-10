from fastapi import APIRouter, HTTPException, status, Depends

from app.utils.get_current_logged_in_user import get_current_user_id
from app.utils.logger_config import LOGGER
from app.utils.chat_conversations import Conversation
from app.services.metrics import MONGO_DB_CONNECTIONS


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


        chat_history = await Conversation.get_chat_history(current_user, other_user_id)
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
