from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from app.schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate
from app.services.notification_service import NotificationService
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
notification_service = NotificationService()
websocket_manager = WebSocketManager()

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 100
):
    """Get user notifications"""
    notifications = await notification_service.get_user_notifications(user_id, skip=skip, limit=limit)
    return notifications

@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    created_notification = await notification_service.create_notification(notification.dict())
    
    # Send real-time notification
    await websocket_manager.send_notification(
        notification.user_id, 
        created_notification
    )
    
    return created_notification

@router.put("/notifications/{notification_id}")
async def mark_notification_read(notification_id: int, user_id: int):
    """Mark notification as read"""
    notification = await notification_service.mark_as_read(notification_id, user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.get("/notifications/{user_id}/unread-count")
async def get_unread_count(user_id: int):
    """Get count of unread notifications"""
    count = await notification_service.get_unread_count(user_id)
    return {"unread_count": count}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time notifications"""
    await websocket_manager.connect_user(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect_user(websocket, user_id)
