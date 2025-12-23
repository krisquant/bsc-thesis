from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one(email=email)

    async def email_exists(self, email: str) -> bool:
        user = await self.get_one(email=email)
        return user is not None
