from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.challenge import Challenge, ChallengeAttempt
from app.repositories.base import BaseRepository


class ChallengeRepository(BaseRepository[Challenge]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Challenge)

    async def get_available_challenges(
        self, friend_ids: List[UUID], page: int = 1, limit: int = 10
    ) -> tuple[List[Challenge], int]:
        # Include challenges created by friends
        filters = [Challenge.creator_id.in_(friend_ids), Challenge.is_active.is_(True)]
        options = [selectinload(Challenge.creator), selectinload(Challenge.source_run)]
        return await self.get_many(
            page=page, limit=limit, filters=filters, options=options
        )

    async def get_by_run_id(self, run_id: UUID) -> Challenge | None:
        query = (
            select(self.model)
            .where(self.model.source_run_id == run_id)
            .options(
                selectinload(Challenge.creator), selectinload(Challenge.source_run)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, challenge_id: UUID) -> Challenge | None:
        query = (
            select(self.model)
            .where(self.model.uuid == challenge_id)
            .options(
                selectinload(Challenge.creator), selectinload(Challenge.source_run)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class ChallengeAttemptRepository(BaseRepository[ChallengeAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChallengeAttempt)

    async def get_attempts_by_challenge(
        self, challenge_id: UUID
    ) -> List[ChallengeAttempt]:
        query = (
            select(self.model)
            .where(self.model.challenge_id == challenge_id)
            .options(
                selectinload(ChallengeAttempt.user), selectinload(ChallengeAttempt.run)
            )
            .order_by(self.model.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
