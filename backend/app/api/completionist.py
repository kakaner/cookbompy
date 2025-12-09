from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from math import ceil
from enum import Enum
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.book import Book
from app.models.read import Read
from app.models.author_canon import AuthorCanon, UserAuthorProgress, CompletionAchievement
from app.core.security import get_current_user
from app.services.completionist_service import CompletionistService
from app.schemas.completionist import (
    AuthorProgressListResponse,
    AuthorProgressItem,
    AuthorDetailResponse,
    GoalRequest,
    GoalResponse,
    AchievementListResponse,
    AchievementResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    CommunityAuthorStats,
    ReadBookInfo,
    TimelineItem,
    Recommendation,
    ReadingPattern
)

router = APIRouter(prefix="/completionist", tags=["completionist"])


class SortOption(str, Enum):
    """Sort options for author progress"""
    BOOKS_READ = "books_read"
    COMPLETION_PCT = "completion_pct"
    RECENT = "recent"
    ALPHABETICAL = "alphabetical"
    ALMOST_THERE = "almost_there"


@router.get("/authors", response_model=AuthorProgressListResponse)
def get_author_progress_list(
    sort: SortOption = Query(SortOption.BOOKS_READ, description="Sort order"),
    min_completion: Optional[float] = Query(None, ge=0, le=1, description="Minimum completion percentage (0-1)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's author progress list with sorting and filtering"""
    service = CompletionistService(db)
    
    # Sync progress for all authors first (could be optimized)
    # For now, we'll just query existing progress
    
    offset = (page - 1) * page_size
    progress_list, total = service.get_user_author_progress_list(
        user_id=current_user.id,
        sort=sort.value,
        min_completion=min_completion,
        limit=page_size,
        offset=offset
    )
    
    # Convert to response format
    author_items = []
    for progress in progress_list:
        canon = progress.canon
        author = canon.author
        
        # Get book covers (simplified - would need actual book queries)
        read_book_covers = []
        unread_book_covers = []
        missing_titles = []
        
        # Get first and most recent read info
        first_read = None
        if progress.first_book_read_id:
            first_book = db.query(Book).filter(Book.id == progress.first_book_read_id).first()
            if first_book:
                first_read = ReadBookInfo(
                    book_id=first_book.id,
                    title=first_book.title,
                    read_date=progress.first_read_date,
                    cover_url=first_book.cover_image_url
                )
        
        most_recent_read = None
        if progress.most_recent_book_read_id:
            recent_book = db.query(Book).filter(Book.id == progress.most_recent_book_read_id).first()
            if recent_book:
                read = db.query(Read).filter(
                    Read.book_id == recent_book.id,
                    Read.user_id == current_user.id,
                    Read.read_status == "READ"
                ).order_by(Read.date_finished.desc()).first()
                if read:
                    most_recent_read = ReadBookInfo(
                        book_id=recent_book.id,
                        title=recent_book.title,
                        read_date=read.date_finished,
                        user_rating=read.rating,
                        cover_url=recent_book.cover_image_url
                    )
        
        # Get achievements
        achievements = db.query(CompletionAchievement).filter(
            CompletionAchievement.user_id == current_user.id,
            CompletionAchievement.author_canon_id == canon.id
        ).all()
        
        author_items.append(AuthorProgressItem(
            author_canon_id=canon.id,
            author_name=author.name,
            author_photo_url=author.photo_url,
            books_read=progress.books_read_count,
            books_total=progress.books_total_count,
            completion_percentage=progress.completion_percentage,
            read_book_covers=read_book_covers,
            unread_book_covers=unread_book_covers,
            missing_titles=missing_titles,
            first_read=first_read,
            most_recent_read=most_recent_read,
            achievements=[a.achievement_type for a in achievements],
            is_goal=progress.is_goal
        ))
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return AuthorProgressListResponse(
        authors=author_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/authors/{author_canon_id}", response_model=AuthorDetailResponse)
def get_author_detail(
    author_canon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed author progress with timeline"""
    service = CompletionistService(db)
    
    detail = service.get_author_detail(current_user.id, author_canon_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Author progress not found")
    
    return AuthorDetailResponse(**detail)


@router.post("/goals", response_model=GoalResponse)
def set_goal(
    goal_data: GoalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a completion goal for an author"""
    progress = db.query(UserAuthorProgress).filter(
        UserAuthorProgress.user_id == current_user.id,
        UserAuthorProgress.author_canon_id == goal_data.author_canon_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Author progress not found")
    
    progress.is_goal = True
    if goal_data.deadline:
        progress.goal_deadline = goal_data.deadline
    db.commit()
    
    return GoalResponse(
        author_canon_id=progress.author_canon_id,
        deadline=progress.goal_deadline,
        notify=goal_data.notify,
        created_at=datetime.now()
    )


@router.get("/achievements", response_model=AchievementListResponse)
def get_achievements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's completion achievements"""
    offset = (page - 1) * page_size
    
    achievements = db.query(CompletionAchievement).filter(
        CompletionAchievement.user_id == current_user.id
    ).order_by(CompletionAchievement.awarded_at.desc()).limit(page_size).offset(offset).all()
    
    total = db.query(CompletionAchievement).filter(
        CompletionAchievement.user_id == current_user.id
    ).count()
    
    achievement_responses = []
    for ach in achievements:
        author_name = None
        if ach.author_canon_id:
            canon = db.query(AuthorCanon).filter(AuthorCanon.id == ach.author_canon_id).first()
            if canon and canon.author:
                author_name = canon.author.name
        
        achievement_responses.append(AchievementResponse(
            id=ach.id,
            achievement_type=ach.achievement_type,
            author_canon_id=ach.author_canon_id,
            author_name=author_name,
            awarded_at=ach.awarded_at,
            metadata=ach.achievement_metadata
        ))
    
    return AchievementListResponse(
        achievements=achievement_responses,
        total=total
    )


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get completionist leaderboard"""
    # Get all users with at least one completed author
    from sqlalchemy import func
    
    completed_authors = db.query(
        UserAuthorProgress.user_id,
        func.count().label('completed_count')
    ).filter(
        UserAuthorProgress.completion_percentage >= 100
    ).group_by(UserAuthorProgress.user_id).subquery()
    
    # Get total authors tracked per user
    total_authors = db.query(
        UserAuthorProgress.user_id,
        func.count().label('total_count'),
        func.avg(UserAuthorProgress.completion_percentage).label('avg_completion')
    ).group_by(UserAuthorProgress.user_id).subquery()
    
    # Join with users
    leaderboard_query = db.query(
        User.id,
        User.username,
        User.display_name,
        func.coalesce(completed_authors.c.completed_count, 0).label('completed'),
        func.coalesce(total_authors.c.total_count, 0).label('total'),
        func.coalesce(total_authors.c.avg_completion, 0).label('avg_completion')
    ).outerjoin(
        completed_authors, User.id == completed_authors.c.user_id
    ).outerjoin(
        total_authors, User.id == total_authors.c.user_id
    ).filter(
        func.coalesce(total_authors.c.total_count, 0) > 0
    ).order_by(
        desc('completed'),
        desc('avg_completion')
    ).limit(100).all()
    
    entries = []
    user_rank = None
    for idx, row in enumerate(leaderboard_query, 1):
        if row.id == current_user.id:
            user_rank = idx
        entries.append(LeaderboardEntry(
            user_id=row.id,
            username=row.username,
            display_name=row.display_name,
            authors_completed=int(row.completed),
            total_authors_tracked=int(row.total),
            completion_rate=float(row.avg_completion) / 100.0
        ))
    
    return LeaderboardResponse(
        entries=entries,
        user_rank=user_rank,
        total_users=len(entries)
    )

