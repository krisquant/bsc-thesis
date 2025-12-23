from uuid import UUID

from app.core.unit_of_work import ABCUnitOfWork
from app.schemas.users import UserResponse, UserUpdateRequest


class UserService:
    async def list_users(
        self, uow: ABCUnitOfWork, page: int = 1, limit: int = 10
    ) -> tuple[list[UserResponse], int]:
        async with uow:
            users, total = await uow.user.get_many(page=page, limit=limit)
            user_responses = [UserResponse.model_validate(user) for user in users]
            return user_responses, total

    async def update_current_user(
        self, uow: ABCUnitOfWork, user_uuid: UUID, data: UserUpdateRequest
    ) -> UserResponse:
        """Update current user information."""
        async with uow:
            # Remove fields that shouldn't be updated directly
            allowed_fields = {"username", "age", "gender", "height", "weight"}
            filtered_data = {
                k: v
                for k, v in data.model_dump(exclude_unset=True).items()
                if k in allowed_fields and v is not None
            }

            user = await uow.user.update_one(user_uuid, filtered_data)
            return UserResponse.model_validate(user)


def get_user_service() -> UserService:
    return UserService()
