from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.book import Book
from app.models.semester import Semester
from app.models.read import Read
from app.models.comment import Comment
from app.schemas.semester import (
    SemesterUpdate,
    SemesterResponse,
    SemesterWithBooks,
    SemesterListResponse,
    SemesterStats
)
from app.core.security import get_current_user
from app.core.semesters import (
    get_semester_date_range,
    get_current_semester,
    format_semester_date_range,
    get_semester_display_name
)
from app.core.enums import ReadStatus
from app.schemas.semester import BookPreview


router = APIRouter(prefix="/semesters", tags=["semesters"])


def _get_book_previews(db: Session, user_id: int, semester_number: int, limit: int = 6) -> List[dict]:
    """Get book previews for semester timeline (memorable reads or reads with book covers)"""
    start_date, end_date = get_semester_date_range(semester_number)
    
    # Get memorable reads first, then reads with book covers, up to limit
    reads = db.query(Read).join(Book).filter(
        Read.user_id == user_id,
        Read.read_status == "READ",
        Read.date_finished >= start_date,
        Read.date_finished <= end_date
    ).order_by(
        Read.is_memorable.desc(),  # Memorable reads first
        Read.date_finished.desc()
    ).limit(limit * 2).all()  # Get more to filter
    
    # Filter to only include books with covers or memorable reads
    previews = []
    seen_book_ids = set()
    for read in reads:
        from sqlalchemy.orm import joinedload
        book = db.query(Book).options(joinedload(Book.author_obj)).filter(Book.id == read.book_id).first()
        if book and (book.cover_image_url or read.is_memorable):
            # Only include each book once
            if book.id not in seen_book_ids:
                previews.append({
                    "id": book.id,
                    "title": book.title,
                    "cover_image_url": book.cover_image_url,
                    "is_memorable": read.is_memorable
                })
                seen_book_ids.add(book.id)
                if len(previews) >= limit:
                    break
    
    return previews


def _build_semester_response(
    semester_number: int,
    user_id: int,
    custom_name: Optional[str] = None,
    semester_id: Optional[int] = None,
    include_stats: bool = True,
    include_previews: bool = True,
    db: Optional[Session] = None
) -> SemesterResponse:
    """Build a semester response object"""
    start_date, end_date = get_semester_date_range(semester_number)
    current_sem = get_current_semester()
    
    stats = None
    if include_stats and db:
        stats = _calculate_semester_stats(db, user_id, semester_number)
    
    book_previews = []
    if include_previews and db:
        book_previews = _get_book_previews(db, user_id, semester_number)
    
    return SemesterResponse(
        id=semester_id,
        user_id=user_id,
        semester_number=semester_number,
        custom_name=custom_name,
        start_date=start_date,
        end_date=end_date,
        date_range_display=format_semester_date_range(semester_number),
        display_name=get_semester_display_name(semester_number, custom_name),
        is_current=(semester_number == current_sem),
        stats=stats,
        book_previews=book_previews
    )


def _calculate_semester_stats(db: Session, user_id: int, semester_number: int) -> SemesterStats:
    """Calculate statistics for a semester based on date range (using reads)"""
    # Get the date range for this semester
    start_date, end_date = get_semester_date_range(semester_number)
    
    # Query reads finished within this semester's date range
    reads = db.query(Read).filter(
        Read.user_id == user_id,
        Read.read_status == "READ",
        Read.date_finished >= start_date,
        Read.date_finished <= end_date
    ).all()
    
    if not reads:
        return SemesterStats()
    
    # Get read IDs
    read_ids = [r.id for r in reads]
    
    # Count reads without reviews (unviewnered)
    total_unviewnered = sum(1 for r in reads if not r.review or not r.review.strip())
    
    # Count reads with comments (commented)
    commented_read_ids = db.query(Comment.read_id).filter(
        Comment.read_id.in_(read_ids),
        Comment.is_deleted == False
    ).distinct().all()
    # Extract read_id from tuples
    commented_count = len(set(row[0] for row in commented_read_ids))
    
    total_points_allegory = sum((r.calculated_points_allegory or 0) / 100.0 for r in reads)
    total_points_reasonable = sum((r.calculated_points_reasonable or 0) / 100.0 for r in reads)
    
    return SemesterStats(
        books_read=len(reads),  # Actually number of reads
        total_unviewnered=total_unviewnered,
        commented=commented_count,
        avg_points_allegory=total_points_allegory / len(reads) if reads else 0,
        avg_points_reasonable=total_points_reasonable / len(reads) if reads else 0,
        total_points_allegory=total_points_allegory,
        total_points_reasonable=total_points_reasonable
    )


