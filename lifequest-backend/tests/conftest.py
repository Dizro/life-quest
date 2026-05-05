import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.task import Task
from app.models.achievement import Achievement
from app.core.security import get_password_hash, create_access_token

# Тестовая БД — SQLite в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    user = User(
        username="test_hero",
        email="hero@lifequest.ru",
        hashed_password=get_password_hash("testpass123"),
        level=5,
        xp=1000,
        gold=500,
        crystals=50,
        streak_days=7,
        max_streak=10,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User) -> dict:
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def sample_task(db: AsyncSession, test_user: User) -> Task:
    task = Task(
        user_id=test_user.id,
        title="Написать unit-тесты для API",
        description="Покрыть все эндпоинты тестами",
        task_type="regular",
        category="work",
        status="active",
        effort_score=8,
        complexity_level="Medium",
        xp_reward=80,
        gold_reward=32,
        client_id="test-client-001",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@pytest_asyncio.fixture(scope="function")
async def seed_achievements(db: AsyncSession):
    """Наполняем БД стандартными достижениями."""
    achievements = [
        Achievement(
            key="first_quest",
            name="Первый шаг",
            description="Выполнена первая задача",
            icon="⭐",
            condition_type="tasks_count",
            condition_value=1,
            crystal_reward=1,
        ),
        Achievement(
            key="week_streak",
            name="Неделя огня",
            description="7 дней стрика",
            icon="🔥",
            condition_type="streak_days",
            condition_value=7,
            crystal_reward=3,
        ),
        Achievement(
            key="century",
            name="Сотня",
            description="100 выполненных квестов",
            icon="💯",
            condition_type="tasks_count",
            condition_value=100,
            crystal_reward=10,
        ),
    ]
    for ach in achievements:
        db.add(ach)
    await db.commit()
    return achievements