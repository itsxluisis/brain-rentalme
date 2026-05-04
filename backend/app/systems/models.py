from typing import Optional

from sqlalchemy import String, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import TimestampedBase


class System(TimestampedBase):
    __tablename__ = "systems"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    category: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    has_api: Mapped[bool] = mapped_column(Boolean, server_default="false")
    api_docs_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), server_default="active")
    tags: Mapped[list] = mapped_column(JSON, server_default="[]")
    metadata_: Mapped[dict] = mapped_column("metadata_", JSON, server_default="{}")

    property_relations = relationship(
        "PropertySystemRelation", back_populates="system", cascade="all, delete-orphan"
    )
