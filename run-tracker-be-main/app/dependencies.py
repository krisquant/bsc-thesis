from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer

from app.core.exc import UserNotAuthenticatedException
from app.core.unit_of_work import ABCUnitOfWork, UnitOfWork
from app.models import User
from app.services.achievement import AchievementService, get_achievement_service
from app.services.auth import AuthService, get_auth_service
from app.services.goal import GoalService, get_goal_service
from app.services.leaderboard import LeaderboardService, get_leaderboard_service
from app.services.run import RunService, get_run_service
from app.services.statistics import StatisticsService, get_statistics_service
from app.services.user import UserService, get_user_service
from app.utils.security import decode_token

UnitOfWorkDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
GoalServiceDep = Annotated[GoalService, Depends(get_goal_service)]
RunServiceDep = Annotated[RunService, Depends(get_run_service)]
AchievementServiceDep = Annotated[AchievementService, Depends(get_achievement_service)]
StatisticsServiceDep = Annotated[StatisticsService, Depends(get_statistics_service)]
LeaderboardServiceDep = Annotated[LeaderboardService, Depends(get_leaderboard_service)]

bearer_scheme = HTTPBearer()


async def get_current_user(
    token: Annotated[str, Depends(bearer_scheme)],
    uow: UnitOfWorkDep,
) -> User:
    try:
        payload = decode_token(token.credentials)
        if payload is None:
            raise UserNotAuthenticatedException()

        user_id: str = payload.get("sub")
        if user_id is None:
            raise UserNotAuthenticatedException()

        async with uow:
            user = await uow.user.get_one(uuid=user_id)
            if user is None:
                raise UserNotAuthenticatedException()

        return user
    except Exception:
        raise UserNotAuthenticatedException()


CurrentUserDep = Annotated[User, Depends(get_current_user)]
