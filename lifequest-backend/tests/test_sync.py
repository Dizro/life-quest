import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task
from app.models.user import User


@pytest.mark.asyncio
async def test_sync_create_task(client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
    """SCRUM-207: Создание задачи через офлайн-синхронизацию."""
    payload = {
        "actions": [
            {
                "action_type": "CREATE_TASK",
                "client_task_id": "offline-uuid-001",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "title": "Задача, созданная офлайн",
                    "description": "Создана без интернета",
                    "task_type": "regular",
                    "category": "work",
                },
            }
        ]
    }
    response = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["processed"] == 1
    assert data["succeeded"] == 1
    assert data["failed"] == 0
    assert data["results"][0]["success"] is True
    assert data["results"][0]["server_task_id"] is not None

    # Проверяем, что задача в БД
    task_id = data["results"][0]["server_task_id"]
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    assert task is not None
    assert task.title == "Задача, созданная офлайн"
    assert task.created_offline is True
    assert task.client_id == "offline-uuid-001"


@pytest.mark.asyncio
async def test_sync_idempotent_create(client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User):
    """SCRUM-207: Повторная синхронизация не создаёт дубликат."""
    action = {
        "action_type": "CREATE_TASK",
        "client_task_id": "offline-uuid-idem",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": {"title": "Идемпотентная задача", "task_type": "regular", "category": "personal"},
    }
    payload = {"actions": [action]}

    # Первый запрос
    r1 = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert r1.status_code == 200

    # Второй запрос с тем же client_task_id
    r2 = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert r2.status_code == 200

    data = r2.json()
    # Должно быть: success=True, conflict=True (ALREADY_EXISTS)
    assert data["results"][0]["conflict"] is True

    # Проверяем, что задача в БД одна
    result = await db.execute(
        select(Task).where(Task.client_id == "offline-uuid-idem")
    )
    tasks = result.scalars().all()
    assert len(tasks) == 1


@pytest.mark.asyncio
async def test_sync_complete_task(
    client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User, sample_task: Task
):
    """SCRUM-207: Завершение задачи через офлайн-синхронизацию."""
    payload = {
        "actions": [
            {
                "action_type": "COMPLETE_TASK",
                "client_task_id": sample_task.client_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {},
            }
        ]
    }
    response = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["results"][0]["success"] is True

    await db.refresh(sample_task)
    assert sample_task.status == "completed"


@pytest.mark.asyncio
async def test_sync_conflict_server_newer(
    client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User, sample_task: Task
):
    """SCRUM-207: Конфликт — серверные данные новее клиентских."""
    # Устанавливаем updated_at в будущем (сервер обновился позже)
    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    sample_task.updated_at = future_time
    await db.commit()

    old_timestamp = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    payload = {
        "actions": [
            {
                "action_type": "COMPLETE_TASK",
                "client_task_id": sample_task.client_id,
                "timestamp": old_timestamp,
                "payload": {},
            }
        ]
    }
    response = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["results"][0]["conflict"] is True
    assert "SERVER_DATA_NEWER" in (data["results"][0]["conflict_reason"] or "")


@pytest.mark.asyncio
async def test_sync_batch_multiple_actions(
    client: AsyncClient, auth_headers: dict, db: AsyncSession, test_user: User
):
    """SCRUM-207: Пакетная обработка нескольких действий."""
    base_time = datetime.now(timezone.utc)
    payload = {
        "actions": [
            {
                "action_type": "CREATE_TASK",
                "client_task_id": f"batch-task-{i}",
                "timestamp": (base_time + timedelta(seconds=i)).isoformat(),
                "payload": {
                    "title": f"Задача {i}",
                    "task_type": "regular",
                    "category": "work",
                },
            }
            for i in range(5)
        ]
    }
    response = await client.post("/api/v1/sync/offline", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["processed"] == 5
    assert data["succeeded"] == 5
    assert data["failed"] == 0