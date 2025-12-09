from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.book import Book
from app.models.read import Read
from app.models.comment import Comment
from app.schemas.read import ReadCreate, ReadUpdate, ReadResponse
from app.core.security import get_current_user
from app.services.point_calculator import PointCalculator
from app.services.file_upload import FileUploadService
from app.core.enums import ReadStatus
from app.core.semesters import get_semester_date_range

router = APIRouter(prefix="/reads", tags=["reads"])
file_upload_service = FileUploadService()


def _add_points_breakdown(read: Read, book: Book):
    """Add points breakdown to read object (modifies in place)"""
    if read.read_status == "READ" and book.book_type:
        base = PointCalculator.get_base_points(
            book.book_type,
            read.base_points if read.base_points_overridden else None
        )
        length_addons = PointCalculator.calculate_length_addons(book.page_count)
        reread_multiplier = 0.5 if read.is_reread else 1.0

        allegory = PointCalculator.format_points(read.calculated_points_allegory) if read.calculated_points_allegory is not None else 0.0
        reasonable = PointCalculator.format_points(read.calculated_points_reasonable) if read.calculated_points_reasonable is not None else 0.0

        breakdown = f"{PointCalculator.format_points(base):.2f} (base) + {PointCalculator.format_points(length_addons):.2f} (length) × {reread_multiplier:.1f} (reread) = {allegory:.2f}"

        setattr(read, 'points', {
            "base": PointCalculator.format_points(base),
            "base_overridden": read.base_points_overridden,
            "length_addons": PointCalculator.format_points(length_addons),
            "reread_multiplier": reread_multiplier,
            "bompyallegory": allegory,
            "bompyreasonable": reasonable,
            "breakdown": breakdown
        })
    else:
        setattr(read, 'points', None)
    return read


