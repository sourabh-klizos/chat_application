import json
from typing import Optional, Dict
from app.services.redis_client import RedisManager
from app.utils.logger_config import LOGGER

class OnlineUserManager:

    @staticmethod
    async def set_online_user(user_id: str, websocket_id: str, user_data: dict) -> None:
        """
        Set a user's online status using Redis HSET.
        """
        try:
            client = await RedisManager.get_redis_client()

            user_key = "online_users"
            user_data = {"websocket_id": websocket_id, "data": user_data}

            await client.hset(user_key, user_id, json.dumps(user_data))

            # print(f"User {user_id} set online =========")
        except Exception as e:
            LOGGER.error("Error occurred while setting online user %s: %s", user_id, str(e), exc_info=True)
            raise

    @staticmethod
    async def get_all_online_users() -> Optional[Dict[str, dict]]:
        """
        Retrieve all online users using Redis HGETALL.
        """
        try:
            client = await RedisManager.get_redis_client()

            user_key = "online_users"
            online_users = await client.hgetall(user_key)

            if not online_users:
                return None

            online_users_dict = {
                user_id: json.loads(user_data)
                for user_id, user_data in online_users.items()
            }

            # print("Online users ==============", online_users_dict)
            return online_users_dict
        except Exception as e:
            LOGGER.error("Error occurred while fetching online users: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def remove_user_online_status(user_id: str) -> None:
        """
        Remove a user's online status using Redis HDEL.
        """
        try:
            client = await RedisManager.get_redis_client()

            user_key = "online_users"

            # Remove the user from the hash
            await client.hdel(user_key, user_id)

            # print(f"User {user_id} removed from online users =========")
        except Exception as e:
            LOGGER.error("Error occurred while removing user %s from online status: %s", user_id, str(e), exc_info=True)
            raise


# class OnlineUserManager:

#     @staticmethod
#     async def set_online_user(
#         user_id: str, websocket_id: str, user_data: dict
#     ) -> None:
#         try:
#             client = await RedisManager.get_redis_client()

#             online_users = await client.get("online_users")

#             if online_users is None:
#                 online_users_dict = dict()
#                 # online_users = dict()
#             else:
#                 online_users_dict = json.loads(online_users)

#             user_data = {"websocket_id": websocket_id, "data": user_data}
#             online_users_dict[user_id] = user_data

#             print(online_users_dict, "set online =========")
#             await client.set("online_users", json.dumps(online_users_dict))
#         except Exception as e:
#             raise Exception(f"Error occurred while setting online users: {str(e)}")

#     @staticmethod
#     async def get_all_online_users() -> Optional[dict]:
#         try:
#             client = await RedisManager.get_redis_client()

#             online_users = await client.get("online_users")
#             if online_users is None:
#                 return None


#             print("online users ==============", online_users)

#             return json.loads(online_users)
#         except Exception as e:
#             raise Exception(
#               f"""Error occurred while fetching all online users: {str(e)}"""
#            )

#     @staticmethod
#     async def remove_user_online_status(user_id: str) -> None:
#         try:
#             client = await RedisManager.get_redis_client()

#             online_users = await client.get("online_users")

#             if online_users is None:
#                 return

#             online_users_dict = json.loads(online_users)

#             if user_id not in online_users_dict:
#                 return

#             online_users_dict.pop(user_id)

#             await client.set("online_users", json.dumps(online_users_dict))
#         except Exception as e:
#             raise Exception(
#                 f"Error occurred while removing user online status: {str(e)}"
#             )
