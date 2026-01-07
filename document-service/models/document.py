from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
import uuid
import datetime


class Document(Base):

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True, default=None
    )
    content = Column(Text, nullable=True)
    document_type = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    workspace = relationship("Workspace", back_populates="documents")
