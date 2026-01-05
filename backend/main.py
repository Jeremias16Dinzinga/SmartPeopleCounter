import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket_manager import ConnectionManager
from people_counter import start_people_counter
from database import engine, Base
from models import PeopleCount

Base.metadata.create_all(bind=engine)

app = FastAPI()
manager = ConnectionManager()

loop = asyncio.get_event_loop()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/start")
def start():
    stream_url = "http://192.168.1.10:8080/video"

    thread = threading.Thread(
        target=start_people_counter,
        args=(stream_url, manager, loop),
        daemon=True
    )
    thread.start()

    return {"status": "contador iniciado"}
