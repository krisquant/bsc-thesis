from app.core.config.base import BaseConfig


class DBConfig(BaseConfig):
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    HOST: str = "localhost"
    PORT: int = 5432
    DB: str = "postgres"

    @property
    def url(self) -> str:
        """Constructs the SQLAlchemy URL using the database configuration."""
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"

    class Config:
        env_prefix = "DB_"
