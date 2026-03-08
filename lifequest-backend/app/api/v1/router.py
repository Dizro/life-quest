"""роутер API v1 — объединяет все модули эндпоинтов."""

from fastapi import APIRouter

from app.api.v1 import users, tasks, achievements

api_v1_router = APIRouter(tags=["v1"])

api_v1_router.include_router(users.router, prefix="/users", tags=["Пользователи"])
api_v1_router.include_router(tasks.router, prefix="/tasks", tags=["Квесты"])
api_v1_router.include_router(
    achievements.router, prefix="/achievements", tags=["Достижения"]
)
