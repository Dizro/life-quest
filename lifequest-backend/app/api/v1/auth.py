# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.models.user_buff import UserBuff
from app.models.task import Task
from app.schemas.token import Token
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_, and_, update

router = APIRouter()

@router.post("/login", response_model=Token, summary="Авторизация по логину и паролю")
async def login_access_token(
    session: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """OAuth2 совместимый эндпоинт для получения JWT (используется для базовой авторизации)."""
    
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный логин или пароль"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь неактивен"
        )
        
    now_utc = datetime.now(timezone.utc)
    
    # ── Механика "Воскрешение" (Забытые легенды) ────────────────────────────────────
    if user.last_active_at:
        days_offline = (now_utc - user.last_active_at).days
        if days_offline >= 7:
            # 1. Архивация испытаний и просроченных задач
            archive_query = (
                update(Task).where(
                    Task.owner_id == user.id,
                    or_(
                        Task.status == "trial",
                        and_(Task.status == "active", Task.due_date != None, Task.due_date < now_utc)
                    )
                ).values(status="archived")
            )
            await session.execute(archive_query)
            
            # 2. Выдача баффа воскрешения x2.0 XP на 3 дня
            resurrection_buff = UserBuff(
                user_id=user.id,
                buff_type="xp_boost",
                multiplier=2.0,
                expires_at=now_utc + timedelta(days=3)
            )
            session.add(resurrection_buff)
            
    # Обновляем активность при логине
    user.last_active_at = now_utc
    session.add(user)
    await session.commit()
    
    return Token(
        access_token=create_access_token(subject=user.id),
        refresh_token=create_refresh_token(subject=user.id)
    )