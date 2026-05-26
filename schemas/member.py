from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime

class UserBase(BaseModel):
    fullname: str
    username: str = Field(min_length=3)
    email: EmailStr
    mental_health_history: bool
    academic_performance: int = Field(ge=0, le=5)
    social_support: int = Field(ge=0, le=3)

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
    mental_health_history: bool | None = None
    academic_performance: int | None = Field(default=None, ge=0, le=5)
    social_support: int | None = Field(default=None, ge=0, le=3)

class UserAuthenticationRequest(BaseModel):
    username: str
    password: str

class UserAuthenticationSuccessResponse(UserBase):
    """
    Response model for successful user authentication.
    Inherits from UserBase and adds authentication-specific fields.
    """
    authenticated: bool = True
    access_token: str

    class Config:
        from_attributes = True

class UserAuthenticationFailedResponse(BaseModel):
    """
    Response model for failed user authentication.
    Does not inherit from UserBase as no user data is returned.
    """
    authenticated: bool = False
    access_token: None = None
    error: list[str] | str = ["Autentikasi gagal"]

    class Config:
        from_attributes = True