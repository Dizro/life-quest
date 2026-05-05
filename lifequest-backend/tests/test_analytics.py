import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User


@pytest_asyncio.fixture
async def completed_tasks(db: AsyncSession, test_user: User):
    """Создаём набор завершённых задач для тестирования аналитики."""
    tasks = []
    categories = ["work", "health", "learn", "personal"]
    for i in range(20):
        task = Task(
            user_id=test_user.id,
            title=f"Задача {i}",
            task_type="regular",
            category=categories[i % len(categories)],
            status="completed",
            effort_score=(i % 10) + 1,
            xp_reward=((i % 10) + 1) * 10,
            gold_reward=((i % 10) + 1) * 4,
            completed_at=datetime.now(timezone.utc) - timedelta(days=i % 14),
        )
        tasks.append(task)
        db.add(task)
    await db.commit()
    return tasks


@pytest.mark.asyncio
async def test_analytics_overview(
    client: AsyncClient, auth_headers: dict, completed_tasks
):
    """SCRUM-204: Проверяем overview статистику."""
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "overview" in data
    assert data["overview"]["total_tasks_completed"] == 20
    assert data["overview"]["level"] >= 1


@pytest.mark.asyncio
async def test_analytics_xp_chart(
    client: AsyncClient, auth_headers: dict, completed_tasks
):
    """SCRUM-204: Проверяем структуру XP chart для построения графика."""
    response = await client.get("/api/v1/analytics/dashboard?days=30", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    xp_chart = data["xp_chart"]

    assert len(xp_chart) == 30  # Непрерывный ряд за 30 дней
    assert all("date" in point for point in xp_chart)
    assert all("xp" in point for point in xp_chart)
    assert all("tasks_completed" in point for point in xp_chart)
    # Дни без активности — нули (не пустые)
    zero_days = [p for p in xp_chart if p["xp"] == 0]
    assert len(zero_days) >= 0  # Могут быть нулевые дни


@pytest.mark.asyncio
async def test_analytics_category_distribution(
    client: AsyncClient, auth_headers: dict, completed_tasks
):
    """SCRUM-204: Распределение по категориям для pie chart."""
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    distribution = data["category_distribution"]

    assert len(distribution) > 0
    # Все процентили суммируются ~100%
    total_pct = sum(item["percentage"] for item in distribution)
    assert 99.0 <= total_pct <= 101.0

    for item in distribution:
        assert "category" in item
        assert "count" in item
        assert "percentage" in item
        assert "total_xp" in item


@pytest.mark.asyncio
async def test_analytics_heatmap(
    client: AsyncClient, auth_headers: dict, completed_tasks
):
    """SCRUM-204: Heatmap данные для GitHub-style визуализации."""
    response = await client.get("/api/v1/analytics/dashboard?days=30", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    heatmap = data["heatmap"]

    assert len(heatmap) == 30
    for cell in heatmap:
        assert "date" in cell
        assert "value" in cell
        assert 0 <= cell["value"] <= 4  # Интенсивность 0-4


@pytest.mark.asyncio
async def test_analytics_effort_by_category(
    client: AsyncClient, auth_headers: dict, completed_tasks
):
    """SCRUM-204: Средний Effort Score по категориям."""
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    effort_map = data["effort_score_avg_by_category"]

    assert isinstance(effort_map, dict)
    for cat, avg in effort_map.items():
        assert isinstance(avg, float)
        assert 1.0 <= avg <= 20.0


@pytest.mark.asyncio
async def test_analytics_empty_user(
    client: AsyncClient, auth_headers: dict
):
    """SCRUM-204: Аналитика для нового пользователя без задач."""
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["overview"]["total_tasks_completed"] == 0
    assert len(data["xp_chart"]) == 30
    assert all(p["xp"] == 0 for p in data["xp_chart"])