"""Tool API: external endpoints for AI agent consumption. Authentication via SHA-256 hashed API keys."""

import hashlib
import os
import secrets
import time
import uuid
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.knowledge.models import KnowledgeBlock
from app.properties.models import Property
from app.rag.service import semantic_search
from app.shared.database import get_db
from app.shared.models import PropertySystemRelation, ToolApiKey, ToolApiLog
from app.systems.models import System as SystemModel

# ─── API Key Management ─────────────────────────────────────────────────────

key_mgmt_router = APIRouter(prefix="/api/v1/api-keys", tags=["api-keys"])


@key_mgmt_router.get("")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(ToolApiKey).order_by(ToolApiKey.created_at))
    keys = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "name": k.name,
            "is_active": k.is_active,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat(),
        }
        for k in keys
    ]


class KeyCreate(BaseModel):
    name: str


@key_mgmt_router.post("", status_code=201)
async def create_api_key(
    body: KeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    raw_key = f"brain_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key = ToolApiKey(
        name=body.name,
        key_hash=key_hash,
        is_active=True,
        created_by=current_user.id,
    )
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return {
        "id": str(key.id),
        "name": key.name,
        "key": raw_key,  # shown ONCE
        "created_at": key.created_at.isoformat(),
    }


@key_mgmt_router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(ToolApiKey).where(ToolApiKey.id == uuid.UUID(key_id)))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.is_active = False
    await db.commit()


# ─── Tool API Auth Dependency ─────────────────────────────────────────────────

async def verify_tool_key(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> ToolApiKey:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    raw_key = authorization[7:]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    result = await db.execute(
        select(ToolApiKey).where(ToolApiKey.key_hash == key_hash, ToolApiKey.is_active == True)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    key.last_used_at = datetime.now(UTC)
    await db.commit()
    return key


# ─── Tool API Endpoints ────────────────────────────────────────────────────────

tool_router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


async def _log_call(db: AsyncSession, key_id, endpoint: str, query_params: dict, response_ms: int, results_count: int):
    log = ToolApiLog(
        key_id=key_id,
        endpoint=endpoint,
        query_params=query_params,
        response_ms=response_ms,
        results_count=results_count,
    )
    db.add(log)
    await db.commit()


@tool_router.get("/search")
async def tool_search(
    q: str = "",
    entity_type: str = "all",
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    if not q:
        return {"results": []}
    results = await semantic_search(db, query=q, scope=entity_type, limit=min(limit, 20))
    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/search", {"q": q, "entity_type": entity_type}, ms, len(results))
    return {"results": results}


@tool_router.get("/property/{slug}")
async def tool_property(
    slug: str,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    result = await db.execute(select(Property).where(Property.slug == slug))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/property", {"slug": slug}, ms, 1)
    return {
        "id": str(prop.id),
        "name": prop.name,
        "slug": prop.slug,
        "type": prop.type,
        "region": prop.region,
        "address": prop.address,
        "capacity": prop.capacity,
        "bedrooms": prop.bedrooms,
        "bathrooms": prop.bathrooms,
        "status": prop.status,
        "tags": prop.tags,
    }


@tool_router.get("/system/{slug}")
async def tool_system(
    slug: str,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    result = await db.execute(select(SystemModel).where(SystemModel.slug == slug))
    system = result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/system", {"slug": slug}, ms, 1)
    return {
        "id": str(system.id),
        "name": system.name,
        "slug": system.slug,
        "category": system.category,
        "description": system.description,
        "has_api": system.has_api,
        "website_url": system.website_url,
        "status": system.status,
    }


@tool_router.get("/property/{slug}/systems")
async def tool_property_systems(
    slug: str,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    prop_result = await db.execute(select(Property).where(Property.slug == slug))
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    rel_result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.property_id == prop.id)
    )
    relations = rel_result.scalars().all()

    systems = []
    for rel in relations:
        sys_result = await db.execute(select(SystemModel).where(SystemModel.id == rel.system_id))
        system = sys_result.scalar_one_or_none()
        if system:
            systems.append({
                "system_id": str(system.id),
                "name": system.name,
                "slug": system.slug,
                "category": system.category,
                "notes": rel.notes,
                "config": rel.config,
            })

    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/property/systems", {"slug": slug}, ms, len(systems))
    return {"property": prop.name, "systems": systems}


@tool_router.get("/system/{slug}/properties")
async def tool_system_properties(
    slug: str,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    sys_result = await db.execute(select(SystemModel).where(SystemModel.slug == slug))
    system = sys_result.scalar_one_or_none()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    rel_result = await db.execute(
        select(PropertySystemRelation).where(PropertySystemRelation.system_id == system.id)
    )
    relations = rel_result.scalars().all()

    props = []
    for rel in relations:
        prop_result = await db.execute(select(Property).where(Property.id == rel.property_id))
        prop = prop_result.scalar_one_or_none()
        if prop:
            props.append({
                "property_id": str(prop.id),
                "name": prop.name,
                "slug": prop.slug,
                "region": prop.region,
                "status": prop.status,
                "notes": rel.notes,
            })

    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/system/properties", {"slug": slug}, ms, len(props))
    return {"system": system.name, "properties": props}


class RagRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    scope: str = "all"
    limit: int = Field(default=5, ge=1, le=20)


@tool_router.post("/rag")
async def tool_rag(
    body: RagRequest,
    db: AsyncSession = Depends(get_db),
    key: ToolApiKey = Depends(verify_tool_key),
):
    t0 = time.monotonic()
    results = await semantic_search(db, query=body.query, scope=body.scope, limit=body.limit)
    ms = int((time.monotonic() - t0) * 1000)
    await _log_call(db, key.id, "/tools/rag", {"query": body.query}, ms, len(results))
    return {"query": body.query, "results": results}
