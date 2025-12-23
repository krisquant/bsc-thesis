from app.enums.base import BaseStrEnum


class GoalType(BaseStrEnum):
    DISTANCE = "DISTANCE"
    DURATION = "DURATION"
    NUMBER_OF_RUNS = "NUMBER_OF_RUNS"


class TimePeriod(BaseStrEnum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
