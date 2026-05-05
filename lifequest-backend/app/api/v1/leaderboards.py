"""
Лидерборды (FR-7.3).

Три независимых лидерборда:
  1. Недельный XP — weekly_xp, сбрасывается каждый понедельник кроном
  2. Текущий стрик — streak_days, не сбрасывается
  3. Кристаллы всего — crystals, никогда не сбрасывается

Карантин 3 дня: новые аккаунты не показываются в лидерборде.
Кэш в Redis: топ не пересчитывается при каждом открытии вкладки.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])

# TTL кэша: 5 минут (лидерборд не требует realtime-точности)
CACHE_TTL_SECONDS = 300
QUARANTINE_DAYS = 3  # FR-7.3: новые аккаунты 3 дня не попадают в топ


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    display_name: Optional[str]
    level: int
    value: int          # Значение метрики (xp / streak / crystals)
    is_current_user: bool = False


class LeaderboardResponse(BaseModel):
    type: str           # "weekly_xp" | "streak" | "crystals"
    entries: List[LeaderboardEntry]
    total_players: int
    current_user_rank: Optional[int]
    updated_at: datetime


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def _build_leaderboard(
    db: AsyncSession,
    order_field,
    leaderboard_type: str,
    limit: int,
    current_user_id: int,
) -> LeaderboardResponse:
    """
    Строит лидерборд напрямую из БД (вызывается при промахе кэша).
    Фильтр карантина: пользователи, зарегистрированные менее 3 дней назад, исключаются.
    """
    quarantine_cutoff = datetime.now(timezone.utc) - timedelta(days=QUARANTINE_DAYS)

    # Топ N записей
    result = await db.execute(
        select(User)
        .where(
            User.is_active == True,
            User.created_at <= quarantine_cutoff,
        )
        .order_by(order_field.desc())
        .limit(limit)
    )
    top_users = result.scalars().all()

    # Общее количество подходящих игроков
    count_result = await db.execute(
        select(sql_func.count(User.id)).where(
            User.is_active == True,
            User.created_at <= quarantine_cutoff,
        )
    )
    total_players = count_result.scalar() or 0

    # Ранг текущего пользователя (оконная функция через подзапрос)
    current_user_rank = None
    if current_user_id:
        rank_result = await db.execute(
            select(sql_func.count(User.id) + 1).where(
                User.is_active == True,
                User.created_at <= quarantine_cutoff,
                order_field > select(order_field).where(User.id == current_user_id).scalar_subquery(),
            )
        )
        current_user_rank = rank_result.scalar() or None

    entries = []
    for rank, user in enumerate(top_users, start=1):
        if leaderboard_type == "weekly_xp":
            value = user.weekly_xp
        elif leaderboard_type == "streak":
            value = user.streak_days
        else:
            value = user.crystals

        entries.append(LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            level=user.level,
            value=value,
            is_current_user=(user.id == current_user_id),
        ))

    return LeaderboardResponse(
        type=leaderboard_type,
        entries=entries,
        total_players=total_players,
        current_user_rank=current_user_rank,
        updated_at=datetime.now(timezone.utc),
    )


@router.get("/weekly-xp", response_model=LeaderboardResponse)
async def get_weekly_xp_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Недельный лидерборд по XP.
    Поле weekly_xp сбрасывается каждый понедельник кроном reset_weekly_xp.
    Кэш в Redis: 5 минут.
    """
    cache_key = f"lb:weekly_xp:{limit}"
    redis = await _get_redis()

    try:
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            response = LeaderboardResponse(**data)
            # Помечаем текущего пользователя
            for entry in response.entries:
                entry.is_current_user = (entry.user_id == current_user.id)
            return response
    except Exception as e:
        logger.warning("Redis cache miss (weekly_xp): %s", e)

    response = await _build_leaderboard(db, User.weekly_xp, "weekly_xp", limit, current_user.id)

    try:
        await redis.setex(cache_key, CACHE_TTL_SECONDS, response.model_dump_json())
    except Exception as e:
        logger.warning("Redis cache write failed: %s", e)
    finally:
        await redis.aclose()

    return response


@router.get("/streak", response_model=LeaderboardResponse)
async def get_streak_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Лидерборд по текущему стрику.
    Не сбрасывается. Показывает кто самый регулярный.
    Кэш: 5 минут.
    """
    cache_key = f"lb:streak:{limit}"
    redis = await _get_redis()

    try:
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            response = LeaderboardResponse(**data)
            for entry in response.entries:
                entry.is_current_user = (entry.user_id == current_user.id)
            return response
    except Exception as e:
        logger.warning("Redis cache miss (streak): %s", e)

    response = await _build_leaderboard(db, User.streak_days, "streak", limit, current_user.id)

    try:
        await redis.setex(cache_key, CACHE_TTL_SECONDS, response.model_dump_json())
    except Exception as e:
        logger.warning("Redis cache write failed: %s", e)
    finally:
        await redis.aclose()

    return response


@router.get("/crystals", response_model=LeaderboardResponse)
async def get_crystals_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Лидерборд по кристаллам (накопленным за всё время).
    Никогда не сбрасывается — престижный рейтинг постоянства.
    Кэш: 5 минут.
    """
    cache_key = f"lb:crystals:{limit}"
    redis = await _get_redis()

    try:
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            response = LeaderboardResponse(**data)
            for entry in response.entries:
                entry.is_current_user = (entry.user_id == current_user.id)
            return response
    except Exception as e:
        logger.warning("Redis cache miss (crystals): %s", e)

    response = await _build_leaderboard(db, User.crystals, "crystals", limit, current_user.id)

    try:
        await redis.setex(cache_key, CACHE_TTL_SECONDS, response.model_dump_json())
    except Exception as e:
        logger.warning("Redis cache write failed: %s", e)
    finally:
        await redis.aclose()

    return response