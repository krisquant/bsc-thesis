from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlalchemy import desc, func, select

from app.core.unit_of_work import ABCUnitOfWork
from app.enums.statistics import StatisticsPeriod
from app.models.run import Run
from app.schemas.statistics import (
    PersonalRecords,
    StreakStats,
    TotalStats,
    UserStatisticsResponse,
    VisualizationDataPoint,
)


class StatisticsService:
    async def get_user_statistics(
        self, uow: ABCUnitOfWork, user_uuid: UUID
    ) -> UserStatisticsResponse:
        async with uow:
            totals = await self._calculate_totals(uow, user_uuid)
            personal_records = await self._calculate_personal_records(uow, user_uuid)
            streaks = await self._calculate_streaks(uow, user_uuid)
            return UserStatisticsResponse(
                totals=totals,
                streaks=streaks,
                personal_records=personal_records,
            )

    async def _calculate_totals(
        self, uow: ABCUnitOfWork, user_uuid: UUID
    ) -> TotalStats:
        stmt = select(
            func.sum(Run.distance),
            func.sum(Run.duration),
            func.count(Run.uuid),
        ).where(Run.user_uuid == user_uuid)

        result = await uow.session.execute(stmt)
        distance, duration, count = result.one()

        return TotalStats(
            total_distance=distance or 0.0,
            total_duration=duration or 0.0,
            total_workouts=count or 0,
        )

    async def _calculate_personal_records(
        self, uow: ABCUnitOfWork, user_uuid: UUID
    ) -> PersonalRecords:
        # Longest Distance
        stmt_dist = select(func.max(Run.distance)).where(Run.user_uuid == user_uuid)
        res_dist = await uow.session.execute(stmt_dist)
        longest_dist = res_dist.scalar()

        # Longest Duration
        stmt_dur = select(func.max(Run.duration)).where(Run.user_uuid == user_uuid)
        res_dur = await uow.session.execute(stmt_dur)
        longest_dur = res_dur.scalar()

        # Fastest Pace (min/km) - Lower is better.
        # Pace = duration / distance. We need to handle division by zero.
        # Let's fetch runs with distance > 0 and calculate in DB or Python.
        # SQL: MIN(duration / distance)
        stmt_pace = select(func.min(Run.duration / Run.distance)).where(
            Run.user_uuid == user_uuid, Run.distance > 0
        )
        res_pace = await uow.session.execute(stmt_pace)
        fastest_pace = res_pace.scalar()

        return PersonalRecords(
            fastest_pace=fastest_pace,
            longest_distance=longest_dist,
            longest_duration=longest_dur,
        )

    async def _calculate_streaks(
        self, uow: ABCUnitOfWork, user_uuid: UUID
    ) -> StreakStats:
        stmt = (
            select(func.date(Run.start_time))
            .where(Run.user_uuid == user_uuid)
            .distinct()
            .order_by(desc(func.date(Run.start_time)))
        )
        result = await uow.session.execute(stmt)
        dates = [row[0] for row in result.all()]

        if not dates:
            return StreakStats(current_streak=0, longest_streak=0)

        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Check if streak is active (run today or yesterday)
        is_active = dates[0] == today or dates[0] == yesterday

        if not is_active:
            current_streak = 0

        # Calculate streaks
        # Dates are sorted desc (newest first)
        # Example: [2023-10-25, 2023-10-24, 2023-10-22]

        # Iterate backwards (oldest to newest) to easily count streaks?
        # Or iterate desc and check diff?
        # Let's sort asc for easier logic
        dates.sort()

        temp_streak = 1
        longest_streak = 1

        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i - 1]).days
            if diff == 1:
                temp_streak += 1
            elif diff > 1:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
            # If diff == 0 (same day), ignore

        longest_streak = max(longest_streak, temp_streak)

        # Calculate current streak
        # We need to check from today backwards
        current_streak = 0
        check_date = today

        # If no run today, check if run yesterday to start streak count
        if dates[-1] != today:
            if dates[-1] == yesterday:
                check_date = yesterday
            else:
                # Streak broken
                return StreakStats(current_streak=0, longest_streak=longest_streak)

        # Now count backwards from check_date
        # We can use a set for O(1) lookup
        dates_set = set(dates)
        while check_date in dates_set:
            current_streak += 1
            check_date -= timedelta(days=1)

        return StreakStats(current_streak=current_streak, longest_streak=longest_streak)

    async def get_visualization_data(
        self, uow: ABCUnitOfWork, user_uuid: UUID, period: StatisticsPeriod
    ) -> List[VisualizationDataPoint]:
        async with uow:
            if period == StatisticsPeriod.LAST_7_DAYS:
                start_date = datetime.now() - timedelta(days=6)
                return await self._aggregate_runs(uow, user_uuid, start_date, "day")
            elif period == StatisticsPeriod.LAST_30_DAYS:
                start_date = datetime.now() - timedelta(days=29)
                return await self._aggregate_runs(uow, user_uuid, start_date, "day")
            elif period == StatisticsPeriod.LAST_YEAR:
                start_date = datetime.now() - timedelta(days=365)
                return await self._aggregate_runs(uow, user_uuid, start_date, "month")
            else:
                raise ValueError("Invalid period")

    async def _aggregate_runs(
        self, uow: ABCUnitOfWork, user_uuid: UUID, start_date: datetime, group_by: str
    ) -> List[VisualizationDataPoint]:
        # This is DB specific (Postgres).
        # We need to truncate date.

        if group_by == "day":
            date_trunc = func.date_trunc("day", Run.start_time)
            label_fmt = "YYYY-MM-DD"
        elif group_by == "month":
            date_trunc = func.date_trunc("month", Run.start_time)
            label_fmt = "YYYY-MM"
        elif group_by == "year":
            date_trunc = func.date_trunc("year", Run.start_time)
            label_fmt = "YYYY"
        else:
            raise ValueError("Invalid group_by")

        stmt = (
            select(
                func.to_char(date_trunc, label_fmt).label("label"),
                func.sum(Run.distance).label("distance"),
                func.sum(Run.duration).label("duration"),
                func.count(Run.uuid).label("count"),
            )
            .where(Run.user_uuid == user_uuid, Run.start_time >= start_date)
            .group_by("label")
            .order_by("label")
        )

        result = await uow.session.execute(stmt)
        db_points = {
            row.label: VisualizationDataPoint(
                label=row.label,
                distance=row.distance or 0.0,
                duration=row.duration or 0.0,
                count=row.count or 0,
            )
            for row in result.all()
        }

        points = []
        current_date = start_date
        end_date = datetime.now()

        # Normalize start_date to ensure correct iteration
        if group_by == "day":
            # Reset time to midnight for daily iteration
            current_date = current_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif group_by == "month":
            # Reset to first day of month
            current_date = current_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        elif group_by == "year":
            current_date = current_date.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )

        while current_date <= end_date:
            if group_by == "day":
                label = current_date.strftime(
                    label_fmt.replace("YYYY", "%Y")
                    .replace("MM", "%m")
                    .replace("DD", "%d")
                )
                next_date = current_date + timedelta(days=1)
            elif group_by == "month":
                label = current_date.strftime(
                    label_fmt.replace("YYYY", "%Y").replace("MM", "%m")
                )
                # Increment month
                if current_date.month == 12:
                    next_date = current_date.replace(
                        year=current_date.year + 1, month=1
                    )
                else:
                    next_date = current_date.replace(month=current_date.month + 1)
            elif group_by == "year":
                label = current_date.strftime(label_fmt.replace("YYYY", "%Y"))
                next_date = current_date.replace(year=current_date.year + 1)
            else:
                break

            if label in db_points:
                points.append(db_points[label])
            else:
                points.append(
                    VisualizationDataPoint(
                        label=label,
                        distance=0.0,
                        duration=0.0,
                        count=0,
                    )
                )

            current_date = next_date

        return points


def get_statistics_service() -> StatisticsService:
    return StatisticsService()
