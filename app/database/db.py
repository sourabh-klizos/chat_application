from motor.motor_asyncio import AsyncIOMotorClient
import os


DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")


async def get_db():

    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()
