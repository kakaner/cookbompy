from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User model with authentication and preferences"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(72), nullable=False)  # bcrypt hash
    display_name = Column(String(100), nullable=True)  # Optional display name
    is_active = Column(Boolean, default=True)
    
    # User preferences
    profile_photo_url = Column(String(500), nullable=True)
    default_book_format = Column(String(50), nullable=True)  # Likely default format for new books (stored as string)
    color_theme = Column(String(50), nullable=True, default="terracotta")  # Color theme preference
    default_page_size = Column(Integer, nullable=True, default=50)  # Pagination preference
    default_home_page = Column(String(50), nullable=True, default="library")  # Default home page: library, semesters, statistics
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    books = relationship("Book", back_populates="user")
    semesters = relationship("Semester", back_populates="user")
    reads = relationship("Read", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    comment_reactions = relationship("CommentReaction", back_populates="user")
    author_progress = relationship("UserAuthorProgress", back_populates="user")
    completion_achievements = relationship("CompletionAchievement", back_populates="user")
    shareable_links = relationship("ShareableLink", back_populates="user", cascade="all, delete-orphan")

