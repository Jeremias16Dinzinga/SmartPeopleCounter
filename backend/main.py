import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal
from models import PeopleCount
from websocket_manager import ConnectionManager
from people_counter import start_people_counter
from database import engine, Base
from threading import Thread

Base.metadata.create_all(bind=engine)

app = FastAPI()
manager = ConnectionManager()

loop = asyncio.get_event_loop()
counter_thread = None 

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/start")
def start_counter():
    global counter_thread
    if counter_thread is not None and counter_thread.is_alive():
        return {"status": "contador já está rodando"}

    # inicia o contador
    counter_thread = Thread(target=start_people_counter, args=(manager, loop), daemon=True)
    counter_thread.start()
    return {"status": "contador iniciado"}


# === CORS para permitir acesso do frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/history")
def get_history():
    db = SessionLocal()
    try:
        records = db.query(PeopleCount).order_by(PeopleCount.id.desc()).limit(25).all()
        return [
            {
                "id": r.id,
                "entered": r.entered,
                "exited": r.exited,
                "current_people": r.current_people,
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for r in records
        ]
    finally:
        db.close()
