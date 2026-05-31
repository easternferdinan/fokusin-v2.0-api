from pydantic import BaseModel, UUID4
from datetime import datetime
from enums.stress_level import StressLevelEnum

class StressAnalysisBase(BaseModel):
    self_esteem: int
    mental_health_history: bool
    depression: int
    headache: int
    sleep_quality: int
    academic_performance: int
    study_load: int
    social_support: int

class StressAnalysisResponse(StressAnalysisBase):
    analysis_id: UUID4
    stress_level: StressLevelEnum
    created_at: datetime

    class Config:
        from_attributes = True

class StressAnalysisCreateRequest(StressAnalysisBase):
    pass