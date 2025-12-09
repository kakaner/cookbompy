from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from enum import Enum

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.statistics_service import StatisticsService
from app.schemas.statistics import (
    StatisticsSummary,
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    FormatBreakdown,
    FormatBreakdownItem,
    BookTypeBreakdown,
    BookTypeBreakdownItem,
    GenreBreakdown,
    GenreBreakdownItem,
    AuthorFrequency,
    AuthorFrequencyItem,
    RatingDistribution,
    ViewnerRateResponse,
    CommentuRateResponse,
    CommunityStats,
    ReadsInCommon,
    ReadsInCommonItem,
    SimilarSentiment,
    SimilarSentimentItem,
    ConjugationHighlights,
    ConjugationItem,
    UserInfo,
    UserReadInfo,
    ReadingPeriod
)

router = APIRouter(prefix="/statistics", tags=["statistics"])


class TimeDimension(str, Enum):
    """Time dimension options"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    SEMESTER = "semester"
    ALLTIME = "alltime"


class PointAlgorithm(str, Enum):
    """Point algorithm options"""
    ALLEGORY = "allegory"
    REASONABLE = "reasonable"


@router.get("/summary", response_model=StatisticsSummary)
def get_statistics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quick summary statistics for library pane"""
    service = StatisticsService(db)
    
    # Get all reads for user
    reads = service.get_reads_query(current_user.id).all()
    
    if not reads:
        return StatisticsSummary(
            total_reads=0,
            unique_books=0,
            lifetime_points_allegory=0.0,
            lifetime_points_reasonable=0.0,
            format_breakdown=[],
            viewner_rate=0.0,
            commentu_rate=0.0,
            reads_in_common_count=0,
            conjugation_highlights_count=0
        )
    
    # Calculate totals
    total_reads = len(reads)
    unique_books = len(set(r.book_id for r in reads if r.book_id))
    
    # Calculate lifetime points
    lifetime_points_allegory = sum(
        (r.calculated_points_allegory or 0) / 100.0 for r in reads
    )
    lifetime_points_reasonable = sum(
        (r.calculated_points_reasonable or 0) / 100.0 for r in reads
    )
    
    # Get format breakdown (top 4)
    format_data = service.calculate_format_breakdown(current_user.id, "alltime")
    format_breakdown = [
        FormatBreakdownItem(
            format=item["format"],
            count=item["count"],
            percentage=item["percentage"]
        )
        for item in format_data[:4]
    ]
    
    # Calculate viewner rate
    _, viewner_rate = service.calculate_viewner_rate(current_user.id, "alltime")
    
    # Calculate commentu rate
    _, commentu_rate = service.calculate_commentu_rate(current_user.id, "alltime")
    
    # Get community stats counts
    reads_in_common = service.calculate_community_reads_in_common(current_user.id, min_user_count=2)
    conjugation_highlights = service.calculate_conjugation_highlights(limit=10)
    
    return StatisticsSummary(
        total_reads=total_reads,
        unique_books=unique_books,
        lifetime_points_allegory=lifetime_points_allegory,
        lifetime_points_reasonable=lifetime_points_reasonable,
        format_breakdown=format_breakdown,
        viewner_rate=viewner_rate,
        commentu_rate=commentu_rate,
        reads_in_common_count=len(reads_in_common),
        conjugation_highlights_count=len(conjugation_highlights)
    )


