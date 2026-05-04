import uuid
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.models import KnowledgeBlock
from app.knowledge.schemas import KnowledgeBlockCreate, KnowledgeBlockUpdate
from app.shared.exceptions import NotFoundError
from app.shared.models import PropertySystemRelation


async def _embed_block(block_id: uuid.UUID) -> None:
    """Background task: embed a single knowledge block."""
    from app.shared.embeddings import embed_text
    from app.shared.database import async_session

    async with async_session() as db:
        result = await db.execute(select(KnowledgeBlock).where(KnowledgeBlock.id == block_id))
        block = result.scalar_one_or_none()
        if not block:
            return
        embedding = await embed_text(block.content)
        if embedding:
            block.content_vector = embedding
            await db.commit()


async def create_block(
    db: AsyncSession,
    data: KnowledgeBlockCreate,
    background_tasks: BackgroundTasks,
) -> KnowledgeBlock:
    block = KnowledgeBlock(
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        block_type=data.block_type,
        title=data.title,
        content=data.content,
        language=data.language,
        source="manual",
        metadata_=data.metadata_,
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    background_tasks.add_task(_embed_block, block.id)
    return block


async def get_blocks(
    db: AsyncSession,
    entity_type: Optional[str] = None,
    entity_id: Optional[uuid.UUID] = None,
    block_type: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[KnowledgeBlock], int]:
    query = select(KnowledgeBlock).where(KnowledgeBlock.is_active == True)
    if entity_type:
        query = query.where(KnowledgeBlock.entity_type == entity_type)
    if entity_id:
        query = query.where(KnowledgeBlock.entity_id == entity_id)
    if block_type:
        query = query.where(KnowledgeBlock.block_type == block_type)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()
    query = query.order_by(KnowledgeBlock.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_block(db: AsyncSession, block_id: uuid.UUID) -> KnowledgeBlock:
    result = await db.execute(select(KnowledgeBlock).where(KnowledgeBlock.id == block_id))
    block = result.scalar_one_or_none()
    if not block:
        raise NotFoundError("Bloque de conocimiento")
    return block


async def update_block(
    db: AsyncSession,
    block_id: uuid.UUID,
    data: KnowledgeBlockUpdate,
    background_tasks: BackgroundTasks,
) -> KnowledgeBlock:
    block = await get_block(db, block_id)
    content_changed = data.content is not None and data.content != block.content

    for field, value in data.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(block, field, value)

    if content_changed:
        block.content_vector = None
        block.source = "manual"

    await db.commit()
    await db.refresh(block)

    if content_changed:
        background_tasks.add_task(_embed_block, block.id)

    return block


async def delete_block(db: AsyncSession, block_id: uuid.UUID) -> None:
    block = await get_block(db, block_id)
    await db.delete(block)
    await db.commit()


async def trigger_embed(db: AsyncSession, block_id: uuid.UUID, background_tasks: BackgroundTasks) -> None:
    block = await get_block(db, block_id)
    background_tasks.add_task(_embed_block, block.id)


# --- Relations ---

async def create_relation(
    db: AsyncSession, property_id: uuid.UUID, system_id: uuid.UUID, notes: Optional[str], config: dict
) -> PropertySystemRelation:
    relation = PropertySystemRelation(
        property_id=property_id,
        system_id=system_id,
        notes=notes,
        config=config,
    )
    db.add(relation)
    await db.commit()
    await db.refresh(relation)
    return relation


async def get_property_relations(db: AsyncSession, property_id: uuid.UUID) -> list[PropertySystemRelation]:
    result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.property_id == property_id)
    )
    return result.scalars().all()


async def get_system_relations(db: AsyncSession, system_id: uuid.UUID) -> list[PropertySystemRelation]:
    result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.system_id == system_id)
    )
    return result.scalars().all()


async def update_relation(
    db: AsyncSession, relation_id: uuid.UUID, notes: Optional[str], config: Optional[dict]
) -> PropertySystemRelation:
    result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.id == relation_id)
    )
    relation = result.scalar_one_or_none()
    if not relation:
        raise NotFoundError("Vinculación")
    if notes is not None:
        relation.notes = notes
    if config is not None:
        relation.config = config
    await db.commit()
    await db.refresh(relation)
    return relation


async def delete_relation(db: AsyncSession, relation_id: uuid.UUID) -> None:
    result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.id == relation_id)
    )
    relation = result.scalar_one_or_none()
    if not relation:
        raise NotFoundError("Vinculación")
    await db.delete(relation)
    await db.commit()
