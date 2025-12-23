from app.core.config.app import AppBaseConfig
from app.core.config.auth import AuthBaseConfig
from app.core.config.base import BaseConfig
from app.core.config.db import DBConfig


class AppSettings(BaseConfig):
    """
    A centralized Settings class that aggregates different configuration components
    """

    app: AppBaseConfig = AppBaseConfig()
    auth: AuthBaseConfig = AuthBaseConfig()
    db: DBConfig = DBConfig()


settings = AppSettings()
