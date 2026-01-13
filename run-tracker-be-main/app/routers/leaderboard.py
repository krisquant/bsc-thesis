from fastapi import APIRouter, Query

from app.dependencies import CurrentUserDep, LeaderboardServiceDep, UnitOfWorkDep
from app.schemas.leaderboard import (
    LeaderboardMetric,
    LeaderboardPeriod,
    LeaderboardResponse,
)

router = APIRouter()


@router.get("/", response_model=LeaderboardResponse)
async def get_leaderboard(
    current_user: CurrentUserDep,
    leaderboard_service: LeaderboardServiceDep,
    uow: UnitOfWorkDep,
    metric: LeaderboardMetric = Query(LeaderboardMetric.DISTANCE),
    period: LeaderboardPeriod = Query(LeaderboardPeriod.WEEK),
    friends_only: bool = Query(False),
) -> LeaderboardResponse:
    return await leaderboard_service.get_leaderboard(
        uow, metric, period, current_user.uuid, friends_only=friends_only
    )
