"""
Аналитика (FR-7.1, FR-7.2, UC-20, UC-21).

Эндпоинты:
  GET /analytics/dashboard — полный дашборд: тепловая карта, XP-чарт, распределение по категориям
"""

from datetime import date, datetime, timezone, timedelta
from typing import List, Dict
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.analytics import (
    AnalyticsDashboardResponse, StatsOverview, DailyXPPoint,
    CategoryDistribution, HeatmapCell,
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Полный дашборд аналитики.
    Возвращает: обзор, XP-чарт за 30 дней, тепловая карта за год, распределение по категориям.
    """
    now_utc = datetime.now(timezone.utc)
    year_ago = now_utc - timedelta(days=365)
    month_ago = now_utc - timedelta(days=30)

    # Все выполненные задачи за последний год
    result = await db.execute(
        select(Task).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.completed_at >= year_ago,
        )
    )
    completed_tasks = result.scalars().all()

    # Общее количество задач
    total_result = await db.execute(
        select(sql_func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
        )
    )
    total_tasks = total_result.scalar() or 0

    # Средний ES
    avg_es_result = await db.execute(
        select(sql_func.avg(Task.effort_score)).where(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.effort_score.isnot(None),
        )
    )
    avg_es = avg_es_result.scalar()

    # ── StatsOverview ─────────────────────────────────────────────
    overview = StatsOverview(
        total_xp=current_user.xp,
        total_tasks_completed=total_tasks,
        current_streak=current_user.streak_days,
        max_streak=current_user.max_streak,
        level=current_user.level,
        gold=current_user.gold,
        crystals=current_user.crystals,
        avg_effort_score=round(float(avg_es), 2) if avg_es else None,
    )

    # ── XP-чарт за 30 дней ───────────────────────────────────────
    xp_by_day: Dict[date, int] = defaultdict(int)
    tasks_by_day: Dict[date, int] = defaultdict(int)

    for task in completed_tasks:
        if task.completed_at and task.completed_at >= month_ago:
            day = task.completed_at.date()
            xp_by_day[day] += (task.xp_reward or 0)
            tasks_by_day[day] += 1

    xp_chart = []
    for i in range(30, -1, -1):
        d = (now_utc - timedelta(days=i)).date()
        xp_chart.append(DailyXPPoint(
            date=d,
            xp=xp_by_day.get(d, 0),
            tasks_completed=tasks_by_day.get(d, 0),
        ))

    # ── Тепловая карта за год ─────────────────────────────────────
    heatmap_by_day: Dict[date, int] = defaultdict(int)
    for task in completed_tasks:
        if task.completed_at:
            heatmap_by_day[task.completed_at.date()] += 1

    heatmap = []
    for i in range(365, -1, -1):
        d = (now_utc - timedelta(days=i)).date()
        count = heatmap_by_day.get(d, 0)
        # Intensity 0-4 (как GitHub)
        intensity = min(4, count)
        heatmap.append(HeatmapCell(date=d, value=intensity))

    # ── Распределение по категориям ───────────────────────────────
    cat_result = await db.execute(
        select(
            Task.category,
            sql_func.count(Task.id).label("count"),
            sql_func.sum(Task.xp_reward).label("total_xp"),
            sql_func.avg(Task.effort_score).label("avg_es"),
        )
        .where(
            Task.user_id == current_user.id,
            Task.status == "completed",
        )
        .group_by(Task.category)
    )
    cat_rows = cat_result.fetchall()

    category_distribution = []
    effort_by_category: Dict[str, float] = {}
    total_cat_count = sum(row.count for row in cat_rows) or 1

    for row in cat_rows:
        category_distribution.append(CategoryDistribution(
            category=row.category,
            count=row.count,
            percentage=round(row.count / total_cat_count * 100, 1),
            total_xp=row.total_xp or 0,
        ))
        if row.avg_es:
            effort_by_category[row.category] = round(float(row.avg_es), 2)

    return AnalyticsDashboardResponse(
        overview=overview,
        xp_chart=xp_chart,
        category_distribution=category_distribution,
        heatmap=heatmap,
        effort_score_avg_by_category=effort_by_category,
    )