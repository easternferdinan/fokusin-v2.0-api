import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from enums.stress_level import StressLevelEnum

class ApiConfigResponse(BaseModel):
    id: uuid.UUID
    api_base_url: str
    stress_threshold: StressLevelEnum
    stress_threshold_frequency: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApiConfigUpdateRequest(BaseModel):
    api_base_url: str
    stress_threshold: StressLevelEnum = StressLevelEnum.TINGGI
    stress_threshold_frequency: int = Field(default=3, ge=1, le=100)
