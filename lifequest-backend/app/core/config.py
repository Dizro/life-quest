from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://lifequest_user:lifequest_pass@db:5432/lifequest_db"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    SECRET_KEY: str = "super-secret-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # YandexGPT
    YANDEX_API_KEY: str = ""
    YANDEX_FOLDER_ID: str = ""

    # AI timeouts and defaults
    AI_TIMEOUT_SECONDS: int = 10
    AI_DEFAULT_EFFORT_SCORE: int = 5
    AI_DEFAULT_COMPLEXITY: str = "Medium"
    AI_DEFAULT_REASONING: str = "Оценка по умолчанию (таймаут ИИ)"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()