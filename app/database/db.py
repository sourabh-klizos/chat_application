from motor.motor_asyncio import AsyncIOMotorClient
from app.config import Settings
from app.utils.logger_config import LOGGER

DATABASE_URL = Settings.DATABASE_URL
DB_NAME = Settings.DB_NAME


async def get_db():
    """Get database client.

    Establishes a connection to the MongoDB database and yields the database client.
    Handles potential exceptions during connection and ensures client closure.
    """

    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
        LOGGER.info("Database connection successful.")
    except Exception as e:
        LOGGER.error(f"Database error: {e}")
    finally:
        client.close()
        LOGGER.info("Database connection closed.")
