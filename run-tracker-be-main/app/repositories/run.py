from app.models.run import Run
from app.repositories.base import BaseRepository


class RunRepository(BaseRepository[Run]):
    def __init__(self, session):
        super().__init__(session, Run)
