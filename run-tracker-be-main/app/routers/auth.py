from fastapi import APIRouter, status

from app.dependencies import AuthServiceDep, UnitOfWorkDep
from app.schemas.auth import (
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
)
from app.schemas.users import UserResponse

router = APIRouter()


@router.post(
    "/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def sign_up(
    data: SignUpRequest,
    uow: UnitOfWorkDep,
    auth_service: AuthServiceDep,
) -> UserResponse:
    return await auth_service.sign_up(uow, data)


@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    data: SignInRequest,
    uow: UnitOfWorkDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.sign_in(uow, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    uow: UnitOfWorkDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.refresh(uow, data)
