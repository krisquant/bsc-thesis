from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel


class LeaderboardMetric(str, Enum):
    DISTANCE = "distance"
    DURATION = "duration"
    RUNS = "runs"


class LeaderboardPeriod(str, Enum):
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


class LeaderboardEntry(BaseModel):
    rank: int
    user_uuid: UUID
    username: str | None
    value: float | int
    is_current_user: bool = False


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    current_user_entry: LeaderboardEntry | None = None
