"""
Группы / Гильдии (FR-8).
CRUD групп, вступление/выход, чат группы.
"""

from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember, GroupMessage

router = APIRouter(prefix="/groups", tags=["groups"])


# ── Schemas ───────────────────────────────────────────────────────────────

class GroupCreate(BaseModel):
    name: str
    description: str = ""
    is_public: bool = True


class MemberOut(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str] = None
    level: int
    role: str


class GroupOut(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    is_public: bool
    member_count: int
    is_member: bool = False
    created_at: Optional[datetime] = None


class GroupDetail(GroupOut):
    members: List[MemberOut] = []


class MessageOut(BaseModel):
    id: int
    user_id: int
    sender_name: str
    text: str
    created_at: datetime


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SendMessage(BaseModel):
    text: str


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[GroupOut])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список всех публичных групп + группы, в которых состоит пользователь."""
    result = await db.execute(
        select(Group).options(selectinload(Group.members))
    )
    groups = result.scalars().all()

    out = []
    for g in groups:
        is_member = any(m.user_id == current_user.id for m in g.members)
        if g.is_public or is_member:
            out.append(GroupOut(
                id=g.id,
                name=g.name,
                description=g.description,
                owner_id=g.owner_id,
                is_public=g.is_public,
                member_count=len(g.members),
                is_member=is_member,
                created_at=g.created_at,
            ))
    return out


@router.post("/", response_model=GroupOut)
async def create_group(
    body: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать группу. Создатель автоматически становится owner. Один пользователь = одна гильдия."""
    # Проверка: уже владеет гильдией?
    owns = await db.execute(
        select(GroupMember).where(
            GroupMember.user_id == current_user.id,
            GroupMember.role == "owner",
        )
    )
    if owns.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ты уже владеешь гильдией. Удали текущую, чтобы создать новую.")

    if not body.name or len(body.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Название группы слишком короткое")

    existing = await db.execute(select(Group).where(Group.name == body.name.strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Группа с таким названием уже существует")

    group = Group(
        name=body.name.strip(),
        description=body.description.strip(),
        is_public=body.is_public,
        owner_id=current_user.id,
    )
    db.add(group)
    await db.flush()

    member = GroupMember(group_id=group.id, user_id=current_user.id, role="owner")
    db.add(member)
    await db.flush()

    return GroupOut(
        id=group.id,
        name=group.name,
        description=group.description,
        owner_id=group.owner_id,
        is_public=group.is_public,
        member_count=1,
        is_member=True,
        created_at=group.created_at,
    )


@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Детали группы с участниками (участники видны только членам)."""
    result = await db.execute(
        select(Group).where(Group.id == group_id).options(selectinload(Group.members))
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    is_member = any(m.user_id == current_user.id for m in group.members)

    members_out = []
    if is_member:
        for m in group.members:
            user_result = await db.execute(select(User).where(User.id == m.user_id))
            u = user_result.scalar_one_or_none()
            if u:
                members_out.append(MemberOut(
                    user_id=u.id,
                    username=u.username,
                    display_name=u.display_name,
                    level=u.level,
                    role=m.role,
                ))

    return GroupDetail(
        id=group.id,
        name=group.name,
        description=group.description,
        owner_id=group.owner_id,
        is_public=group.is_public,
        member_count=len(group.members),
        is_member=is_member,
        created_at=group.created_at,
        members=members_out,
    )


@router.patch("/{group_id}", response_model=GroupOut)
async def update_group(
    group_id: int,
    body: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование гильдии (только owner)."""
    result = await db.execute(
        select(Group).where(Group.id == group_id).options(selectinload(Group.members))
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может редактировать гильдию")

    if body.name is not None:
        name = body.name.strip()
        if len(name) < 2:
            raise HTTPException(status_code=400, detail="Название слишком короткое")
        dup = await db.execute(select(Group).where(Group.name == name, Group.id != group_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Группа с таким названием уже существует")
        group.name = name

    if body.description is not None:
        group.description = body.description.strip()[:500]

    await db.flush()

    return GroupOut(
        id=group.id, name=group.name, description=group.description,
        owner_id=group.owner_id, is_public=group.is_public,
        member_count=len(group.members), is_member=True, created_at=group.created_at,
    )


@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить гильдию (только owner). Каскадно удаляет участников и сообщения."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может удалить гильдию")

    await db.delete(group)
    await db.flush()
    return {"success": True, "message": "Гильдия удалена"}


@router.post("/{group_id}/join")
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Вступить в группу."""
    result = await db.execute(
        select(Group).where(Group.id == group_id).options(selectinload(Group.members))
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    if any(m.user_id == current_user.id for m in group.members):
        raise HTTPException(status_code=400, detail="Ты уже в этой группе")

    if len(group.members) >= group.max_members:
        raise HTTPException(status_code=400, detail="Группа переполнена")

    member = GroupMember(group_id=group.id, user_id=current_user.id, role="member")
    db.add(member)
    await db.flush()

    return {"success": True, "message": f"Вы вступили в группу «{group.name}»"}


@router.post("/{group_id}/leave")
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Покинуть группу."""
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=400, detail="Ты не состоишь в этой группе")

    if membership.role == "owner":
        raise HTTPException(status_code=400, detail="Владелец не может покинуть группу. Передайте права или удалите её.")

    await db.delete(membership)
    await db.flush()

    return {"success": True, "message": "Вы покинули группу"}


# ── Чат группы ────────────────────────────────────────────────────────────

@router.get("/{group_id}/messages", response_model=List[MessageOut])
async def get_messages(
    group_id: int,
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Последние сообщения чата группы."""
    # Проверка членства
    mem = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not mem.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Вы не состоите в этой группе")

    result = await db.execute(
        select(GroupMessage)
        .where(GroupMessage.group_id == group_id)
        .order_by(GroupMessage.created_at.desc())
        .limit(limit)
    )
    msgs = result.scalars().all()
    msgs.reverse()

    out = []
    for msg in msgs:
        user_result = await db.execute(select(User).where(User.id == msg.user_id))
        u = user_result.scalar_one_or_none()
        out.append(MessageOut(
            id=msg.id,
            user_id=msg.user_id,
            sender_name=u.display_name or u.username if u else "???",
            text=msg.text,
            created_at=msg.created_at,
        ))
    return out


@router.post("/{group_id}/messages", response_model=MessageOut)
async def send_message(
    group_id: int,
    body: SendMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отправить сообщение в чат группы."""
    mem = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    if not mem.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Вы не состоите в этой группе")

    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    msg = GroupMessage(
        group_id=group_id,
        user_id=current_user.id,
        text=body.text.strip()[:1000],
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)

    return MessageOut(
        id=msg.id,
        user_id=current_user.id,
        sender_name=current_user.display_name or current_user.username,
        text=msg.text,
        created_at=msg.created_at,
    )