@router.get("", response_model=SemesterListResponse)
def list_semesters(
    limit: int = Query(default=4, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List semesters with stats.
    Loads from current semester backwards by default.
    """
    current_sem = get_current_semester()
    
    # Get custom names for user's semesters
    user_semesters = db.query(Semester).filter(
        Semester.user_id == current_user.id
    ).all()
    custom_names = {s.semester_number: (s.custom_name, s.id) for s in user_semesters}
    
    # Build list of semesters from current backwards
    semesters = []
    start_sem = current_sem - offset
    
    for i in range(limit):
        sem_num = start_sem - i
        if sem_num < 1:
            break
        
        custom_name, sem_id = custom_names.get(sem_num, (None, None))
        semester = _build_semester_response(
            semester_number=sem_num,
            user_id=current_user.id,
            custom_name=custom_name,
            semester_id=sem_id,
            include_stats=True,
            db=db
        )
        semesters.append(semester)
    
    # Check if there are more semesters
    has_more = (start_sem - limit) >= 1
    
    return SemesterListResponse(
        items=semesters,
        total=current_sem,
        has_more=has_more,
        current_semester=current_sem
    )


@router.get("/current", response_model=SemesterResponse)
def get_current_semester_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current semester info"""
    current_sem = get_current_semester()
    
    # Check for custom name
    semester = db.query(Semester).filter(
        Semester.user_id == current_user.id,
        Semester.semester_number == current_sem
    ).first()
    
    return _build_semester_response(
        semester_number=current_sem,
        user_id=current_user.id,
        custom_name=semester.custom_name if semester else None,
        semester_id=semester.id if semester else None,
        include_stats=True,
        db=db
    )


@router.get("/{semester_number}", response_model=SemesterWithBooks)
def get_semester(
    semester_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single semester with its books"""
    if semester_number < 1:
        raise HTTPException(status_code=400, detail="Invalid semester number")
    
    current_sem = get_current_semester()
    if semester_number > current_sem + 4:  # Allow viewing up to 4 future semesters
        raise HTTPException(status_code=400, detail="Semester too far in the future")
    
    # Get semester custom name if exists
    semester = db.query(Semester).filter(
        Semester.user_id == current_user.id,
        Semester.semester_number == semester_number
    ).first()
    
    # Get date range for this semester
    start_date, end_date = get_semester_date_range(semester_number)
    
    # Get reads finished within this semester's date range
    reads = db.query(Read).join(Book).filter(
        Read.user_id == current_user.id,
        Read.read_status == "READ",
        Read.date_finished >= start_date,
        Read.date_finished <= end_date
    ).order_by(Read.is_memorable.desc(), Read.date_finished.desc()).all()
    
    # Build response
    stats = _calculate_semester_stats(db, current_user.id, semester_number)
    
    # Convert reads to dict with book info, prioritizing memorable reads
    from sqlalchemy.orm import joinedload
    books_data = []
    for read in reads:
        book = db.query(Book).options(joinedload(Book.author_obj)).filter(Book.id == read.book_id).first()
        if book:
            books_data.append({
                "id": book.id,
                "read_id": read.id,
                "title": book.title,
                "author": book.author_obj.name if book.author_obj else (book.author or "Unknown"),
                "cover_image_url": book.cover_image_url,
                "format": book.format.value if book.format else None,
                "book_type": book.book_type.value if book.book_type else None,
                "date_finished": read.date_finished.isoformat() if read.date_finished else None,
                "page_count": book.page_count,
                "is_memorable": read.is_memorable,
                "is_reread": read.is_reread,
                "review": read.review,
                "calculated_points_allegory": (read.calculated_points_allegory or 0) / 100.0,
                "calculated_points_reasonable": (read.calculated_points_reasonable or 0) / 100.0
            })
    
    return SemesterWithBooks(
        id=semester.id if semester else None,
        user_id=current_user.id,
        semester_number=semester_number,
        custom_name=semester.custom_name if semester else None,
        start_date=start_date,
        end_date=end_date,
        date_range_display=format_semester_date_range(semester_number),
        display_name=get_semester_display_name(semester_number, semester.custom_name if semester else None),
        is_current=(semester_number == current_sem),
        stats=stats,
        books=books_data
    )


@router.put("/{semester_number}", response_model=SemesterResponse)
def update_semester(
    semester_number: int,
    semester_data: SemesterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a semester's custom name"""
    if semester_number < 1:
        raise HTTPException(status_code=400, detail="Invalid semester number")
    
    # Find or create semester record
    semester = db.query(Semester).filter(
        Semester.user_id == current_user.id,
        Semester.semester_number == semester_number
    ).first()
    
    if not semester:
        # Create new semester record
        semester = Semester(
            user_id=current_user.id,
            semester_number=semester_number,
            custom_name=semester_data.custom_name
        )
        db.add(semester)
    else:
        # Update existing
        semester.custom_name = semester_data.custom_name
    
    db.commit()
    db.refresh(semester)
    
    return _build_semester_response(
        semester_number=semester_number,
        user_id=current_user.id,
        custom_name=semester.custom_name,
        semester_id=semester.id,
        include_stats=True,
        db=db
    )

