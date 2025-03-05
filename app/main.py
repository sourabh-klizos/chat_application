from fastapi import FastAPI, Request, Response
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

settings = Settings()
load_dotenv(".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    try:
        method = request.method
        endpoint = request.url.path
        response = await call_next(request)
        status_code = response.status_code
        HTTP_REQUESTS.inc()
        return response
    except Exception as e:
        print(f"Error in middleware: {e}")
        pass


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.get("/metrics")
async def metrics():
    return Response(get_metrics(), media_type=CONTENT_TYPE_LATEST)
