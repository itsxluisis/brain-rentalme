from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.systems.schemas import SystemCreate, SystemDetail, SystemSummary, SystemUpdate
from app.systems.service import (
    create_system,
    delete_system,
    get_systems,
    get_system_by_slug,
    seed_systems,
    update_system,
)
from app.shared.database import get_db
from app.shared.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/systems", tags=["systems"])


@router.get("", response_model=PaginatedResponse[SystemSummary])
async def list_systems(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_systems(db, page, limit, category, status, search)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=SystemDetail, status_code=status.HTTP_201_CREATED)
async def create(
    data: SystemCreate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_system(db, data)


@router.get("/{slug}", response_model=SystemDetail)
async def get_detail(
    slug: str,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_system_by_slug(db, slug)


@router.patch("/{slug}", response_model=SystemDetail)
async def update(
    slug: str,
    data: SystemUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_system(db, slug, data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    slug: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await delete_system(db, slug)


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    created = await seed_systems(db)
    return {"created": created, "detail": f"{created} sistemas creados"}
