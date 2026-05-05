from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.user_buff import UserBuff

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Схемы для авторизации ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# --- Эндпоинты ---
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового героя"""
    # Проверка username
    query = await db.execute(select(User).where(User.username == user_data.username))
    if query.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Это имя пользователя уже занято")

    # Проверка email
    email_query = await db.execute(select(User).where(User.email == user_data.email))
    if email_query.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    now_utc = datetime.now(timezone.utc)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        display_name=user_data.display_name or user_data.username,
        gold=50,
        level=1,
        xp=0,
        xp_to_next_level=100,
        crystals=0,
        streak_days=0,
        max_streak=0,
        weekly_xp=0,
        daily_xp_earned=0,
        character_class="Авантюрист",
        rank_title="Новобранец",
        theme="dark",
        notifications_deadlines=True,
        notifications_evening=True,
        notifications_achievements=True,
        language="ru",
        xp_multiplier=1.0,
        last_active_at=now_utc,
    )
    db.add(new_user)
    await db.flush()

    # Стартовый бафф
    start_buff = UserBuff(
        user_id=new_user.id,
        buff_type="xp_boost",
        multiplier=2.0,
        expires_at=now_utc + timedelta(days=3)
    )
    db.add(start_buff)

    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Вход в аккаунт"""
    query = await db.execute(select(User).where(User.username == user_data.username))
    user = query.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}