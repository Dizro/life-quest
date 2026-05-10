"""
Точка входа FastAPI-приложения LifeQuest.

Swagger UI:   http://localhost:8000/docs
ReDoc:        http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import root_router
from app.core.config import settings
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# ── создание приложения ──────────────────────────────────────

app = FastAPI(
    title=settings.APP_TITLE,
    description=(
        "**LifeQuest** — геймифицированный трекер задач в формате RPG.\n\n"
        "Каждая задача — это квест, за выполнение которого герой получает "
        "очки опыта, монеты и достижения.\n\n"
        "### Основные ресурсы\n"
        "| Ресурс | Описание |\n"
        "|--------|----------|\n"
        "| **Users** | Регистрация, профиль героя, прокачка |\n"
        "| **Tasks** | Квесты: создание, редактирование, выполнение |\n"
        "| **Achievements** | Каталог достижений и разблокировки |\n"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Команда LifeQuest",
        "url": "https://codelab.tpu.ru/egk17/lifequest",
    },
    license_info={
        "name": "MIT",
    },
)

# ── настройка лимитера (после создания app) ─────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS (разрешаем фронтенду обращаться к API) ─────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── подключение роутеров ─────────────────────────────────────

app.include_router(root_router)


# ── проверка здоровья сервиса ────────────────────────────────

@app.get("/health", tags=["Система"])
async def health_check():
    """проверка работоспособности API."""
    return {"status": "ok", "message": "LifeQuest API работает"}