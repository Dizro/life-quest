"""
Эндпоинты задач (FR-2, FR-6).
Включает: CRUD, complete (с поддержкой Испытаний), redeem, PATCH с защитой.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskCompleteResponse
from app.services.reward_service import (
    calculate_rewards, apply_xp, apply_gold, get_farrix_phrase,
    get_status_mult, calc_habit_tick, apply_habit_plus, apply_habit_minus,
)
from app.services.achievement_service import check_and_unlock_achievements
from app.services.ai_service import get_effort_score
from app.core.config import settings

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Проверка на дубликат по client_id (для offline sync)
    if data.client_id:
        existing = await db.execute(
            select(Task).where(Task.client_id == data.client_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Задача с таким client_id уже существует")

    task = Task(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        task_type=data.task_type,
        category=data.category,
        deadline=data.deadline,
        status="pending_es",
        client_id=data.client_id,
        created_offline=bool(data.client_id),
        client_created_at=data.client_created_at,
    )
    db.add(task)
    await db.flush()

    # Синхронная ИИ-оценка сложности
    try:
        ai_response = await get_effort_score(task.title)
        es = ai_response.effort_score
        task.effort_score = es.value
        task.effort_confidence = es.confidence
        task.effort_reasoning = es.reasoning
        task.complexity_level = es.complexity_level.value
        task.status = "active"
        xp, gold = calculate_rewards(es.value, task.task_type)
        task.xp_reward = xp
        task.gold_reward = gold
    except Exception:
        task.status = "active"
        task.effort_score = settings.AI_DEFAULT_EFFORT_SCORE
        task.complexity_level = settings.AI_DEFAULT_COMPLEXITY
        task.effort_reasoning = settings.AI_DEFAULT_REASONING
        xp, gold = calculate_rewards(task.effort_score, task.task_type)
        task.xp_reward = xp
        task.gold_reward = gold

    await db.commit()
    await db.refresh(task)
    return task


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status: str = None,
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).where(Task.user_id == current_user.id)
    if status:
        query = query.where(Task.status == status)
    if category:
        query = query.where(Task.category == category)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование задачи. В статусе 'trial' текст/описание/deadline ЗАПРЕЩЕНЫ (FR-2.8)."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = data.model_dump(exclude_unset=True)

    # Защита от злоупотреблений: текст испытания нельзя менять
    if task.status == "trial":
        for blocked in ("title", "description", "deadline"):
            if blocked in update_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Нельзя изменить '{blocked}' у задачи в статусе Испытание",
                )

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    await db.delete(task)
    await db.commit()
    return {"success": True}


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Завершить задачу (включая Испытание).
    - Для trial: применяется status_mult, стрик НЕ засчитывается.
    - Для habit: стрик НЕ засчитывается.
    - weekly_xp обновляется.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.status not in ("active", "pending_es", "trial"):
        raise HTTPException(status_code=400, detail=f"Нельзя завершить задачу со статусом {task.status}")

    was_trial = task.status == "trial"
    effort = task.effort_score or 5

    # ── Привычки: отдельная логика с +/− тиками ──────────────────────
    if task.task_type == "habit":
        actual_xp, actual_gold, leveled_up = apply_habit_plus(current_user, effort)
        task.completion_count += 1
        # Показываем за-тик награду на карточке
        tick_xp, tick_gold = calc_habit_tick(effort)
        task.xp_reward = tick_xp
        task.gold_reward = tick_gold
    else:
        # Обычные/daily/trial задачи
        smult = get_status_mult(task)
        xp_raw, gold_raw = calculate_rewards(effort, task.task_type, status_mult=smult)
        actual_xp, leveled_up = apply_xp(current_user, xp_raw)
        actual_gold = apply_gold(current_user, gold_raw)
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        task.xp_reward = actual_xp
        task.gold_reward = actual_gold

    # ── Стрик (раздел 6.7) ────────────────────────────────────────────
    # Испытания и привычки НЕ засчитываются в стрик
    if not was_trial and task.task_type != "habit":
        now_date = datetime.now(timezone.utc).date()
        if current_user.last_activity_date:
            delta = (now_date - current_user.last_activity_date.date()).days
            if delta == 1:
                current_user.streak_days += 1
            elif delta > 1:
                current_user.streak_days = 1
            # delta == 0 → уже засчитано сегодня, не трогаем
        else:
            current_user.streak_days = 1
        current_user.max_streak = max(current_user.max_streak, current_user.streak_days)
        current_user.last_activity_date = datetime.now(timezone.utc)

    await db.flush()

    # Проверка ачивок
    new_achievements = await check_and_unlock_achievements(current_user, db)
    achievement_name = new_achievements[0].name if new_achievements else None

    await db.commit()
    await db.refresh(task)

    return TaskCompleteResponse(
        task=task,
        xp_gained=actual_xp,
        gold_gained=actual_gold,
        leveled_up=leveled_up,
        new_level=current_user.level if leveled_up else None,
        achievement_unlocked=achievement_name,
        farrix_phrase=get_farrix_phrase(
            effort, leveled_up,
            user_name=current_user.display_name or current_user.username,
            task_title=task.title,
        ),
    )


@router.post("/{task_id}/redeem")
async def redeem_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Выкуп Испытания за Gold (FR-6.5).
    Стоимость = ES × 10. Лимит: 3 выкупа в сутки.
    Статус → redeemed, 0 XP, стрик НЕ засчитывается.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.status != "trial":
        raise HTTPException(status_code=400, detail="Выкупить можно только Испытание")

    # Лимит 3 выкупа в сутки
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    redeemed_today = await db.execute(
        select(sql_func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "redeemed",
            Task.completed_at >= today_start,
        )
    )
    count = redeemed_today.scalar() or 0
    if count >= 3:
        raise HTTPException(status_code=400, detail="Лимит выкупа: 3 испытания в сутки")

    # Стоимость = ES × 10
    cost = (task.effort_score or 5) * 10
    if current_user.gold < cost:
        raise HTTPException(status_code=400, detail=f"Недостаточно золота ({cost} Gold)")

    current_user.gold -= cost
    task.status = "redeemed"
    task.completed_at = datetime.now(timezone.utc)
    task.xp_reward = 0
    task.gold_reward = 0

    await db.commit()
    return {
        "success": True,
        "message": f"Испытание искуплено за {cost} Gold",
        "gold_remaining": current_user.gold,
    }


@router.post("/{task_id}/habit-minus")
async def habit_decrement(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Откатить привычку (−1).
    Уменьшает completion_count (минимум 0) и отнимает XP/Gold за 1 тик.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.task_type != "habit":
        raise HTTPException(status_code=400, detail="Только для привычек")
    if task.completion_count <= 0:
        raise HTTPException(status_code=400, detail="Счётчик уже 0")

    effort = task.effort_score or 5
    xp_lost, gold_lost = apply_habit_minus(current_user, effort)
    task.completion_count -= 1

    await db.commit()
    await db.refresh(task)
    return {
        "completion_count": task.completion_count,
        "xp_lost": xp_lost,
        "gold_lost": gold_lost,
    }