from openai import AsyncOpenAI

from app.credentials.service import get_credential
from app.shared.database import async_session

_client: AsyncOpenAI | None = None


async def get_openai_client() -> AsyncOpenAI | None:
    global _client
    if _client:
        return _client

    async with async_session() as db:
        api_key = await get_credential(db, "OPENAI_API_KEY")

    if not api_key:
        return None

    _client = AsyncOpenAI(api_key=api_key)
    return _client


def reset_client():
    global _client
    _client = None


async def embed_text(text: str) -> list[float] | None:
    client = await get_openai_client()
    if not client:
        return None

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def embed_texts(texts: list[str]) -> list[list[float]] | None:
    client = await get_openai_client()
    if not client:
        return None

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]
