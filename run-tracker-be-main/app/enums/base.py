from enum import StrEnum
from typing import List, Type, TypeVar

E = TypeVar("E", bound="BaseStrEnum")


class BaseStrEnum(StrEnum):
    @classmethod
    def list(cls) -> list[str]:
        return list(cls.__members__.values())

    @classmethod
    def members(cls: Type[E]) -> List[E]:
        return list(cls)
