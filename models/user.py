from sqlalchemy import Column, Integer, String
from core.database import Base


class User(Base):

    __tablename__ = "users"
    id: int = Column(Integer, index=True, primary_key=True)
    email: str = Column(index=True, unique=True, nullable=False)
    hashed_password: str = Column(min_length=4, max_length=50, nullable=False)
    token: str = Column(nullable=False)
    name: str = Column(nullable=False)