@router.post("", response_model=ReadResponse, status_code=status.HTTP_201_CREATED)
def create_read(
    book_id: int,
    read_data: ReadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new read for a book"""
    # Verify book exists and belongs to user
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Calculate points if read is completed
    base_points_int = None
    base_points_overridden = False
    if read_data.base_points is not None:
        base_points_int = PointCalculator.parse_points(read_data.base_points)
        base_points_overridden = True
    
    calculated_points_allegory = None
    calculated_points_reasonable = None
    if read_data.read_status == "READ" and book.book_type:
        allegory, reasonable = PointCalculator.calculate_points(
            book_type=book.book_type,
            page_count=book.page_count,
            is_reread=read_data.is_reread,
            overridden_base=base_points_int
        )
        calculated_points_allegory = allegory
        calculated_points_reasonable = reasonable
    
    # Create read
    read = Read(
        book_id=book_id,
        user_id=current_user.id,
        date_started=read_data.date_started,
        date_finished=read_data.date_finished,
        read_status=read_data.read_status,
        is_reread=read_data.is_reread,
        review=read_data.review,
        read_vibe_photo_url=read_data.read_vibe_photo_url,
        base_points=base_points_int,
        base_points_overridden=base_points_overridden,
        calculated_points_allegory=calculated_points_allegory,
        calculated_points_reasonable=calculated_points_reasonable,
        is_memorable=read_data.is_memorable,
        rating=read_data.rating
    )
    
    db.add(read)
    db.commit()
    db.refresh(read)
    
    # Add points breakdown
    read = _add_points_breakdown(read, book)
    
    return read


@router.get("/book/{book_id}", response_model=List[ReadResponse])
def get_reads_for_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reads for a book (current user only)"""
    # Verify book exists and belongs to user
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    reads = db.query(Read).filter(
        Read.book_id == book_id,
        Read.user_id == current_user.id
    ).order_by(Read.date_finished.desc(), Read.created_at.desc()).all()
    
    # Add points breakdown to each read
    for read in reads:
        _add_points_breakdown(read, book)
    
    return reads


def _normalize_book_identifier(title: str, author: str) -> tuple:
    """Normalize book title and author for matching across users"""
    import re
    # Convert to lowercase, strip whitespace, and normalize multiple spaces to single space
    # Also remove common punctuation that might differ
    if title:
        normalized_title = re.sub(r'\s+', ' ', title.lower().strip())
        # Remove common punctuation that might differ between entries
        normalized_title = re.sub(r'[.,;:!?\'"()]', '', normalized_title)
    else:
        normalized_title = ""
    if author:
        normalized_author = re.sub(r'\s+', ' ', author.lower().strip())
        # Remove common punctuation
        normalized_author = re.sub(r'[.,;:!?\'"()]', '', normalized_author)
    else:
        normalized_author = ""
    return (normalized_title, normalized_author)


@router.get("/book/{book_id}/community", response_model=List[ReadResponse])
def get_community_reads_for_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reads for a book from all community users, matching by title and author"""
    # Get the book to extract title and author
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Normalize title and author for matching
    normalized_title, normalized_author = _normalize_book_identifier(book.title, book.author)
    
    # Find all books and match by normalized title and author
    # We fetch all books and normalize in Python for more reliable matching
    all_books = db.query(Book).all()
    matching_book_ids = []
    
    # Also include the original book_id to ensure backwards compatibility
    matching_book_ids.append(book_id)
    
    for b in all_books:
        # Skip the original book (already added)
        if b.id == book_id:
            continue
            
        b_normalized_title, b_normalized_author = _normalize_book_identifier(b.title, b.author)
        if b_normalized_title == normalized_title and b_normalized_author == normalized_author:
            matching_book_ids.append(b.id)
    
    if not matching_book_ids:
        # If no matching books found, return empty list
        return []
    
    # Get all reads for all matching books from all users, with user info
    reads = db.query(Read).options(
        joinedload(Read.user)
    ).filter(
        Read.book_id.in_(matching_book_ids)
    ).order_by(
        Read.date_finished.desc().nullslast(),
        Read.date_started.desc().nullslast(),
        Read.created_at.desc()
    ).all()
    
    # Add comment count and points breakdown to each read
    for read in reads:
        # Count comments for this read
        comment_count = db.query(func.count(Comment.id)).filter(
            Comment.read_id == read.id
        ).scalar() or 0
        
        # Add comment count as attribute
        setattr(read, 'comment_count', comment_count)
        
        # Get the book for this read to calculate points
        read_book = db.query(Book).filter(Book.id == read.book_id).first()
        if read_book:
            # Add points breakdown using the read's book
            _add_points_breakdown(read, read_book)
    
    return reads


@router.get("/{read_id}", response_model=ReadResponse)
def get_read(
    read_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single read"""
    read = db.query(Read).filter(
        Read.id == read_id,
        Read.user_id == current_user.id
    ).first()
    
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    book = db.query(Book).filter(Book.id == read.book_id).first()
    if book:
        _add_points_breakdown(read, book)
    
    return read


@router.put("/{read_id}", response_model=ReadResponse)
def update_read(
    read_id: int,
    read_data: ReadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a read"""
    read = db.query(Read).filter(
        Read.id == read_id,
        Read.user_id == current_user.id
    ).first()
    
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    book = db.query(Book).filter(Book.id == read.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Handle base_points override
    update_data = read_data.model_dump(exclude_unset=True, exclude={"base_points"})
    
    if read_data.base_points is not None:
        read.base_points = PointCalculator.parse_points(read_data.base_points)
        read.base_points_overridden = True
        update_data["base_points_overridden"] = True
    elif "base_points" in update_data and update_data["base_points"] is None:
        read.base_points = None
        read.base_points_overridden = False
    
    # Update fields
    for field, value in update_data.items():
        setattr(read, field, value)
    
    # Recalculate points if needed
    if read.read_status == "READ" and book.book_type:
        base_points_int = read.base_points if read.base_points_overridden else None
        allegory, reasonable = PointCalculator.calculate_points(
            book_type=book.book_type,
            page_count=book.page_count,
            is_reread=read.is_reread,
            overridden_base=base_points_int
        )
        read.calculated_points_allegory = allegory
        read.calculated_points_reasonable = reasonable
    else:
        read.calculated_points_allegory = None
        read.calculated_points_reasonable = None
    
    db.commit()
    db.refresh(read)
    
    # Add points breakdown
    read = _add_points_breakdown(read, book)
    
    return read


@router.delete("/{read_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_read(
    read_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a read"""
    read = db.query(Read).filter(
        Read.id == read_id,
        Read.user_id == current_user.id
    ).first()
    
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    db.delete(read)
    db.commit()
    
    return None


@router.post("/{read_id}/vibe-photo", response_model=ReadResponse)
async def upload_read_vibe_photo(
    read_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a read vibe photo for a read"""
    read = db.query(Read).filter(
        Read.id == read_id,
        Read.user_id == current_user.id
    ).first()
    
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    # Upload the file
    photo_url = await file_upload_service.upload_read_vibe_photo(file, current_user.id, read_id)
    
    # Update read record
    read.read_vibe_photo_url = photo_url
    db.commit()
    db.refresh(read)
    
    # Get book for points calculation
    book = db.query(Book).filter(Book.id == read.book_id).first()
    if book:
        read = _add_points_breakdown(read, book)
    
    return read

