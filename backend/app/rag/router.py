from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.shared.database import get_db
from app.rag.service import semantic_search

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    scope: str = "all"
    entity_id: str | None = None
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/search")
async def rag_search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    results = await semantic_search(
        db,
        query=body.query,
        scope=body.scope,  # type: ignore
        entity_id=body.entity_id,
        limit=body.limit,
    )
    return {"results": results}
