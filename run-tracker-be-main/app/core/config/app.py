from typing import Annotated

from pydantic import field_validator
from pydantic_settings import NoDecode

from app.core.config.base import BaseConfig


class AppBaseConfig(BaseConfig):
    PROJECT_NAME: str = "Conflict Management"
    HOST: str = "localhost"
    PORT: int = 8000
    RELOAD: bool = True
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = []

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, value: str) -> list[str]:
        return value.split(",")
