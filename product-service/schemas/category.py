from typing import List, Optional
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


class CategoryResponse(BaseModel):
    id: int = Field(..., description="ids")
    name: str = Field(..., description="category name")
    slug: str = Field(..., description="slug")
    description: Optional[str] = Field(None, description="description")

    class Config:
        from_attributes = True


class CategoryResponseList(BaseModel):
    categories: List[CategoryResponse] = Field(..., description="list of categories")

    class Config:
        from_attributes = True
