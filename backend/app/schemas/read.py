from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


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
    base_points: Optional[float] = None
    base_points_overridden: bool = False
    calculated_points_allegory: Optional[float] = None
    calculated_points_reasonable: Optional[float] = None
    points: Optional[dict] = None  # Calculated breakdown
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

