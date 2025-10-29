"""SQLAlchemy models for database tables."""

from sqlalchemy import Column, Integer, String, Text
from core.database import Base


class Item(Base):
    """
    Item model representing items in the database.
    
    Attributes:
        id: Primary key and unique identifier
        name: Name of the item (indexed for faster queries)
        description: Detailed description of the item
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the Item."""
        return f"<Item(id={self.id}, name='{self.name}')>"
