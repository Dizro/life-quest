"""
Эндпоинты квестов (задач).
Все операции строго привязаны к текущему авторизованному пользователю.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.task import Task
from app.models.user import User
from app.schemas.task import (
    TaskCreate, TaskRead, TaskUpdate, TaskComplete, TaskListResponse,
    SubtaskCreate, TaskStatusEnum, TaskCategoryEnum
)

from app.api.dependencies import get_current_user
from app.services.reward_service import calculate_rewards, apply_rewards_and_check_levelup
from app.services.achievement_service import check_and_grant_achievements
from app.services.ai_service import should_reevaluate
from app.tasks.celery_tasks import evaluate_es_task

from app.core.limiter import limiter

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
    description=(
        "Создаёт квест и запускает асинхронную оценку Effort Score через YandexGPT (§7.1). "
        "Задача сохраняется сразу, ES придёт через Celery-воркер (≤3 сек)."
    ),
)
@limiter.limit("100/minute")
async def create_task(
    request: Request,
    body: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TaskRead:

    # ── Проверка лимита: не более 500 активных задач (FR-2.9) ─────────────────
    active_count = await session.execute(
        select(func.count()).select_from(Task).where(
            Task.owner_id == current_user.id,
            Task.status.in_(["active", "pending_es", "trial"])
        )
    )
    if (active_count.scalar() or 0) >= 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Превышен лимит в 500 активных задач"
        )
        
    # ── Проверка Слой 0: Дубликат названия за 24ч ────────────────────────────
    now_utc = datetime.now(timezone.utc)
    day_ago = now_utc - timedelta(hours=24)
    duplicate = await session.execute(
        select(Task.id).where(
            Task.owner_id == current_user.id,
            Task.title == body.title,
            Task.created_at >= day_ago
        ).limit(1)
    )
    if duplicate.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Точный дубликат задачи за последние 24 часа. Сформулируйте иначе."
        )

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
        effort_score=None,  # будет заполнен Celery-воркером после ИИ-оценки
        status="pending_es",  # BPMN: ожидает ИИ-оценки ES
    )
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # ── Слой 1: запускаем асинхронную ИИ-оценку ES (BPMN: задача → Celery → YandexGPT)
    evaluate_es_task.delay(str(new_task.id), new_task.title)

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

@router.post(
    "/{task_id}/subtasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать подзадачу",
    description="Добавляет подзадачу к существующему квесту (родительской задаче)."
)
async def create_subtask(
    task_id: uuid.UUID,
    body: SubtaskCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    # Проверяем, существует ли родительская задача
    parent_result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Родительский квест не найден")

    # Запрещаем создание подзадач для уже завершённых или архивных задач
    if parent.status.value in ("completed", "redeemed", "archived"):
        raise HTTPException(
            status_code=400,
            detail="Нельзя добавить подзадачу к завершённому или архивному квесту"
        )

    # Проверка на максимальную глубину вложенности (допустим один уровень)
    if parent.parent_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Подзадача не может иметь свои подзадачи (поддерживается только один уровень вложенности)"
        )

    # Создаём подзадачу
    new_subtask = Task(
        owner_id=current_user.id,
        parent_id=parent.id,
        title=body.title,
        description=body.description,
        task_type=body.task_type.value,
        priority=body.priority.value,
        category=body.category.value,
        recurrence=body.recurrence.value,
        xp_reward=body.xp_reward,
        coin_reward=body.coin_reward,
        due_date=body.due_date,
        effort_score=None,          # будет оценён Celery-воркером
        status="pending_es",
    )
    session.add(new_subtask)
    await session.commit()
    await session.refresh(new_subtask)

    # Запускаем асинхронную оценку ES (если нужно)
    from app.tasks.celery_tasks import evaluate_es_task
    evaluate_es_task.delay(str(new_subtask.id), new_subtask.title)

    return new_subtask

@router.get(
    "/{task_id}/subtasks",
    response_model=list[TaskRead],
    summary="Получить подзадачи",
    description="Возвращает все подзадачи указанного квеста."
)
async def get_subtasks(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[TaskRead]:
    result = await session.execute(
        select(Task).where(Task.parent_id == task_id, Task.owner_id == current_user.id)
    )
    subtasks = result.scalars().all()
    return subtasks

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

    # ⚑ Запрет редактирования текста и срока задачи в статусе «Испытание»
    if task.status.value == "trial":
        if any(v is not None for v in [body.title, body.description, body.due_date]):
            raise HTTPException(
                status_code=400,
                detail="Редактирование названия, описания и срока запрещено в статусе «Испытание»"
            )

    # Запоминаем старый title для проверки кэша ES (§7.3)
    old_title = task.title

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # ── Пересчёт ES при изменении текста >20% (§7.3, FR-3.4)
    # Если текст изменён менее чем на 20% символов — кэшированный ES остаётся
    if (
        body.title is not None
        and task.status.value != "trial"
        and should_reevaluate(old_title, task.title)
    ):
        evaluate_es_task.delay(str(task.id), task.title)

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
@limiter.limit("100/minute")
async def complete_task(
    request: Request,
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
    if task.status.value == "pending_es":
        raise HTTPException(
            status_code=400,
            detail="Квест ещё ожидает ИИ-оценки сложности. Попробуйте через несколько секунд."
        )
    if task.status.value in ("completed", "redeemed", "archived"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Нельзя выполнить квест со статусом «{task.status.value}»"
        )

    # ── Слой 2: Агрегация дневных наград ──────────────────────────────────────
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    totals_query = select(
        func.sum(Task.xp_reward).label("total_xp"),
        func.sum(Task.coin_reward).label("total_gold")
    ).where(
        Task.owner_id == current_user.id,
        Task.status == "completed",
        Task.completed_at >= today_start
    )
    totals_res = (await session.execute(totals_query)).first()
    today_xp = totals_res.total_xp or 0
    today_gold = totals_res.total_gold or 0
    
    habit_query = select(func.sum(Task.xp_reward)).where(
        Task.owner_id == current_user.id,
        Task.status == "completed",
        Task.task_type == "habit",
        Task.completed_at >= today_start
    )
    today_habit_xp = (await session.execute(habit_query)).scalar() or 0

    # ── рассчитать награду ────────────────────────────────────────────────────
    xp_earned, gold_earned = calculate_rewards(
        task, 
        current_user,
        today_xp=today_xp,
        today_gold=today_gold,
        today_habit_xp=today_habit_xp
    )

    # ── обновить задачу ───────────────────────────────────────────────────────
    is_trial = (task.status.value == "trial")
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    task.xp_reward = xp_earned      # Сохраняем реальную полученную награду
    task.coin_reward = gold_earned  # для агрегации потолка
    session.add(task)

    # ── начисление стрика ─────────────────────────────────────────────────────
    if task.task_type.value == "daily" and not is_trial:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today_query = select(Task.id).where(
            Task.owner_id == current_user.id,
            Task.task_type == "daily",
            Task.status == "completed",
            Task.completed_at >= today_start,
            Task.id != task.id
        ).limit(1)
        already_completed = (await session.execute(completed_today_query)).first()

        if not already_completed:
            current_user.current_streak += 1
            if current_user.current_streak > current_user.best_streak:
                current_user.best_streak = current_user.current_streak
    
    # Если завершённая задача является подзадачей (имеет parent_id)
    if task.parent_id is not None:
        # Загружаем родительскую задачу
        parent_result = await session.execute(
            select(Task).where(Task.id == task.parent_id, Task.owner_id == current_user.id)
        )
        parent = parent_result.scalar_one_or_none()
        
        if parent and parent.status.value not in ("completed", "redeemed", "archived"):
            # Загружаем все подзадачи этой родительской задачи
            subtasks_result = await session.execute(
                select(Task).where(Task.parent_id == parent.id)
            )
            all_subtasks = subtasks_result.scalars().all()
            
            # Проверяем, все ли подзадачи уже имеют статус "completed"
            all_completed = all(st.status == "completed" for st in all_subtasks)
            
            if all_completed:
                # Суммируем XP и Gold всех подзадач
                total_xp = sum(st.xp_reward for st in all_subtasks)
                total_gold = sum(st.coin_reward for st in all_subtasks)
                
                # Бонус = 20% от суммы
                bonus_xp = int(total_xp * 0.2)
                bonus_gold = int(total_gold * 0.2)
                
                # Завершаем родительскую задачу
                parent.status = "completed"
                parent.completed_at = datetime.now(timezone.utc)
                parent.xp_reward = bonus_xp
                parent.coin_reward = bonus_gold
                session.add(parent)
                
                # Добавляем бонус к награде текущего выполнения (чтобы пользователь его получил)
                xp_earned += bonus_xp
                gold_earned += bonus_gold

    # ── начислить награду и проверить уровень ─────────────────────────────────
    leveled_up = apply_rewards_and_check_levelup(current_user, xp_earned, gold_earned)
    # ── проверка выдачи достижений ────────────────────────────────────────────
    unlocked_ach = await check_and_grant_achievements(
        session=session,
        user=current_user,
        is_trial_completed=is_trial,
        task_completed=True,
    )

    # ── генерация комментария Фаррикса (заглушка/MVP) ─────────────────────────
    farrix_comment = None
    if task.effort_score == 0:
        farrix_comment = "Можешь обманывать себя, но Фаррикса не проведешь. Оценка: спам. Награда: 0."
    elif task.effort_score is not None and task.effort_score >= 6:
        farrix_comment = "Отличная работа! Это был трудный квест, но ты справился блестяще!"
    elif xp_earned > 0: # если это не спам-задача
        farrix_comment = "Молодец! Ещё один шаг к величию!"

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
        achievement_unlocked=",".join(unlocked_ach) if unlocked_ach else None,
        farrix_comment=farrix_comment,
    )


@router.post(
    "/{task_id}/redeem",
    summary="Выкупить квест за монеты",
    description="Выкупает просроченную задачу (испытание) за Gold. Лимит: 3 раза в сутки.",
)
async def redeem_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Квест не найден")
        
    if task.status.value != "trial":
        raise HTTPException(status_code=400, detail="Можно выкупить только квест в статусе «Испытание»")
        
    # Проверка лимита: 3 выкупа в сутки
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    redeem_count_res = await session.execute(
        select(func.count()).select_from(Task).where(
            Task.owner_id == current_user.id,
            Task.status == "redeemed",
            Task.updated_at >= today_start
        )
    )
    count = redeem_count_res.scalar() or 0
    if count >= 3:
        raise HTTPException(status_code=400, detail="Достигнут дневной лимит: не более 3 выкупов в сутки")
        
    es = task.effort_score if task.effort_score is not None else 5
    cost = es * 10
    
    if current_user.coins < cost:
        raise HTTPException(status_code=400, detail=f"Недостаточно монет для выкупа (нужно {cost} Gold)")
        
    current_user.coins -= cost
    task.status = "redeemed"
    # task.updated_at обновится автоматически
    
    session.add(current_user)
    session.add(task)
    await session.commit()
    await session.refresh(current_user)
    
    return {
        "task_id": task.id,
        "redeemed": True,
        "cost": cost,
        "remaining_coins": current_user.coins
    }
