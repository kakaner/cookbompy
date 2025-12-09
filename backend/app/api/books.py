from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_, case
from typing import Optional, List
from math import ceil
from enum import Enum
from datetime import date

from app.database import get_db
from app.models.book import Book
from app.models.user import User
from app.models.read import Read
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse, BookSearchResult, ExistingBookResult
from app.core.security import get_current_user
from app.core.enums import Format, BookType, ReadStatus
from app.core.semesters import calculate_semester_number
from app.services.book_search import SearchService
from app.services.synopsis_fetch import SynopsisFetchService
from app.services.file_upload import FileUploadService

router = APIRouter(prefix="/books", tags=["books"])

search_service = SearchService()
synopsis_service = SynopsisFetchService()
file_upload_service = FileUploadService()


class SortOption(str, Enum):
    """Sort options for books"""
    TITLE_ASC = "title_asc"
    TITLE_DESC = "title_desc"
    AUTHOR_ASC = "author_asc"
    AUTHOR_DESC = "author_desc"
    DATE_ADDED_ASC = "date_added_asc"
    DATE_ADDED_DESC = "date_added_desc"
    DATE_READ_ASC = "date_read_asc"
    DATE_READ_DESC = "date_read_desc"
    PUBLICATION_DATE_ASC = "publication_date_asc"
    PUBLICATION_DATE_DESC = "publication_date_desc"
    FORMAT = "format"
    SEMESTER_ASC = "semester_asc"
    SEMESTER_DESC = "semester_desc"


