from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List, Union
from datetime import date, datetime
from app.core.enums import Format, BookType, ReadStatus, DescriptionSource


class BookBase(BaseModel):
    """Base book schema with common fields"""
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=500, description="Author name as string (will be resolved to Author entity)")
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
    author: Optional[Union[str, int]] = Field(None, description="Author name (string) or author_id (int)")
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
    author_id: Optional[int] = None
    author_obj: Optional["AuthorResponse"] = None  # Full author object when loaded
    reads: List["ReadResponse"] = []  # List of reads for this book
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def author_name(self) -> str:
        """Get author name from author object or fallback to author field"""
        if self.author_obj:
            return self.author_obj.name
        if isinstance(self.author, str):
            return self.author
        return ""
    
    @computed_field
    @property
    def read_status(self) -> str:
        """Compute read_status from the most recent read"""
        reads_list = self.reads if self.reads is not None else []
        if not reads_list:
            return "UNREAD"
        
        # Find the most recent read by date_finished, then date_started, then created_at
        most_recent = None
        most_recent_date = None
        
        for read in reads_list:
            # Prioritize date_finished, then date_started, then created_at
            read_date = None
            if hasattr(read, 'date_finished') and read.date_finished:
                read_date = read.date_finished
            elif hasattr(read, 'date_started') and read.date_started:
                read_date = read.date_started
            elif hasattr(read, 'created_at') and read.created_at:
                read_date = read.created_at.date() if isinstance(read.created_at, datetime) else read.created_at
            
            if read_date:
                if most_recent_date is None or read_date > most_recent_date:
                    most_recent_date = read_date
                    most_recent = read
        
        # If no dates found, use the most recently created read
        if most_recent is None and reads_list:
            try:
                most_recent = max(reads_list, key=lambda r: r.created_at if hasattr(r, 'created_at') and r.created_at else datetime.min)
            except (ValueError, TypeError):
                # Fallback to first read if max fails
                most_recent = reads_list[0] if reads_list else None
        
        return most_recent.read_status if most_recent and hasattr(most_recent, 'read_status') else "UNREAD"
    
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


class ExistingBookResult(BaseModel):
    """Existing book in the database that can be linked to"""
    id: int
    title: str
    author: str
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    publication_date: Optional[date] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    cover_image_url: Optional[str] = None
    owner_username: str
    owner_display_name: Optional[str] = None
    owner_id: int
    is_my_book: bool  # True if this book belongs to the current user
    read_count: int  # Number of reads for this book


# Import ReadResponse and AuthorResponse and rebuild models to resolve forward references
from app.schemas.read import ReadResponse
from app.schemas.author import AuthorResponse

# Rebuild models that use forward references
BookResponse.model_rebuild()
BookListResponse.model_rebuild()

