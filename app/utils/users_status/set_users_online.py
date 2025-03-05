# from app.services.redis_client import set_online_users
from app.utils.online_user_manager import OnlineUserManager
from app.database.db import get_db

# from pymongo.collection import Collection
from bson import ObjectId
from app.utils.serializers import Serializers

from pymongo import errors


async def set_users_status_online(user_id, websocket_id):
    try:

        async for db in get_db():
            user_collection = db["users"]
            bson_id = ObjectId(user_id)

            user_details = await user_collection.find_one(
                {"_id": bson_id}, {"username": 1}
            )

            if user_details is None:
                raise Exception(f"User with ID {user_id} not found.")

            user_details_dict = await Serializers.convert_id_to_string(user_details)

            await OnlineUserManager.set_online_users(
                user_id, websocket_id, user_details_dict
            )

    except errors.PyMongoError as e:
        print(f"Database error occurred: {e}")
    except Exception as e:

        print(f"An error occurred: {e}")
