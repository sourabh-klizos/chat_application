from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.config import Settings

# load_dotenv(".env")


# DATABASE_URL = os.getenv("DATABASE_URL")
# DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = Settings.DATABASE_URL
DB_NAME = Settings.DB_NAME

# print("db =======================", DATABASE_URL, DB_NAME)

async def get_db():

    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()
