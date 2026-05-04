"""RAG pipeline: embed query → pgvector cosine search → top-K results."""

from typing import Literal
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.models import KnowledgeBlock
from app.properties.models import Property
from app.systems.models import System
from app.shared.embeddings import embed_text


async def semantic_search(
    db: AsyncSession,
    query: str,
    scope: Literal["all", "properties", "systems"] = "all",
    entity_id: str | None = None,
    limit: int = 5,
) -> list[dict]:
    query_vector = await embed_text(query)
    if not query_vector:
        return []

    vector_str = f"[{','.join(str(x) for x in query_vector)}]"

    filters = ["kb.content_vector IS NOT NULL", "kb.is_active = TRUE"]
    if scope == "properties":
        filters.append("kb.entity_type = 'property'")
    elif scope == "systems":
        filters.append("kb.entity_type = 'system'")
    if entity_id:
        filters.append(f"kb.entity_id = '{entity_id}'")

    where_clause = " AND ".join(filters)

    sql = text(f"""
        SELECT
            kb.id,
            kb.entity_type,
            kb.entity_id,
            kb.block_type,
            kb.title,
            kb.content,
            1 - (kb.content_vector <=> '{vector_str}'::vector) AS score
        FROM knowledge_blocks kb
        WHERE {where_clause}
        ORDER BY kb.content_vector <=> '{vector_str}'::vector
        LIMIT :limit
    """)

    result = await db.execute(sql, {"limit": limit})
    rows = result.fetchall()

    results = []
    for row in rows:
        entity_name = None
        if row.entity_type == "property":
            prop = await db.get(Property, row.entity_id)
            entity_name = prop.name if prop else None
        elif row.entity_type == "system":
            sys = await db.get(System, row.entity_id)
            entity_name = sys.name if sys else None

        results.append({
            "block_id": str(row.id),
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id),
            "entity_name": entity_name,
            "block_type": row.block_type,
            "title": row.title,
            "content_preview": row.content[:300] if row.content else "",
            "score": round(float(row.score), 4),
        })

    return results


def build_context_prompt(results: list[dict], query: str) -> str:
    context_parts = []
    for r in results:
        context_parts.append(
            f"[{r['entity_type'].upper()}: {r['entity_name']} — {r['title']}]\n{r['content_preview']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    return f"""Eres un asistente de conocimiento para RentalMe.es, una empresa española de gestión de alquileres vacacionales.

Responde en español. Sé preciso y conciso. Si la información no está en el contexto, dilo claramente.

CONTEXTO RELEVANTE:
{context}

PREGUNTA DEL USUARIO: {query}"""
