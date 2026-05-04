"""Guesty sync orchestrator. Fetches listings and maps them to properties + knowledge blocks."""

import asyncio
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.credentials.service import get_credential
from app.properties.models import Property
from app.properties.service import _unique_slug
from app.knowledge.models import KnowledgeBlock
from app.shared.models import SyncLog
from app.shared.embeddings import embed_text
from app.sync.providers.guesty import fetch_listings


def _map_type(listing: dict) -> str:
    title = (listing.get("title") or listing.get("nickname") or "").lower()
    for kw, ptype in [("hostel", "hostel_room"), ("villa", "villa"), ("casa", "apartment")]:
        if kw in title:
            return ptype
    return "apartment"


def _map_region(listing: dict) -> str:
    address = (listing.get("address") or {})
    city = (address.get("city") or "").lower()
    for kw, region in [
        ("asturias", "asturias"), ("oviedo", "asturias"), ("gijon", "asturias"),
        ("madrid", "madrid"), ("malaga", "malaga"), ("brava", "costa_brava"),
        ("ibiza", "ibiza"), ("manga", "la_manga"),
    ]:
        if kw in city:
            return region
    return "other"


def _build_description_content(listing: dict) -> str:
    parts = []
    addr = listing.get("address") or {}
    if addr.get("full"):
        parts.append(f"Dirección: {addr['full']}")
    if listing.get("accommodates"):
        parts.append(f"Capacidad: {listing['accommodates']} huéspedes")
    amenities = listing.get("amenities") or []
    if amenities:
        parts.append(f"Servicios: {', '.join(amenities[:20])}")
    if listing.get("houseRules"):
        parts.append(f"\nNormas de la casa:\n{listing['houseRules']}")
    if listing.get("checkInInstructions"):
        parts.append(f"\nInstrucciones de entrada:\n{listing['checkInInstructions']}")
    if listing.get("checkOutInstructions"):
        parts.append(f"\nInstrucciones de salida:\n{listing['checkOutInstructions']}")
    return "\n".join(parts)


async def run_guesty_sync(db: AsyncSession, triggered_by_id=None) -> SyncLog:
    api_key = await get_credential(db, "GUESTY_API_KEY")
    if not api_key:
        raise ValueError("GUESTY_API_KEY not configured")

    log = SyncLog(
        provider="guesty",
        status="running",
        started_at=datetime.now(UTC),
        errors=[],
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    listings_processed = 0
    blocks_created = 0
    blocks_updated = 0
    blocks_skipped = 0
    errors: list[str] = []

    skip = 0
    limit = 50

    while True:
        try:
            await asyncio.sleep(0.5)  # rate limit courtesy
            page = await fetch_listings(api_key, limit=limit, skip=skip)
        except Exception as exc:
            errors.append(f"Fetch error at skip={skip}: {str(exc)}")
            break

        items: list[dict] = page.get("results") or page.get("data") or []
        if not items:
            break

        for listing in items:
            try:
                guesty_id = listing.get("_id") or listing.get("id")
                if not guesty_id:
                    continue

                name = listing.get("nickname") or listing.get("title") or guesty_id
                addr = listing.get("address") or {}
                full_address = addr.get("full")
                capacity = listing.get("accommodates")
                bedrooms = listing.get("bedrooms")
                bathrooms = listing.get("bathrooms")

                result = await db.execute(
                    select(Property).where(Property.guesty_listing_id == guesty_id)
                )
                prop = result.scalar_one_or_none()

                if prop is None:
                    slug = await _unique_slug(db, name)
                    prop = Property(
                        name=name,
                        slug=slug,
                        type=_map_type(listing),
                        region=_map_region(listing),
                        address=full_address,
                        capacity=capacity,
                        bedrooms=bedrooms,
                        bathrooms=bathrooms,
                        guesty_listing_id=guesty_id,
                        status="active",
                    )
                    db.add(prop)
                    await db.flush()
                else:
                    prop.name = name
                    prop.address = full_address
                    prop.capacity = capacity
                    prop.bedrooms = bedrooms
                    prop.bathrooms = bathrooms

                description = _build_description_content(listing)

                block_result = await db.execute(
                    select(KnowledgeBlock).where(
                        KnowledgeBlock.entity_type == "property",
                        KnowledgeBlock.entity_id == prop.id,
                        KnowledgeBlock.block_type == "description",
                        KnowledgeBlock.source == "guesty_sync",
                    )
                )
                block = block_result.scalar_one_or_none()

                if block is None:
                    block = KnowledgeBlock(
                        entity_type="property",
                        entity_id=prop.id,
                        block_type="description",
                        title=f"Descripción — {name}",
                        content=description,
                        source="guesty_sync",
                        language="es",
                        is_active=True,
                    )
                    db.add(block)
                    blocks_created += 1
                elif block.source == "guesty_sync":
                    # Only update if not manually edited
                    block.content = description
                    block.title = f"Descripción — {name}"
                    blocks_updated += 1
                else:
                    blocks_skipped += 1

                listings_processed += 1

            except Exception as exc:
                errors.append(f"Error processing listing {listing.get('_id', '?')}: {str(exc)}")

        await db.commit()
        skip += limit
        if len(items) < limit:
            break

    log.status = "completed" if not errors else "failed"
    log.listings_processed = listings_processed
    log.blocks_created = blocks_created
    log.blocks_updated = blocks_updated
    log.blocks_skipped = blocks_skipped
    log.errors = errors[:50]  # cap to avoid huge JSONB
    log.completed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(log)
    return log
