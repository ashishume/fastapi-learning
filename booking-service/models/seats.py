from datetime import date
import datetime
from enum import Enum
from sqlalchemy import UUID, Column, Date, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from database import Base
import uuid
from sqlalchemy.orm import relationship


class SeatType(str, Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    VIP = "vip"
    RECLINER = "recliner"



class Seat(Base):

    __tablename__ = "seats"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    # theater_id = Column(UUID(as_uuid=True), ForeignKey("theaters.id"), nullable=False)
    showing_id = Column(UUID(as_uuid=True), ForeignKey("showings.id"), nullable=False)
    seat_number = Column(String(255), nullable=False)
    row = Column(String(255), nullable=False) # A-Z
    column = Column(String(255), nullable=False) # 1-100
    seat_type = Column(SQLEnum(SeatType), nullable=False,default=SeatType.REGULAR) # regular, premium, vip, recliner
    
    
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,onupdate=datetime.datetime.utcnow)

    # Relationships
    # theater = relationship("Theater", back_populates="seats")
    bookings = relationship("Booking", back_populates="seats")
    showing = relationship("Showing", back_populates="seats", primaryjoin="Seat.showing_id == Showing.id")
    

    # TODO: Remove this once the schema is updated to use the movie and theater relationships
    # @property
    # def movie(self):
    #     """Expose movie through showing relationship for SeatResponse schema"""
    #     return self.showing.movie if self.showing else None
    
    # @property
    # def theater(self):
    #     """Expose theater through showing relationship for SeatResponse schema"""
    #     return self.showing.theater if self.showing else None