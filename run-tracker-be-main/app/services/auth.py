from fastapi import HTTPException, status

from app.core.exc import InvalidCredentialsException, UserNotAuthenticatedException
from app.core.unit_of_work import ABCUnitOfWork
from app.schemas.auth import (
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
)
from app.schemas.users import UserResponse
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    async def sign_up(self, uow: ABCUnitOfWork, data: SignUpRequest) -> UserResponse:
        async with uow:
            existing_user = await uow.user.get_by_email(data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Create new user
            hashed_password = get_password_hash(data.password)
            user_data = {
                "email": data.email,
                "hashed_password": hashed_password,
                "username": data.username,
                "age": data.age,
                "gender": data.gender,
                "height": data.height,
                "weight": data.weight,
            }

            user = await uow.user.create_one(user_data)
            return UserResponse.model_validate(user)

    async def sign_in(self, uow: ABCUnitOfWork, data: SignInRequest) -> TokenResponse:
        async with uow:
            # Get user by email
            user = await uow.user.get_by_email(data.email)
            if not user:
                raise InvalidCredentialsException()

            # Verify password
            if not verify_password(data.password, user.hashed_password):
                raise InvalidCredentialsException()

            # Create tokens
            access_token = create_access_token(data={"sub": str(user.uuid)})
            refresh_token = create_refresh_token(data={"sub": str(user.uuid)})

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )

    async def refresh(
        self, uow: ABCUnitOfWork, data: RefreshTokenRequest
    ) -> TokenResponse:
        payload = decode_token(data.refresh_token)
        if payload is None:
            raise UserNotAuthenticatedException()

        user_id: str = payload.get("sub")
        if user_id is None:
            raise UserNotAuthenticatedException()

        async with uow:
            user = await uow.user.get_one(uuid=user_id)
            if user is None:
                raise UserNotAuthenticatedException()

            # Create new tokens
            access_token = create_access_token(data={"sub": str(user.uuid)})
            refresh_token = create_refresh_token(data={"sub": str(user.uuid)})

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )


def get_auth_service() -> AuthService:
    return AuthService()
