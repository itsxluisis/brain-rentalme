"""APScheduler 4.x integration. Scheduler lifecycle managed in FastAPI lifespan."""

from datetime import datetime, UTC
from typing import Optional

from apscheduler import AsyncScheduler
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.config import settings
from app.shared.models import AutomationTask

_scheduler: Optional[AsyncScheduler] = None


def get_scheduler() -> AsyncScheduler:
    if _scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    return _scheduler


async def create_scheduler() -> AsyncScheduler:
    global _scheduler
    data_store = SQLAlchemyDataStore(settings.DATABASE_URL)
    event_broker = LocalEventBroker()
    _scheduler = AsyncScheduler(data_store=data_store, event_broker=event_broker)
    return _scheduler


def build_trigger(schedule_type: str, schedule_config: dict):
    """Build APScheduler trigger from task config."""
    if schedule_type == "cron":
        return CronTrigger(
            hour=schedule_config.get("hour", 2),
            minute=schedule_config.get("minute", 0),
        )
    elif schedule_type == "interval":
        hours = schedule_config.get("hours", 24)
        return IntervalTrigger(hours=hours)
    raise ValueError(f"Unknown schedule_type: {schedule_type}")


async def sync_tasks_to_scheduler(db: AsyncSession, scheduler: AsyncScheduler):
    """Load active AutomationTasks from DB and register them with the scheduler."""
    from app.sync.service import run_guesty_sync as _sync_fn

    result = await db.execute(select(AutomationTask).where(AutomationTask.is_active == True))
    tasks = result.scalars().all()

    for task in tasks:
        job_id = f"automation_{task.id}"
        try:
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


async def _guesty_sync_job():
    """Job function called by APScheduler. Creates its own DB session."""
    from app.shared.database import async_session
    from app.sync.service import run_guesty_sync

    async with async_session() as db:
        try:
            await run_guesty_sync(db)
        except Exception:
            pass
