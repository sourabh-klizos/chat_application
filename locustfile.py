import json
import random
import logging
from datetime import datetime
from pymongo import MongoClient
from locust import User, task
from websocket import create_connection

client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]

existing_users_count = users_collection.count_documents({})
if existing_users_count < 500:
    users_to_create = 500 - existing_users_count
    new_users = [
        {"username": f"user{i}", "email": f"user{i}@example.com", "password": "123"}
        for i in range(existing_users_count, 500)
    ]
    users_collection.insert_many(new_users)
    logging.info(f"Added {users_to_create} new users.")

user_ids = [str(user["_id"]) for user in users_collection.find({}, {"_id": 1})]

if len(user_ids) < 2:
    raise ValueError("Not enough users for WebSocket testing.")


class WebSocketLocust(User):
    """Simulates WebSocket user behavior for load testing."""

    def on_start(self):
        """Initialize WebSocket connection."""
        self.current_id = random.choice(user_ids)
        self.selected_user_id = random.choice(
            [uid for uid in user_ids if uid != self.current_id]
        )
        self.ws_url = (
            f"ws://localhost:8000/ws/{self.current_id}/{self.selected_user_id}/"
        )

        try:
            self.ws = create_connection(self.ws_url)
            logging.info(f"Connected: {self.ws_url}")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            self.ws = None

    def on_stop(self):
        """Close WebSocket connection."""
        if self.ws:
            self.ws.close()
            logging.info("Connection closed")

    @task
    def send_message(self):
        """Send and receive a WebSocket message."""
        if not self.ws:
            logging.error("No WebSocket connection.")
            return

        message = {
            "text": "Hello from WebSocket load test.",
            "sender_id": self.current_id,
            "receiver_id": self.selected_user_id,
            "created_at": datetime.now().isoformat(),
        }

        try:
            self.ws.send(json.dumps(message))
            logging.info(f"Sent: {message}")
            response = self.ws.recv()
            logging.info(f"Received: {response}")
        except Exception as e:
            logging.error(f"Message error: {e}")
