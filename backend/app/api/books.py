from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from math import ceil

from app.database import get_db
from app.models.book import Book
from app.models.user import User
from app.models.read import Read
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse, BookSearchResult
from app.core.security import get_current_user
from app.core.enums import Format, BookType, ReadStatus
from app.services.book_search import SearchService
from app.services.synopsis_fetch import SynopsisFetchService
from app.services.file_upload import FileUploadService

router = APIRouter(prefix="/books", tags=["books"])

search_service = SearchService()
synopsis_service = SynopsisFetchService()
file_upload_service = FileUploadService()


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new book"""
    # Auto-fetch synopsis if not provided
    description = book_data.description
    description_source = book_data.description_source
    
    if not description and (book_data.isbn_13 or book_data.isbn_10 or book_data.title):
        synopsis, source = synopsis_service.fetch_synopsis(
            isbn=book_data.isbn_13 or book_data.isbn_10,
            title=book_data.title,
            author=book_data.author
        )
        if synopsis:
            description = synopsis
            description_source = source
    
    # Create book (no reading fields - those go in Read model)
    book = Book(
        user_id=current_user.id,
        title=book_data.title,
        author=book_data.author,
        isbn_10=book_data.isbn_10,
        isbn_13=book_data.isbn_13,
        publication_date=book_data.publication_date,
        publisher=book_data.publisher,
        edition=book_data.edition,
        page_count=book_data.page_count,
        language=book_data.language or "en",
        cover_image_url=book_data.cover_image_url,
        description=description,
        description_source=description_source,
        genres=book_data.genres,
        book_type=book_data.book_type,
        series=book_data.series,
        series_number=book_data.series_number,
        original_title=book_data.original_title,
        translator=book_data.translator,
        illustrator=book_data.illustrator,
        awards=book_data.awards,
        acquisition_date=book_data.acquisition_date,
        acquisition_source=book_data.acquisition_source,
        physical_location=book_data.physical_location,
        condition_notes=book_data.condition_notes,
        lending_status=book_data.lending_status,
        format=book_data.format,
    )
    
    db.add(book)
    db.commit()
    db.refresh(book)
    
    # Eager load reads for response
    from sqlalchemy.orm import joinedload
    book = db.query(Book).options(joinedload(Book.reads)).filter(Book.id == book.id).first()
    
    return book


@router.get("", response_model=BookListResponse)
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    format: Optional[Format] = None,
    book_type: Optional[BookType] = None,
    read_status: Optional[ReadStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List books with pagination and filtering"""
    # Base query - only user's books
    query = db.query(Book).filter(Book.user_id == current_user.id)
    
    # Apply filters
    if format:
        query = query.filter(Book.format == format)
    if book_type:
        query = query.filter(Book.book_type == book_type)
    # Note: read_status filter now needs to check reads table - will implement later
    # if read_status:
    #     query = query.filter(Book.read_status == read_status)
    
    # Apply search (fuzzy search on title, author, description)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.description.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    # Order by most recent read date_finished, then by book created_at
    # Use a subquery to get the max date_finished for each book
    books = query.options(joinedload(Book.reads)).outerjoin(
        Read, (Book.id == Read.book_id) & (Read.read_status == "READ")
    ).group_by(Book.id).order_by(
        func.max(Read.date_finished).desc().nullslast(),
        Book.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return BookListResponse(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single book by ID"""
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Add points breakdown to response
    book = _add_points_breakdown(book)
    
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a book (reading fields are now in Read model)"""
    from sqlalchemy.orm import joinedload
    book = db.query(Book).options(joinedload(Book.reads)).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update only provided fields (no reading fields - those are in Read model)
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    
    # Reload with reads
    book = db.query(Book).options(joinedload(Book.reads)).filter(Book.id == book.id).first()
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a book"""
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    
    return None


@router.post("/{book_id}/cover", response_model=BookResponse)
async def upload_cover(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload cover image for a book"""
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Upload file
    cover_url = await file_upload_service.upload_cover_image(file, current_user.id, book_id)
    
    # Update book
    book.cover_image_url = cover_url
    db.commit()
    db.refresh(book)
    
    return book


@router.get("/search/external", response_model=List[BookSearchResult])
def search_external(
    q: str = Query(..., description="Search query (title, author, ISBN)"),
    isbn: Optional[str] = Query(None, description="Optional ISBN for direct lookup"),
    current_user: User = Depends(get_current_user)
):
    """Search external book databases"""
    results = search_service.search_external(q, isbn)
    return results

