from pydantic import BaseModel
from schemas.task import TaskResponse

class DashboardBase(BaseModel):
    incomplete_tasks_count: int
    high_priority_tasks_count: int
    deadline_is_tomorrow_tasks_count: int
    today_pomodoro_minutes: int
    latest_burnout_prediction: str | None = None
    deadline_is_tomorrow_tasks: list[TaskResponse] | None = None

class DashboardResponse(DashboardBase):
    pass

    class Config:
        from_attributes = True