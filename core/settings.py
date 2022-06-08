from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, EmailStr
from starlette.config import Config

config = Config(".env")


class Settings(BaseSettings):
    """System Settings file for app configuration.

    Args:
        BaseSettings (object): Abstract base settings.
    """

    # project declaratives.
    project_name: str = config("PROJECT_NAME", cast=str, default="Pixel_Tracker")
    environment: str = config("ENVIRONMENT", cast=str, default="DEV")
    default_page_limit: int = config("DEFAULT_PAGE_LIMIT", cast=int, default=50)

    # db settings
    db_host: str = config("MONGO_HOST", cast=str, default="mongo")
    db_port: int = config("MONGO_PORT", cast=int, default="27017")
    db_name: str = config("MONGO_DB_NAME", cast=str, default="pixel_tracker")
    db_user: str = config("MONGO_INITDB_ROOT_USERNAME", cast=str, default="aayush")
    db_password: str = config("MONGO_INITDB_ROOT_PASSWORD", cast=str, default="password")
    db_pool_min_size: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=2)
    db_pool_max_size: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
    db_force_rollback: bool = False
    mongo_db_url: str = config(
        "MONGO_URL", cast=str,
        default="mongodb+srv://searchtest:adcuratio@searchtest.9j4ms.mongodb.net/test")

class ProdSettings(Settings):
    debug: bool = False


class DevSettings(Settings):
    debug: bool = True


class TestSettings(Settings):
    debug: bool = True
    testing: bool = True
    db_force_rollback: bool = True

class FactoryConfig:
    """
    Returns a config instance depends on the ENV_STATE variable.
    """

    def __init__(self, environment: Optional[str] = "DEV"):
        self.environment = environment

    def __call__(self):
        if self.environment == "PROD":
            return ProdSettings()
        elif self.environment == "TEST":
            return TestSettings()
        return DevSettings()
        
@lru_cache()
def get_app_settings():
    return FactoryConfig(Settings().environment)()
