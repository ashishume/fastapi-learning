"""Pydantic schemas for item validation and serialization."""

from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ItemCreate(BaseModel):
    """Schema for creating a new item."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the item",
        examples=["Laptop", "Phone"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="A description of the item",
        examples=["A high-performance laptop"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop",
                "description": "A high-performance laptop for developers"
            }
        }
    )


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="The name of the item"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="A description of the item"
    )


class ItemResponse(BaseModel):
    """Schema for item response."""
    
    id: int = Field(..., description="The unique identifier of the item")
    name: str = Field(..., description="The name of the item")
    description: Optional[str] = Field(None, description="The description of the item")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "A high-performance laptop for developers"
            }
        }
    )


class ItemListResponse(BaseModel):
    """Schema for list of items response."""
    
    items: List[ItemResponse] = Field(
        ...,
        description="List of items"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Laptop",
                        "description": "A high-performance laptop"
                    },
                    {
                        "id": 2,
                        "name": "Phone",
                        "description": "A smartphone"
                    }
                ]
            }
        }
    )
