from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.properties.schemas import PropertyCreate, PropertyDetail, PropertySummary, PropertyUpdate
from app.properties.service import (
    create_property,
    delete_property,
    get_properties,
    get_property_by_slug,
    update_property,
)
from app.shared.database import get_db
from app.shared.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])


@router.get("", response_model=PaginatedResponse[PropertySummary])
async def list_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    region: Optional[str] = None,
    type: Optional[str] = Query(None, alias="type"),
    status: Optional[str] = None,
    search: Optional[str] = None,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_properties(db, page, limit, region, type, status, search)
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=PropertyDetail, status_code=status.HTTP_201_CREATED)
async def create(
    data: PropertyCreate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_property(db, data)


@router.get("/{slug}", response_model=PropertyDetail)
async def get_detail(
    slug: str,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_property_by_slug(db, slug)


@router.patch("/{slug}", response_model=PropertyDetail)
async def update(
    slug: str,
    data: PropertyUpdate,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_property(db, slug, data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    slug: str,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await delete_property(db, slug)
