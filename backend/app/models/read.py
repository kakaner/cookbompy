from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.enums import ReadStatus


class Read(Base):
    """Read model - represents a single reading session of a book"""
    __tablename__ = "reads"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Reading dates
    date_started = Column(Date, nullable=True)
    date_finished = Column(Date, nullable=True, index=True)  # Indexed for semester queries
    
    # Reading status
    read_status = Column(String(50), nullable=False, default="UNREAD", index=True)  # UNREAD, READING, READ, DNF
    
    # Re-read flag
    is_reread = Column(Boolean, default=False)
    
    # Review and vibe
    review = Column(Text, nullable=True)  # User's review/notes for this read
    read_vibe_photo_url = Column(String(500), nullable=True)  # Photo taken during/after this read
    
    # Point calculation for this read
    base_points = Column(Integer, nullable=True)  # User override for base points (stored as integer * 100)
    base_points_overridden = Column(Boolean, default=False)
    calculated_points_allegory = Column(Integer, nullable=True)  # Stored as integer * 100
    calculated_points_reasonable = Column(Integer, nullable=True)  # Stored as integer * 100
    
    # Memorable flag (for semester features)
    is_memorable = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    book = relationship("Book", back_populates="reads")
    user = relationship("User", back_populates="reads")

