from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from app.core.enums import Format, BookType, ReadStatus, DescriptionSource


class BookBase(BaseModel):
    """Base book schema with common fields"""
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=500)
    isbn_10: Optional[str] = Field(None, max_length=13)
    isbn_13: Optional[str] = Field(None, max_length=17)
    publication_date: Optional[date] = None
    publisher: Optional[str] = Field(None, max_length=255)
    edition: Optional[str] = Field(None, max_length=100)
    page_count: Optional[int] = Field(None, ge=0)
    language: Optional[str] = Field(default="en", max_length=50)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    
    # Extended fields
    description: Optional[str] = None
    description_source: Optional[DescriptionSource] = None
    genres: Optional[List[str]] = None
    book_type: Optional[BookType] = None
    series: Optional[str] = Field(None, max_length=255)
    series_number: Optional[int] = Field(None, ge=0)
    original_title: Optional[str] = Field(None, max_length=500)
    translator: Optional[str] = Field(None, max_length=255)
    illustrator: Optional[str] = Field(None, max_length=255)
    awards: Optional[str] = None
    
    # User-managed fields
    acquisition_date: Optional[date] = None
    acquisition_source: Optional[str] = Field(None, max_length=255)
    physical_location: Optional[str] = Field(None, max_length=255)
    condition_notes: Optional[str] = None
    lending_status: Optional[str] = Field(None, max_length=255)
    read_vibe_photo_url: Optional[str] = Field(None, max_length=500)
    
    # Note: Reading fields (date_started, date_finished, is_reread, read_status, etc.) 
    # are now in the Read model - a book can have multiple reads
    
    # Format (required)
    format: Format


class BookCreate(BookBase):
    """Schema for creating a new book"""
    # Point system (optional)
    base_points: Optional[float] = Field(None, description="Override base points (optional)")


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    base_points: Optional[float] = Field(None, description="Override base points (will set base_points_overridden=True)")
    author: Optional[str] = Field(None, min_length=1, max_length=500)
    isbn_10: Optional[str] = Field(None, max_length=13)
    isbn_13: Optional[str] = Field(None, max_length=17)
    publication_date: Optional[date] = None
    publisher: Optional[str] = Field(None, max_length=255)
    edition: Optional[str] = Field(None, max_length=100)
    page_count: Optional[int] = Field(None, ge=0)
    language: Optional[str] = Field(None, max_length=50)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    description_source: Optional[DescriptionSource] = None
    genres: Optional[List[str]] = None
    book_type: Optional[BookType] = None
    series: Optional[str] = Field(None, max_length=255)
    series_number: Optional[int] = Field(None, ge=0)
    original_title: Optional[str] = Field(None, max_length=500)
    translator: Optional[str] = Field(None, max_length=255)
    illustrator: Optional[str] = Field(None, max_length=255)
    awards: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_source: Optional[str] = Field(None, max_length=255)
    physical_location: Optional[str] = Field(None, max_length=255)
    condition_notes: Optional[str] = None
    lending_status: Optional[str] = Field(None, max_length=255)
    read_vibe_photo_url: Optional[str] = Field(None, max_length=500)
    format: Optional[Format] = None


class BookPoints(BaseModel):
    """Point calculation breakdown"""
    base: float
    base_overridden: bool
    length_addons: float
    reread_multiplier: float
    bompyallegory: float
    bompyreasonable: float
    breakdown: str


class BookResponse(BookBase):
    """Schema for book response"""
    id: int
    user_id: int
    reads: List["ReadResponse"] = []  # List of reads for this book
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """Paginated list response"""
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BookSearchResult(BaseModel):
    """External search result"""
    title: str
    author: str
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    publication_year: Optional[int] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    description: Optional[str] = None
    genres: Optional[List[str]] = None
    cover_url: Optional[str] = None
    source: str  # "goodreads", "google_books", "open_library"


# Import ReadResponse and rebuild models to resolve forward references
from app.schemas.read import ReadResponse

# Rebuild models that use forward references
BookResponse.model_rebuild()
BookListResponse.model_rebuild()

