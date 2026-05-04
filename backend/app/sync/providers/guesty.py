import asyncio
import httpx
from typing import Any


GUESTY_BASE_URL = "https://open-api.guesty.com/v1"


async def test_guesty_connection(api_key: str) -> dict[str, str]:
    """Test connectivity to Guesty API with the given key."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{GUESTY_BASE_URL}/listings", headers=headers, params={"limit": 1})
        if response.status_code == 200:
            return {"status": "ok", "message": "Conexión a Guesty establecida correctamente"}
        if response.status_code == 401:
            return {"status": "error", "message": "API key inválida o sin permisos"}
        return {"status": "error", "message": f"Guesty respondió con código {response.status_code}"}
    except httpx.TimeoutException:
        return {"status": "error", "message": "Timeout conectando a Guesty"}
    except Exception as exc:
        return {"status": "error", "message": f"Error de conexión: {str(exc)}"}


async def fetch_listings(api_key: str, limit: int = 100, skip: int = 0) -> dict[str, Any]:
    """Fetch listings from Guesty API with pagination."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    params = {"limit": limit, "skip": skip, "fields": "nickname,title,address,accommodates,bedrooms,bathrooms,amenities,houseRules,checkInInstructions,checkOutInstructions"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{GUESTY_BASE_URL}/listings", headers=headers, params=params)
    response.raise_for_status()
    return response.json()
