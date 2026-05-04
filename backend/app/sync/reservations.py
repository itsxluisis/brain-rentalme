"""Read-only reservations from Guesty API, cached 5 minutes in memory."""

import time
from typing import Any

import httpx

GUESTY_BASE_URL = "https://open-api.guesty.com/v1"

_cache: dict[str, Any] = {}
_CACHE_TTL = 300  # 5 minutes


async def fetch_reservations(
    api_key: str,
    property_id: str | None = None,
    status: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> dict:
    cache_key = f"{property_id}:{status}:{from_date}:{to_date}:{limit}:{skip}"
    cached = _cache.get(cache_key)
    if cached and time.time() - cached["ts"] < _CACHE_TTL:
        return cached["data"]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    params: dict = {"limit": limit, "skip": skip}
    if status:
        params["status"] = status
    if from_date:
        params["checkIn[$gte]"] = from_date
    if to_date:
        params["checkOut[$lte]"] = to_date
    if property_id:
        params["listingId"] = property_id

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{GUESTY_BASE_URL}/reservations", headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    _cache[cache_key] = {"data": data, "ts": time.time()}
    return data


def map_reservation(r: dict, property_name: str | None, property_slug: str | None) -> dict:
    return {
        "id": r.get("_id") or r.get("id", ""),
        "guest_name": (r.get("guest") or {}).get("fullName") or "Huésped",
        "property_name": property_name or r.get("listingId", ""),
        "property_slug": property_slug,
        "check_in": r.get("checkIn"),
        "check_out": r.get("checkOut"),
        "status": r.get("status", ""),
        "channel": (r.get("source") or {}).get("name") or r.get("source", ""),
        "guests_count": r.get("guestsCount", 1),
    }
