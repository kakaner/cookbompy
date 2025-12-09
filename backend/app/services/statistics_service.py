"""
Statistics service for calculating reading statistics and analytics
All statistics are based on reads (not books) as the first-class citizen
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from collections import defaultdict
import statistics

from app.models.read import Read
from app.models.book import Book
from app.models.comment import Comment
from app.models.user import User
from app.core.semesters import calculate_semester_number, get_semester_date_range
from app.core.enums import Format, BookType


class StatisticsService:
    """Service for calculating statistics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_time_dimension_grouping(self, time_dimension: str, read_date: date) -> str:
        """
        Group a date by the specified time dimension.
        Returns a label string for grouping.
        """
        if time_dimension == "day":
            return read_date.isoformat()
        elif time_dimension == "week":
            # ISO week format: YYYY-Www
            year, week, _ = read_date.isocalendar()
            return f"{year}-W{week:02d}"
        elif time_dimension == "month":
            return f"{read_date.year}-{read_date.month:02d}"
        elif time_dimension == "year":
            return str(read_date.year)
        elif time_dimension == "semester":
            sem_num = calculate_semester_number(read_date)
            return f"S{sem_num}"
        elif time_dimension == "alltime":
            return "alltime"
        else:
            return "alltime"
    
    def get_reads_query(self, user_id: int, time_dimension: str = "alltime", 
                       start_date: Optional[date] = None, end_date: Optional[date] = None):
        """Get base query for reads filtered by user and time"""
        from sqlalchemy.orm import joinedload
        query = self.db.query(Read).options(
            joinedload(Read.book).joinedload(Book.author_obj)
        ).join(Book).filter(
            Read.user_id == user_id,
            Read.read_status == "READ",
            Read.date_finished.isnot(None)
        )
        
        if time_dimension != "alltime":
            if start_date:
                query = query.filter(Read.date_finished >= start_date)
            if end_date:
                query = query.filter(Read.date_finished <= end_date)
        
        return query
    
    def calculate_reading_stats(self, user_id: int, time_dimension: str = "alltime") -> List[Dict]:
        """Calculate reading statistics over time"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return []
        
        # Group by time dimension
        grouped = defaultdict(lambda: {"count": 0, "points_allegory": 0.0, "points_reasonable": 0.0})
        
        for read in reads:
            if read.date_finished:
                label = self.get_time_dimension_grouping(time_dimension, read.date_finished)
                grouped[label]["count"] += 1
                if read.calculated_points_allegory:
                    grouped[label]["points_allegory"] += (read.calculated_points_allegory / 100.0)
                if read.calculated_points_reasonable:
                    grouped[label]["points_reasonable"] += (read.calculated_points_reasonable / 100.0)
        
        # Convert to sorted list
        result = []
        for label in sorted(grouped.keys()):
            result.append({
                "label": label,
                "read_count": grouped[label]["count"],
                "points_allegory": grouped[label]["points_allegory"],
                "points_reasonable": grouped[label]["points_reasonable"]
            })
        
        return result
    
    def calculate_format_breakdown(self, user_id: int, time_dimension: str = "alltime") -> List[Dict]:
        """Calculate format distribution based on reads"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return []
        
        format_counts = defaultdict(int)
        total = len(reads)
        
        for read in reads:
            if read.book and read.book.format:
                format_counts[read.book.format.value] += 1
        
        result = []
        for fmt, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True):
            result.append({
                "format": fmt,
                "count": count,
                "percentage": (count / total * 100) if total > 0 else 0
            })
        
        return result
    
    def calculate_book_type_breakdown(self, user_id: int, time_dimension: str = "alltime") -> List[Dict]:
        """Calculate book type distribution based on reads"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return []
        
        type_counts = defaultdict(int)
        total = len(reads)
        
        for read in reads:
            if read.book and read.book.book_type:
                type_counts[read.book.book_type.value] += 1
        
        result = []
        for book_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            result.append({
                "book_type": book_type,
                "count": count,
                "percentage": (count / total * 100) if total > 0 else 0
            })
        
        return result
    
    def calculate_genre_breakdown(self, user_id: int, time_dimension: str = "alltime", limit: int = 10) -> List[Dict]:
        """Calculate genre distribution based on reads"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return []
        
        genre_counts = defaultdict(int)
        total = len(reads)
        
        for read in reads:
            if read.book and read.book.genres:
                for genre in read.book.genres:
                    genre_counts[genre] += 1
        
        result = []
        for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            result.append({
                "genre": genre,
                "count": count,
                "percentage": (count / total * 100) if total > 0 else 0
            })
        
        return result
    
    def calculate_author_frequency(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Calculate most-read authors based on read count"""
        reads = self.get_reads_query(user_id).all()
        
        if not reads:
            return []
        
        author_read_counts = defaultdict(int)
        author_book_counts = defaultdict(set)
        
        for read in reads:
            if read.book:
                # Get author name - use author_obj relationship or legacy author string
                author_name = None
                if read.book.author_obj:  # Author relationship object
                    author_name = read.book.author_obj.name
                elif read.book.author:  # Legacy string field
                    author_name = read.book.author
                
                if author_name:
                    author_read_counts[author_name] += 1
                    author_book_counts[author_name].add(read.book_id)
        
        result = []
        for author_name, read_count in sorted(author_read_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            result.append({
                "author": author_name,
                "read_count": read_count,
                "unique_books": len(author_book_counts[author])
            })
        
        return result
    
    def calculate_rating_distribution(self, user_id: int, time_dimension: str = "alltime") -> Tuple[List[Dict], float]:
        """Calculate rating distribution based on reads"""
        # Note: Ratings are stored on reads, but we need to check if there's a rating model
        # For now, we'll return empty distribution as ratings might be stored differently
        # This will need to be implemented based on the actual rating model structure
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        # TODO: Implement rating distribution when rating model is available
        return [], 0.0
    
    def calculate_viewner_rate(self, user_id: int, time_dimension: str = "alltime") -> Tuple[List[Dict], float]:
        """Calculate viewner rate (percentage of reads with reviews) over time"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return [], 0.0
        
        # Group by time dimension
        grouped = defaultdict(lambda: {"total": 0, "with_review": 0})
        
        for read in reads:
            if read.date_finished:
                label = self.get_time_dimension_grouping(time_dimension, read.date_finished)
                grouped[label]["total"] += 1
                if read.review and read.review.strip():
                    grouped[label]["with_review"] += 1
        
        # Calculate overall rate
        total_reads = len(reads)
        reads_with_review = sum(1 for r in reads if r.review and r.review.strip())
        overall_rate = (reads_with_review / total_reads * 100) if total_reads > 0 else 0.0
        
        # Convert to list
        result = []
        for label in sorted(grouped.keys()):
            total = grouped[label]["total"]
            with_review = grouped[label]["with_review"]
            rate = (with_review / total * 100) if total > 0 else 0.0
            result.append({
                "label": label,
                "value": rate,
                "count": with_review,
                "total": total
            })
        
        return result, overall_rate
    
    def calculate_commentu_rate(self, user_id: int, time_dimension: str = "alltime") -> Tuple[List[Dict], float]:
        """Calculate commentu rate (percentage of reads with comments) over time"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return [], 0.0
        
        # Get read IDs
        read_ids = [r.id for r in reads]
        
        # Get reads with comments
        commented_read_ids = self.db.query(Comment.read_id).filter(
            Comment.read_id.in_(read_ids),
            Comment.is_deleted == False
        ).distinct().all()
        commented_read_ids_set = set(row[0] for row in commented_read_ids)
        
        # Group by time dimension
        grouped = defaultdict(lambda: {"total": 0, "with_comments": 0})
        
        for read in reads:
            if read.date_finished:
                label = self.get_time_dimension_grouping(time_dimension, read.date_finished)
                grouped[label]["total"] += 1
                if read.id in commented_read_ids_set:
                    grouped[label]["with_comments"] += 1
        
        # Calculate overall rate
        total_reads = len(reads)
        reads_with_comments = len(commented_read_ids_set)
        overall_rate = (reads_with_comments / total_reads * 100) if total_reads > 0 else 0.0
        
        # Convert to list
        result = []
        for label in sorted(grouped.keys()):
            total = grouped[label]["total"]
            with_comments = grouped[label]["with_comments"]
            rate = (with_comments / total * 100) if total > 0 else 0.0
            result.append({
                "label": label,
                "value": rate,
                "count": with_comments,
                "total": total
            })
        
        return result, overall_rate
    
    def calculate_points_trends(self, user_id: int, time_dimension: str = "alltime", 
                                algorithm: str = "allegory") -> List[Dict]:
        """Calculate points trends over time"""
        reads = self.get_reads_query(user_id, time_dimension).all()
        
        if not reads:
            return []
        
        # Group by time dimension
        grouped = defaultdict(lambda: {"points": 0.0, "count": 0})
        
        for read in reads:
            if read.date_finished:
                label = self.get_time_dimension_grouping(time_dimension, read.date_finished)
                grouped[label]["count"] += 1
                if algorithm == "allegory" and read.calculated_points_allegory:
                    grouped[label]["points"] += (read.calculated_points_allegory / 100.0)
                elif algorithm == "reasonable" and read.calculated_points_reasonable:
                    grouped[label]["points"] += (read.calculated_points_reasonable / 100.0)
        
        # Convert to sorted list
        result = []
        for label in sorted(grouped.keys()):
            result.append({
                "label": label,
                "value": grouped[label]["points"],
                "count": grouped[label]["count"]
            })
        
        return result
    
    def _get_user_info(self, user_id: int) -> Dict:
        """Get user information for conjugation responses"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "user_id": user.id,
                "username": user.username,
                "display_name": user.display_name or user.username,
                "profile_photo_url": user.profile_photo_url
            }
        return {
            "user_id": user_id,
            "username": f"user_{user_id}",
            "display_name": f"user_{user_id}",
            "profile_photo_url": None
        }
    
    def _calculate_overlap_percentage(self, start1: date, end1: date, start2: date, end2: date) -> float:
        """Calculate percentage overlap between two date ranges"""
        if not start1 or not end1 or not start2 or not end2:
            return 0.0
        
        # Find overlap period
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_start > overlap_end:
            return 0.0
        
        overlap_days = (overlap_end - overlap_start).days + 1
        range1_days = (end1 - start1).days + 1
        range2_days = (end2 - start2).days + 1
        
        # Calculate overlap as percentage of the shorter range
        min_range_days = min(range1_days, range2_days)
        if min_range_days == 0:
            return 0.0
        
        return (overlap_days / min_range_days) * 100.0
    
    def calculate_community_reads_in_common(self, user_id: int, min_user_count: int = 2) -> List[Dict]:
        """Calculate reads in common across all users with user information"""
        # Get all reads from all users
        all_reads = self.db.query(Read).join(Book).filter(
            Read.read_status == "READ",
            Read.date_finished.isnot(None)
        ).all()
        
        # Group by normalized title+author (to catch same books with different book_ids)
        # Map normalized key to a canonical book_id
        title_author_map = {}  # normalized_key -> canonical_book_id
        book_user_counts = defaultdict(set)
        book_read_counts = defaultdict(int)
        book_info = {}
        book_formats = defaultdict(set)
        book_users = defaultdict(list)  # Store user info per book
        
        for read in all_reads:
            if read.book:
                # Normalize title and author for matching
                # Get author for normalization - use author_obj or legacy author field
                author_for_norm = read.book.author_obj.name if read.book.author_obj else read.book.author
                normalized_title, normalized_author = self._normalize_book_identifier(read.book.title, author_for_norm)
                normalized_key = f"{normalized_title}|{normalized_author}"
                
                # Use canonical book_id (first one we see for this title+author)
                if normalized_key not in title_author_map:
                    title_author_map[normalized_key] = read.book_id
                    # Get author name - use author_obj relationship or legacy author string
                    author_name = None
                    if read.book.author_obj:  # Author relationship object
                        author_name = read.book.author_obj.name
                    elif read.book.author:  # Legacy string field
                        author_name = read.book.author
                    book_info[read.book_id] = {
                        "title": read.book.title,
                        "author": author_name or ""
                    }
                
                canonical_book_id = title_author_map[normalized_key]
                
                book_user_counts[canonical_book_id].add(read.user_id)
                book_read_counts[canonical_book_id] += 1
                
                if read.book.format:
                    book_formats[canonical_book_id].add(read.book.format.value)
                
                # Add user info (avoid duplicates)
                if read.user_id not in [u["user_id"] for u in book_users[canonical_book_id]]:
                    book_users[canonical_book_id].append(self._get_user_info(read.user_id))
        
        # Filter to books read by at least min_user_count users
        result = []
        for book_id, users in book_user_counts.items():
            if len(users) >= min_user_count:
                result.append({
                    "book_id": book_id,
                    "title": book_info[book_id]["title"],
                    "author": book_info[book_id]["author"],
                    "user_count": len(users),
                    "read_count": book_read_counts[book_id],
                    "formats": list(book_formats[book_id]),
                    "users": book_users[book_id]
                })
        
        # Sort by user_count descending
        result.sort(key=lambda x: x["user_count"], reverse=True)
        
        return result
    
    def _normalize_book_identifier(self, title: str, author) -> tuple:
        """Normalize book title and author for matching across users
        
        Args:
            title: Book title string
            author: Author string or Author object (relationship)
        """
        import re
        # Convert to lowercase, strip whitespace, and normalize multiple spaces to single space
        # Also remove common punctuation that might differ
        if title:
            normalized_title = re.sub(r'\s+', ' ', title.lower().strip())
            # Remove common punctuation that might differ between entries
            normalized_title = re.sub(r'[.,;:!?\'"()]', '', normalized_title)
        else:
            normalized_title = ""
        
        # Handle author - could be string or Author object
        author_str = None
        if author:
            if hasattr(author, 'name'):  # Author object
                author_str = author.name
            elif isinstance(author, str):  # String (legacy)
                author_str = author
            else:
                author_str = str(author)
        
        if author_str:
            normalized_author = re.sub(r'\s+', ' ', author_str.lower().strip())
            # Remove common punctuation
            normalized_author = re.sub(r'[.,;:!?\'"()]', '', normalized_author)
        else:
            normalized_author = ""
        return (normalized_title, normalized_author)
    
    def calculate_similar_sentiment(self, threshold: float = 1.5) -> List[Dict]:
        """Calculate books with similar sentiment (low rating std dev)"""
        from sqlalchemy.orm import joinedload
        # Get all reads with ratings from all users, eager load author relationship
        all_reads = self.db.query(Read).options(joinedload(Read.book).joinedload(Book.author_obj)).join(Book).filter(
            Read.read_status == "READ",
            Read.rating.isnot(None)
        ).all()
        
        # Group by normalized title+author (to catch same books with different book_ids)
        title_author_map = {}  # normalized_key -> canonical_book_id
        book_ratings = defaultdict(list)
        book_info = {}
        book_users = defaultdict(list)
        
        for read in all_reads:
            if read.book and read.rating is not None:
                # Normalize title and author for matching
                normalized_key = self._normalize_book_identifier(read.book.title, read.book.author)
                normalized_key_str = f"{normalized_key[0]}|{normalized_key[1]}"
                
                # Use canonical book_id (first one we see for this title+author)
                if normalized_key_str not in title_author_map:
                    title_author_map[normalized_key_str] = read.book_id
                    # Get author name - use author_obj relationship or legacy author string
                    author_name = None
                    if read.book.author_obj:  # Author relationship object
                        author_name = read.book.author_obj.name
                    elif read.book.author:  # Legacy string field
                        author_name = read.book.author
                    book_info[read.book_id] = {
                        "title": read.book.title,
                        "author": author_name or ""
                    }
                
                canonical_book_id = title_author_map[normalized_key_str]
                
                book_ratings[canonical_book_id].append({
                    "user_id": read.user_id,
                    "rating": read.rating
                })
        
        # Calculate std dev for each book
        result = []
        for book_id, ratings_list in book_ratings.items():
            if len(ratings_list) < 2:
                continue  # Need at least 2 ratings
            
            ratings = [r["rating"] for r in ratings_list]
            std_dev = statistics.stdev(ratings) if len(ratings) > 1 else 0.0
            
            if std_dev <= threshold:
                avg_rating = statistics.mean(ratings)
                user_ratings = {}
                users_info = []
                
                for rating_data in ratings_list:
                    user_info = self._get_user_info(rating_data["user_id"])
                    user_ratings[user_info["username"]] = rating_data["rating"]
                    users_info.append(user_info)
                
                result.append({
                    "book_id": book_id,
                    "title": book_info[book_id]["title"],
                    "author": book_info[book_id]["author"],
                    "average_rating": avg_rating,
                    "rating_std_dev": std_dev,
                    "user_ratings": user_ratings,
                    "users": users_info
                })
        
        # Sort by average rating descending
        result.sort(key=lambda x: x["average_rating"], reverse=True)
        
        return result
    
    def calculate_conjugation_highlights(self, limit: int = 10) -> List[Dict]:
        """Calculate conjugation highlights with overlapping periods and user info"""
        from sqlalchemy.orm import joinedload
        # Get all reads from all users, eager load author relationship
        all_reads = self.db.query(Read).options(joinedload(Read.book).joinedload(Book.author_obj)).join(Book).filter(
            Read.read_status == "READ",
            Read.date_finished.isnot(None)
        ).all()
        
        # Group by book_id (match by title and author for same book across users)
        # Also group by normalized title+author to catch same books with different IDs
        book_reads = defaultdict(list)
        book_info = {}
        title_author_map = {}  # Map normalized title+author to book_ids
        
        for read in all_reads:
            if read.book:
                # Normalize title and author for matching
                # Get author for normalization - use author_obj or legacy author field
                author_for_norm = read.book.author_obj.name if read.book.author_obj else read.book.author
                normalized_title, normalized_author = self._normalize_book_identifier(read.book.title, author_for_norm)
                normalized_key = f"{normalized_title}|{normalized_author}"
                
                # If we've seen this title+author before, use the same book_id group
                if normalized_key in title_author_map:
                    actual_book_id = title_author_map[normalized_key]
                    book_reads[actual_book_id].append(read)
                else:
                    # First time seeing this book, use its actual book_id
                    book_reads[read.book_id].append(read)
                    title_author_map[normalized_key] = read.book_id
                    # Get author name - use author_obj relationship or legacy author string
                    author_name = None
                    if read.book.author_obj:  # Author relationship object
                        author_name = read.book.author_obj.name
                    elif read.book.author:  # Legacy string field
                        author_name = read.book.author
                    book_info[read.book_id] = {
                        "title": read.book.title,
                        "author": author_name or ""
                    }
        
        # Calculate conjugation scores
        result = []
        for book_id, reads in book_reads.items():
            if len(reads) < 2:
                continue
            
            # Collect reading periods and user info
            reading_periods = {}
            users_info = []
            finish_dates = {}
            
            for read in reads:
                if read.date_finished:
                    user_info = self._get_user_info(read.user_id)
                    username = user_info["username"]
                    
                    # Use date_started if available, otherwise estimate (30 days before finish)
                    start_date = read.date_started
                    if not start_date:
                        start_date = read.date_finished - timedelta(days=30)
                    
                    reading_periods[username] = {
                        "start_date": start_date,
                        "end_date": read.date_finished
                    }
                    finish_dates[username] = read.date_finished
                    
                    users_info.append({
                        **user_info,
                        "format": read.book.format.value if read.book.format else None
                    })
            
            if len(finish_dates) < 2:
                continue
            
            # Calculate conjugation score based on finish dates and overlap
            dates_list = list(finish_dates.values())
            dates_list.sort()
            date_range = (dates_list[-1] - dates_list[0]).days
            
            # Calculate overlap percentages between all pairs
            overlap_percentages = []
            usernames = list(reading_periods.keys())
            for i in range(len(usernames)):
                for j in range(i + 1, len(usernames)):
                    period1 = reading_periods[usernames[i]]
                    period2 = reading_periods[usernames[j]]
                    overlap = self._calculate_overlap_percentage(
                        period1["start_date"], period1["end_date"],
                        period2["start_date"], period2["end_date"]
                    )
                    overlap_percentages.append(overlap)
            
            avg_overlap = statistics.mean(overlap_percentages) if overlap_percentages else 0.0
            
            # Determine conjugation score
            # More lenient: if multiple users read the same book, show it even if dates are far apart
            # Just use lower score for wider date ranges
            if date_range <= 2 or avg_overlap >= 80.0:
                score = "high"
            elif date_range <= 4 or avg_overlap >= 50.0:
                score = "medium"
            elif date_range <= 7 or avg_overlap >= 25.0:
                score = "low"
            elif date_range <= 30:
                # Show books read within 30 days with lower score
                score = "low"
            else:
                # Still show books read by multiple users, just with lowest priority
                score = "low"
            
            # Find overlapping date ranges for visualization
            overlap_dates = []
            if len(usernames) >= 2:
                # Find the intersection of all reading periods
                all_starts = [reading_periods[u]["start_date"] for u in usernames]
                all_ends = [reading_periods[u]["end_date"] for u in usernames]
                overlap_start = max(all_starts)
                overlap_end = min(all_ends)
                if overlap_start <= overlap_end:
                    overlap_dates = [overlap_start, overlap_end]
            
            result.append({
                "book_id": book_id,
                "title": book_info[book_id]["title"],
                "author": book_info[book_id]["author"],
                "conjugation_score": score,
                "finish_dates": finish_dates,
                "reading_periods": reading_periods,
                "overlap_percentage": avg_overlap,
                "overlap_dates": overlap_dates,
                "users": users_info
            })
        
        # Sort by score (high > medium > low) and limit
        score_order = {"high": 3, "medium": 2, "low": 1}
        result.sort(key=lambda x: score_order.get(x["conjugation_score"], 0), reverse=True)
        
        return result[:limit]

