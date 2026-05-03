import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import uuid
from typing import AsyncGenerator, Dict

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import async_session_factory
from app.models.user import User
from app.models.task import Task
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="session")
def event_loop():
    """Создаёт event loop для сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для тестирования FastAPI приложения."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_user() -> Dict:
    """Создаёт тестового пользователя в БД и возвращает его данные."""
    async with async_session_factory() as session:
        # Генерируем уникальные данные
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        email = f"{username}@example.com"
        hashed_password = get_password_hash("Test1234!")
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            display_name="Test Hero",
            coins=500,  # достаточно для выкупа
            level=1,
            experience_points=0,
            current_streak=0,
            best_streak=0,
            daily_xp=0,
            daily_gold=0,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {
            "id": user.id,
            "username": username,
            "email": email,
            "password": "Test1234!",
            "access_token": create_access_token(str(user.id)),
        }


@pytest.fixture(scope="function")
async def auth_headers(test_user: Dict) -> Dict[str, str]:
    """Заголовки авторизации с Bearer токеном."""
    token = test_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function", autouse=True)
async def clean_db():
    """Очищает созданные задачи после каждого теста (вручную)."""
    yield
    async with async_session_factory() as session:
        # Удаляем все тестовые задачи (созданные в этом тесте по title)
        await session.execute(
            Task.__table__.delete().where(Task.title.like("test_%"))
        )
        # Удаляем тестовых пользователей (опционально, если нужно)
        # await session.execute(User.__table__.delete().where(User.username.like("testuser_%")))
        await session.commit()