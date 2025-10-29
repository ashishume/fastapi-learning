from sqlalchemy import Column, Integer, String, Text
from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False)
    slug = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=True)
