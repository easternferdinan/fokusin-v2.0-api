from pydantic import BaseModel, Field, UUID4
from datetime import datetime

from enums.member_enums import MemberRole


class AdminCreateRequest(BaseModel):
    fullname: str
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


class AdminUpdateRequest(BaseModel):
    fullname: str | None = None
    username: str | None = Field(default=None, min_length=3)
    password: str | None = Field(default=None, min_length=8)


class AdminResponse(BaseModel):
    user_id: UUID4
    fullname: str
    username: str
    email: str
    role: MemberRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
