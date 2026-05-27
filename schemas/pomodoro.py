from enums.pomodoro_enums import PomodoroStatus
from pydantic import BaseModel, UUID4
from datetime import datetime

class PomodoroBase(BaseModel):
    title: str
    status: PomodoroStatus
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
    session_end: datetime | None = None
    elapsed_time: int | None = None

class PomodoroUpdateRequest(BaseModel):
    pomodoro_id: UUID4
    title: str | None = None
    status: PomodoroStatus | None = None
    session_start: datetime | None = None
    session_end: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    elapsed_time: int | None = None
    duration: int | None = None
    break_duration: int | None = None
    completed: bool | None = None

class PomodoroStartRequest(BaseModel):
    pomodoro_id: UUID4

class PomodoroStopRequest(BaseModel):
    pomodoro_id: UUID4

class PomodoroCompletionRequest(BaseModel):
    pomodoro_id: UUID4
    completed: bool

class PomodoroDeleteRequest(BaseModel):
    pomodoro_id: UUID4