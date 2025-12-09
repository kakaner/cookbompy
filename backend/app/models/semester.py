from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Semester(Base):
    """Semester model for organizing books by reading periods"""
    __tablename__ = "semesters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    semester_number = Column(Integer, nullable=False, index=True)
    custom_name = Column(String(100), nullable=True)
    
    # Unique constraint: each user can have only one record per semester
    __table_args__ = (
        UniqueConstraint('user_id', 'semester_number', name='uq_user_semester'),
    )
    
    # Relationships
    user = relationship("User", back_populates="semesters")
    comments = relationship("Comment", back_populates="semester", cascade="all, delete-orphan")

