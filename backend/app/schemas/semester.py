from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class SemesterBase(BaseModel):
    """Base semester schema"""
    semester_number: int
    custom_name: Optional[str] = Field(None, max_length=100)


class SemesterCreate(SemesterBase):
    """Schema for creating a semester (usually auto-created)"""
    pass


class SemesterUpdate(BaseModel):
    """Schema for updating a semester (just the custom name)"""
    custom_name: Optional[str] = Field(None, max_length=100)


class SemesterStats(BaseModel):
    """Statistics for a semester"""
    books_read: int = 0
    total_unviewnered: int = 0
    commented: int = 0
    avg_points_allegory: float = 0.0
    avg_points_reasonable: float = 0.0
    total_points_allegory: float = 0.0
    total_points_reasonable: float = 0.0


class BookPreview(BaseModel):
    """Minimal book info for semester preview"""
    id: int
    title: str
    cover_image_url: Optional[str] = None
    is_memorable: bool = False


class SemesterResponse(SemesterBase):
    """Semester response with computed fields"""
    id: Optional[int] = None
    user_id: int
    start_date: date
    end_date: date
    date_range_display: str
    display_name: str
    is_current: bool = False
    stats: Optional[SemesterStats] = None
    book_previews: List[BookPreview] = []  # Preview of memorable books (or books with covers)
    
    class Config:
        from_attributes = True


class SemesterWithBooks(SemesterResponse):
    """Semester with its books included"""
    books: List[dict] = []  # Will contain BookResponse objects


class SemesterListResponse(BaseModel):
    """Paginated list of semesters"""
    items: List[SemesterResponse]
    total: int
    has_more: bool
    current_semester: int

