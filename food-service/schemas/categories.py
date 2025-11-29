from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class CategorySchema(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    created_at: datetime
    updated_at: datetime


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
