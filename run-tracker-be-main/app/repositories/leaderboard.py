from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.run import Run
from app.models.user import User
from app.schemas.leaderboard import LeaderboardMetric


class LeaderboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_leaderboard(
        self,
        metric: LeaderboardMetric,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        user_ids: Optional[List[UUID]] = None,
    ) -> List[dict]:
        value_expr = self._get_metric_expression(metric)

        # Build join conditions
        join_conditions = [User.uuid == Run.user_uuid]
        if start_date:
            join_conditions.append(Run.start_time >= start_date)
        if end_date:
            join_conditions.append(Run.start_time <= end_date)

        query = select(
            User.uuid.label("user_uuid"),
            User.username,
            value_expr.label("value"),
            func.rank().over(order_by=desc(value_expr)).label("rank"),
        ).outerjoin(Run, and_(*join_conditions))

        if user_ids:
            query = query.where(User.uuid.in_(user_ids))

        stmt = (
            query.group_by(User.uuid, User.username)
            .order_by(desc("value"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_user_entry(
        self,
        user_uuid: UUID,
        metric: LeaderboardMetric,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_ids: Optional[List[UUID]] = None,
    ) -> Optional[dict]:
        value_expr = self._get_metric_expression(metric)

        # Build join conditions
        join_conditions = [User.uuid == Run.user_uuid]
        if start_date:
            join_conditions.append(Run.start_time >= start_date)
        if end_date:
            join_conditions.append(Run.start_time <= end_date)

        query = select(
            User.uuid.label("user_uuid"),
            User.username,
            value_expr.label("value"),
            func.rank().over(order_by=desc(value_expr)).label("rank"),
        ).outerjoin(Run, and_(*join_conditions))

        if user_ids:
            query = query.where(User.uuid.in_(user_ids))

        subquery = query.group_by(User.uuid, User.username)

        subquery = subquery.subquery()

        stmt = select(subquery).where(subquery.c.user_uuid == user_uuid)

        result = await self.session.execute(stmt)
        return result.one_or_none()

    def _get_metric_expression(self, metric: LeaderboardMetric) -> Any:
        if metric == LeaderboardMetric.DISTANCE:
            return func.coalesce(func.sum(Run.distance), 0)
        elif metric == LeaderboardMetric.DURATION:
            return func.coalesce(func.sum(Run.duration), 0)
        elif metric == LeaderboardMetric.RUNS:
            return func.count(Run.uuid)
        else:
            raise ValueError(f"Unknown metric: {metric}")
