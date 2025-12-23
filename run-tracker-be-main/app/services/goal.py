from uuid import UUID

from app.core.exc import ObjectNotFoundException
from app.core.unit_of_work import ABCUnitOfWork
from app.schemas.goals import GoalCreateRequest, GoalResponse


class GoalService:
    async def create_goal(
        self, uow: ABCUnitOfWork, user_uuid: UUID, data: GoalCreateRequest
    ) -> GoalResponse:
        async with uow:
            goal_data = data.model_dump()
            goal_data["user_uuid"] = user_uuid
            goal = await uow.goal.create_one(goal_data)
            return GoalResponse.model_validate(goal)

    async def list_goals(
        self, uow: ABCUnitOfWork, user_uuid: UUID, page: int = 1, limit: int = 10
    ) -> tuple[list[GoalResponse], int]:
        async with uow:
            goals, total = await uow.goal.get_many(
                page=page, limit=limit, user_uuid=user_uuid
            )
            goal_responses = [GoalResponse.model_validate(goal) for goal in goals]
            return goal_responses, total

    async def get_goal(
        self, uow: ABCUnitOfWork, user_uuid: UUID, goal_uuid: UUID
    ) -> GoalResponse:
        async with uow:
            goal = await uow.goal.get_one(uuid=goal_uuid, user_uuid=user_uuid)
            if not goal:
                raise ObjectNotFoundException(goal_uuid, "Goal")
            return GoalResponse.model_validate(goal)

    async def delete_goal(
        self, uow: ABCUnitOfWork, user_uuid: UUID, goal_uuid: UUID
    ) -> GoalResponse:
        async with uow:
            goal = await uow.goal.get_one(uuid=goal_uuid, user_uuid=user_uuid)
            if not goal:
                raise ObjectNotFoundException(goal_uuid, "Goal")

            deleted_goal = await uow.goal.delete_one(goal_uuid)
            return GoalResponse.model_validate(deleted_goal)


def get_goal_service() -> GoalService:
    return GoalService()
