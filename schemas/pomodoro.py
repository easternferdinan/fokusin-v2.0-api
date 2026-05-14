from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

# TODO: Break down into more granular schemas per endpoint. 
# e.g. PomodoroStartRequest, PomodoroStopRequest, PomodoroCompleteRequest etc.

class PomodoroBase(BaseModel):
    title: str
    status: str
    session_start: datetime
    session_end: datetime
    elapsed_time: int
    duration: int
    break_duration: int
    completed: bool

class PomodoroResponse(PomodoroBase):
    pomodoro_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PomodoroCreateRequest(PomodoroBase):
    pass

class PomodoroUpdateRequest(BaseModel):
    pomodoro_id: UUID4
    title: Optional[str] = None
    status: Optional[str] = None
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_time: Optional[int] = None
    duration: Optional[int] = None
    break_duration: Optional[int] = None
    completed: Optional[bool] = None

class PomodoroStartRequest(BaseModel):
    pomodoro_id: UUID4

class PomodoroStopRequest(BaseModel):
    pomodoro_id: UUID4

class PomodoroCompletionRequest(BaseModel):
    pomodoro_id: UUID4
    completed: bool

class PomodoroDeleteRequest(BaseModel):
    pomodoro_id: UUID4