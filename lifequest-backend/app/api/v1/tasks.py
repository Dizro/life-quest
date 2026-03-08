"""
Mock-эндпоинты квестов (задач).
Возвращают захардкоженные данные, чтобы фронтенд мог начать интеграцию сразу.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskComplete,
    TaskListResponse,
    TaskStatusEnum,
    TaskPriorityEnum,
    TaskCategoryEnum,
    TaskRecurrenceEnum,
)

router = APIRouter()

# ── тестовые данные ──────────────────────────────────────────

_MOCK_USER_ID = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
_NOW = datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc)

_MOCK_TASKS: list = [
    TaskRead(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        owner_id=_MOCK_USER_ID,
        title="Утренняя медитация",
        description="15 минут осознанного дыхания перед завтраком",
        status=TaskStatusEnum.COMPLETED,
        priority=TaskPriorityEnum.COMMON,
        category=TaskCategoryEnum.HEALTH,
        recurrence=TaskRecurrenceEnum.DAILY,
        xp_reward=10,
        coin_reward=1,
        due_date=None,
        completed_at=_NOW,
        created_at=_NOW,
        updated_at=_NOW,
    ),
    TaskRead(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        owner_id=_MOCK_USER_ID,
        title="Закончить отчёт по проекту",
        description="Подготовить финальный отчёт и отправить руководителю",
        status=TaskStatusEnum.ACTIVE,
        priority=TaskPriorityEnum.RARE,
        category=TaskCategoryEnum.WORK,
        recurrence=TaskRecurrenceEnum.NONE,
        xp_reward=50,
        coin_reward=5,
        due_date=datetime(2026, 3, 10, 23, 59, 59, tzinfo=timezone.utc),
        completed_at=None,
        created_at=_NOW,
        updated_at=_NOW,
    ),
    TaskRead(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        owner_id=_MOCK_USER_ID,
        title="Освоить систему дизайна",
        description="Изучить Figma-токены и компоненты UI-кита",
        status=TaskStatusEnum.ACTIVE,
        priority=TaskPriorityEnum.EPIC,
        category=TaskCategoryEnum.STUDY,
        recurrence=TaskRecurrenceEnum.NONE,
        xp_reward=200,
        coin_reward=20,
        due_date=datetime(2026, 3, 15, 23, 59, 59, tzinfo=timezone.utc),
        completed_at=None,
        created_at=_NOW,
        updated_at=_NOW,
    ),
    TaskRead(
        id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
        owner_id=_MOCK_USER_ID,
        title="Ревью Pull Requests команды",
        description=None,
        status=TaskStatusEnum.ACTIVE,
        priority=TaskPriorityEnum.UNCOMMON,
        category=TaskCategoryEnum.WORK,
        recurrence=TaskRecurrenceEnum.DAILY,
        xp_reward=30,
        coin_reward=3,
        due_date=None,
        completed_at=None,
        created_at=_NOW,
        updated_at=_NOW,
    ),
]


# ── эндпоинты ───────────────────────────────────────────────

@router.get(
    "/",
    response_model=TaskListResponse,
    summary="Список квестов",
    description=(
        "Возвращает постраничный список квестов текущего пользователя. "
        "Поддерживает фильтрацию по статусу и категории."
    ),
)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[TaskStatusEnum] = Query(None, alias="status"),
    category: Optional[TaskCategoryEnum] = Query(None),
) -> TaskListResponse:
    filtered = _MOCK_TASKS
    if status_filter is not None:
        filtered = [t for t in filtered if t.status == status_filter]
    if category is not None:
        filtered = [t for t in filtered if t.category == category]
    return TaskListResponse(
        total=len(filtered),
        page=page,
        size=size,
        items=filtered,
    )


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый квест",
    description="Принимает данные квеста и возвращает созданную запись.",
)
async def create_task(body: TaskCreate) -> TaskRead:
    new_id = uuid.uuid4()
    return TaskRead(
        id=new_id,
        owner_id=_MOCK_USER_ID,
        title=body.title,
        description=body.description,
        status=TaskStatusEnum.ACTIVE,
        priority=body.priority,
        category=body.category,
        recurrence=body.recurrence,
        xp_reward=body.xp_reward,
        coin_reward=body.coin_reward,
        due_date=body.due_date,
        completed_at=None,
        created_at=_NOW,
        updated_at=_NOW,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Получить квест по ID",
    description="Возвращает данные одного квеста по его UUID.",
)
async def get_task(task_id: uuid.UUID) -> TaskRead:
    for t in _MOCK_TASKS:
        if t.id == task_id:
            return t
    raise HTTPException(status_code=404, detail="Квест не найден")


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Обновить квест",
    description="Частичное обновление полей квеста.",
)
async def update_task(task_id: uuid.UUID, body: TaskUpdate) -> TaskRead:
    for t in _MOCK_TASKS:
        if t.id == task_id:
            data = t.model_dump()
            update = body.model_dump(exclude_unset=True)
            data.update(update)
            return TaskRead(**data)
    raise HTTPException(status_code=404, detail="Квест не найден")


@router.post(
    "/{task_id}/complete",
    response_model=TaskComplete,
    summary="Выполнить квест",
    description=(
        "Отмечает квест как выполненный. Возвращает полученные ОП, монеты, "
        "новый уровень, звание и разблокированное достижение (если есть)."
    ),
)
async def complete_task(task_id: uuid.UUID) -> TaskComplete:
    for t in _MOCK_TASKS:
        if t.id == task_id:
            return TaskComplete(
                task_id=t.id,
                xp_earned=t.xp_reward,
                coins_earned=t.coin_reward,
                new_total_xp=135 + t.xp_reward,
                new_level=2,
                new_rank_title="Путешественник",
                achievement_unlocked=None,
            )
    raise HTTPException(status_code=404, detail="Квест не найден")


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить квест",
    description="Удаляет квест по UUID. Операция необратима.",
    response_class=Response,
)
async def delete_task(task_id: uuid.UUID):
    for t in _MOCK_TASKS:
        if t.id == task_id:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Квест не найден")
