import uuid
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.properties.models import Property
from app.properties.schemas import PropertyCreate, PropertyUpdate
from app.shared.exceptions import NotFoundError, ConflictError
from app.shared.slug import slugify


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    counter = 1
    while True:
        result = await db.execute(select(Property).where(Property.slug == candidate))
        if not result.scalar_one_or_none():
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


async def create_property(db: AsyncSession, data: PropertyCreate) -> Property:
    slug = await _unique_slug(db, data.name)
    prop = Property(
        name=data.name,
        slug=slug,
        type=data.type,
        region=data.region,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        capacity=data.capacity,
        bedrooms=data.bedrooms,
        bathrooms=data.bathrooms,
        guesty_listing_id=data.guesty_listing_id,
        cloudbeds_property_id=data.cloudbeds_property_id,
        status=data.status,
        tags=data.tags,
        metadata_=data.metadata_,
    )
    db.add(prop)
    await db.commit()
    await db.refresh(prop)
    return prop


async def get_properties(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    region: Optional[str] = None,
    type_: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Property], int]:
    query = select(Property)

    if region:
        query = query.where(Property.region == region)
    if type_:
        query = query.where(Property.type == type_)
    if status:
        query = query.where(Property.status == status)
    if search:
        query = query.where(
            or_(
                Property.name.ilike(f"%{search}%"),
                Property.address.ilike(f"%{search}%"),
            )
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Property.name).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_property_by_slug(db: AsyncSession, slug: str) -> Property:
    result = await db.execute(select(Property).where(Property.slug == slug))
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundError("Propiedad")
    return prop


async def update_property(db: AsyncSession, slug: str, data: PropertyUpdate) -> Property:
    prop = await get_property_by_slug(db, slug)
    for field, value in data.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(prop, field, value)
    await db.commit()
    await db.refresh(prop)
    return prop


async def delete_property(db: AsyncSession, slug: str) -> None:
    prop = await get_property_by_slug(db, slug)
    await db.delete(prop)
    await db.commit()
