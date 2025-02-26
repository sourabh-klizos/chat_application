from fastapi import FastAPI, WebSocket, WebSocketDisconnect , Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List , Dict
import asyncio
from app.routes.auth import  auth_routes
from dotenv import load_dotenv

load_dotenv(".env")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: Dict[str, List] = dict()

app.include_router(auth_routes)


@app.get("/")
async def main():
    return {"message": "Hello World"}

@app.websocket("/ws/{i}/{other}")
async def websocket_endpoint(websocket: WebSocket,i: str, other: str):

    print(i)
    print(other)

    group = None
    if (i and other) and (other != "null"):
        group:str = i + other
        group = "".join(sorted(group))
        # print(f"Your sorted group is: {group}")
  
    await websocket.accept()

    if not active_connections.get(group):
        active_connections[group] = list()
        active_connections[group].append(websocket)
    else:
        active_connections[group].append(websocket)

    # print(active_connections)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
  
            await asyncio.gather(
                *[conn.send_text(f"{data}") for conn in active_connections[group]]
            )
            
    except WebSocketDisconnect:
        # [conn.remove(websocket) for conn in active_connections[gropu] ]
        active_connections[group].remove(websocket)


























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
       