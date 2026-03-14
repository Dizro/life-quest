"""
Эндпоинты квестов (задач).
Все операции строго привязаны к текущему авторизованному пользователю.
"""

import uuid
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
    
    # Базовый запрос с фильтрацией по владельцу
    query = select(Task).where(Task.owner_id == current_user.id)
    
    if status_filter:
        query = query.where(Task.status == status_filter.value)
    if category:
        query = query.where(Task.category == category.value)
        
    # Подсчет общего количества (для пагинации)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total_count = total_result.scalar() or 0
    
    # Получение элементов страницы
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
        
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if isinstance(value, getattr(TaskStatusEnum, '__class__', type)):
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