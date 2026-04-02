from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., min_length=6, examples=["securePassword123"])


class UserResponse(BaseModel):
    id: int = Field(..., examples=[1])
    email: str = Field(..., examples=["john@example.com"])
    role: UserRole = Field(..., examples=["viewer"])
    is_active: bool = Field(..., examples=[True])

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., examples=["securePassword123"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.abc123"])
    token_type: str = Field(default="bearer", examples=["bearer"])


class UpdateRoleRequest(BaseModel):
    role: UserRole = Field(..., examples=["analyst"])


class UpdateStatusRequest(BaseModel):
    is_active: bool = Field(..., examples=[False])
