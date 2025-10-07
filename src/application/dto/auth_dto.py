"""Authentication DTOs."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request DTO."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Registration request DTO."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)


class TokenResponse(BaseModel):
    """Token response DTO."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response DTO."""

    id: str
    email: str
    full_name: str
    is_active: bool
    permissions: list[str]

    class Config:
        from_attributes = True
