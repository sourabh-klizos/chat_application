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

        if len(self.all_users) >= 2:
            await self.chat_with_random_user_async()
        else:
            print("Not enough users available for chat. Waiting for more users...")

    async def chat_with_random_user_async(self):
        selected_user = random.choice(self.all_users)
        selected_user_id = selected_user["user_id"]

        # print(
        #     f"Total users ==================== {self.all_users}.
        #  Response: {selected_user_id}"
        # )

        # Get the current user's token
        current_user = random.choice(
            [u for u in self.all_users if u["user_id"] != selected_user_id]
        )

        current_id = current_user["user_id"]

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

    def get_random_user_from_mongodb(self):
        """Query a random user from MongoDB."""
        count = users_collection.count_documents({})
        if count == 0:
            print("No users found in the database.")
            return None

        random_index = random.randint(0, count - 1)
        random_user = users_collection.find().skip(random_index).limit(1).next()
        return random_user


async def main():
    user_behavior = UserBehavior()
    await user_behavior.on_start()

    await asyncio.gather(*[user_behavior.chat_with_random_user() for _ in range(200)])

    while True:
        await asyncio.sleep(5)


asyncio.run(main())
