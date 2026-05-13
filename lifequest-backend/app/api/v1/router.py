from fastapi import APIRouter

from app.api.v1 import auth, users, tasks, analytics, leaderboards, chat, equipment, sync, shop, groups

api_router = APIRouter(prefix="/api/v1")

# Авторизация
api_router.include_router(auth.router)

# Пользователи
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Остальные модули
api_router.include_router(tasks.router)
api_router.include_router(analytics.router)
api_router.include_router(leaderboards.router)
api_router.include_router(chat.router)
api_router.include_router(equipment.router)
api_router.include_router(shop.router)
api_router.include_router(groups.router)
api_router.include_router(sync.router)