def parse_search_query(search: str) -> dict:
    """Parse search query for field-specific syntax"""
    result = {
        "general": None,
        "author": None,
        "tag": None,
        "type": None,
        "semester": None,
        "format": None,
        "isbn": None
    }
    
    if not search:
        return result
    
    # Check for ISBN (10 or 13 digits, with optional dashes/spaces)
    import re
    isbn_pattern = r'\b(?:\d{10}|\d{13}|\d{3}-?\d{10}|\d{3}-?\d{9}[Xx])\b'
    isbn_match = re.search(isbn_pattern, search)
    if isbn_match:
        result["isbn"] = re.sub(r'[-\s]', '', isbn_match.group())
        # Remove ISBN from general search
        search = search.replace(isbn_match.group(), '').strip()
    
    # Check for field-specific syntax
    if 'author:' in search:
        parts = search.split('author:')
        if len(parts) > 1:
            result["author"] = parts[1].split()[0] if parts[1] else None
            search = parts[0].strip()
    
    if 'tag:' in search:
        parts = search.split('tag:')
        if len(parts) > 1:
            result["tag"] = parts[1].split()[0] if parts[1] else None
            search = parts[0].strip()
    
    if 'type:' in search:
        parts = search.split('type:')
        if len(parts) > 1:
            result["type"] = parts[1].split()[0] if parts[1] else None
            search = parts[0].strip()
    
    if 'semester:' in search or 'S' in search.upper():
        # Check for semester syntax like "S42" or "semester:42"
        sem_match = re.search(r'(?:semester:)?S?(\d+)', search, re.IGNORECASE)
        if sem_match:
            result["semester"] = int(sem_match.group(1))
            search = re.sub(r'(?:semester:)?S?\d+', '', search, flags=re.IGNORECASE).strip()
    
    if 'format:' in search:
        parts = search.split('format:')
        if len(parts) > 1:
            result["format"] = parts[1].split()[0] if parts[1] else None
            search = parts[0].strip()
    
    # Remaining search is general
    if search:
        result["general"] = search
    
    return result


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    link_to_existing_book_id: Optional[int] = Query(None, description="Optional: Link to existing book by ID instead of creating new"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new book or link to an existing book"""
    # If linking to existing book, verify it exists and return it
    if link_to_existing_book_id:
        existing_book = db.query(Book).filter(Book.id == link_to_existing_book_id).first()
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book to link to not found")
        
        # Eager load reads for response
        from sqlalchemy.orm import joinedload
        book = db.query(Book).options(joinedload(Book.reads)).filter(Book.id == existing_book.id).first()
        return book
    
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
    format: Optional[List[Format]] = Query(None),
    book_type: Optional[List[BookType]] = Query(None),
    read_status: Optional[ReadStatus] = None,
    language: Optional[str] = None,
    has_review: Optional[bool] = None,
    semester: Optional[int] = None,
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    series: Optional[str] = None,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    sort: SortOption = Query(SortOption.DATE_READ_DESC),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List books with pagination, filtering, and sorting"""
    from sqlalchemy.orm import joinedload
    
    # Base query - only user's books
    query = db.query(Book).filter(Book.user_id == current_user.id)
    
    # Parse search query for field-specific syntax
    search_params = parse_search_query(search) if search else {}
    
    # Apply format filter (multi-select)
    if format:
        query = query.filter(Book.format.in_(format))
    elif search_params.get("format"):
        # Format from search syntax
        try:
            format_enum = Format[search_params["format"].upper()]
            query = query.filter(Book.format == format_enum)
        except (KeyError, AttributeError):
            pass
    
    # Apply book_type filter (multi-select)
    if book_type:
        query = query.filter(Book.book_type.in_(book_type))
    elif search_params.get("type"):
        # Type from search syntax
        try:
            type_enum = BookType[search_params["type"].upper()]
            query = query.filter(Book.book_type == type_enum)
        except (KeyError, AttributeError):
            pass
    
    # Apply language filter
    if language:
        query = query.filter(Book.language.ilike(f"%{language}%"))
    
    # Apply author filter
    if author or search_params.get("author"):
        author_term = author or search_params.get("author")
        query = query.filter(Book.author.ilike(f"%{author_term}%"))
    
    # Apply publisher filter
    if publisher:
        query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
    
    # Apply series filter
    if series:
        query = query.filter(Book.series.ilike(f"%{series}%"))
    
    # Apply genre filter (genres is JSON array)
    if genre:
        query = query.filter(Book.genres.contains([genre]))
    
    # Apply ISBN search
    if search_params.get("isbn"):
        isbn = search_params["isbn"]
        query = query.filter(
            or_(
                Book.isbn_10 == isbn,
                Book.isbn_13 == isbn,
                Book.isbn_10.like(f"{isbn}%"),
                Book.isbn_13.like(f"{isbn}%")
            )
        )
    
    # Apply general search (title, author, description)
    if search_params.get("general"):
        search_term = f"%{search_params['general']}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.description.ilike(search_term)
            )
        )
    elif search and not any(search_params.values()):
        # Fallback: if search doesn't match any syntax, treat as general
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.description.ilike(search_term)
            )
        )
    
    # Build read-related filters using subqueries to avoid multiple joins
    read_filters = []
    
    # Apply read_status filter (check reads table)
    if read_status:
        if read_status == ReadStatus.READ:
            # Books that have at least one READ read
            read_filters.append(
                Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.read_status == "READ",
                        Read.user_id == current_user.id
                    ).distinct()
                )
            )
        elif read_status == ReadStatus.UNREAD:
            # Books with no READ reads
            read_filters.append(
                ~Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.read_status == "READ",
                        Read.user_id == current_user.id
                    ).distinct()
                )
            )
        elif read_status == ReadStatus.READING:
            # Books with READING status
            read_filters.append(
                Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.read_status == "READING",
                        Read.user_id == current_user.id
                    ).distinct()
                )
            )
        elif read_status == ReadStatus.DNF:
            # Books with DNF status
            read_filters.append(
                Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.read_status == "DNF",
                        Read.user_id == current_user.id
                    ).distinct()
                )
            )
    
    # Apply has_review filter
    if has_review is not None:
        if has_review:
            # Books with at least one read that has a review
            read_filters.append(
                Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.user_id == current_user.id,
                        Read.review.isnot(None),
                        Read.review != ""
                    ).distinct()
                )
            )
        else:
            # Books with no reviews on any reads
            read_filters.append(
                ~Book.id.in_(
                    db.query(Read.book_id).filter(
                        Read.user_id == current_user.id,
                        Read.review.isnot(None),
                        Read.review != ""
                    ).distinct()
                )
            )
    
    # Apply semester filter
    if semester or search_params.get("semester"):
        sem_num = semester or search_params.get("semester")
        # Get date range for semester
        from app.core.semesters import get_semester_date_range
        start_date, end_date = get_semester_date_range(sem_num)
        # Books with reads finished in this semester
        read_filters.append(
            Book.id.in_(
                db.query(Read.book_id).filter(
                    Read.user_id == current_user.id,
                    Read.read_status == "READ",
                    Read.date_finished >= start_date,
                    Read.date_finished <= end_date
                ).distinct()
            )
        )
    
    # Apply all read filters
    if read_filters:
        for read_filter in read_filters:
            query = query.filter(read_filter)
    
    # Get total count before applying sorting
    # Get distinct book IDs first, then count them to avoid issues with complex queries
    distinct_book_ids = query.with_entities(Book.id).distinct().all()
    total = len(distinct_book_ids)
    
    # Apply sorting
    from sqlalchemy.orm import joinedload
    query = query.options(joinedload(Book.reads).joinedload(Read.user))
    
    if sort == SortOption.TITLE_ASC:
        query = query.order_by(Book.title.asc())
    elif sort == SortOption.TITLE_DESC:
        query = query.order_by(Book.title.desc())
    elif sort == SortOption.AUTHOR_ASC:
        query = query.order_by(Book.author.asc())
    elif sort == SortOption.AUTHOR_DESC:
        query = query.order_by(Book.author.desc())
    elif sort == SortOption.DATE_ADDED_ASC:
        query = query.order_by(Book.created_at.asc())
    elif sort == SortOption.DATE_ADDED_DESC:
        query = query.order_by(Book.created_at.desc())
    elif sort == SortOption.PUBLICATION_DATE_ASC:
        query = query.order_by(Book.publication_date.asc().nullslast())
    elif sort == SortOption.PUBLICATION_DATE_DESC:
        query = query.order_by(Book.publication_date.desc().nullslast())
    elif sort == SortOption.FORMAT:
        query = query.order_by(Book.format.asc())
    elif sort == SortOption.DATE_READ_DESC:
        # Most recent read first - use outerjoin with group_by
        query = query.outerjoin(
            Read, and_(
                Book.id == Read.book_id,
                Read.read_status == "READ",
                Read.user_id == current_user.id
            )
        ).group_by(Book.id).order_by(
            func.max(Read.date_finished).desc().nullslast(),
            Book.created_at.desc()
        )
    elif sort == SortOption.DATE_READ_ASC:
        # Oldest read first
        query = query.outerjoin(
            Read, and_(
                Book.id == Read.book_id,
                Read.read_status == "READ",
                Read.user_id == current_user.id
            )
        ).group_by(Book.id).order_by(
            func.min(Read.date_finished).asc().nullslast(),
            Book.created_at.asc()
        )
    elif sort == SortOption.SEMESTER_DESC:
        # Most recent semester first (same as date_read_desc)
        query = query.outerjoin(
            Read, and_(
                Book.id == Read.book_id,
                Read.read_status == "READ",
                Read.user_id == current_user.id
            )
        ).group_by(Book.id).order_by(
            func.max(Read.date_finished).desc().nullslast(),
            Book.created_at.desc()
        )
    elif sort == SortOption.SEMESTER_ASC:
        # Oldest semester first (same as date_read_asc)
        query = query.outerjoin(
            Read, and_(
                Book.id == Read.book_id,
                Read.read_status == "READ",
                Read.user_id == current_user.id
            )
        ).group_by(Book.id).order_by(
            func.min(Read.date_finished).asc().nullslast(),
            Book.created_at.asc()
        )
    else:
        # Default: most recent read
        query = query.outerjoin(
            Read, and_(
                Book.id == Read.book_id,
                Read.read_status == "READ",
                Read.user_id == current_user.id
            )
        ).group_by(Book.id).order_by(
            func.max(Read.date_finished).desc().nullslast(),
            Book.created_at.desc()
        )
    
    # Apply pagination
    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()
    
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
    from sqlalchemy.orm import joinedload
    book = db.query(Book).options(
        joinedload(Book.reads).joinedload(Read.user)
    ).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
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


