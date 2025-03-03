from motor.motor_asyncio import AsyncIOMotorClient
from app.config import Settings


DATABASE_URL = Settings.DATABASE_URL
DB_NAME = Settings.DB_NAME


async def get_db():

    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()
