from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    username: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, max_length=255)
    height: Optional[int] = Field(None, ge=1, le=300)  # cm
    weight: Optional[int] = Field(None, ge=1, le=500)  # kg


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
