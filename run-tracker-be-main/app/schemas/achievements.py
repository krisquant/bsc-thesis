from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    uuid: UUID
    user_uuid: UUID
    title: str
    description: Optional[str]
    earned_at: datetime
    achievement_type: str
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AchievementListResponse(BaseModel):
    achievements: list[AchievementResponse]
    total: int
    page: int
    limit: int
    total_pages: int
