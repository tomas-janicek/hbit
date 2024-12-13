import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

if not (HBIT_API_URL := os.getenv("HBIT_API_URL")):
    raise ValueError("ENV variable HBIT_API_URL must be set!")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    HBIT_API_URL: str
    DEFAULT_TIMEOUT: int = 10
    LOGGING_LEVEL: str = "INFO"
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str


settings = Settings()  # type: ignore

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(asctime)s][%(levelname)s]: %(message)s"},
        "rich": {"format": "%(message)s", "datefmt": "[%x %X]"},
    },
    "handlers": {
        "console": {
            "level": settings.LOGGING_LEVEL,
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "markup": True,
            "show_path": True,
        },
        "file": {
            "level": settings.LOGGING_LEVEL,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "backupCount": "4",
            "filename": "app.log",
        },
    },
    "loggers": {
        "root": {
            "level": settings.LOGGING_LEVEL,
            "handlers": ["console", "file"],
        },
    },
}
