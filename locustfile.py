from locust import HttpUser, task, between

import random
import string
import asyncio
import websockets
import json
from pymongo import MongoClient

from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]


def get_random_user_from_mongodb():
    """Query a random user from MongoDB."""
    random_user = users_collection.aggregate([{"$sample": {"size": 1}}]).next()
    return str(random_user["_id"])


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user_data = self.signup()
        if self.user_data:
            self.login()

    def random_string(self, length=8):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def signup(self):
        random_username = self.random_string()
        user_payload = {
            "username": random_username,
            "email": f"{random_username}@example.com",
            "password": "testpassword123",
        }

        response = self.client.post("/api/v1/auth/signup", json=user_payload)

        if response.status_code == 201:
            return {
                "email": user_payload["email"],
                "password": user_payload["password"],
            }
        else:

            return None

    @task
    def login(self):
        if self.user_data:
            login_payload = {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            }

        response = self.client.post("/api/v1/auth/login", json=login_payload)

        if response.status_code == 200:
            data = response.json()
            self.user_id = data["user_id"]
            self.access_token = data["access_token"]
            self.selected_user_id = get_random_user_from_mongodb()
            self.ws_url = (
                f"ws://127.0.0.1:8000/ws/{self.user_id}/{self.selected_user_id}/"
            )
            # websocket_url = f"ws://localhost:8000/ws/{current_id}/{selected_user_id}/"

            print(f"Login successful! WebSocket URL: {self.ws_url}")
        else:
            print(f"Login failed: {response.text}")

    @task
    def websocket_chat(self):
        if hasattr(self, "ws_url"):
            asyncio.run(self.ws_connect(self.ws_url))

    async def ws_connect(self, ws_url):
        try:
            async with websockets.connect(ws_url) as websocket:
                print(f"WebSocket connected: {ws_url}")

                message = {
                    "text": "Hello! This is a message from WebSocket load test.",
                    "sender_id": self.user_id,
                    "receiver_id": self.selected_user_id,
                    "created_at": str(datetime.now()),
                }

                message_str = json.dumps(message)

                await websocket.send(message_str)
                print(f"Sent: {message}")

                response = await websocket.recv()
                print(f"Received: {response}")

        except Exception as e:
            print(f"WebSocket error: {e}")
