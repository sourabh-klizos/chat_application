from pymongo.collection import Collection
from app.utils.serializers import Serializers
from datetime import datetime
from app.database.db import get_db
import json


class Conversation:
    @staticmethod
    async def get_chat_history(user_1, user_2):
        """
        Retrieve chat history between two users sorted by creation time.
        :param db_generator: Async generator for the database connection
        :param user_1: First user ID
        :param user_2: Second user ID
        :return: List of chat messages
        """
        async for db in get_db():
            chat_collection: Collection = db["chats"]
            query = {
                "$or": [
                    {"sender_id": user_1, "receiver_id": user_2},
                    {"sender_id": user_2, "receiver_id": user_1},
                ]
            }
            cursor = chat_collection.find(query).sort("created_at", 1)
            chats_list = await cursor.to_list(length=100)
            chats_history = await Serializers.convert_ids_to_strings(chats_list)
            return chats_history

    @staticmethod
    async def insert_chat(data: str):
        """Insert a new chat message into MongoDB."""
        json_data = json.loads(data)

        async for db in get_db():
            chat_collection: Collection = db["chats"]

            chat_message = {
                "sender_id": json_data["sender_id"],
                "receiver_id": json_data["receiver_id"],
                "text": json_data["text"],
                "created_at": datetime.now(),
            }
            await chat_collection.insert_one(chat_message)