@router.get("/search/existing", response_model=List[ExistingBookResult])
def search_existing_books(
    isbn_10: Optional[str] = Query(None, description="Search by ISBN-10"),
    isbn_13: Optional[str] = Query(None, description="Search by ISBN-13"),
    title: Optional[str] = Query(None, description="Search by title"),
    author: Optional[str] = Query(None, description="Search by author"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for existing books in the database that can be linked to"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Book).options(joinedload(Book.user), joinedload(Book.reads))
    
    # Build search conditions
    conditions = []
    
    # Search by ISBN if provided
    if isbn_10:
        # Normalize ISBN (remove dashes and spaces)
        isbn_10_clean = isbn_10.replace('-', '').replace(' ', '')
        conditions.append(Book.isbn_10 == isbn_10_clean)
    
    if isbn_13:
        # Normalize ISBN (remove dashes and spaces)
        isbn_13_clean = isbn_13.replace('-', '').replace(' ', '')
        conditions.append(Book.isbn_13 == isbn_13_clean)
    
    # Search by title and author if provided
    # If both title and author are provided, use AND logic (both must match)
    # If only one is provided, use that
    # ISBN searches are always exact matches
    title_author_conditions = []
    
    if title:
        title_author_conditions.append(func.lower(Book.title).contains(func.lower(title)))
    
    if author:
        title_author_conditions.append(func.lower(Book.author).contains(func.lower(author)))
    
    # If we have ISBN conditions, those are OR'd with title/author
    # If we have both title and author, they must BOTH match (AND)
    # If we only have title or only author, use that
    if title_author_conditions:
        if len(title_author_conditions) == 2:
            # Both title and author: use AND
            title_author_filter = and_(*title_author_conditions)
        else:
            # Only one: use it directly
            title_author_filter = title_author_conditions[0]
        
        if conditions:
            # We have ISBN conditions, so OR them with title/author
            conditions.append(title_author_filter)
            query = query.filter(or_(*conditions))
        else:
            # Only title/author conditions
            query = query.filter(title_author_filter)
    elif conditions:
        # Only ISBN conditions
        if len(conditions) > 1:
            query = query.filter(or_(*conditions))
        else:
            query = query.filter(conditions[0])
    else:
        # No conditions at all
        return []
    
    # Get matching books
    books = query.all()
    
    # Format results
    results = []
    for book in books:
        # Count reads for this book
        read_count = len(book.reads) if book.reads else 0
        
        # Check if this is the current user's book
        is_my_book = book.user_id == current_user.id
        
        result = ExistingBookResult(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn_10=book.isbn_10,
            isbn_13=book.isbn_13,
            publication_date=book.publication_date,
            publisher=book.publisher,
            page_count=book.page_count,
            cover_image_url=book.cover_image_url,
            owner_username=book.user.username if book.user else "Unknown",
            owner_display_name=book.user.display_name if book.user else None,
            owner_id=book.user_id,
            is_my_book=is_my_book,
            read_count=read_count
        )
        results.append(result)
    
    return results

