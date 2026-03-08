"""
Конфигурация приложения через pydantic-settings.
Все переменные окружения валидируются при старте — если чего-то не хватает,
приложение сразу упадёт с понятной ошибкой.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── PostgreSQL ──────────────────────────────────────────────
    POSTGRES_USER: str = "lifequest_user"
    POSTGRES_PASSWORD: str = "lifequest_pass"
    POSTGRES_DB: str = "lifequest_db"
    DATABASE_URL: str = (
        "postgresql+asyncpg://lifequest_user:lifequest_pass@db:5432/lifequest_db"
    )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """синхронный URL для Alembic-миграций (psycopg2 вместо asyncpg)."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")

    # ── Redis / Celery ─────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── Приложение ─────────────────────────────────────────────
    APP_TITLE: str = "LifeQuest API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True


settings = Settings()
