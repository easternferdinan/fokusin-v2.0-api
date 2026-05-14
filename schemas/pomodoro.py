from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# TODO: Break down into more granular schemas per endpoint. 
# e.g. PomodoroStartRequest, PomodoroStopRequest, PomodoroCompleteRequest etc.

class PomodoroBase(BaseModel):
    title: str
    status: str
    session_start: datetime
    session_end: datetime
    started_at: datetime # CLARIFY: redundant?
    completed_at: datetime # CLARIFY: redundant?
    elapsed_time: int
    duration: int # CLARIFY: redundant?
    break_duration: int
    completed: bool

class PomodoroResponse(PomodoroBase):
    pomodoroId: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PomodoroCreateRequest(PomodoroBase):
    user_id: str
    pass
    created_at: datetime

# class PomodoroCreateResponse(PomodoroBase):
#     pomodoro_id: str
#     title: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

class PomodoroUpdateRequest(PomodoroBase):
    pomodoro_id: str
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

# class PomodoroUpdateResponse(PomodoroBase):
#     pomodoro_id: str
#     title: str
#     updated_at: datetime

#     class Config:
#         from_attributes = True

class PomodoroCompletionRequest(PomodoroBase):
    pomodoroId: str
    completed: bool

# class PomodoroCompletionResponse(PomodoroBase):
#     pomodoro_id: str
#     title: str
#     completed: bool
#     completed_at: Optional[datetime] = None

#     class Config:
#         from_attributes = True

class PomodoroDeleteRequest(PomodoroBase):
    pomodoroId: str

# class PomodoroDeleteResponse(PomodoroBase):
#     pomodoro_id: str
#     title: str

#     class Config:
#         from_attributes = True