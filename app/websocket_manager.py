from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # stores user_id → list of their open WebSocket connections
        # list because one user might have multiple tabs open
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        # The route should call `websocket.accept()` once before invoking
        # `manager.connect()` to avoid duplicate ASGI accept messages.
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total online: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            # clean up if no connections left for this user
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"User {user_id} disconnected.")

    async def send_notification(self, user_id: int, message: dict):
        """Push a notification to a specific user if they're online."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections


# single shared instance — imported wherever needed
manager = ConnectionManager()