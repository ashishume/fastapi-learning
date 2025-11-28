from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import UUID

class CategorySchema(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    image: Optional[str] = Field(None, min_length=1, max_length=255)
    created_at: datetime
    updated_at: datetime


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    image: Optional[str] = Field(None, min_length=1, max_length=255)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    image: Optional[str] = Field(None, min_length=1, max_length=255)
