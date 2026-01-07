from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List


class DocumentCreate(BaseModel):
    name: str
    description: str
    workspace_id: UUID
    content: str
    document_type: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: str
    workspace_id: UUID
    content: str
    document_type: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    documents: List[DocumentResponse]
