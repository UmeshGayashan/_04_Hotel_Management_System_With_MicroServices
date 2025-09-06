import json
from typing import Dict, List
from fastapi import WebSocket
from app.schemas.notification import NotificationResponse

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[user_id].remove(connection)

    async def broadcast(self, message: str):
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    pass

class WebSocketManager:
    def __init__(self):
        self.manager = ConnectionManager()
    
    async def connect_user(self, websocket: WebSocket, user_id: int):
        await self.manager.connect(websocket, user_id)
    
    def disconnect_user(self, websocket: WebSocket, user_id: int):
        self.manager.disconnect(websocket, user_id)
    
    async def send_notification(self, user_id: int, notification):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "data": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
        }
        await self.manager.send_personal_message(json.dumps(message), user_id)
    
    async def broadcast_notification(self, notification):
        """Broadcast notification to all connected users"""
        message = {
            "type": "broadcast",
            "data": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
        }
        await self.manager.broadcast(json.dumps(message))
