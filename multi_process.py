import asyncio
import random
import string
import websockets
from pymongo import MongoClient
import json
from datetime import datetime
from multiprocessing import Process

# MongoDB setup
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
        """Starts a chat session between two random users."""
        await self.get_all_users_from_mongodb()

        if len(self.all_users) >= 2:
            await self.chat_with_random_user_async()
        else:
            print("Not enough users available for chat. Waiting for more users...")

    async def get_all_users_from_mongodb(self):
        """Query all users from MongoDB and store user_ids."""
        self.all_users = [
            {"user_id": user["_id"]} for user in users_collection.find({})
        ]
        print(f"Total users fetched from MongoDB: {len(self.all_users)}")

    async def chat_with_random_user_async(self):
        """Selects two random users and establishes a WebSocket chat session."""
        selected_user = random.choice(self.all_users)
        selected_user_id = selected_user["user_id"]

        while True:
            current_user = random.choice(self.all_users)
            if current_user["user_id"] != selected_user_id:
                current_id = current_user["user_id"]
                break

        websocket_url = f"ws://localhost:8000/ws/{current_id}/{selected_user_id}/"
        print(f"Connecting WebSocket URL: {websocket_url}")
        await self.send_message_via_websocket(
            websocket_url, current_id, selected_user_id
        )

    async def send_message_via_websocket(
        self, websocket_url, current_id, selected_user_id
    ):
        """Handles WebSocket connection, sending & receiving messages."""
        try:
            async with websockets.connect(websocket_url) as ws:
                self.active_connections += 1
                print(f"Active WebSocket connections: {self.active_connections}")

                while True:
                    message = {
                        "text": "Hello! This is a message from WebSocket load test.",
                        "sender_id": current_id,
                        "receiver_id": selected_user_id,
                        "created_at": datetime.now(),
                    }
                    await ws.send(json.dumps(message, default=str))
                    print(f"Sent message: {message}")

                    response = await ws.recv()
                    print(f"Received message: {response}")

                    await asyncio.sleep(random.uniform(1, 2))
        except websockets.ConnectionClosed:
            print(f"Connection closed: {websocket_url}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.active_connections -= 1
            print(
                f"Active WebSocket connections after closure: {self.active_connections}"
            )

    async def on_start(self):
        """This method is called when a simulated user starts."""
        await asyncio.sleep(random.uniform(1, 3))


async def run_clients(start, end):
    """Runs a batch of WebSocket clients asynchronously in a single process."""
    user_behavior = UserBehavior()
    await user_behavior.on_start()

    tasks = [user_behavior.chat_with_random_user() for _ in range(start, end)]
    await asyncio.gather(*tasks)


def start_process(start, end):
    """Starts a separate event loop for each process."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_clients(start, end))


if __name__ == "__main__":
    num_clients = 500  # Total number of WebSocket clients
    num_processes = 5  # Number of parallel processes
    clients_per_process = num_clients // num_processes

    processes = []
    for i in range(num_processes):
        start = i * clients_per_process
        end = start + clients_per_process
        p = Process(target=start_process, args=(start, end))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
