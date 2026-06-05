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


class StressLevelPercentage(BaseModel):
    tinggi: float
    sedang: float
    rendah: float


class CorrelatedAcademicStressStats(BaseModel):
    mode_academic_1_2: StressLevelEnum | None
    mode_academic_3_5: StressLevelEnum | None


class CorrelatedSocialStressStats(BaseModel):
    mode_social_1: StressLevelEnum | None
    mode_social_2: StressLevelEnum | None
    mode_social_3: StressLevelEnum | None


class DailyStressTrend(BaseModel):
    date: str
    label: str
    mode_stress: StressLevelEnum | None


class DailyStressTrendResponse(BaseModel):
    items: list[DailyStressTrend]


class AdminDashboardResponse(BaseModel):
    total_mahasiswa: int
    stress_level_percentages: StressLevelPercentage
    correlated_academic_stress_stats: CorrelatedAcademicStressStats
    correlated_social_stress_stats: CorrelatedSocialStressStats
    mental_health_history_effect: str
