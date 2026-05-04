from datetime import datetime, UTC

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.credentials.service import get_credential
from app.knowledge.models import KnowledgeBlock
from app.properties.models import Property
from app.shared.database import get_db
from app.shared.models import SyncLog
from app.shared.pagination import PaginatedResponse
from app.sync.providers.guesty import fetch_listings
from app.sync.service import run_guesty_sync, _build_description_content

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

_running: dict[str, bool] = {}


class SyncTriggerRequest(BaseModel):
    provider: str = "guesty"


class SyncLogResponse(BaseModel):
    id: str
    provider: str
    status: str
    listings_processed: int
    blocks_created: int
    blocks_updated: int
    blocks_skipped: int
    errors: list[str]
    started_at: str
    completed_at: str | None

    @classmethod
    def from_orm(cls, log: SyncLog) -> "SyncLogResponse":
        return cls(
            id=str(log.id),
            provider=log.provider,
            status=log.status,
            listings_processed=log.listings_processed,
            blocks_created=log.blocks_created,
            blocks_updated=log.blocks_updated,
            blocks_skipped=log.blocks_skipped,
            errors=log.errors or [],
            started_at=log.started_at.isoformat(),
            completed_at=log.completed_at.isoformat() if log.completed_at else None,
        )


async def _background_sync(db: AsyncSession, user_id: str):
    try:
        _running["guesty"] = True
        await run_guesty_sync(db, triggered_by_id=user_id)
    finally:
        _running["guesty"] = False
        await db.close()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_sync(
    body: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if body.provider != "guesty":
        raise HTTPException(status_code=400, detail="Only 'guesty' provider supported")
    if _running.get("guesty"):
        raise HTTPException(status_code=409, detail="Sync already running")
    background_tasks.add_task(_background_sync, db, str(current_user.id))
    return {"message": "Sync started", "provider": body.provider}


@router.get("/status")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SyncLog).where(SyncLog.provider == "guesty").order_by(desc(SyncLog.started_at)).limit(1)
    )
    last_log = result.scalar_one_or_none()
    return {
        "is_running": _running.get("guesty", False),
        "last_sync": SyncLogResponse.from_orm(last_log) if last_log else None,
    }


@router.get("/logs")
async def get_sync_logs(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    offset = (page - 1) * limit
    result = await db.execute(
        select(SyncLog).order_by(desc(SyncLog.started_at)).offset(offset).limit(limit)
    )
    logs = result.scalars().all()

    count_result = await db.execute(select(SyncLog))
    total = len(count_result.scalars().all())

    return PaginatedResponse(
        items=[SyncLogResponse.from_orm(l) for l in logs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/conflicts")
async def get_conflicts(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Returns knowledge blocks that were manually edited and belong to Guesty-synced properties."""
    result = await db.execute(
        select(KnowledgeBlock, Property)
        .join(Property, Property.id == KnowledgeBlock.entity_id)
        .where(
            KnowledgeBlock.entity_type == "property",
            KnowledgeBlock.source == "manual",
            Property.guesty_listing_id.isnot(None),
        )
    )
    rows = result.all()
    return [
        {
            "block_id": str(block.id),
            "title": block.title,
            "local_content": block.content,
            "property_name": prop.name,
            "property_slug": prop.slug,
            "updated_at": block.updated_at.isoformat(),
        }
        for block, prop in rows
    ]


class ConflictResolveRequest(BaseModel):
    resolution: str  # "keep_local" | "accept_remote"


@router.post("/conflicts/{block_id}/resolve")
async def resolve_conflict(
    block_id: str,
    body: ConflictResolveRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    import uuid as _uuid

    result = await db.execute(
        select(KnowledgeBlock).where(KnowledgeBlock.id == _uuid.UUID(block_id))
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    if body.resolution == "keep_local":
        return {"status": "kept_local", "block_id": block_id}

    if body.resolution == "accept_remote":
        prop_result = await db.execute(
            select(Property).where(Property.id == block.entity_id)
        )
        prop = prop_result.scalar_one_or_none()
        if not prop or not prop.guesty_listing_id:
            raise HTTPException(status_code=400, detail="Property not linked to Guesty")

        api_key = await get_credential(db, "GUESTY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="GUESTY_API_KEY not configured")

        page = await fetch_listings(api_key, limit=1, skip=0)
        items = page.get("results") or page.get("data") or []
        listing = next((l for l in items if l.get("_id") == prop.guesty_listing_id), None)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found in Guesty")

        block.content = _build_description_content(listing)
        block.source = "guesty_sync"
        block.content_vector = None  # trigger re-embed
        await db.commit()
        return {"status": "accepted_remote", "block_id": block_id}

    raise HTTPException(status_code=400, detail="Invalid resolution. Use 'keep_local' or 'accept_remote'")
