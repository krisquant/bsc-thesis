from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import CurrentUserDep, GoalServiceDep, UnitOfWorkDep
from app.schemas.goals import (
    GoalCreateRequest,
    GoalListResponse,
    GoalResponse,
)

router = APIRouter()


@router.post("/", response_model=GoalResponse, status_code=201)
async def create_goal(
    current_user: CurrentUserDep,
    data: GoalCreateRequest,
    goal_service: GoalServiceDep,
    uow: UnitOfWorkDep,
) -> GoalResponse:
    return await goal_service.create_goal(uow, current_user.uuid, data)


@router.get("/", response_model=GoalListResponse)
async def list_goals(
    current_user: CurrentUserDep,
    goal_service: GoalServiceDep,
    uow: UnitOfWorkDep,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> GoalListResponse:
    goals, total = await goal_service.list_goals(
        uow, current_user.uuid, page=page, limit=limit
    )
    total_pages = (total + limit - 1) // limit

    return GoalListResponse(
        goals=goals, total=total, page=page, limit=limit, total_pages=total_pages
    )


@router.get("/{goal_uuid}", response_model=GoalResponse)
async def get_goal(
    current_user: CurrentUserDep,
    goal_uuid: UUID,
    goal_service: GoalServiceDep,
    uow: UnitOfWorkDep,
) -> GoalResponse:
    return await goal_service.get_goal(uow, current_user.uuid, goal_uuid)


@router.delete("/{goal_uuid}", response_model=GoalResponse)
async def delete_goal(
    current_user: CurrentUserDep,
    goal_uuid: UUID,
    goal_service: GoalServiceDep,
    uow: UnitOfWorkDep,
) -> GoalResponse:
    return await goal_service.delete_goal(uow, current_user.uuid, goal_uuid)
