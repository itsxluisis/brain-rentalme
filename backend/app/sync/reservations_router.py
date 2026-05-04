from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.credentials.service import get_credential
from app.properties.models import Property
from app.shared.database import get_db
from app.sync.reservations import fetch_reservations, map_reservation

router = APIRouter(prefix="/api/v1/reservations", tags=["reservations"])


@router.get("")
async def list_reservations(
    property_slug: str | None = None,
    status: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    api_key = await get_credential(db, "GUESTY_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Guesty API key not configured")

    guesty_listing_id = None
    property_name = None
    prop_slug = None

    if property_slug:
        result = await db.execute(select(Property).where(Property.slug == property_slug))
        prop = result.scalar_one_or_none()
        if prop:
            guesty_listing_id = prop.guesty_listing_id
            property_name = prop.name
            prop_slug = prop.slug

    skip = (page - 1) * limit

    try:
        data = await fetch_reservations(
            api_key,
            property_id=guesty_listing_id,
            status=status,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            skip=skip,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Guesty API error: {str(exc)}")

    raw_items = data.get("results") or data.get("data") or []
    total = data.get("count") or len(raw_items)

    # Build property name lookup for batch
    prop_cache: dict[str, tuple[str | None, str | None]] = {}
    if guesty_listing_id and property_name:
        prop_cache[guesty_listing_id] = (property_name, prop_slug)

    items = []
    for r in raw_items:
        listing_id = r.get("listingId")
        if listing_id and listing_id not in prop_cache:
            prop_result = await db.execute(
                select(Property).where(Property.guesty_listing_id == listing_id)
            )
            p = prop_result.scalar_one_or_none()
            prop_cache[listing_id] = (p.name if p else None, p.slug if p else None)
        pname, pslug = prop_cache.get(listing_id or "", (None, None))
        items.append(map_reservation(r, pname, pslug))

    return {"items": items, "total": total, "page": page, "limit": limit}
