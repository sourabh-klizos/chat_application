from jose import jwt

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pymongo.collection import Collection
import os
# from dotenv import load_dotenv
from app.config import Settings

# load_dotenv(".env")

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")

SECRET_KEY = Settings.SECRET_KEY
ALGORITHM = Settings.ALGORITHM


async def create_access_token(user_id: str, minutes: int = None) -> dict:

    if not minutes:
        minutes = 30

    payload_to_encode = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
        "typ": "access_token",
    }

    access_token = jwt.encode(payload_to_encode, SECRET_KEY, ALGORITHM)

    return access_token


async def create_refresh_token(user_id: str, db, hours: int = None) -> dict:
    refresh_token_collection: Collection = db["refresh_tokens"]

    if not hours:
        hours = 24 * 7

    payload_to_encode = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
        "typ": "refresh_token",
    }

    refresh_token = jwt.encode(payload_to_encode, SECRET_KEY, ALGORITHM)

    condition = {"user_id": user_id}
    update = {
        "$set": {
            "refresh_token": refresh_token,
            "jti": payload_to_encode["jti"],
        }
    }

    await refresh_token_collection.find_one_and_update(condition, update, upsert=True)

    return refresh_token


async def decode_jwt(access_token: str, token_type: str) -> dict:
    try:

        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["typ"] == token_type:
            return decoded_token

    except Exception as e:
        return f"Error decoding token: {e}"
