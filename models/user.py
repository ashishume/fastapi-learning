from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from core.database import Base


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), index=True, unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), nullable=False, default=Role.USER)
