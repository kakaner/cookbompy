from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series"""
    label: str
    value: float
    count: Optional[int] = None  # For counts (reads, books, etc.)


class TimeSeriesResponse(BaseModel):
    """Time series data for charts"""
    data: List[TimeSeriesDataPoint]
    time_dimension: str


class FormatBreakdownItem(BaseModel):
    """Format breakdown item"""
    format: str
    count: int
    percentage: float
    icon: Optional[str] = None


class FormatBreakdown(BaseModel):
    """Format distribution"""
    items: List[FormatBreakdownItem]
    total: int
    time_dimension: str


class BookTypeBreakdownItem(BaseModel):
    """Book type breakdown item"""
    book_type: str
    count: int
    percentage: float


class BookTypeBreakdown(BaseModel):
    """Book type distribution"""
    items: List[BookTypeBreakdownItem]
    total: int
    time_dimension: str


class GenreBreakdownItem(BaseModel):
    """Genre breakdown item"""
    genre: str
    count: int
    percentage: float


class GenreBreakdown(BaseModel):
    """Genre distribution"""
    items: List[GenreBreakdownItem]
    total: int
    time_dimension: str


class AuthorFrequencyItem(BaseModel):
    """Author frequency item"""
    author: str
    read_count: int
    unique_books: int


class AuthorFrequency(BaseModel):
    """Author frequency list"""
    items: List[AuthorFrequencyItem]
    limit: int


class RatingDistributionItem(BaseModel):
    """Rating distribution item"""
    rating: float
    count: int
    percentage: float


class RatingDistribution(BaseModel):
    """Rating distribution"""
    items: List[RatingDistributionItem]
    total: int
    average_rating: float
    time_dimension: str


class ViewnerRateResponse(BaseModel):
    """Viewner rate over time"""
    data: List[TimeSeriesDataPoint]
    overall_rate: float
    time_dimension: str


class CommentuRateResponse(BaseModel):
    """Commentu rate over time"""
    data: List[TimeSeriesDataPoint]
    overall_rate: float
    time_dimension: str


class UserInfo(BaseModel):
    """User information for conjugation responses"""
    user_id: int
    username: str
    display_name: str
    profile_photo_url: Optional[str] = None


class UserReadInfo(UserInfo):
    """User information with read format"""
    format: Optional[str] = None


class ReadingPeriod(BaseModel):
    """Reading period (start and end dates)"""
    start_date: date
    end_date: date


class ReadsInCommonItem(BaseModel):
    """Reads in common item"""
    book_id: int
    title: str
    author: str
    user_count: int
    read_count: int
    formats: List[str]  # Formats users read this in
    users: List[UserInfo]  # User information


class ReadsInCommon(BaseModel):
    """Reads in common list"""
    items: List[ReadsInCommonItem]
    min_user_count: int


class SimilarSentimentItem(BaseModel):
    """Similar sentiment item"""
    book_id: int
    title: str
    author: str
    average_rating: float
    rating_std_dev: float
    user_ratings: Dict[str, float]  # username -> rating
    users: List[UserInfo]  # User information


class SimilarSentiment(BaseModel):
    """Similar sentiment books"""
    items: List[SimilarSentimentItem]
    threshold: float


class ConjugationItem(BaseModel):
    """Conjugation item"""
    book_id: int
    title: str
    author: str
    conjugation_score: str  # "high", "medium", "low"
    finish_dates: Dict[str, date]  # username -> finish_date
    reading_periods: Dict[str, ReadingPeriod]  # username -> ReadingPeriod
    overlap_percentage: float
    overlap_dates: Optional[List[date]] = None  # [start, end] of overlap period
    users: List[UserReadInfo]  # User information with format


class ConjugationHighlights(BaseModel):
    """Conjugation highlights"""
    items: List[ConjugationItem]
    limit: int


class CommunityStats(BaseModel):
    """Community statistics"""
    reads_in_common: ReadsInCommon
    similar_sentiment: SimilarSentiment
    conjugation_highlights: ConjugationHighlights


class StatisticsSummary(BaseModel):
    """Quick summary statistics for library pane"""
    total_reads: int
    unique_books: int
    lifetime_points_allegory: float
    lifetime_points_reasonable: float
    format_breakdown: List[FormatBreakdownItem]  # Top 4
    viewner_rate: float
    commentu_rate: float
    reads_in_common_count: int
    conjugation_highlights_count: int