@router.get("/reading", response_model=TimeSeriesResponse)
def get_reading_statistics(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reading statistics over time (reads count)"""
    service = StatisticsService(db)
    stats = service.calculate_reading_stats(current_user.id, time_dimension.value)
    
    data_points = [
        TimeSeriesDataPoint(
            label=item["label"],
            value=float(item["read_count"]),
            count=item["read_count"]
        )
        for item in stats
    ]
    
    return TimeSeriesResponse(
        data=data_points,
        time_dimension=time_dimension.value
    )


@router.get("/points", response_model=TimeSeriesResponse)
def get_points_statistics(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    algorithm: PointAlgorithm = Query(default=PointAlgorithm.ALLEGORY),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get points earned over time"""
    service = StatisticsService(db)
    stats = service.calculate_points_trends(
        current_user.id, 
        time_dimension.value, 
        algorithm.value
    )
    
    data_points = [
        TimeSeriesDataPoint(
            label=item["label"],
            value=item["value"],
            count=item["count"]
        )
        for item in stats
    ]
    
    return TimeSeriesResponse(
        data=data_points,
        time_dimension=time_dimension.value
    )


@router.get("/format-breakdown", response_model=FormatBreakdown)
def get_format_breakdown(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get format distribution over time"""
    service = StatisticsService(db)
    format_data = service.calculate_format_breakdown(current_user.id, time_dimension.value)
    
    total = sum(item["count"] for item in format_data)
    
    items = [
        FormatBreakdownItem(
            format=item["format"],
            count=item["count"],
            percentage=item["percentage"]
        )
        for item in format_data
    ]
    
    return FormatBreakdown(
        items=items,
        total=total,
        time_dimension=time_dimension.value
    )


@router.get("/book-type-breakdown", response_model=BookTypeBreakdown)
def get_book_type_breakdown(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get book type distribution over time"""
    service = StatisticsService(db)
    type_data = service.calculate_book_type_breakdown(current_user.id, time_dimension.value)
    
    total = sum(item["count"] for item in type_data)
    
    items = [
        BookTypeBreakdownItem(
            book_type=item["book_type"],
            count=item["count"],
            percentage=item["percentage"]
        )
        for item in type_data
    ]
    
    return BookTypeBreakdown(
        items=items,
        total=total,
        time_dimension=time_dimension.value
    )


@router.get("/genre-breakdown", response_model=GenreBreakdown)
def get_genre_breakdown(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get genre distribution over time"""
    service = StatisticsService(db)
    genre_data = service.calculate_genre_breakdown(current_user.id, time_dimension.value, limit)
    
    total = sum(item["count"] for item in genre_data)
    
    items = [
        GenreBreakdownItem(
            genre=item["genre"],
            count=item["count"],
            percentage=item["percentage"]
        )
        for item in genre_data
    ]
    
    return GenreBreakdown(
        items=items,
        total=total,
        time_dimension=time_dimension.value
    )


@router.get("/author-frequency", response_model=AuthorFrequency)
def get_author_frequency(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most-read authors based on read count"""
    service = StatisticsService(db)
    author_data = service.calculate_author_frequency(current_user.id, limit)
    
    items = [
        AuthorFrequencyItem(
            author=item["author"],
            read_count=item["read_count"],
            unique_books=item["unique_books"]
        )
        for item in author_data
    ]
    
    return AuthorFrequency(
        items=items,
        limit=limit
    )


@router.get("/viewner-rate", response_model=ViewnerRateResponse)
def get_viewner_rate(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get viewner rate (percentage of reads with reviews) over time"""
    service = StatisticsService(db)
    data, overall_rate = service.calculate_viewner_rate(current_user.id, time_dimension.value)
    
    data_points = [
        TimeSeriesDataPoint(
            label=item["label"],
            value=item["value"],
            count=item["count"]
        )
        for item in data
    ]
    
    return ViewnerRateResponse(
        data=data_points,
        overall_rate=overall_rate,
        time_dimension=time_dimension.value
    )


@router.get("/commentu-rate", response_model=CommentuRateResponse)
def get_commentu_rate(
    time_dimension: TimeDimension = Query(default=TimeDimension.ALLTIME),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get commentu rate (percentage of reads with comments) over time"""
    service = StatisticsService(db)
    data, overall_rate = service.calculate_commentu_rate(current_user.id, time_dimension.value)
    
    data_points = [
        TimeSeriesDataPoint(
            label=item["label"],
            value=item["value"],
            count=item["count"]
        )
        for item in data
    ]
    
    return CommentuRateResponse(
        data=data_points,
        overall_rate=overall_rate,
        time_dimension=time_dimension.value
    )


@router.get("/community", response_model=CommunityStats)
def get_community_statistics(
    min_user_count: int = Query(default=2, ge=2),
    conjugation_limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get community statistics (reads in common, sentiment, conjugation)"""
    service = StatisticsService(db)
    
    # Reads in common
    reads_in_common_data = service.calculate_community_reads_in_common(
        current_user.id, 
        min_user_count
    )
    reads_in_common_items = [
        ReadsInCommonItem(
            book_id=item["book_id"],
            title=item["title"],
            author=item["author"],
            user_count=item["user_count"],
            read_count=item["read_count"],
            formats=item["formats"],
            users=[UserInfo(**user) for user in item["users"]]
        )
        for item in reads_in_common_data
    ]
    
    # Similar sentiment
    similar_sentiment_data = service.calculate_similar_sentiment(threshold=1.5)
    similar_sentiment_items = [
        SimilarSentimentItem(
            book_id=item["book_id"],
            title=item["title"],
            author=item["author"],
            average_rating=item["average_rating"],
            rating_std_dev=item["rating_std_dev"],
            user_ratings=item["user_ratings"],
            users=[UserInfo(**user) for user in item["users"]]
        )
        for item in similar_sentiment_data
    ]
    
    # Conjugation highlights
    conjugation_data = service.calculate_conjugation_highlights(conjugation_limit)
    conjugation_items = [
        ConjugationItem(
            book_id=item["book_id"],
            title=item["title"],
            author=item["author"],
            conjugation_score=item["conjugation_score"],
            finish_dates=item["finish_dates"],
            reading_periods={
                username: ReadingPeriod(**period)
                for username, period in item["reading_periods"].items()
            },
            overlap_percentage=item["overlap_percentage"],
            overlap_dates=item.get("overlap_dates"),
            users=[UserReadInfo(**user) for user in item["users"]]
        )
        for item in conjugation_data
    ]
    
    return CommunityStats(
        reads_in_common=ReadsInCommon(
            items=reads_in_common_items,
            min_user_count=min_user_count
        ),
        similar_sentiment=SimilarSentiment(
            items=similar_sentiment_items,
            threshold=1.5
        ),
        conjugation_highlights=ConjugationHighlights(
            items=conjugation_items,
            limit=conjugation_limit
        )
    )

