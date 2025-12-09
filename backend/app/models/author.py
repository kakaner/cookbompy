from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Author(Base):
    """Author model - first-class entity for authors"""
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, unique=True, index=True)
    normalized_name = Column(String(500), nullable=False, index=True)  # For normalization/duplicate detection
    
    # Optional metadata
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)
    nationality = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)
    biography = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    books = relationship("Book", back_populates="author_obj")
    canons = relationship("AuthorCanon", back_populates="author")

