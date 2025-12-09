from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import secrets


class ShareableLink(Base):
    """Shareable link model for temporary external sharing of book pages"""
    __tablename__ = "shareable_links"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Unique token for the link
    token = Column(String(64), nullable=False, unique=True, index=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Tracking
    view_count = Column(Integer, default=0, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    book = relationship("Book", back_populates="shareable_links")
    user = relationship("User", back_populates="shareable_links")
    
    @staticmethod
    def generate_token():
        """Generate a secure random token for the shareable link"""
        return secrets.token_urlsafe(48)  # 64 characters when base64 encoded
    
    def is_expired(self):
        """Check if the link has expired"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Handle both timezone-aware and timezone-naive datetimes
        # SQLite may return timezone-naive datetimes even if defined as timezone-aware
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            # If timezone-naive, assume UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return now > expires_at
    
    def is_valid(self):
        """Check if the link is valid (not expired and not revoked)"""
        return not self.is_expired() and not self.is_revoked

