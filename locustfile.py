import json
import random
import logging
from datetime import datetime
from pymongo import MongoClient
from locust import User, task


from websocket import create_connection  # WebSocket


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]

existing_users_count = users_collection.count_documents({})
if existing_users_count < 1000:
    users_to_create = 1000 - existing_users_count
    new_users = [
        {"username": f"user{i}", "email": f"user{i}@example.com", "password": "123"}
        for i in range(existing_users_count, 1000)
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


# locust -f locustfile.py  --headless -u 10 -r 2 --host ws://localhost:8000

# locust -f locustfile.py  --headless -u 2000 -r 20 --host ws://localhost:8000

# 1. locust
# This is the command to run Locust.

# 2. -f locustfile.py
# Specifies the test script file (named locustfile.py)
#  that contains the Locust load test configuration.

# 3. --headless
# Runs Locust without the web UI (useful for automation or CLI-based testing).
# 4. -u 10


# Sets the number of concurrent users (simulated clients) to 10.
# 5. -r 2

# Specifies the spawn rate, meaning 2 users
# per second will be added until the total reaches 10 users.
# 6. --host ws://localhost:8000
# Defines the WebSocket server host that Locust will connect to.
# In this case, it is ws://localhost:8000, meaning Locust
#  will test a WebSocket server running on port 8000 on the local machine.
