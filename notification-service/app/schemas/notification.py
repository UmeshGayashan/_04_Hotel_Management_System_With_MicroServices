from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    user_id: int

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    read: bool = True
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    id: int
    read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WebSocketMessage(BaseModel):
    type: str
    data: dict
