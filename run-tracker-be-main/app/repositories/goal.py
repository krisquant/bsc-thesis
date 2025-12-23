from app.models.goal import Goal
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, session):
        super().__init__(session, Goal)
