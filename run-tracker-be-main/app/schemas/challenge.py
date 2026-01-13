from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.runs import RunResponse
from app.schemas.users import UserResponse


class ChallengeBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class ChallengeCreate(ChallengeBase):
    source_run_id: UUID


class ChallengeResponse(ChallengeBase):
    uuid: UUID
    creator_id: UUID
    source_run_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    creator: Optional[UserResponse] = None
    source_run: Optional[RunResponse] = None

    model_config = {"from_attributes": True}


class ChallengeListResponse(BaseModel):
    items: List[ChallengeResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class ChallengeAttemptCreate(BaseModel):
    run_id: UUID


class ChallengeAttemptResponse(BaseModel):
    uuid: UUID
    challenge_id: UUID
    user_id: UUID
    run_id: UUID
    success: bool
    created_at: datetime

    user: Optional[UserResponse] = None
    run: Optional[RunResponse] = None

    model_config = {"from_attributes": True}
