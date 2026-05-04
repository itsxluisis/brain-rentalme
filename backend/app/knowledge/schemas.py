import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBlockCreate(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    block_type: str
    title: str
    content: str
    language: str = "es"
    metadata_: dict = Field(default_factory=dict, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class KnowledgeBlockUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    block_type: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    metadata_: Optional[dict] = Field(default=None, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class KnowledgeBlockResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    block_type: str
    title: str
    content: str
    source: str
    language: str
    is_active: bool
    has_embedding: bool
    metadata_: dict = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RelationCreate(BaseModel):
    property_id: uuid.UUID
    system_id: uuid.UUID
    notes: Optional[str] = None
    config: dict = Field(default_factory=dict)


class RelationUpdate(BaseModel):
    notes: Optional[str] = None
    config: Optional[dict] = None


class RelationResponse(BaseModel):
    id: uuid.UUID
    property_id: uuid.UUID
    system_id: uuid.UUID
    notes: Optional[str] = None
    config: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
