"""
Completionist service for tracking author completion progress
"""
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, desc, asc
from collections import defaultdict

from app.models.author import Author
from app.models.author_canon import AuthorCanon, AuthorWork, UserAuthorProgress, CompletionAchievement
from app.models.book import Book
from app.models.read import Read
from app.models.user import User
from app.services.author_service import find_or_create_author, normalize_author_name


class CompletionistService:
    """Service for completionist tracking and calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def ensure_author_canon(self, author_id: int) -> AuthorCanon:
        """Ensure an AuthorCanon exists for an author, create if not"""
        canon = self.db.query(AuthorCanon).filter(
            AuthorCanon.author_id == author_id
        ).first()
        
        if not canon:
            author = self.db.query(Author).filter(Author.id == author_id).first()
            if not author:
                raise ValueError(f"Author with id {author_id} not found")
            
            canon = AuthorCanon(
                author_id=author_id,
                total_works_count=0,
                bibliography_source='manual',
                is_living=True  # Default assumption
            )
            self.db.add(canon)
            self.db.flush()
        
        return canon
    
    def sync_user_progress(self, user_id: int, author_id: int) -> UserAuthorProgress:
        """
        Sync user's progress for an author based on their reads.
        This analyzes which books by the author the user has read.
        """
        # Ensure canon exists
        canon = self.ensure_author_canon(author_id)
        
        # Get all books by this author that the user owns
        user_books = self.db.query(Book).filter(
            Book.user_id == user_id,
            Book.author_id == author_id
        ).all()
        
        # Get all reads for these books
        book_ids = [b.id for b in user_books]
        reads = self.db.query(Read).filter(
            Read.user_id == user_id,
            Read.book_id.in_(book_ids),
            Read.read_status == "READ"
        ).order_by(Read.date_finished.asc()).all()
        
        # Count unique books read
        books_read_set = set(r.book_id for r in reads)
        books_read_count = len(books_read_set)
        
        # Get total works count from canon (or estimate from user's books)
        books_total = canon.total_works_count
        if books_total == 0:
            # Estimate: use number of unique books by this author in the system
            books_total = self.db.query(Book).filter(
                Book.author_id == author_id
            ).distinct(Book.title).count()
            if books_total == 0:
                books_total = len(user_books)  # Fallback to user's books
        
        # Calculate completion percentage
        completion_percentage = int((books_read_count / books_total * 100)) if books_total > 0 else 0
        
        # Find first and most recent reads
        first_read = reads[0] if reads else None
        most_recent_read = reads[-1] if reads else None
        
        # Get or create progress record
        progress = self.db.query(UserAuthorProgress).filter(
            UserAuthorProgress.user_id == user_id,
            UserAuthorProgress.author_canon_id == canon.id
        ).first()
        
        if not progress:
            progress = UserAuthorProgress(
                user_id=user_id,
                author_canon_id=canon.id,
                books_read_count=books_read_count,
                books_total_count=books_total,
                completion_percentage=completion_percentage,
                first_book_read_id=first_read.book_id if first_read else None,
                first_read_date=first_read.date_finished if first_read and first_read.date_finished else None,
                most_recent_book_read_id=most_recent_read.book_id if most_recent_read else None,
                most_recent_read_date=most_recent_read.date_finished if most_recent_read and most_recent_read.date_finished else None
            )
            self.db.add(progress)
        else:
            # Update existing progress
            progress.books_read_count = books_read_count
            progress.books_total_count = books_total
            progress.completion_percentage = completion_percentage
            progress.first_book_read_id = first_read.book_id if first_read else progress.first_book_read_id
            progress.first_read_date = first_read.date_finished if first_read and first_read.date_finished else progress.first_read_date
            progress.most_recent_book_read_id = most_recent_read.book_id if most_recent_read else progress.most_recent_book_read_id
            progress.most_recent_read_date = most_recent_read.date_finished if most_recent_read and most_recent_read.date_finished else progress.most_recent_read_date
        
        self.db.flush()
        
        # Check for achievements
        self.check_achievements(user_id, canon.id, progress)
        
        return progress
    
    def check_achievements(self, user_id: int, author_canon_id: int, progress: UserAuthorProgress):
        """Check and award achievements based on progress"""
        achievements_to_check = []
        
        # Canon Complete (100%)
        if progress.completion_percentage >= 100:
            achievements_to_check.append('canon_complete')
        
        # Nearly There (90%+)
        if progress.completion_percentage >= 90:
            achievements_to_check.append('nearly_there')
        
        # Deep Dive (10+ books)
        if progress.books_read_count >= 10:
            achievements_to_check.append('deep_dive')
        
        # Award achievements if not already awarded
        for achievement_type in achievements_to_check:
            existing = self.db.query(CompletionAchievement).filter(
                CompletionAchievement.user_id == user_id,
                CompletionAchievement.author_canon_id == author_canon_id,
                CompletionAchievement.achievement_type == achievement_type
            ).first()
            
            if not existing:
                achievement = CompletionAchievement(
                    user_id=user_id,
                    author_canon_id=author_canon_id,
                    achievement_type=achievement_type
                )
                self.db.add(achievement)
        
        self.db.flush()
    
    def get_user_author_progress_list(
        self, 
        user_id: int,
        sort: str = "books_read",  # books_read, completion_pct, recent, alphabetical, almost_there
        min_completion: Optional[float] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[UserAuthorProgress], int]:
        """Get list of user's author progress with sorting and filtering"""
        
        query = self.db.query(UserAuthorProgress).filter(
            UserAuthorProgress.user_id == user_id
        ).join(AuthorCanon).join(Author)
        
        # Apply minimum completion filter
        if min_completion is not None:
            query = query.filter(UserAuthorProgress.completion_percentage >= min_completion * 100)
        
        # Apply sorting
        if sort == "completion_pct":
            query = query.order_by(desc(UserAuthorProgress.completion_percentage))
        elif sort == "recent":
            query = query.order_by(desc(UserAuthorProgress.most_recent_read_date))
        elif sort == "alphabetical":
            query = query.order_by(asc(Author.name))
        elif sort == "almost_there":
            # Sort by completion %, but only show 80%+
            query = query.filter(UserAuthorProgress.completion_percentage >= 80)
            query = query.order_by(desc(UserAuthorProgress.completion_percentage))
        else:  # Default: books_read
            query = query.order_by(desc(UserAuthorProgress.books_read_count))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        if limit:
            query = query.limit(limit).offset(offset)
        
        results = query.all()
        return results, total
    
    def get_author_detail(self, user_id: int, author_canon_id: int) -> Optional[Dict]:
        """Get detailed author progress with timeline"""
        progress = self.db.query(UserAuthorProgress).filter(
            UserAuthorProgress.user_id == user_id,
            UserAuthorProgress.author_canon_id == author_canon_id
        ).first()
        
        if not progress:
            return None
        
        canon = progress.canon
        author = canon.author  # AuthorCanon.author relationship (not Book.author)
        
        # Get timeline (works sorted by publication year)
        works = self.db.query(AuthorWork).filter(
            AuthorWork.author_canon_id == author_canon_id,
            AuthorWork.is_major_work == True
        ).order_by(AuthorWork.publication_year.asc()).all()
        
        # Get user's reads for this author's books
        user_books = self.db.query(Book).filter(
            Book.user_id == user_id,
            Book.author_id == author.id
        ).all()
        book_ids = [b.id for b in user_books]
        
        reads = self.db.query(Read).filter(
            Read.user_id == user_id,
            Read.book_id.in_(book_ids),
            Read.read_status == "READ"
        ).all()
        
        read_book_ids = set(r.book_id for r in reads)
        read_by_book = {r.book_id: r for r in reads}
        
        # Build timeline
        timeline = []
        for work in works:
            # Try to match work to user's books
            matched_book = None
            for book in user_books:
                if (book.title.lower() == work.title.lower() or
                    (work.isbn_13 and book.isbn_13 == work.isbn_13) or
                    (work.isbn_10 and book.isbn_10 == work.isbn_10)):
                    matched_book = book
                    break
            
            if matched_book and matched_book.id in read_book_ids:
                read = read_by_book[matched_book.id]
                timeline.append({
                    'year': work.publication_year,
                    'title': work.title,
                    'read': True,
                    'read_date': read.date_finished,
                    'user_rating': read.rating,
                    'page_count': work.page_count,
                    'book_id': matched_book.id,
                    'work_id': work.id
                })
            else:
                timeline.append({
                    'year': work.publication_year,
                    'title': work.title,
                    'read': False,
                    'page_count': work.page_count,
                    'work_id': work.id
                })
        
        # Calculate reading pattern
        reading_pattern = self._calculate_reading_pattern(timeline, author.birth_year)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(works, read_book_ids, user_books)
        
        # Get achievements
        achievements = self.db.query(CompletionAchievement).filter(
            CompletionAchievement.user_id == user_id,
            CompletionAchievement.author_canon_id == author_canon_id
        ).all()
        
        return {
            'author_canon_id': author_canon_id,
            'author_name': author.name,
            'author_photo_url': author.photo_url,
            'books_read': progress.books_read_count,
            'books_total': progress.books_total_count,
            'completion_percentage': progress.completion_percentage,
            'achievements': [a.achievement_type for a in achievements],
            'reading_pattern': reading_pattern,
            'timeline': timeline,
            'recommendations': recommendations
        }
    
    def _calculate_reading_pattern(self, timeline: List[Dict], birth_year: Optional[int]) -> Dict:
        """Calculate reading pattern analysis"""
        if not timeline:
            return {
                'early_works_completion': 0.0,
                'middle_period_completion': 0.0,
                'recent_works_completion': 0.0,
                'insight': None
            }
        
        # Divide into periods
        years = [t['year'] for t in timeline if t.get('year')]
        if not years:
            return {
                'early_works_completion': 0.0,
                'middle_period_completion': 0.0,
                'recent_works_completion': 0.0,
                'insight': None
            }
        
        min_year = min(years)
        max_year = max(years)
        span = max_year - min_year
        
        # Define periods (roughly thirds)
        early_end = min_year + span // 3
        middle_end = min_year + (span * 2) // 3
        
        early = [t for t in timeline if t.get('year') and t['year'] <= early_end]
        middle = [t for t in timeline if t.get('year') and early_end < t['year'] <= middle_end]
        recent = [t for t in timeline if t.get('year') and t['year'] > middle_end]
        
        early_completion = sum(1 for t in early if t.get('read', False)) / len(early) if early else 0.0
        middle_completion = sum(1 for t in middle if t.get('read', False)) / len(middle) if middle else 0.0
        recent_completion = sum(1 for t in recent if t.get('read', False)) / len(recent) if recent else 0.0
        
        # Generate insight
        insight = None
        if middle_completion > early_completion and middle_completion > recent_completion:
            insight = "You gravitated toward this author's middle period! Consider exploring their early experimental works."
        elif recent_completion > early_completion and recent_completion > middle_completion:
            insight = "You prefer this author's recent works. Try exploring their earlier foundational works."
        elif early_completion > middle_completion and early_completion > recent_completion:
            insight = "You've focused on the early works. The author's later works might offer new perspectives."
        
        return {
            'early_works_completion': early_completion,
            'middle_period_completion': middle_completion,
            'recent_works_completion': recent_completion,
            'insight': insight
        }
    
    def _generate_recommendations(
        self, 
        works: List[AuthorWork], 
        read_book_ids: set, 
        user_books: List[Book]
    ) -> List[Dict]:
        """Generate recommendations for next books to read"""
        recommendations = []
        
        # Find unread works
        for work in works:
            # Check if user has a matching book
            has_book = False
            for book in user_books:
                if (book.title.lower() == work.title.lower() or
                    (work.isbn_13 and book.isbn_13 == work.isbn_13) or
                    (work.isbn_10 and book.isbn_10 == work.isbn_10)):
                    has_book = True
                    if book.id not in read_book_ids:
                        recommendations.append({
                            'title': work.title,
                            'work_id': work.id,
                            'reason': 'You own this book but haven\'t read it yet',
                            'priority': 1,
                            'publication_year': work.publication_year,
                            'page_count': work.page_count
                        })
                    break
        
        # Sort by priority and publication year
        recommendations.sort(key=lambda x: (x['priority'], x.get('publication_year', 0)))
        
        return recommendations[:5]  # Top 5 recommendations

