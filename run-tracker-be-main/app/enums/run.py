from app.enums.base import BaseStrEnum


class RunSortBy(BaseStrEnum):
    DATE = "DATE"
    DISTANCE = "DISTANCE"
    DURATION = "DURATION"


class SortOrder(BaseStrEnum):
    ASC = "ASC"
    DESC = "DESC"
