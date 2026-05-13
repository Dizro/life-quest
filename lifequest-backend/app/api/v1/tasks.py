from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskCompleteResponse
from app.services.reward_service import calculate_rewards, apply_xp, get_farrix_phrase
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
    await db.flush()  # Получаем id

    # Синхронная ИИ-оценка сложности (убрали Celery для Render Free tier)
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


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
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
    if task.status not in ("active", "pending_es"):
        raise HTTPException(status_code=400, detail=f"Нельзя завершить задачу со статусом {task.status}")

    effort = task.effort_score or 5
    xp_raw, gold = calculate_rewards(effort, task.task_type)
    actual_xp, leveled_up = apply_xp(current_user, xp_raw)

    current_user.gold += gold
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    task.xp_reward = actual_xp
    task.gold_reward = gold

    # Стрик
    now = datetime.now(timezone.utc).date()
    if current_user.last_activity_date:
        delta = (now - current_user.last_activity_date.date()).days
        if delta == 1:
            current_user.streak_days += 1
        elif delta > 1:
            current_user.streak_days = 1
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
        gold_gained=gold,
        leveled_up=leveled_up,
        new_level=current_user.level if leveled_up else None,
        achievement_unlocked=achievement_name,
        farrix_phrase=get_farrix_phrase(effort, leveled_up),
    )