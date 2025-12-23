from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.core.unit_of_work import ABCUnitOfWork
from app.repositories.leaderboard import LeaderboardRepository
from app.schemas.leaderboard import (
    LeaderboardEntry,
    LeaderboardMetric,
    LeaderboardPeriod,
    LeaderboardResponse,
)


class LeaderboardService:
    async def get_leaderboard(
        self,
        uow: ABCUnitOfWork,
        metric: LeaderboardMetric,
        period: LeaderboardPeriod,
        current_user_uuid: UUID,
        limit: int = 50,
    ) -> LeaderboardResponse:
        async with uow:
            repo = LeaderboardRepository(uow.session)
            start_date = self._get_start_date(period)

            # Get top N entries
            raw_entries = await repo.get_leaderboard(
                metric, start_date=start_date, limit=limit
            )

            entries = [
                LeaderboardEntry(
                    rank=row.rank,
                    user_uuid=row.user_uuid,
                    username=row.username,
                    value=row.value or 0,
                    is_current_user=(row.user_uuid == current_user_uuid),
                )
                for row in raw_entries
            ]

            # Check if current user is in the top N
            current_user_entry = None
            user_in_top = any(e.user_uuid == current_user_uuid for e in entries)

            if user_in_top:
                # Find the entry in the list
                current_user_entry = next(
                    e for e in entries if e.user_uuid == current_user_uuid
                )
            else:
                # Fetch user's specific rank
                raw_user_entry = await repo.get_user_entry(
                    current_user_uuid, metric, start_date=start_date
                )
                if raw_user_entry:
                    current_user_entry = LeaderboardEntry(
                        rank=raw_user_entry.rank,
                        user_uuid=raw_user_entry.user_uuid,
                        username=raw_user_entry.username,
                        value=raw_user_entry.value or 0,
                        is_current_user=True,
                    )

            return LeaderboardResponse(
                entries=entries, current_user_entry=current_user_entry
            )

    def _get_start_date(self, period: LeaderboardPeriod) -> Optional[datetime]:
        now = datetime.now()
        if period == LeaderboardPeriod.WEEK:
            # Start of current week (Monday)
            start_of_week = now - timedelta(days=now.weekday())
            return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == LeaderboardPeriod.MONTH:
            # Start of current month
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == LeaderboardPeriod.ALL_TIME:
            return None
        return None


def get_leaderboard_service() -> LeaderboardService:
    return LeaderboardService()
