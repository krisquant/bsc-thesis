from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import CurrentUserDep, UnitOfWorkDep
from app.schemas.friendship import (
    FriendListResponse,
    FriendRequestCreate,
    FriendRequestListResponse,
    FriendRequestRespond,
    FriendshipResponse,
)
from app.services.friendship import FriendshipService, get_friendship_service

router = APIRouter()

FriendshipServiceDep = Annotated[FriendshipService, Depends(get_friendship_service)]


@router.post("/request", response_model=FriendshipResponse)
async def send_friend_request(
    current_user: CurrentUserDep,
    data: FriendRequestCreate,
    service: FriendshipServiceDep,
    uow: UnitOfWorkDep,
) -> FriendshipResponse:
    return await service.send_request(uow, current_user, data.email)


@router.get("/requests", response_model=FriendRequestListResponse)
async def list_friend_requests(
    current_user: CurrentUserDep,
    service: FriendshipServiceDep,
    uow: UnitOfWorkDep,
) -> FriendRequestListResponse:
    return await service.list_requests(uow, current_user.uuid)


@router.post("/{request_id}/respond")
async def respond_to_friend_request(
    request_id: UUID,
    current_user: CurrentUserDep,
    data: FriendRequestRespond,
    service: FriendshipServiceDep,
    uow: UnitOfWorkDep,
) -> None:
    await service.respond_to_request(uow, current_user.uuid, request_id, data.action)


@router.get("/", response_model=FriendListResponse)
async def list_friends(
    current_user: CurrentUserDep,
    service: FriendshipServiceDep,
    uow: UnitOfWorkDep,
) -> FriendListResponse:
    return await service.list_friends(uow, current_user.uuid)
