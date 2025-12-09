from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class AuthorWorkResponse(BaseModel):
    """Author work in timeline"""
    id: int
    title: str
    publication_year: Optional[int] = None
    work_type: Optional[str] = None
    page_count: Optional[int] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    is_major_work: bool = True
    
    class Config:
        from_attributes = True


class ReadBookInfo(BaseModel):
    """Information about a book that was read"""
    book_id: int
    title: str
    read_date: Optional[date] = None
    user_rating: Optional[float] = None
    cover_url: Optional[str] = None


class UnreadBookInfo(BaseModel):
    """Information about an unread book"""
    work_id: int
    title: str
    publication_year: Optional[int] = None
    page_count: Optional[int] = None
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None


class AuthorProgressItem(BaseModel):
    """Author progress summary for list view"""
    author_canon_id: int
    author_name: str
    author_photo_url: Optional[str] = None
    books_read: int
    books_total: int
    completion_percentage: float
    read_book_covers: List[str] = []  # URLs or IDs of read books
    unread_book_covers: List[str] = []  # URLs or IDs of unread books
    missing_titles: List[str] = []
    first_read: Optional[ReadBookInfo] = None
    most_recent_read: Optional[ReadBookInfo] = None
    achievements: List[str] = []  # Achievement type strings
    is_goal: bool = False


class AuthorProgressListResponse(BaseModel):
    """List of author progress items"""
    authors: List[AuthorProgressItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReadingPattern(BaseModel):
    """Reading pattern analysis for an author"""
    early_works_completion: float  # 0.0 to 1.0
    middle_period_completion: float
    recent_works_completion: float
    insight: Optional[str] = None


class TimelineItem(BaseModel):
    """Timeline item (book/work)"""
    year: Optional[int] = None
    title: str
    read: bool
    read_date: Optional[date] = None
    user_rating: Optional[float] = None
    page_count: Optional[int] = None
    synopsis: Optional[str] = None
    cover_url: Optional[str] = None
    work_id: Optional[int] = None
    book_id: Optional[int] = None


class Recommendation(BaseModel):
    """Recommendation for next book to read"""
    title: str
    work_id: int
    reason: str
    priority: int
    publication_year: Optional[int] = None
    page_count: Optional[int] = None


class AuthorDetailResponse(BaseModel):
    """Detailed author progress view"""
    author_canon_id: int
    author_name: str
    author_photo_url: Optional[str] = None
    books_read: int
    books_total: int
    completion_percentage: float
    achievements: List[str] = []
    reading_pattern: Optional[ReadingPattern] = None
    timeline: List[TimelineItem] = []
    recommendations: List[Recommendation] = []


class GoalRequest(BaseModel):
    """Request to set a completion goal"""
    author_canon_id: int
    deadline: Optional[date] = None
    notify: bool = False


class GoalResponse(BaseModel):
    """Goal response"""
    author_canon_id: int
    deadline: Optional[date] = None
    notify: bool = False
    created_at: datetime


class AchievementResponse(BaseModel):
    """Achievement response"""
    id: int
    achievement_type: str
    author_canon_id: Optional[int] = None
    author_name: Optional[str] = None
    awarded_at: datetime
    metadata: Optional[str] = None
    
    class Config:
        from_attributes = True


class AchievementListResponse(BaseModel):
    """List of achievements"""
    achievements: List[AchievementResponse]
    total: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    user_id: int
    username: str
    display_name: Optional[str] = None
    authors_completed: int  # Number of authors 100% complete
    total_authors_tracked: int
    completion_rate: float  # Overall completion rate


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int


class CommunityAuthorStats(BaseModel):
    """Community-wide author completion stats"""
    author_canon_id: int
    author_name: str
    total_users: int  # Users tracking this author
    users_100_percent: int  # Users who completed
    average_completion: float  # Average completion percentage
    most_completed_by: Optional[str] = None  # Username of user with highest completion

