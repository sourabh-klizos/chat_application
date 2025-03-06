import json
from typing import Optional
from app.services.redis_client import RedisManager


class OnlineUserManager:

    @staticmethod
    async def set_online_users(
        user_id: str, websocket_id: str, user_data: dict
    ) -> None:
        try:
            client = await RedisManager.get_redis_client()

            online_users = await client.get("online_users")

            if online_users is None:
                # online_users_dict = dict()
                online_users = dict()
            else:
                online_users_dict = json.loads(online_users)

            user_data = {"websocket_id": websocket_id, "data": user_data}
            online_users_dict[user_id] = user_data
            await client.set("online_users", json.dumps(online_users_dict))
        except Exception as e:
            raise Exception(f"Error occurred while setting online users: {str(e)}")

    @staticmethod
    async def get_all_online_users() -> Optional[dict]:
        try:
            client = await RedisManager.get_redis_client()

            online_users = await client.get("online_users")
            if online_users is None:
                return None

            return json.loads(online_users)
        except Exception as e:
            raise Exception(f"Error occurred while fetching all online users: {str(e)}")

    @staticmethod
    async def remove_user_online_status(user_id: str) -> None:
        try:
            client = await RedisManager.get_redis_client()

            online_users = await client.get("online_users")

            if online_users is None:
                return

            online_users_dict = json.loads(online_users)

            if user_id not in online_users_dict:
                return

            online_users_dict.pop(user_id)

            await client.set("online_users", json.dumps(online_users_dict))
        except Exception as e:
            raise Exception(
                f"Error occurred while removing user online status: {str(e)}"
            )
