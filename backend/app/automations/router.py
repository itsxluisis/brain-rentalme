from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.shared.database import get_db
from app.automations import service as automation_service
from app.automations.scheduler import get_scheduler, build_trigger, _guesty_sync_job

router = APIRouter(prefix="/api/v1/automations", tags=["automations"])


class TaskCreate(BaseModel):
    name: str
    action_type: str
    schedule_type: str
    schedule_config: dict


class TaskUpdate(BaseModel):
    name: str | None = None
    schedule_type: str | None = None
    schedule_config: dict | None = None
    is_active: bool | None = None


def _serialize(task) -> dict:
    return {
        "id": str(task.id),
        "name": task.name,
        "action_type": task.action_type,
        "schedule_type": task.schedule_type,
        "schedule_config": task.schedule_config,
        "is_active": task.is_active,
        "last_run_at": task.last_run_at.isoformat() if task.last_run_at else None,
        "next_run_at": task.next_run_at.isoformat() if task.next_run_at else None,
        "last_status": task.last_status,
        "created_at": task.created_at.isoformat(),
    }


@router.get("")
async def list_automations(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    tasks = await automation_service.list_tasks(db)
    return [_serialize(t) for t in tasks]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_automation(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    task = await automation_service.create_task(
        db,
        name=body.name,
        action_type=body.action_type,
        schedule_type=body.schedule_type,
        schedule_config=body.schedule_config,
    )

    # Register with scheduler
    try:
        scheduler = get_scheduler()
        trigger = build_trigger(task.schedule_type, task.schedule_config)
        if task.action_type == "guesty_sync":
            await scheduler.add_job(
                _guesty_sync_job,
                trigger=trigger,
                id=f"automation_{task.id}",
                conflict_policy="replace",
            )
    except Exception:
        pass

    return _serialize(task)


@router.patch("/{task_id}")
async def update_automation(
    task_id: str,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    task = await automation_service.update_task(db, task_id, **fields)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Sync scheduler state
    try:
        scheduler = get_scheduler()
        job_id = f"automation_{task_id}"
        if not task.is_active:
            try:
                await scheduler.remove_job(job_id)
            except Exception:
                pass
        else:
            trigger = build_trigger(task.schedule_type, task.schedule_config)
            if task.action_type == "guesty_sync":
                await scheduler.add_job(
                    _guesty_sync_job,
                    trigger=trigger,
                    id=job_id,
                    conflict_policy="replace",
                )
    except Exception:
        pass

    return _serialize(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    deleted = await automation_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        scheduler = get_scheduler()
        await scheduler.remove_job(f"automation_{task_id}")
    except Exception:
        pass
