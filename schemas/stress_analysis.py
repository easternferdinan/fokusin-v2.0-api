from pydantic import BaseModel, UUID4
from datetime import datetime
from enums.stress_level import StressLevelEnum

class StressAnalysisBase(BaseModel):
    self_esteem: int
    depression: int
    headache: int
    sleep_quality: int

class StressAnalysisResponse(StressAnalysisBase):
    analysis_id: UUID4
    mental_health_history: bool
    academic_performance: int
    social_support: int
    study_load: int
    stress_level: StressLevelEnum
    created_at: datetime

    class Config:
        from_attributes = True

class StressAnalysisRequirementsStatusResponse(BaseModel):
    task_done_today: bool = False
    pomodoro_done_today: bool = False
    stress_assesment_done_today: bool = False

class StressAnalysisFollowUpRequest(BaseModel):
    self_esteem: int | None
    depression: int | None
    headache: int | None
    sleep_quality: int | None

class StressAnalysisCreateRequest(StressAnalysisBase):
    pass

class StressTrendResponse(BaseModel):
    labels: list[str]
    values: list[float]