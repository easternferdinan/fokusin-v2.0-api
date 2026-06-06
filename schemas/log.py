from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, Any, Dict
from enums.log_enums import LogLevel

class LogBase(BaseModel):
    level: LogLevel = LogLevel.INFO
    event_type: str
    message: str
    extra_data: Optional[Dict[str, Any]] = None

class LogCreateRequest(LogBase):
    user_id: Optional[UUID4] = None

class LogResponse(LogBase):
    log_id: UUID4
    user_id: Optional[UUID4]
    username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
