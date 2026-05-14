from pydantic import BaseModel
from datetime import datetime

# CLARIFY: Are notifications sent by system or by request of the admin?
class NotificationBase(BaseModel):
    message: str
    is_read: bool

class NotificationResponse(NotificationBase):
    notification_id: str
    created_at: datetime

    class Config:
        from_attributes = True