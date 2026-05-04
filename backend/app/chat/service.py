"""Chat session and message CRUD."""

import uuid
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import ChatSession, ChatMessage


async def list_sessions(db: AsyncSession, user_id: str) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == uuid.UUID(user_id), ChatSession.is_active == True)
        .order_by(desc(ChatSession.updated_at))
        .limit(50)
    )
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: str, user_id: str) -> Optional[ChatSession]:
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == uuid.UUID(session_id),
            ChatSession.user_id == uuid.UUID(user_id),
        )
    )
    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession,
    user_id: str,
    scope: str = "all",
    scope_entity_id: Optional[str] = None,
) -> ChatSession:
    session = ChatSession(
        user_id=uuid.UUID(user_id),
        scope=scope,
        scope_entity_id=uuid.UUID(scope_entity_id) if scope_entity_id else None,
        is_active=True,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def update_session_title(db: AsyncSession, session_id: str, user_id: str, title: str) -> Optional[ChatSession]:
    session = await get_session(db, session_id, user_id)
    if not session:
        return None
    session.title = title
    await db.commit()
    await db.refresh(session)
    return session


async def delete_session(db: AsyncSession, session_id: str, user_id: str) -> bool:
    session = await get_session(db, session_id, user_id)
    if not session:
        return False
    session.is_active = False
    await db.commit()
    return True


async def get_session_messages(db: AsyncSession, session_id: str) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == uuid.UUID(session_id))
        .order_by(ChatMessage.created_at)
        .limit(50)
    )
    return list(result.scalars().all())


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    sources: Optional[list] = None,
) -> ChatMessage:
    msg = ChatMessage(
        session_id=uuid.UUID(session_id),
        role=role,
        content=content,
        sources=sources,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def auto_title_session(db: AsyncSession, session: ChatSession, first_message: str):
    if not session.title:
        title = first_message[:60].strip()
        if len(first_message) > 60:
            title += "…"
        session.title = title
        await db.commit()
