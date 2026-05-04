import uuid
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Boolean, Text, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import TimestampedBase


class KnowledgeBlock(TimestampedBase):
    __tablename__ = "knowledge_blocks"

    entity_type: Mapped[str] = mapped_column(String(20))
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    block_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    content_vector = mapped_column(Vector(1536), nullable=True)
    source: Mapped[str] = mapped_column(String(20), server_default="manual")
    language: Mapped[str] = mapped_column(String(10), server_default="es")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    metadata_: Mapped[dict] = mapped_column("metadata_", JSON, server_default="{}")

    @property
    def has_embedding(self) -> bool:
        return self.content_vector is not None
