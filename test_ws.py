import asyncio
import random
import string
import websockets
from pymongo import MongoClient
import json
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]


def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class UserBehavior:
    def __init__(self):
        self.all_users = []
        self.active_connections = 0

    async def chat_with_random_user(self):

        await self.get_all_users_from_mongodb()

        if len(self.all_users) >= 2:
            await self.chat_with_random_user_async()
        else:
            print("Not enough users available for chat. Waiting for more users...")

    async def get_all_users_from_mongodb(self):
        """Query all users from MongoDB and store user_ids."""
        self.all_users = []

        users = users_collection.find({})
        for user in users:
            self.all_users.append(
                {
                    "user_id": user.get("_id"),
                }
            )

        print(f"Total users fetched from MongoDB: {len(self.all_users)}")

    async def chat_with_random_user_async(self):

        selected_user_index = random.randint(0, len(self.all_users) - 1)
        selected_user = self.all_users[selected_user_index]
        selected_user_id = selected_user["user_id"]

        # print(
        #     f"Total users ==================== {self.all_users}.
        #  Response: {selected_user_id}"
        # )

        while True:
            current_user_index = random.randint(0, len(self.all_users) - 1)
            if self.all_users[current_user_index]["user_id"] != selected_user_id:
                current_user = self.all_users[current_user_index]
                current_id = current_user["user_id"]
                break

        websocket_url = f"ws://localhost:8000/ws/{current_id}/{selected_user_id}/"

        print(f"WebSocket URL ==================== {websocket_url}.")

        await self.send_message_via_websocket(
            websocket_url, current_id, selected_user_id
        )

    async def send_message_via_websocket(
        self, websocket_url, current_id, selected_user_id
    ):

        async with websockets.connect(websocket_url) as ws:
            self.active_connections += 1
            print(f"Active WebSocket connections: {self.active_connections}")

            try:
                while True:

                    message = {
                        "text": "Hello! This is a message from WebSocket load test.",
                        "sender_id": current_id,
                        "receiver_id": selected_user_id,
                        "created_at": datetime.now(),
                    }
                    message = json.dumps(message, default=str)
                    await ws.send(message)
                    print(f"Sent message: {message}")

                    response = await ws.recv()
                    print(f"Received message: {response}")

                    await asyncio.sleep(random.uniform(1, 2))
            except websockets.ConnectionClosed:
                print(f"Connection closed: {websocket_url}")
            finally:
                self.active_connections -= 1
                print(
                    f"""Active WebSocket connections after closure:
                     {self.active_connections}"""
                )

    async def on_start(self):
        """This method is called when a simulated user starts."""
        await asyncio.sleep(random.uniform(1, 3))


async def main():
    user_behavior = UserBehavior()
    await user_behavior.on_start()

    await asyncio.gather(*[user_behavior.chat_with_random_user() for _ in range(300)])

    while True:
        await asyncio.sleep(5)


# Run the main function
asyncio.run(main())
