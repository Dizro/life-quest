"""
Эндпоинты квестов (задач).
Все операции строго привязаны к текущему авторизованному пользователю.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    TaskCreate, TaskRead, TaskUpdate, TaskComplete, TaskListResponse,
    TaskStatusEnum, TaskCategoryEnum
)
from app.api.dependencies import get_current_user
from app.services.reward_service import calculate_rewards, apply_rewards_and_check_levelup

router = APIRouter()


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="Список моих квестов",
)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[TaskStatusEnum] = Query(None, alias="status"),
    category: Optional[TaskCategoryEnum] = Query(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TaskListResponse:

    query = select(Task).where(Task.owner_id == current_user.id)

    if status_filter:
        query = query.where(Task.status == status_filter.value)
    if category:
        query = query.where(Task.category == category.value)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total_count = total_result.scalar() or 0

    result = await session.execute(query.offset((page - 1) * size).limit(size))
    tasks = result.scalars().all()

    return TaskListResponse(
        total=total_count,
        page=page,
        size=size,
        items=tasks
    )


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый квест",
)
async def create_task(
    body: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TaskRead:

    new_task = Task(
        owner_id=current_user.id,
        title=body.title,
        description=body.description,
        task_type=body.task_type.value,
        priority=body.priority.value,
        category=body.category.value,
        recurrence=body.recurrence.value,
        xp_reward=body.xp_reward,
        coin_reward=body.coin_reward,
        due_date=body.due_date,
    )
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return new_task


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Получить квест",
)
async def get_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TaskRead:

    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Квест не найден или у вас нет доступа")
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Обновить квест",
)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TaskRead:

    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Квест не найден")

    # ⚑ Запрет редактирования текста задачи в статусе «Испытание» (ТЗ §6.6)
    if task.status.value == "trial" and body.title is not None:
        raise HTTPException(
            status_code=400,
            detail="Редактирование текста задачи в статусе «Испытание» запрещено"
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить квест",
    response_class=Response,
)
async def delete_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Квест не найден")

    await session.delete(task)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{task_id}/complete",
    response_model=TaskComplete,
    summary="Выполнить квест",
    description=(
        "Отмечает квест выполненным, начисляет XP и Gold по формуле ТЗ §6.2. "
        "Проверяет повышение уровня. Нельзя выполнить уже выполненный или архивный квест."
    ),
)
async def complete_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TaskComplete:

    # ── найти задачу ──────────────────────────────────────────────────────────
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Квест не найден")

    # ── проверить статус ──────────────────────────────────────────────────────
    if task.status.value in ("completed", "redeemed", "archived"):
        raise HTTPException(
            status_code=400,
            detail=f"Нельзя выполнить квест со статусом «{task.status.value}»"
        )

    # ── рассчитать награду ────────────────────────────────────────────────────
    xp_earned, gold_earned = calculate_rewards(task, current_user)

    # ── обновить задачу ───────────────────────────────────────────────────────
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    session.add(task)

    # ── начислить награду и проверить уровень ─────────────────────────────────
    leveled_up = apply_rewards_and_check_levelup(current_user, xp_earned, gold_earned)
    current_user.last_active_at = datetime.now(timezone.utc)
    session.add(current_user)

    await session.commit()
    await session.refresh(current_user)

    return TaskComplete(
        task_id=task.id,
        xp_earned=xp_earned,
        coins_earned=gold_earned,
        new_total_xp=current_user.experience_points,
        new_level=current_user.level,
        new_rank_title=current_user.rank_title,
        leveled_up=leveled_up,
    )