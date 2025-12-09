from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Comment(Base):
    """Comment model - comments on reads or semesters"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    read_id = Column(Integer, ForeignKey("reads.id", ondelete="CASCADE"), nullable=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    
    content = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    read = relationship("Read", back_populates="comments")
    semester = relationship("Semester", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent_comment = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent_comment", cascade="all, delete-orphan")
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")


class CommentReaction(Base):
    """Comment reaction model - emoji reactions on comments"""
    __tablename__ = "comment_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_type = Column(String(20), nullable=False)  # 'heart', 'thumbs_up', 'laugh', 'think', 'target', 'book', 'clap'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User", back_populates="comment_reactions")

