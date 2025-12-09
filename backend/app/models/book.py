from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.enums import Format, BookType, ReadStatus, DescriptionSource


class Book(Base):
    """Book model with full metadata"""
    __tablename__ = "books"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Core fields
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(500), nullable=False, index=True)
    isbn_10 = Column(String(13), nullable=True, index=True)
    isbn_13 = Column(String(17), nullable=True, index=True)
    publication_date = Column(Date, nullable=True)
    publisher = Column(String(255), nullable=True)
    edition = Column(String(100), nullable=True)
    page_count = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True, default="en")
    cover_image_url = Column(String(500), nullable=True)
    
    # Extended fields
    description = Column(Text, nullable=True)
    description_source = Column(SQLEnum(DescriptionSource), nullable=True)
    genres = Column(JSON, nullable=True)  # Array of genre strings
    book_type = Column(SQLEnum(BookType), nullable=True, index=True)
    series = Column(String(255), nullable=True)
    series_number = Column(Integer, nullable=True)
    original_title = Column(String(500), nullable=True)
    translator = Column(String(255), nullable=True)
    illustrator = Column(String(255), nullable=True)
    awards = Column(Text, nullable=True)  # Can be multiple, store as text
    
    # User-managed fields
    acquisition_date = Column(Date, nullable=True)
    acquisition_source = Column(String(255), nullable=True)
    physical_location = Column(String(255), nullable=True)
    condition_notes = Column(Text, nullable=True)
    lending_status = Column(String(255), nullable=True)
    
    # Format (required)
    format = Column(SQLEnum(Format), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="books")
    reads = relationship("Read", back_populates="book", cascade="all, delete-orphan")
    shareable_links = relationship("ShareableLink", back_populates="book", cascade="all, delete-orphan")

