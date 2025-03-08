import json
import random
import logging
from datetime import datetime
from pymongo import MongoClient
from locust import User, task, events
from websocket import create_connection, WebSocket


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]

user_ids = [str(user["_id"]) for user in users_collection.find({}, {"_id": 1})]

if len(user_ids) < 2:
    raise ValueError("Not enough users in the database to test WebSocket connections.")


class WebSocketLocust(User):
    """Locust WebSocket User"""

    # host = "ws://localhost:8000"

    def on_start(self):
        """Establish WebSocket connection when the test starts"""
        self.current_id = random.choice(user_ids)
        self.selected_user_id = random.choice(
            [uid for uid in user_ids if uid != self.current_id]
        )

        self.ws_url = (
            f"ws://localhost:8000/ws/{self.current_id}/{self.selected_user_id}/"
        )

        try:
            self.ws = create_connection(self.ws_url)
            logging.info(f"Connected to WebSocket: {self.ws_url}")
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            self.ws = None

    def on_stop(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            logging.info("WebSocket connection closed")

    @task
    def send_message(self):
        """Send a WebSocket message and receive a response"""
        if not self.ws:
            logging.error("WebSocket connection is not established.")
            return

        message = {
            "text": "Hello! This is a message from WebSocket load test.",
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
            logging.error(f"Error sending/receiving WebSocket message: {e}")
