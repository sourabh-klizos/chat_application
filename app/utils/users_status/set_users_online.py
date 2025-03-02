from app.services.redis_client import set_online_users
from app.database.db import get_db
from pymongo.collection import Collection
from bson import ObjectId
from app.utils.serializers import Serializers


async def set_users_status_online(websocket_id: str, user_id: str):

    async for db in get_db():
        user_collection: Collection = db["users"]
        bson_id = ObjectId(user_id)
        user_details = await user_collection.find_one({"_id": bson_id}, {"username": 1})

        user_details_dict = await Serializers.convert_id_to_string(user_details)

        await set_online_users(user_id, websocket_id, user_details_dict)
