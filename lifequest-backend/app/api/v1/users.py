"""
Эндпоинты пользователей.
Реализована безопасная регистрация и работа с профилем через JWT-токен.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.user_buff import UserBuff
from app.models.task import Task
from app.models.user_achievement import UserAchievement
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserProfile
from app.api.dependencies import get_current_user
from datetime import datetime, timezone, timedelta

router = APIRouter()


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создаёт аккаунт игрока с хешированием пароля и сохраняет в БД."
)
async def create_user(
    body: UserCreate, 
    session: AsyncSession = Depends(get_async_session)
) -> UserRead:
    # Проверка уникальности логина и email
    query = select(User).where((User.username == body.username) | (User.email == body.email))
    result = await session.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь с таким логином или email уже существует"
        )
    
    # Создание пользователя (FR-1.5: стартовый капитал 50 монет)
    now_utc = datetime.now(timezone.utc)
    new_user = User(
        username=body.username,
        email=body.email,
        hashed_password=get_password_hash(body.password),
        display_name=body.display_name,
        coins=50,
        last_active_at=now_utc
    )
    session.add(new_user)
    await session.flush()
    
    # Стартовый бафф х2.0 XP на 3 дня
    start_buff = UserBuff(
        user_id=new_user.id,
        buff_type="xp_boost",
        multiplier=2.0,
        expires_at=now_utc + timedelta(days=3)
    )
    session.add(start_buff)
    
    await session.commit()
    await session.refresh(new_user)
    
    return new_user


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Профиль героя (Мой)",
    description="Возвращает расширенный профиль текущего авторизованного пользователя."
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserProfile:
    """
    Возвращает профиль текущего пользователя с реальной статистикой:
    - количество выполненных задач
    - количество полученных достижений
    """
    
    # 1. Количество выполненных задач (quests_completed)
    tasks_result = await session.execute(
        select(func.count()).select_from(Task).where(
            Task.owner_id == current_user.id,
            Task.status == "completed"
        )
    )
    quests_completed = tasks_result.scalar() or 0
    
    # 2. Количество полученных достижений (achievements_count)
    achievements_result = await session.execute(
        select(func.count()).select_from(UserAchievement).where(
            UserAchievement.user_id == current_user.id
        )
    )
    achievements_count = achievements_result.scalar() or 0
    
    # 3. Возвращаем профиль с реальными значениями
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        level=current_user.level,
        experience_points=current_user.experience_points,
        coins=current_user.coins,
        rank_title=current_user.rank_title,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        avatar_url=current_user.avatar_url,
        quests_completed=quests_completed,
        achievements_count=achievements_count,
        current_streak=current_user.current_streak,
    )


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Обновить свой профиль",
    description="Частичное обновление данных авторизованного пользователя."
)
async def update_my_profile(
    body: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> UserRead:
    
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    
    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить свой аккаунт",
    description="Удаляет текущего пользователя и все его данные.",
    response_class=Response,
)
async def delete_my_account(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    await session.delete(current_user)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
