from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enums.goal import GoalType, TimePeriod


class GoalResponse(BaseModel):
    uuid: UUID
    user_uuid: UUID
    goal_type: GoalType
    target: int
    time_period: TimePeriod
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalCreateRequest(BaseModel):
    goal_type: GoalType
    target: int = Field(..., gt=0, description="Target value")
    time_period: TimePeriod


class GoalListResponse(BaseModel):
    goals: list[GoalResponse]
    total: int
    page: int
    limit: int
    total_pages: int
