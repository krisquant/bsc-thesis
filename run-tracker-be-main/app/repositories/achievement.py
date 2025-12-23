from app.models.achievement import Achievement
from app.repositories.base import BaseRepository


class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, session):
        super().__init__(session, Achievement)
