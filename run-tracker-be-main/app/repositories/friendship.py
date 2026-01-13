from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from app.models.friendship import Friendship, FriendshipStatus
from app.repositories.base import BaseRepository


class FriendshipRepository(BaseRepository[Friendship]):
    def __init__(self, session):
        super().__init__(session, Friendship)

    async def get_friendship(self, user_id_1, user_id_2):
        stmt = select(self.model).where(
            or_(
                and_(
                    self.model.requester_id == user_id_1,
                    self.model.addressee_id == user_id_2,
                ),
                and_(
                    self.model.requester_id == user_id_2,
                    self.model.addressee_id == user_id_1,
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_friends(self, user_id):
        # Fetch friendships where user is involved and status is ACCEPTED
        stmt = select(self.model).where(
            and_(
                or_(
                    self.model.requester_id == user_id,
                    self.model.addressee_id == user_id,
                ),
                self.model.status == FriendshipStatus.ACCEPTED,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_requests(self, user_id, type="incoming"):
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.requester), selectinload(self.model.addressee)
            )
            .where(self.model.status == FriendshipStatus.PENDING)
        )

        if type == "incoming":
            stmt = stmt.where(self.model.addressee_id == user_id)
        else:
            stmt = stmt.where(self.model.requester_id == user_id)

        result = await self.session.execute(stmt)
        return result.scalars().all()
