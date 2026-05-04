from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.systems.models import System
from app.systems.schemas import SystemCreate, SystemUpdate
from app.shared.exceptions import NotFoundError
from app.shared.slug import slugify

SEED_SYSTEMS = [
    {"name": "Guesty", "category": "pms", "has_api": True, "website_url": "https://guesty.com", "api_docs_url": "https://api.guesty.com"},
    {"name": "Avantio", "category": "pms", "has_api": True, "website_url": "https://avantio.com"},
    {"name": "Cloudbeds", "category": "pms", "has_api": True, "website_url": "https://cloudbeds.com", "api_docs_url": "https://api.cloudbeds.com"},
    {"name": "UpMarket", "category": "ai_response", "has_api": False, "website_url": "https://upmarket.co"},
    {"name": "INTO", "category": "ai_response", "has_api": False},
    {"name": "IA Cloudbeds", "category": "ai_response", "has_api": False},
    {"name": "YACAN", "category": "access", "has_api": True},
    {"name": "Vikey", "category": "access", "has_api": True, "website_url": "https://vikey.it", "tags": ["checkin"]},
    {"name": "Nuki", "category": "access", "has_api": True, "website_url": "https://nuki.io", "api_docs_url": "https://developer.nuki.io"},
    {"name": "Pricelabs", "category": "pricing", "has_api": True, "website_url": "https://pricelabs.co"},
    {"name": "Pricepoint", "category": "pricing", "has_api": True},
    {"name": "Beyond", "category": "pricing", "has_api": True, "website_url": "https://beyondpricing.com"},
]


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    counter = 1
    while True:
        result = await db.execute(select(System).where(System.slug == candidate))
        if not result.scalar_one_or_none():
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


async def seed_systems(db: AsyncSession) -> int:
    created = 0
    for data in SEED_SYSTEMS:
        existing = await db.execute(select(System).where(System.name == data["name"]))
        if existing.scalar_one_or_none():
            continue
        slug = await _unique_slug(db, data["name"])
        system = System(
            name=data["name"],
            slug=slug,
            category=data["category"],
            has_api=data.get("has_api", False),
            website_url=data.get("website_url"),
            api_docs_url=data.get("api_docs_url"),
            tags=data.get("tags", []),
        )
        db.add(system)
        created += 1
    await db.commit()
    return created


async def create_system(db: AsyncSession, data: SystemCreate) -> System:
    slug = await _unique_slug(db, data.name)
    system = System(
        name=data.name,
        slug=slug,
        category=data.category,
        description=data.description,
        website_url=data.website_url,
        has_api=data.has_api,
        api_docs_url=data.api_docs_url,
        status=data.status,
        tags=data.tags,
        metadata_=data.metadata_,
    )
    db.add(system)
    await db.commit()
    await db.refresh(system)
    return system


async def get_systems(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[System], int]:
    query = select(System)
    if category:
        query = query.where(System.category == category)
    if status:
        query = query.where(System.status == status)
    if search:
        query = query.where(
            or_(System.name.ilike(f"%{search}%"), System.description.ilike(f"%{search}%"))
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()
    query = query.order_by(System.name).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_system_by_slug(db: AsyncSession, slug: str) -> System:
    result = await db.execute(select(System).where(System.slug == slug))
    system = result.scalar_one_or_none()
    if not system:
        raise NotFoundError("Sistema")
    return system


async def update_system(db: AsyncSession, slug: str, data: SystemUpdate) -> System:
    system = await get_system_by_slug(db, slug)
    for field, value in data.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(system, field, value)
    await db.commit()
    await db.refresh(system)
    return system


async def delete_system(db: AsyncSession, slug: str) -> None:
    system = await get_system_by_slug(db, slug)
    await db.delete(system)
    await db.commit()
