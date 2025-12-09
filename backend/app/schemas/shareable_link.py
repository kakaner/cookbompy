from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ShareableLinkCreate(BaseModel):
    """Schema for creating a shareable link"""
    book_id: int


class ShareableLinkResponse(BaseModel):
    """Schema for shareable link response"""
    id: int
    book_id: int
    token: str
    expires_at: datetime
    view_count: int
    is_revoked: bool
    revoked_at: Optional[datetime] = None
    created_at: datetime
    share_url: str  # Full URL for sharing
    
    class Config:
        from_attributes = True


class SharedBookResponse(BaseModel):
    """Schema for book data accessible via shareable link (limited fields)"""
    id: int
    title: str
    author: str
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    description_source: Optional[str] = None
    genres: Optional[list] = None
    book_type: Optional[str] = None
    series: Optional[str] = None
    format: Optional[str] = None
    
    # Sharing user's review and rating only
    sharing_user: dict  # {id, username, display_name, profile_photo_url}
    sharing_user_review: Optional[str] = None
    sharing_user_rating: Optional[float] = None
    sharing_user_date_read: Optional[str] = None  # ISO format date string
    
    class Config:
        from_attributes = True

