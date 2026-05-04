import uuid
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Text, JSON, Uuid, LargeBinary, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.shared.database import TimestampedBase, Base
from sqlalchemy import func


class PropertySystemRelation(TimestampedBase):
    __tablename__ = "property_system_relations"

    property_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("properties.id", ondelete="CASCADE")
    )
    system_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("systems.id", ondelete="CASCADE")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, server_default="{}")

    property = relationship("Property", back_populates="system_relations")
    system = relationship("System", back_populates="property_relations")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    provider: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    listings_processed: Mapped[int] = mapped_column(Integer, server_default="0")
    blocks_created: Mapped[int] = mapped_column(Integer, server_default="0")
    blocks_updated: Mapped[int] = mapped_column(Integer, server_default="0")
    blocks_skipped: Mapped[int] = mapped_column(Integer, server_default="0")
    errors: Mapped[list] = mapped_column(JSON, server_default="[]")
    started_at: Mapped[datetime] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)


class ChatSession(TimestampedBase):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scope: Mapped[str] = mapped_column(String(30), server_default="all")
    scope_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("chat_sessions.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class ToolApiKey(Base):
    __tablename__ = "tool_api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255))
    key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ToolApiLog(Base):
    __tablename__ = "tool_api_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    key_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tool_api_keys.id"))
    endpoint: Mapped[str] = mapped_column(String(255))
    query_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    results_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class EncryptedCredential(Base):
    __tablename__ = "encrypted_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid()
    )
    service_name: Mapped[str] = mapped_column(String(100), unique=True)
    encrypted_value: Mapped[bytes] = mapped_column(LargeBinary)
    iv: Mapped[bytes] = mapped_column(LargeBinary)
    tag: Mapped[bytes] = mapped_column(LargeBinary)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AutomationTask(TimestampedBase):
    __tablename__ = "automation_tasks"

    name: Mapped[str] = mapped_column(String(255))
    action_type: Mapped[str] = mapped_column(String(30))
    schedule_type: Mapped[str] = mapped_column(String(20))
    schedule_config: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    last_run_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
