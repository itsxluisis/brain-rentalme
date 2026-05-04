import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.knowledge.models import KnowledgeBlock
from app.knowledge.schemas import (
    KnowledgeBlockCreate,
    KnowledgeBlockResponse,
    KnowledgeBlockUpdate,
    RelationCreate,
    RelationResponse,
    RelationUpdate,
)
from app.knowledge.service import (
    create_block,
    create_relation,
    delete_block,
    delete_relation,
    get_block,
    get_blocks,
    get_property_relations,
    get_system_relations,
    trigger_embed,
    update_block,
    update_relation,
)
from app.shared.database import get_db
from app.shared.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1", tags=["knowledge"])


# --- Knowledge Blocks ---

@router.get("/knowledge", response_model=PaginatedResponse[KnowledgeBlockResponse])
async def list_blocks(
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    block_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_blocks(db, entity_type, entity_id, block_type, page, limit)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.post("/knowledge", response_model=KnowledgeBlockResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: KnowledgeBlockCreate,
    background_tasks: BackgroundTasks,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_block(db, data, background_tasks)


@router.get("/knowledge/{block_id}", response_model=KnowledgeBlockResponse)
async def get_detail(
    block_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_block(db, block_id)


@router.patch("/knowledge/{block_id}", response_model=KnowledgeBlockResponse)
async def update(
    block_id: uuid.UUID,
    data: KnowledgeBlockUpdate,
    background_tasks: BackgroundTasks,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_block(db, block_id, data, background_tasks)


@router.delete("/knowledge/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    block_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_block(db, block_id)


@router.post("/knowledge/{block_id}/embed", status_code=status.HTTP_202_ACCEPTED)
async def embed(
    block_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await trigger_embed(db, block_id, background_tasks)
    return {"status": "embedding_queued"}


# --- Relations ---

@router.post("/relations", response_model=RelationResponse, status_code=status.HTTP_201_CREATED)
async def create_rel(
    data: RelationCreate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_relation(db, data.property_id, data.system_id, data.notes, data.config)


@router.patch("/relations/{relation_id}", response_model=RelationResponse)
async def update_rel(
    relation_id: uuid.UUID,
    data: RelationUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_relation(db, relation_id, data.notes, data.config)


@router.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rel(
    relation_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_relation(db, relation_id)


@router.get("/properties/{property_id}/relations", response_model=list[RelationResponse])
async def property_relations(
    property_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_property_relations(db, property_id)


@router.get("/systems/{system_id}/relations", response_model=list[RelationResponse])
async def system_relations(
    system_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_system_relations(db, system_id)


# --- Embedding Stats ---

@router.get("/knowledge/stats/embeddings")
async def embedding_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total_result = await db.execute(select(func.count()).select_from(KnowledgeBlock).where(KnowledgeBlock.is_active == True))
    total = total_result.scalar_one()

    embedded_result = await db.execute(
        select(func.count()).select_from(KnowledgeBlock).where(
            KnowledgeBlock.is_active == True,
            KnowledgeBlock.content_vector.isnot(None),
        )
    )
    embedded = embedded_result.scalar_one()
    pending = total - embedded

    return {
        "total": total,
        "embedded": embedded,
        "pending": pending,
        "coverage_pct": round(embedded / total * 100, 1) if total > 0 else 0,
    }


@router.post("/knowledge/reindex", status_code=status.HTTP_202_ACCEPTED)
async def bulk_reindex(
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeBlock).where(
            KnowledgeBlock.is_active == True,
            KnowledgeBlock.content_vector.is_(None),
        )
    )
    blocks = result.scalars().all()
    for block in blocks:
        await trigger_embed(db, block.id, background_tasks)
    return {"queued": len(blocks)}
