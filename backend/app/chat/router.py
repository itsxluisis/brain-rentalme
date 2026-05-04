"""Chat HTTP endpoints (session CRUD) + WebSocket streaming endpoint."""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_token
from app.auth.models import User
from app.chat import service as chat_service
from app.rag.service import semantic_search, build_context_prompt
from app.shared.database import get_db, async_session
from app.shared.llm import chat_stream

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def _serialize_session(s) -> dict:
    return {
        "id": str(s.id),
        "title": s.title,
        "scope": s.scope,
        "scope_entity_id": str(s.scope_entity_id) if s.scope_entity_id else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _serialize_message(m) -> dict:
    return {
        "id": str(m.id),
        "role": m.role,
        "content": m.content,
        "sources": m.sources,
        "created_at": m.created_at.isoformat(),
    }


class SessionCreate(BaseModel):
    scope: str = "all"
    scope_entity_id: str | None = None


class SessionRename(BaseModel):
    title: str


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = await chat_service.list_sessions(db, str(current_user.id))
    return [_serialize_session(s) for s in sessions]


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await chat_service.create_session(
        db, str(current_user.id), scope=body.scope, scope_entity_id=body.scope_entity_id
    )
    return _serialize_session(session)


@router.patch("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    body: SessionRename,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await chat_service.update_session_title(db, session_id, str(current_user.id), body.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_session(session)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await chat_service.delete_session(db, session_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await chat_service.get_session(db, session_id, str(current_user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = await chat_service.get_session_messages(db, session_id)
    return [_serialize_message(m) for m in messages]


@router.websocket("/sessions/{session_id}/ws")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for streaming chat. Auth via cookie on handshake."""
    await websocket.accept()

    # Validate JWT from cookie
    token = websocket.cookies.get("brain_token")
    if not token:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload.get("sub")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_message = data.get("message", "").strip()

            if not user_message:
                continue

            # Use a fresh DB session per message
            async with async_session() as db:
                session = await chat_service.get_session(db, session_id, user_id)
                if not session:
                    await websocket.send_text(json.dumps({"error": "Session not found"}))
                    break

                # Auto-title on first message
                await chat_service.auto_title_session(db, session, user_message)

                # Save user message
                await chat_service.save_message(db, session_id, "user", user_message)

                # RAG search
                results = await semantic_search(
                    db,
                    query=user_message,
                    scope=session.scope,  # type: ignore
                    entity_id=str(session.scope_entity_id) if session.scope_entity_id else None,
                    limit=5,
                )

                # Build context and stream
                system_prompt = build_context_prompt(results, user_message)

                # Send sources first
                await websocket.send_text(json.dumps({
                    "type": "sources",
                    "sources": results,
                }))

                # Stream Claude response
                full_response = ""
                async for chunk in chat_stream(system_prompt, [{"role": "user", "content": user_message}]):
                    full_response += chunk
                    await websocket.send_text(json.dumps({
                        "type": "chunk",
                        "text": chunk,
                    }))

                # Signal completion
                await websocket.send_text(json.dumps({"type": "done"}))

                # Persist assistant response
                await chat_service.save_message(db, session_id, "assistant", full_response, sources=results)

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": "Error interno del servidor"}))
        except Exception:
            pass
