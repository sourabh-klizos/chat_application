from fastapi import APIRouter, HTTPException, status, Depends

from pymongo.collection import Collection
from app.utils.convert_bson_id_str import convert_objectids_list, convert_objectid

from app.database.db import get_db
from app.utils.chat_conversations import Conversation


chat_routes = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@chat_routes.get(
    "/history/{user_1}/{user_2}",
    status_code=status.HTTP_200_OK,
)
async def get_chat_history(
    user_1: str,
    user_2: str,
    db=Depends(get_db),
):

    try:

        chat_history = await Conversation.get_chat_history(user_1, user_2)

        # chat_collection: Collection = db["chats"]

        # query = {
        #     "$or": [
        #         {"sender_id": user_1, "receiver_id": user_2},
        #         {"sender_id": user_2, "receiver_id": user_1},
        #     ]
        # }

        # cursor = chat_collection.find(query).sort("created_at", 1)
        # chats_list = await cursor.to_list(length=100)

        # chat_history = await convert_objectids_list(chats_list)
        return chat_history

    except HTTPException as http_error:
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail,
        )

    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving chat history.",
        )
