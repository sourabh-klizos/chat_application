from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import auth_routes
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.services.redis_client import get_redis_client
from app.routes.websockets import ws_routes

load_dotenv(".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await get_redis_client()

    yield
    client.close()


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


@app.get("/")
async def main():
    return {"message": "Hello World"}


# @app.websocket("/ws/{i}/{other}")
# async def websocket_endpoint(websocket: WebSocket,i: str, other: str):
#     gropu = None
#     if (i and other) and (other != "null"):
#         gropu:str = i + other
#         gropu = "".join(sorted(gropu))
#         print(gropu)


#     await websocket.accept()

#     active_connections.append(websocket)

#     try:
#         while True:
#             data = await websocket.receive_text()
#             print(f"Received message: {data}")

#             await asyncio.gather(
#                 *[connection.send_text(f"{data}") for connection in active_connections]
#             )

#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
