from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import CurrentUserDep, UnitOfWorkDep
from app.schemas.challenge import (
    ChallengeAttemptCreate,
    ChallengeAttemptResponse,
    ChallengeCreate,
    ChallengeListResponse,
    ChallengeResponse,
)
from app.services.challenge import ChallengeService, get_challenge_service

router = APIRouter()

ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]


@router.post(
    "/",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new challenge",
)
async def create_challenge(
    data: ChallengeCreate,
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
) -> ChallengeResponse:
    return await service.create_challenge(uow, current_user, data)


@router.get(
    "/",
    response_model=ChallengeListResponse,
    summary="List available challenges (from friends)",
)
async def list_challenges(
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> ChallengeListResponse:
    return await service.list_available_challenges(uow, current_user.uuid, page, limit)


@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse,
    summary="Get challenge details",
)
async def get_challenge(
    challenge_id: UUID,
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
) -> ChallengeResponse:
    return await service.get_challenge(uow, challenge_id)


@router.get(
    "/run/{run_id}",
    response_model=ChallengeResponse | None,
    summary="Get challenge by source run ID",
)
async def get_challenge_by_run(
    run_id: UUID,
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
) -> ChallengeResponse | None:
    return await service.get_challenge_by_run(uow, run_id)


@router.post(
    "/{challenge_id}/attempt",
    response_model=ChallengeAttemptResponse,
    summary="Submit an attempt for a challenge",
)
async def attempt_challenge(
    challenge_id: UUID,
    data: ChallengeAttemptCreate,
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
) -> ChallengeAttemptResponse:
    return await service.attempt_challenge(uow, current_user.uuid, challenge_id, data)


@router.get(
    "/{challenge_id}/attempts",
    response_model=list[ChallengeAttemptResponse],
    summary="Get all attempts for a challenge",
)
async def get_challenge_attempts(
    challenge_id: UUID,
    uow: UnitOfWorkDep,
    service: ChallengeServiceDep,
    current_user: CurrentUserDep,
) -> list[ChallengeAttemptResponse]:
    return await service.get_challenge_attempts(uow, challenge_id)
