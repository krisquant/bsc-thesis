from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import CurrentUserDep, UnitOfWorkDep, UserServiceDep
from app.schemas.users import UserListResponse, UserResponse, UserUpdateRequest

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUserDep,
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_info(
    current_user: CurrentUserDep,
    update_data: UserUpdateRequest,
    user_service: UserServiceDep,
    uow: UnitOfWorkDep,
) -> UserResponse:
    return await user_service.update_current_user(uow, current_user.uuid, update_data)


@router.get("/", response_model=UserListResponse)
async def list_users(
    user_service: UserServiceDep,
    uow: UnitOfWorkDep,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> UserListResponse:
    users, total = await user_service.list_users(uow, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit  # Ceiling division

    return UserListResponse(
        users=users, total=total, page=page, limit=limit, total_pages=total_pages
    )
