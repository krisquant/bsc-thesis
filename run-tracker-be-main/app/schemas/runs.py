from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RunResponse(BaseModel):
    uuid: UUID
    user_uuid: UUID
    name: Optional[str]
    start_time: datetime
    end_time: datetime
    duration: float
    distance: float
    calories: Optional[int]
    route: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RunCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    start_time: datetime
    end_time: datetime
    duration: float = Field(..., gt=0, description="Duration in minutes")
    distance: float = Field(..., ge=0, description="Distance in km")
    calories: Optional[int] = Field(None, ge=0)
    route: Optional[List[Dict[str, Any]]] = None


class RunUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)


class RunListResponse(BaseModel):
    runs: list[RunResponse]
    total: int
    page: int
    limit: int
    total_pages: int
