from collections.abc import AsyncGenerator

import anthropic

from app.credentials.service import get_credential
from app.shared.database import async_session

_client: anthropic.AsyncAnthropic | None = None


async def get_anthropic_client() -> anthropic.AsyncAnthropic | None:
    global _client
    if _client:
        return _client

    async with async_session() as db:
        api_key = await get_credential(db, "ANTHROPIC_API_KEY")

    if not api_key:
        return None

    _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


def reset_client():
    global _client
    _client = None


async def chat_stream(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    client = await get_anthropic_client()
    if not client:
        yield "Error: API de Anthropic no configurada. Configure la clave en Configuración > Integraciones."
        return

    async with client.messages.stream(
        model="claude-sonnet-4-20250514",
        system=system_prompt,
        messages=messages,
        max_tokens=max_tokens,
    ) as stream:
        async for text in stream.text_stream:
            yield text
