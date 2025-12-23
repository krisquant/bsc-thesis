from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from app.core.unit_of_work import ABCUnitOfWork
from app.enums.goal import GoalType, TimePeriod
from app.models.run import Run
from app.schemas.achievements import AchievementResponse


class AchievementService:
    async def check_and_award_achievements(
        self, uow: ABCUnitOfWork, user_uuid: UUID
    ) -> None:
        async with uow:
            # 1. Fetch active goals
            goals, total = await uow.goal.get_many(user_uuid=user_uuid, is_active=True)

            for goal in goals:
                # 2. Determine time period range
                start_date, end_date, period_identifier = self._get_period_range(
                    goal.time_period
                )

                # 3. Calculate progress
                progress = await self._calculate_progress(
                    uow, user_uuid, goal.goal_type, start_date, end_date
                )

                # 4. Check if goal is met
                if progress >= goal.target:
                    achievements, _ = await uow.achievement.get_many(
                        user_uuid=user_uuid, achievement_type="GOAL_COMPLETION"
                    )

                    already_awarded = False
                    for ach in achievements:
                        if (
                            ach.meta_data.get("goal_id") == str(goal.uuid)
                            and ach.meta_data.get("period") == period_identifier
                        ):
                            already_awarded = True
                            break

                    if not already_awarded:
                        # 6. Award achievement
                        await uow.achievement.create_one(
                            {
                                "user_uuid": user_uuid,
                                "title": f"{goal.time_period.value.title()} {goal.goal_type.value.title()} Goal Met",
                                "description": f"You achieved your goal of {goal.target} {self._get_unit(goal.goal_type)}!",
                                "earned_at": datetime.now(),
                                "achievement_type": "GOAL_COMPLETION",
                                "meta_data": {
                                    "goal_id": str(goal.uuid),
                                    "period": period_identifier,
                                    "target": goal.target,
                                    "achieved": progress,
                                    "goal_type": goal.goal_type.value,
                                    "time_period": goal.time_period.value,
                                },
                            }
                        )

    def _get_period_range(
        self, time_period: TimePeriod
    ) -> tuple[datetime, datetime, str]:
        now = datetime.now()
        if time_period == TimePeriod.WEEKLY:
            # Monday start
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
            period_identifier = f"{start_date.year}-W{start_date.isocalendar()[1]}"
        elif time_period == TimePeriod.MONTHLY:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Next month calculation
            if now.month == 12:
                end_date = now.replace(year=now.year + 1, month=1, day=1)
            else:
                end_date = now.replace(month=now.month + 1, day=1)
            period_identifier = f"{start_date.year}-M{start_date.month}"
        elif time_period == TimePeriod.YEARLY:
            start_date = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = now.replace(year=now.year + 1, month=1, day=1)
            period_identifier = f"{start_date.year}"
        else:
            raise ValueError(f"Unsupported time period: {time_period}")

        return start_date, end_date, period_identifier

    async def _calculate_progress(
        self,
        uow: ABCUnitOfWork,
        user_uuid: UUID,
        goal_type: GoalType,
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        # We can use SQL aggregation for efficiency
        if goal_type == GoalType.DISTANCE:
            stmt = select(func.sum(Run.distance)).where(
                Run.user_uuid == user_uuid,
                Run.start_time >= start_date,
                Run.start_time < end_date,
            )
        elif goal_type == GoalType.DURATION:
            stmt = select(func.sum(Run.duration)).where(
                Run.user_uuid == user_uuid,
                Run.start_time >= start_date,
                Run.start_time < end_date,
            )
        elif goal_type == GoalType.NUMBER_OF_RUNS:
            stmt = select(func.count(Run.uuid)).where(
                Run.user_uuid == user_uuid,
                Run.start_time >= start_date,
                Run.start_time < end_date,
            )
        else:
            return 0.0

        result = await uow.session.execute(stmt)
        return result.scalar() or 0.0

    def _get_unit(self, goal_type: GoalType) -> str:
        if goal_type == GoalType.DISTANCE:
            return "km"
        elif goal_type == GoalType.DURATION:
            return "minutes"
        elif goal_type == GoalType.NUMBER_OF_RUNS:
            return "runs"
        return ""

    async def list_achievements(
        self, uow: ABCUnitOfWork, user_uuid: UUID, page: int = 1, limit: int = 10
    ) -> tuple[list[AchievementResponse], int]:
        async with uow:
            achievements, total = await uow.achievement.get_many(
                page=page, limit=limit, user_uuid=user_uuid
            )
            responses = [
                AchievementResponse.model_validate(ach) for ach in achievements
            ]
            return responses, total


def get_achievement_service() -> AchievementService:
    return AchievementService()
