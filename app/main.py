from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import auth_routes
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.services.redis_client import RedisManager
from app.routes.websockets import ws_routes
from app.routes.chats import chat_routes


load_dotenv(".env")
# load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):

    # client = await get_redis_client()

    # await get_redis_client_pubsub()

    client = await RedisManager.get_redis_client()

    yield
    await client.close()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ws_routes)
app.include_router(auth_routes)
app.include_router(chat_routes)


@app.get("/")
async def main():
    return {"message": "Hello World"}
