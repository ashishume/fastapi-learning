from sqlalchemy import UUID, Column, ForeignKey, DateTime
from database import Base
import uuid
import datetime
from sqlalchemy.orm import relationship

class LockedSeat(Base):
    __tablename__ = "locked_seats"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(minutes=10))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,onupdate=datetime.datetime.utcnow)


    # Relationships
    seat = relationship("Seat", back_populates="locked_seats")
    showing = relationship("Showing", back_populates="locked_seats")