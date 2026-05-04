import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyCreate(BaseModel):
    name: str
    type: str
    region: str
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    capacity: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    guesty_listing_id: Optional[str] = None
    cloudbeds_property_id: Optional[str] = None
    status: str = "active"
    tags: list = Field(default_factory=list)
    metadata_: dict = Field(default_factory=dict, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    capacity: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[list] = None
    metadata_: Optional[dict] = Field(default=None, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class PropertySummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    type: str
    region: str
    status: str
    capacity: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    tags: list = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PropertyDetail(PropertySummary):
    address: Optional[str] = None
    guesty_listing_id: Optional[str] = None
    cloudbeds_property_id: Optional[str] = None
    metadata_: dict = Field(default_factory=dict, alias="metadata_")
