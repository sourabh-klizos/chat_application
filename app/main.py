from fastapi import FastAPI, Request, Response 
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import auth_routes
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.services.redis_client import RedisManager
from app.routes.websockets import ws_routes
from app.routes.chats import chat_routes
from app.services.metrics import HTTP_REQUESTS, get_metrics
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from app.config import Settings
from app.utils.store_message_redis import RedisChatHandler
import asyncio
settings = Settings()
load_dotenv(".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await RedisManager.get_redis_client()
    move_chat_to_mongo_task_1 = asyncio.create_task(
        RedisChatHandler.move_chat_to_mongo()
    )
    # move_chat_to_mongo_task_2 = asyncio.create_task(
    #     RedisChatHandler.move_chat_to_mongo()
    # )
    # move_chat_to_mongo_task_3 = asyncio.create_task(
    #     RedisChatHandler.move_chat_to_mongo()
    # )
    yield
    move_chat_to_mongo_task_1.cancel()
    # move_chat_to_mongo_task_2.cancel()
    # move_chat_to_mongo_task_3.cancel()
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


# @app.middleware("http")
# async def add_metrics(request: Request, call_next):
#     try:

#         response = await call_next(request)
#         HTTP_REQUESTS.inc()
#         return response
#     except Exception as e:
#         print(f"Error in middleware: {e}")



@app.middleware("http")
async def add_metrics(request: Request, call_next):
    try:
        response = await call_next(request)
        HTTP_REQUESTS.inc()
        return response
    except Exception as e:
        print(f"Error in middleware: {e}")
        return JSONResponse(
            content={"detail": "Internal Server Error"},
            status_code=500
        )


@app.get("/")
async def main():
    """Root endpoint.

    Returns a simple health check message.
    """

    return {"message": "I Am Healthy"}


@app.get("/metrics")
async def metrics():
    """Metrics endpoint.

    Returns application metrics in Prometheus format.
    """
    return Response(get_metrics(), media_type=CONTENT_TYPE_LATEST)
