from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AuthorCanon(Base):
    """Author canon - complete published works of an author"""
    __tablename__ = "author_canons"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False, index=True)
    
    # Metadata
    total_works_count = Column(Integer, default=0)
    bibliography_source = Column(String(100), nullable=True)  # 'goodreads', 'wikipedia', 'manual'
    bibliography_last_updated = Column(DateTime(timezone=True), nullable=True)
    is_living = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    author = relationship("Author", back_populates="canons")
    works = relationship("AuthorWork", back_populates="canon", cascade="all, delete-orphan")
    user_progress = relationship("UserAuthorProgress", back_populates="canon", cascade="all, delete-orphan")


class AuthorWork(Base):
    """Individual work by an author (book, short story collection, etc.)"""
    __tablename__ = "author_works"
    
    id = Column(Integer, primary_key=True, index=True)
    author_canon_id = Column(Integer, ForeignKey("author_canons.id"), nullable=False, index=True)
    
    # Work details
    title = Column(String(500), nullable=False)
    publication_year = Column(Integer, nullable=True, index=True)
    work_type = Column(String(50), nullable=True)  # 'novel', 'short_story_collection', 'poetry', 'essay'
    page_count = Column(Integer, nullable=True)
    isbn_10 = Column(String(13), nullable=True)
    isbn_13 = Column(String(17), nullable=True)
    goodreads_id = Column(String(50), nullable=True)
    is_major_work = Column(Boolean, default=True)  # Exclude minor essays, articles
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    canon = relationship("AuthorCanon", back_populates="works")


class UserAuthorProgress(Base):
    """User's progress toward completing an author's canon"""
    __tablename__ = "user_author_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    author_canon_id = Column(Integer, ForeignKey("author_canons.id"), nullable=False, index=True)
    
    # Progress tracking
    books_read_count = Column(Integer, default=0)
    books_total_count = Column(Integer, default=0)
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Reading history
    first_book_read_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    first_read_date = Column(DateTime(timezone=True), nullable=True)
    most_recent_book_read_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    most_recent_read_date = Column(DateTime(timezone=True), nullable=True)
    
    # Goals
    is_goal = Column(Boolean, default=False)
    goal_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="author_progress")
    canon = relationship("AuthorCanon", back_populates="user_progress")
    first_book = relationship("Book", foreign_keys=[first_book_read_id])
    most_recent_book = relationship("Book", foreign_keys=[most_recent_book_read_id])
    
    # Unique constraint: one progress record per user per author canon
    __table_args__ = (
        UniqueConstraint('user_id', 'author_canon_id', name='uq_user_author_progress'),
    )


class CompletionAchievement(Base):
    """Achievement badges for completionist milestones"""
    __tablename__ = "completion_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_type = Column(String(100), nullable=False, index=True)
    # Achievement types: 'canon_complete', 'nearly_there', 'deep_dive', etc.
    
    author_canon_id = Column(Integer, ForeignKey("author_canons.id"), nullable=True)
    
    # Metadata (JSON-like data stored as text)
    achievement_metadata = Column(Text, nullable=True)  # Store JSON string for additional data
    
    # Timestamps
    awarded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="completion_achievements")
    canon = relationship("AuthorCanon")

