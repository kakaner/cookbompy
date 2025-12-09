from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.book import Book
from app.models.read import Read
from app.models.shareable_link import ShareableLink
from app.schemas.shareable_link import (
    ShareableLinkCreate,
    ShareableLinkResponse,
    SharedBookResponse
)
from app.core.security import get_current_user
from app.config import settings

router = APIRouter(prefix="/shareable-links", tags=["shareable-links"])


@router.post("", response_model=ShareableLinkResponse, status_code=status.HTTP_201_CREATED)
def create_shareable_link(
    link_data: ShareableLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new shareable link for a book"""
    # Verify book exists and belongs to user
    book = db.query(Book).filter(
        Book.id == link_data.book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if there's an existing valid link for this book by this user
    existing_link = db.query(ShareableLink).filter(
        ShareableLink.book_id == link_data.book_id,
        ShareableLink.user_id == current_user.id,
        ShareableLink.is_revoked == False
    ).first()
    
    # If existing link is expired, create a new one
    if existing_link and existing_link.is_expired():
        existing_link.is_revoked = True
        existing_link.revoked_at = datetime.now(timezone.utc)
        db.commit()
        existing_link = None
    
    # If there's a valid existing link, return it
    if existing_link and existing_link.is_valid():
        share_url = f"{settings.FRONTEND_URL}/share/{existing_link.token}"
        return ShareableLinkResponse(
            id=existing_link.id,
            book_id=existing_link.book_id,
            token=existing_link.token,
            expires_at=existing_link.expires_at,
            view_count=existing_link.view_count,
            is_revoked=existing_link.is_revoked,
            revoked_at=existing_link.revoked_at,
            created_at=existing_link.created_at,
            share_url=share_url
        )
    
    # Create new link
    token = ShareableLink.generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    shareable_link = ShareableLink(
        book_id=link_data.book_id,
        user_id=current_user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(shareable_link)
    db.commit()
    db.refresh(shareable_link)
    
    share_url = f"{settings.FRONTEND_URL}/share/{token}"
    
    return ShareableLinkResponse(
        id=shareable_link.id,
        book_id=shareable_link.book_id,
        token=shareable_link.token,
        expires_at=shareable_link.expires_at,
        view_count=shareable_link.view_count,
        is_revoked=shareable_link.is_revoked,
        revoked_at=shareable_link.revoked_at,
        created_at=shareable_link.created_at,
        share_url=share_url
    )


@router.get("/book/{book_id}", response_model=Optional[ShareableLinkResponse])
def get_shareable_link_for_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current shareable link for a book (if exists and valid)"""
    # Verify book belongs to user
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    link = db.query(ShareableLink).filter(
        ShareableLink.book_id == book_id,
        ShareableLink.user_id == current_user.id,
        ShareableLink.is_revoked == False
    ).first()
    
    if not link or not link.is_valid():
        return None
    
    share_url = f"{settings.FRONTEND_URL}/share/{link.token}"
    
    return ShareableLinkResponse(
        id=link.id,
        book_id=link.book_id,
        token=link.token,
        expires_at=link.expires_at,
        view_count=link.view_count,
        is_revoked=link.is_revoked,
        revoked_at=link.revoked_at,
        created_at=link.created_at,
        share_url=share_url
    )


@router.get("/book/{book_id}/all", response_model=List[ShareableLinkResponse])
def get_all_shareable_links_for_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all shareable links for a book (including revoked ones)"""
    # Verify book belongs to user
    book = db.query(Book).filter(
        Book.id == book_id,
        Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Get all links for this book by this user, ordered by created_at DESC
    links = db.query(ShareableLink).filter(
        ShareableLink.book_id == book_id,
        ShareableLink.user_id == current_user.id
    ).order_by(ShareableLink.created_at.desc()).all()
    
    # Format response with share_url for each link
    result = []
    for link in links:
        share_url = f"{settings.FRONTEND_URL}/share/{link.token}"
        result.append(ShareableLinkResponse(
            id=link.id,
            book_id=link.book_id,
            token=link.token,
            expires_at=link.expires_at,
            view_count=link.view_count,
            is_revoked=link.is_revoked,
            revoked_at=link.revoked_at,
            created_at=link.created_at,
            share_url=share_url
        ))
    
    return result


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_shareable_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a shareable link"""
    link = db.query(ShareableLink).filter(
        ShareableLink.id == link_id,
        ShareableLink.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Shareable link not found")
    
    if link.is_revoked:
        raise HTTPException(status_code=400, detail="Link already revoked")
    
    link.is_revoked = True
    link.revoked_at = datetime.now(timezone.utc)
    db.commit()
    
    return None


@router.get("/token/{token}", response_model=SharedBookResponse)
def get_shared_book_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Get book data via shareable link token (public, no auth required)"""
    link = db.query(ShareableLink).filter(ShareableLink.token == token).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Shareable link not found")
    
    if not link.is_valid():
        raise HTTPException(status_code=410, detail="Shareable link has expired or been revoked")
    
    # Increment view count
    link.view_count += 1
    db.commit()
    
    # Load book with relationships
    from sqlalchemy.orm import joinedload
    book = db.query(Book).options(
        joinedload(Book.user)
    ).filter(Book.id == link.book_id).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Get sharing user's review, rating, and date read
    sharing_user_review = None
    sharing_user_rating = None
    sharing_user_date_read = None
    
    # Get the most recent read by the sharing user
    read = db.query(Read).filter(
        Read.book_id == book.id,
        Read.user_id == link.user_id,
        Read.read_status == "READ"
    ).order_by(Read.date_finished.desc(), Read.created_at.desc()).first()
    
    if read:
        sharing_user_review = read.review
        sharing_user_rating = read.rating
        if read.date_finished:
            sharing_user_date_read = read.date_finished.isoformat()
    
    # Format sharing user info
    sharing_user = {
        "id": book.user.id,
        "username": book.user.username,
        "display_name": book.user.display_name,
        "profile_photo_url": book.user.profile_photo_url
    }
    
    return SharedBookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn_10=book.isbn_10,
        isbn_13=book.isbn_13,
        publication_date=book.publication_date.isoformat() if book.publication_date else None,
        publisher=book.publisher,
        page_count=book.page_count,
        language=book.language,
        cover_image_url=book.cover_image_url,
        description=book.description,
        description_source=book.description_source.value if book.description_source else None,
        genres=book.genres,
        book_type=book.book_type.value if book.book_type else None,
        series=book.series,
        format=book.format.value if book.format else None,
        sharing_user=sharing_user,
        sharing_user_review=sharing_user_review,
        sharing_user_rating=sharing_user_rating,
        sharing_user_date_read=sharing_user_date_read
    )

