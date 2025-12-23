from typing import List, Optional

from pydantic import BaseModel


class TotalStats(BaseModel):
    total_distance: float
    total_duration: float
    total_workouts: int


class StreakStats(BaseModel):
    current_streak: int
    longest_streak: int


class PersonalRecords(BaseModel):
    fastest_pace: Optional[float]  # min/km
    longest_distance: Optional[float]  # km
    longest_duration: Optional[float]  # minutes


class VisualizationDataPoint(BaseModel):
    label: str  # date or month
    distance: float
    duration: float
    count: int


class UserStatisticsResponse(BaseModel):
    totals: TotalStats
    streaks: StreakStats
    personal_records: PersonalRecords


class VisualizationResponse(BaseModel):
    data: List[VisualizationDataPoint]
