from pydantic import BaseModel, UUID4
from datetime import datetime

class NotificationBase(BaseModel):
    message: str
    is_read: bool

class NotificationResponse(NotificationBase):
    notification_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationCreateRequest(NotificationBase):
    pass

class NotificationUpdateRequest(BaseModel):
    message: str | None = None
    is_read: bool | None = None