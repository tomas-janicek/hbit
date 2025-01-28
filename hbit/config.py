from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ROOT_DIT: Path = Path(__file__).parent.parent
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    STATIC_DIR: Path = ROOT_DIT / "static"

    HBIT_API_URL: str
    DEFAULT_TIMEOUT: int = 10
    LOGGING_LEVEL: str = "INFO"
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    DB_SCHEMA: str
    DB_SERVER: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    GROQ_API_KEY: str
    MODEL_SEED: int = 0
    REQUESTS_PER_SECOND: float = 0.5

    N_VULNERABILITIES: int = 10
    N_TOKEN_GENERATION_LIMIT: int = 15_000

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        db_url = URL.create(
            drivername=self.DB_SCHEMA,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_SERVER,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )
        return str(db_url)

    @computed_field
    @property
    def READ_SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"{self.SQLALCHEMY_DATABASE_URI}?immutable=1"


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
            "backupCount": 1,
            "filename": "logs/ml.log",
        },
    },
    "loggers": {
        "root": {
            "level": settings.LOGGING_LEVEL,
            "handlers": ["console", "file"],
        },
    },
}
