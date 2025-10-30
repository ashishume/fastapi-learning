"""Pydantic schemas for item validation and serialization."""

from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict
from schemas.category import CategoryResponse


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the item",
        examples=["Laptop", "Phone"],
    )
    description: Optional[str] = Field(
        None,
        # max_length=500,
        description="A description of the item",
        examples=["A high-performance laptop"],
    )

    category_id: int = Field(..., description="The category ID of the item")


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="The name of the item"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="A description of the item"
    )

    category_id: Optional[int] = Field(None, description="The category ID of the item")


class ItemResponse(BaseModel):
    """Schema for item response."""

    id: int = Field(..., description="The unique identifier of the item")
    name: str = Field(..., description="The name of the item")
    description: Optional[str] = Field(None, description="The description of the item")
    category_id: int = Field(..., description="The category ID of the item")
    category: CategoryResponse = Field(..., description="The category details")

    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Schema for list of items response."""

    items: List[ItemResponse] = Field(..., description="List of items")
