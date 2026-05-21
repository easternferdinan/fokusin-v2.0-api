from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime

class UserBase(BaseModel):
    fullname: str
    username: str = Field(min_length=3)
    email: EmailStr
    mental_health_history: bool
    academic_performance: int
    social_support: int

class UserResponse(UserBase):
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreateRequest(UserBase):
    password: str = Field(min_length=8)

class UserUpdateRequest(BaseModel):
    fullname: str | None = None
    username: str | None = Field(default=None, min_length=3)
    password: str | None = Field(default=None, min_length=8)
    email: EmailStr | None = None

class UserAuthenticationRequest(BaseModel):
    username: str
    password: str

class UserAuthenticationResponse(BaseModel):
    authenticated: bool
    access_token: str | None = None
    error: list[str] | None = None