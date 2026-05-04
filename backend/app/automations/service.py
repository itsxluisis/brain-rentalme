"""AutomationTask CRUD — manages persisted task definitions in the DB."""

from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import AutomationTask


async def list_tasks(db: AsyncSession) -> list[AutomationTask]:
    result = await db.execute(select(AutomationTask).order_by(AutomationTask.created_at))
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: str) -> Optional[AutomationTask]:
    import uuid as _uuid
    result = await db.execute(
        select(AutomationTask).where(AutomationTask.id == _uuid.UUID(task_id))
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    name: str,
    action_type: str,
    schedule_type: str,
    schedule_config: dict,
) -> AutomationTask:
    task = AutomationTask(
        name=name,
        action_type=action_type,
        schedule_type=schedule_type,
        schedule_config=schedule_config,
        is_active=True,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task_id: str,
    **fields,
) -> Optional[AutomationTask]:
    task = await get_task(db, task_id)
    if not task:
        return None
    for key, val in fields.items():
        if val is not None:
            setattr(task, key, val)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: str) -> bool:
    task = await get_task(db, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    return True
