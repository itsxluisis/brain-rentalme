"""Admin dashboard stats and activity logs."""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.knowledge.models import KnowledgeBlock
from app.properties.models import Property
from app.shared.database import get_db
from app.shared.models import SyncLog, ToolApiLog, ToolApiKey, ChatMessage
from app.systems.models import System

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    props_count = (await db.execute(select(func.count()).select_from(Property))).scalar_one()
    systems_count = (await db.execute(select(func.count()).select_from(System))).scalar_one()
    blocks_count = (await db.execute(select(func.count()).select_from(KnowledgeBlock).where(KnowledgeBlock.is_active == True))).scalar_one()
    embedded_count = (await db.execute(
        select(func.count()).select_from(KnowledgeBlock).where(
            KnowledgeBlock.is_active == True,
            KnowledgeBlock.content_vector.isnot(None),
        )
    )).scalar_one()

    last_sync = (await db.execute(
        select(SyncLog).order_by(desc(SyncLog.started_at)).limit(1)
    )).scalar_one_or_none()

    return {
        "properties_count": props_count,
        "systems_count": systems_count,
        "knowledge_blocks_count": blocks_count,
        "blocks_with_embeddings": embedded_count,
        "last_sync": {
            "status": last_sync.status,
            "started_at": last_sync.started_at.isoformat(),
            "listings_processed": last_sync.listings_processed,
        } if last_sync else None,
    }


@router.get("/logs")
async def get_activity_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    # Recent sync logs
    sync_result = await db.execute(
        select(SyncLog).order_by(desc(SyncLog.started_at)).limit(20)
    )
    syncs = sync_result.scalars().all()

    # Recent tool API calls
    tool_result = await db.execute(
        select(ToolApiLog, ToolApiKey)
        .join(ToolApiKey, ToolApiKey.id == ToolApiLog.key_id)
        .order_by(desc(ToolApiLog.created_at))
        .limit(50)
    )
    tool_calls = tool_result.all()

    return {
        "sync_logs": [
            {
                "type": "sync",
                "provider": s.provider,
                "status": s.status,
                "listings_processed": s.listings_processed,
                "started_at": s.started_at.isoformat(),
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in syncs
        ],
        "tool_api_calls": [
            {
                "type": "tool_call",
                "key_name": key.name,
                "endpoint": log.endpoint,
                "response_ms": log.response_ms,
                "results_count": log.results_count,
                "created_at": log.created_at.isoformat(),
            }
            for log, key in tool_calls
        ],
    }
