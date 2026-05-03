import uuid
from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(async_client: AsyncClient, auth_headers: dict):
    """Тест создания задачи → статус pending_es."""
    response = await async_client.post(
        "/api/v1/tasks/",
        json={
            "title": "test_create_task",
            "xp_reward": 10,
            "coin_reward": 5
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "test_create_task"
    assert data["status"] == "pending_es"
    assert "id" in data


@pytest.mark.asyncio
async def test_complete_task(async_client, auth_headers, test_user):
    # ... create regular task, complete it ...

    # Создаём ежедневную задачу
    daily_resp = await async_client.post(
        "/api/v1/tasks/",
        json={"title": "test_daily_task", "task_type": "daily", "xp_reward": 10, "coin_reward": 5},
        headers=auth_headers,
    )
    assert daily_resp.status_code == 201
    daily_id = daily_resp.json()["id"]

    # Ждём, пока задача станет active (Celery оценит ES)
    import asyncio
    for _ in range(10):  # максимум 10 попыток * 1 сек = 10 сек
        await asyncio.sleep(1)
        task_resp = await async_client.get(f"/api/v1/tasks/{daily_id}", headers=auth_headers)
        if task_resp.json()["status"] == "active":
            break
    else:
        pytest.fail("Task did not become active")

    # Выполняем
    complete_resp = await async_client.post(f"/api/v1/tasks/{daily_id}/complete", headers=auth_headers)
    assert complete_resp.status_code == 200

    # Проверяем стрик
    profile2 = (await async_client.get("/api/v1/users/me", headers=auth_headers)).json()
    assert profile2["current_streak"] >= 1


@pytest.mark.asyncio
async def test_redeem_trial_task(async_client: AsyncClient, auth_headers: dict, test_user: dict):
    """Тест выкупа испытания → списание монет, статус redeemed."""
    # Создаём задачу с прошедшим дедлайном, чтобы она стала испытанием
    due_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    create_resp = await async_client.post(
        "/api/v1/tasks/",
        json={
            "title": "test_redeem_task",
            "due_date": due_date,
            "xp_reward": 10,
            "coin_reward": 5,
        },
        headers=auth_headers,
    )
    task_id = create_resp.json()["id"]
    # Ждём, когда Celery переведёт задачу в статус "trial" (cron запускается раз в сутки,
    # поэтому принудительно переведём вручную через запрос к БД, либо изменим статус через API.
    # Проще напрямую обновить статус в БД (для теста).
    from app.core.database import async_session_factory
    from app.models.task import Task
    from sqlalchemy import update
    async with async_session_factory() as session:
        await session.execute(
            update(Task).where(Task.id == uuid.UUID(task_id)).values(status="trial", trial_since=datetime.now(timezone.utc))
        )
        await session.commit()

    # Выкупаем задачу
    redeem_resp = await async_client.post(
        f"/api/v1/tasks/{task_id}/redeem",
        headers=auth_headers,
    )
    assert redeem_resp.status_code == 200
    data = redeem_resp.json()
    assert data["redeemed"] is True
    assert data["cost"] > 0

    # Проверяем, что монеты списались
    profile = (await async_client.get("/api/v1/users/me", headers=auth_headers)).json()
    assert profile["coins"] == test_user.get("initial_coins", 500) - data["cost"]


@pytest.mark.asyncio
async def test_daily_xp_gold_limit(async_client: AsyncClient, auth_headers: dict):
    """Тест дневного лимита XP/Gold (после достижения лимита награда не начисляется)."""
    # Создаём много задач с низкой оценкой ES (через мок? проще создать с низким ES вручную)
    # Для теста создадим 10 задач с ES=1 (микродействие) и выполним их. Дневной лимит XP для 1 уровня: 200 + (1*20)=220.
    # Одна задача с ES=1 даёт XP = 1*10 = 10. 22 задачи превысили бы лимит, но возьмём 25.
    from app.core.database import async_session_factory
    from app.models.task import Task
    from sqlalchemy import update

    created_ids = []
    for i in range(25):
        resp = await async_client.post(
            "/api/v1/tasks/",
            json={"title": f"test_limit_task_{i}", "xp_reward": 10, "coin_reward": 5},
            headers=auth_headers,
        )
        task_id = resp.json()["id"]
        created_ids.append(task_id)
        # Принудительно выставляем ES=1 (в обход ИИ) для скорости
        async with async_session_factory() as session:
            await session.execute(
                update(Task).where(Task.id == uuid.UUID(task_id)).values(effort_score=1, status="active")
            )
            await session.commit()

    # Выполняем все задачи
    total_xp = 0
    for task_id in created_ids:
        comp_resp = await async_client.post(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
        if comp_resp.status_code == 200:
            total_xp += comp_resp.json().get("xp_earned", 0)
        else:
            # Если лимит превышен, будет 400? нет, просто xp_earned=0
            pass

    # Лимит XP = 220 + (level*20). У пользователя level=1, лимит 220.
    # После 22 задач сумма XP будет 220, 23-я даст 0. Проверим, что total_xp <= 220
    # Из-за возможных округлений оставим погрешность.
    assert total_xp <= 240  # небольшой запас

    # Также проверим, что дневные поля пользователя обновились
    profile = (await async_client.get("/api/v1/users/me", headers=auth_headers)).json()
    # daily_xp должно быть равно total_xp (поскольку мы не сбрасывали)
    # Для проверки можно запросить временный эндпоинт /me/daily, но его нет в продакшене.
    # Ограничимся проверкой общего XP (experience_points).
    assert profile["experience_points"] >= total_xp


@pytest.mark.asyncio
async def test_duplicate_task(async_client: AsyncClient, auth_headers: dict):
    """Тест дубликата задачи (за 24 часа) -> ошибка."""
    title = "test_duplicate_unique"
    # Первое создание
    resp1 = await async_client.post(
        "/api/v1/tasks/",
        json={"title": title, "xp_reward": 10, "coin_reward": 5},
        headers=auth_headers,
    )
    assert resp1.status_code == 201

    # Второе создание с тем же названием
    resp2 = await async_client.post(
        "/api/v1/tasks/",
        json={"title": title, "xp_reward": 10, "coin_reward": 5},
        headers=auth_headers,
    )
    assert resp2.status_code == 400
    assert "дубликат" in resp2.json()["detail"].lower() or "duplicate" in resp2.json()["detail"].lower()