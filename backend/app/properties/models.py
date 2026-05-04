from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Integer, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import TimestampedBase


class Property(TimestampedBase):
    __tablename__ = "properties"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    type: Mapped[str] = mapped_column(String(30))
    region: Mapped[str] = mapped_column(String(30))
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    guesty_listing_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    cloudbeds_property_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), server_default="active")
    tags: Mapped[list] = mapped_column(JSON, server_default="[]")
    metadata_: Mapped[dict] = mapped_column("metadata_", JSON, server_default="{}")

    system_relations = relationship(
        "PropertySystemRelation", back_populates="property", cascade="all, delete-orphan"
    )
