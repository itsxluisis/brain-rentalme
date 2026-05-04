import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SystemCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    has_api: bool = False
    api_docs_url: Optional[str] = None
    status: str = "active"
    tags: list = Field(default_factory=list)
    metadata_: dict = Field(default_factory=dict, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class SystemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    has_api: Optional[bool] = None
    api_docs_url: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list] = None
    metadata_: Optional[dict] = Field(default=None, alias="metadata_")

    model_config = ConfigDict(populate_by_name=True)


class SystemSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category: str
    has_api: bool
    status: str
    tags: list = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemDetail(SystemSummary):
    description: Optional[str] = None
    website_url: Optional[str] = None
    api_docs_url: Optional[str] = None
    metadata_: dict = Field(default_factory=dict, alias="metadata_")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
