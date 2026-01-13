from abc import ABC, abstractmethod
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import async_session
from app.repositories.achievement import AchievementRepository
from app.repositories.challenge import ChallengeAttemptRepository, ChallengeRepository
from app.repositories.friendship import FriendshipRepository
from app.repositories.goal import GoalRepository
from app.repositories.run import RunRepository
from app.repositories.user import UserRepository


class ABCUnitOfWork(ABC):
    session: AsyncSession

    user: UserRepository
    goal: GoalRepository
    run: RunRepository
    achievement: AchievementRepository
    friendship: FriendshipRepository
    challenge: ChallengeRepository
    challenge_attempt: ChallengeAttemptRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> "ABCUnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        raise NotImplementedError


class UnitOfWork(ABCUnitOfWork):
    def __init__(self) -> None:
        self.session_maker = async_session

    async def __aenter__(self) -> "ABCUnitOfWork":
        self.session = self.session_maker()

        self.user = UserRepository(self.session)
        self.goal = GoalRepository(self.session)
        self.run = RunRepository(self.session)
        self.achievement = AchievementRepository(self.session)
        self.friendship = FriendshipRepository(self.session)
        self.challenge = ChallengeRepository(self.session)
        self.challenge_attempt = ChallengeAttemptRepository(self.session)

        return self

    async def __aexit__(self, *args: Any) -> None:
        exc_type, exc, tb = args
        if exc:
            log_func = logger.exception if settings.app.RELOAD else logger.error
            log_func(
                "An error occurred while processing the request. Rolling back. Error: {exc}",
                exc=exc,
            )
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
        await logger.complete()

        if exc:
            raise exc

    async def rollback(self) -> None:
        await self.session.rollback()
