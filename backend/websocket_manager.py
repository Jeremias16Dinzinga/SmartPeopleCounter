from fastapi import WebSocket
from typing import List

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.last_counters = {"entered": 0, "exited": 0, "current": 0, "alert": ""}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Envia imediatamente os últimos valores para o frontend
        await websocket.send_json(self.last_counters)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        self.last_counters = data  # atualiza últimos valores
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                to_remove.append(connection)
        for conn in to_remove:
            self.disconnect(conn)


