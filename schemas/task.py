from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# TODO: should we make enums modular?
class TaskCategory(str, Enum):
    STUDY = 'study'
    PROJECT = 'project'
    ASSIGNMENT = 'assignment'

class TaskPriority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: TaskCategory
    priority: TaskPriority
    target_duration: int = Field(gt=0)
    deadline: datetime
    reminder_offset: int = Field(ge=0)

class TaskResponse(TaskBase):
    task_id: str
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskCreateRequest(TaskBase):
    pass

class TaskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    category: TaskCategory | None = None
    priority: TaskPriority | None = None
    target_duration: int | None = Field(default=None, gt=0)
    deadline: datetime | None = None
    reminder_offset: int | None = Field(default=None, ge=0)

class TaskCompletionRequest(BaseModel):
    completed: bool