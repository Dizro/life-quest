from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task
from app.schemas.sync import SyncRequest, SyncResponse, SyncActionResult
from app.services.reward_service import calculate_rewards, apply_xp
from app.tasks.celery_tasks import process_effort_score

router = APIRouter(prefix="/sync", tags=["sync"])


def _ensure_tz(dt: datetime | None) -> datetime | None:
    """Универсальное решение для тестов (SQLite) и боя (PostgreSQL)"""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.post("/offline", response_model=SyncResponse)
async def sync_offline_actions(
    sync_data: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SCRUM-207: Принимает массив накопленных офлайн-действий,
    обрабатывает их пакетно с разрешением конфликтов.
    """
    sorted_actions = sorted(sync_data.actions, key=lambda a: a.timestamp)

    results: list[SyncActionResult] = []
    processed, succeeded, failed, conflicts = 0, 0, 0, 0

    for action in sorted_actions:
        processed += 1
        result = SyncActionResult(
            client_task_id=action.client_task_id,
            action_type=action.action_type,
            success=False,
        )

        try:
            if action.action_type == "CREATE_TASK":
                res = await _handle_create(action, current_user, db)
                result.success = res["success"]
                result.server_task_id = res.get("server_task_id")
                result.conflict = res.get("conflict", False)
                result.conflict_reason = res.get("conflict_reason")

            elif action.action_type == "COMPLETE_TASK":
                res = await _handle_complete(action, current_user, db)
                result.success = res["success"]
                result.server_task_id = res.get("server_task_id")
                result.conflict = res.get("conflict", False)
                result.conflict_reason = res.get("conflict_reason")

            elif action.action_type == "UPDATE_TASK":
                res = await _handle_update(action, current_user, db)
                result.success = res["success"]
                result.server_task_id = res.get("server_task_id")
                result.conflict = res.get("conflict", False)
                result.conflict_reason = res.get("conflict_reason")

            elif action.action_type == "DELETE_TASK":
                res = await _handle_delete(action, current_user, db)
                result.success = res["success"]
                result.conflict = res.get("conflict", False)

            if result.success:
                succeeded += 1
            if result.conflict:
                conflicts += 1

        except Exception as e:
            result.success = False
            result.error = str(e)
            failed += 1

        results.append(result)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка сохранения синхронизации")

    return SyncResponse(
        processed=processed,
        succeeded=succeeded,
        failed=failed,
        conflicts=conflicts,
        results=results,
        server_time=datetime.now(timezone.utc),
    )


async def _handle_create(action, user: User, db: AsyncSession) -> dict:
    existing = await db.execute(
        select(Task).where(Task.client_id == action.client_task_id)
    )
    existing_task = existing.scalar_one_or_none()
    
    if existing_task:
        return {
            "success": True,
            "conflict": True,
            "conflict_reason": "ALREADY_EXISTS",
            "server_task_id": existing_task.id,
        }

    payload = action.payload
    task = Task(
        user_id=user.id,
        title=payload.get("title", "Задача без названия")[:500],
        description=payload.get("description", "")[:2000],
        task_type=payload.get("task_type", "regular"),
        category=payload.get("category", "personal"),
        status="pending_es",
        client_id=action.client_task_id,
        created_offline=True,
        client_created_at=action.timestamp,
        deadline=_parse_datetime(payload.get("deadline")),
    )
    db.add(task)
    await db.flush()

    process_effort_score.delay(task.id)

    return {"success": True, "conflict": False, "server_task_id": task.id}


async def _handle_complete(action, user: User, db: AsyncSession) -> dict:
    task = await _find_task(action.client_task_id, user.id, db)
    if not task:
        return {"success": False, "error": "TASK_NOT_FOUND"}

    if task.status == "completed":
        return {
            "success": True,
            "conflict": True,
            "conflict_reason": "ALREADY_COMPLETED",
            "server_task_id": task.id,
        }

    if task.status not in ("active", "pending_es"):
        return {
            "success": False,
            "conflict": True,
            "conflict_reason": f"INVALID_STATUS_{task.status}",
            "server_task_id": task.id,
        }

    task_updated = _ensure_tz(task.updated_at)
    action_time = _ensure_tz(action.timestamp)

    if task_updated and action_time and task_updated > action_time:
        return {
            "success": False,
            "conflict": True,
            "conflict_reason": "SERVER_DATA_NEWER",
            "server_task_id": task.id,
        }

    effort = task.effort_score or 5
    xp_raw, gold = calculate_rewards(effort, task.task_type)
    apply_xp(user, xp_raw)
    user.gold += gold

    task.status = "completed"
    task.completed_at = action.timestamp
    await db.flush()

    return {"success": True, "conflict": False, "server_task_id": task.id}


async def _handle_update(action, user: User, db: AsyncSession) -> dict:
    task = await _find_task(action.client_task_id, user.id, db)
    if not task:
        return {"success": False, "error": "TASK_NOT_FOUND"}

    if task.status == "completed":
        return {
            "success": False,
            "conflict": True,
            "conflict_reason": "TASK_ALREADY_COMPLETED",
            "server_task_id": task.id,
        }

    task_updated = _ensure_tz(task.updated_at)
    action_time = _ensure_tz(action.timestamp)

    if task_updated and action_time and task_updated > action_time:
        return {
            "success": False,
            "conflict": True,
            "conflict_reason": "SERVER_DATA_NEWER",
            "server_task_id": task.id,
        }

    payload = action.payload
    if "title" in payload:
        task.title = payload["title"][:500]
    if "description" in payload:
        task.description = payload.get("description", "")[:2000]
    if "category" in payload:
        task.category = payload["category"]
    if "deadline" in payload:
        task.deadline = _parse_datetime(payload.get("deadline"))

    await db.flush()
    return {"success": True, "conflict": False, "server_task_id": task.id}


async def _handle_delete(action, user: User, db: AsyncSession) -> dict:
    task = await _find_task(action.client_task_id, user.id, db)
    if not task:
        return {"success": True, "conflict": False}

    if task.status == "completed":
        return {"success": False, "conflict": True, "conflict_reason": "TASK_ALREADY_COMPLETED"}

    task.status = "archived"
    await db.flush()
    return {"success": True, "conflict": False}


async def _find_task(client_task_id: str, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Task).where(Task.client_id == client_task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task and client_task_id.isdigit():
        result = await db.execute(
            select(Task).where(Task.id == int(client_task_id), Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

    return task


def _parse_datetime(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None