from pymongo.collection import Collection
from app.utils.serializers import Serializers
from app.database.db import get_db
import json
from app.services.metrics import MONGO_DB_CONNECTIONS
from app.utils.logger_config import LOGGER

class Conversation:
    """
    Handles chat history retrieval and message insertion in MongoDB.
    """

    @staticmethod
    async def get_chat_history(user_1, user_2):
        """
        Retrieve chat history between two users sorted by creation time.

        :param user_1: First user's ID.
        :param user_2: Second user's ID.
        :return: List of chat messages with converted IDs, or an empty list on failure.
        """
        try:
            async for db in get_db():
                chat_collection: Collection = db["chats"]
                query = {
                    "$or": [
                        {"sender_id": user_1, "receiver_id": user_2},
                        {"sender_id": user_2, "receiver_id": user_1},
                    ]
                }
                cursor = chat_collection.find(query).sort("created_at", 1)
                chats_list = await cursor.to_list(length=None)

                if not chats_list:
                    return list()

                chats_history = await Serializers.convert_ids_to_strings(chats_list)
                return chats_history
                
        except Exception as e:
            LOGGER.error("Error occurred while retrieving chat history: %s", str(e), exc_info=True)
            return list()

    @staticmethod
    async def insert_chat(data: str):
        """
        Insert a single chat message into MongoDB.

        :param data: JSON string containing chat message details.
        """

        try:
            json_data = json.loads(data)

            async for db in get_db():
                chat_collection: Collection = db["chats"]

                # chat_message = {
                #     "sender_id": json_data["sender_id"],
                #     "receiver_id": json_data["receiver_id"],
                #     "text": json_data["text"],
                #     "created_at": datetime.now().isoformat(),
                # }

                MONGO_DB_CONNECTIONS.inc()
                await chat_collection.insert_one(json_data)
        except Exception as e:
            LOGGER.error("Error occurred while inserting chat message: %s", str(e), exc_info=True)


    @staticmethod
    async def bulk_insert_chat(data: list[dict]):
        """Insert bulk new  chat message into MongoDB."""

        try:
            async for db in get_db():
                chat_collection: Collection = db["chats"]

                MONGO_DB_CONNECTIONS.inc()
                await chat_collection.insert_many(data)
        except Exception as e:
            LOGGER.error("Error occurred while inserting bulk chat message: %s", str(e), exc_info=True)

