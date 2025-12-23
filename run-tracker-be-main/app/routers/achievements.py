from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import AchievementServiceDep, CurrentUserDep, UnitOfWorkDep
from app.schemas.achievements import AchievementListResponse

router = APIRouter()


@router.get("/", response_model=AchievementListResponse)
async def list_achievements(
    current_user: CurrentUserDep,
    achievement_service: AchievementServiceDep,
    uow: UnitOfWorkDep,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> AchievementListResponse:
    achievements, total = await achievement_service.list_achievements(
        uow, current_user.uuid, page=page, limit=limit
    )
    total_pages = (total + limit - 1) // limit

    return AchievementListResponse(
        achievements=achievements,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
