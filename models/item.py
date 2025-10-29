"""SQLAlchemy models for database tables."""

from sqlalchemy import Column, Integer, String, Text
from core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(index=True, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}')>"
