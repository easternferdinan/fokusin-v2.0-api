from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum

class MemberRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'

class UserBase(BaseModel):
    fullname: str
    username: str = Field(min_length=3)
    email: EmailStr

class UserResponse(UserBase):
    user_id: str
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