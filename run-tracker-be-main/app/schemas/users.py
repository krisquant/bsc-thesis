from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    uuid: UUID
    email: str
    username: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    height: Optional[int]
    weight: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = Field(None, max_length=255)
    height: Optional[int] = Field(None, ge=1, le=300)  # cm
    weight: Optional[int] = Field(None, ge=1, le=500)  # kg


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int
