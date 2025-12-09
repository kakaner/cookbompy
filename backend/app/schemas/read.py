from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from app.schemas.comment import UserBasic


class ReadBase(BaseModel):
    """Base read schema"""
    date_started: Optional[date] = None
    date_finished: Optional[date] = None
    read_status: str = "UNREAD"  # UNREAD, READING, READ, DNF
    is_reread: bool = False
    review: Optional[str] = None
    read_vibe_photo_url: Optional[str] = Field(None, max_length=500)
    base_points: Optional[float] = Field(None, description="Override base points (will set base_points_overridden=True)")
    is_memorable: bool = False
    rating: Optional[float] = Field(None, description="Rating from 0.5 to 10.0 in 0.5 increments")
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None:
            if v < 0.5 or v > 10.0:
                raise ValueError('Rating must be between 0.5 and 10.0')
            # Check if it's a valid 0.5 increment
            if (v * 2) % 1 != 0:
                raise ValueError('Rating must be in 0.5 increments (0.5, 1.0, 1.5, ..., 10.0)')
        return v


class ReadCreate(ReadBase):
    """Schema for creating a new read"""
    pass


class ReadUpdate(BaseModel):
    """Schema for updating a read (all fields optional)"""
    date_started: Optional[date] = None
    date_finished: Optional[date] = None
    read_status: Optional[str] = None
    is_reread: Optional[bool] = None
    review: Optional[str] = None
    read_vibe_photo_url: Optional[str] = Field(None, max_length=500)
    base_points: Optional[float] = Field(None, description="Override base points")
    is_memorable: Optional[bool] = None
    rating: Optional[float] = Field(None, description="Rating from 0.5 to 10.0 in 0.5 increments")
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None:
            if v < 0.5 or v > 10.0:
                raise ValueError('Rating must be between 0.5 and 10.0')
            # Check if it's a valid 0.5 increment
            if (v * 2) % 1 != 0:
                raise ValueError('Rating must be in 0.5 increments (0.5, 1.0, 1.5, ..., 10.0)')
        return v


class ReadPoints(BaseModel):
    """Point calculation breakdown for a read"""
    base: float
    base_overridden: bool
    length_addons: float
    reread_multiplier: float
    bompyallegory: float
    bompyreasonable: float
    breakdown: str


class ReadResponse(ReadBase):
    """Schema for read response"""
    id: int
    book_id: int
    user_id: int
    user: Optional[UserBasic] = None  # User who made this read
    base_points: Optional[float] = None
    base_points_overridden: bool = False
    calculated_points_allegory: Optional[float] = None
    calculated_points_reasonable: Optional[float] = None
    points: Optional[dict] = None  # Calculated breakdown
    rating: Optional[float] = None  # Rating from 0.5 to 10.0
    comment_count: Optional[int] = 0  # Number of comments on this read
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Convert integer points to float for response
        if hasattr(obj, 'base_points') and obj.base_points is not None:
            obj.base_points = obj.base_points / 100.0 if obj.base_points else None
        if hasattr(obj, 'calculated_points_allegory') and obj.calculated_points_allegory is not None:
            obj.calculated_points_allegory = obj.calculated_points_allegory / 100.0 if obj.calculated_points_allegory else None
        if hasattr(obj, 'calculated_points_reasonable') and obj.calculated_points_reasonable is not None:
            obj.calculated_points_reasonable = obj.calculated_points_reasonable / 100.0 if obj.calculated_points_reasonable else None
        return super().model_validate(obj, **kwargs)

