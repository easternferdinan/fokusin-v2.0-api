from typing import List

from enums.member_enums import MemberRole
from enums.stress_level import StressLevelEnum
from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime

from schemas.stress_analysis import StressAnalysisResponse


class MahasiswaCreateByAdminRequest(BaseModel):
    fullname: str
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)
    mental_health_history: bool
    academic_performance: int = Field(ge=0, le=5)
    social_support: int = Field(ge=0, le=3)

class UserAdminResponse(BaseModel):
    user_id: UUID4
    fullname: str
    username: str
    email: str
    role: MemberRole
    latest_stress_level: StressLevelEnum | None = None
    mental_health_history: bool
    academic_performance: int
    social_support: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StressHistoryAdminResponse(BaseModel):
    items: List[StressAnalysisResponse]
    total: int
    page: int
    size: int
