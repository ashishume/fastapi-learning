from sqlalchemy import Column, ForeignKey, Text, DateTime, UUID
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base
from sqlalchemy.orm import relationship
import uuid
import datetime


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    documents = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )
    members = relationship(
        "WorkspaceMembers", back_populates="workspace", cascade="all, delete-orphan"
    )
