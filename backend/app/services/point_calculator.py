"""
Point calculation service for bompyallegory and bompyreasonable algorithms
"""
from typing import Optional
from app.core.enums import BookType


class PointCalculator:
    """Calculate points for books based on bompyallegory and bompyreasonable algorithms"""
    
    # Base points by book type (stored as integer * 100 for precision)
    BASE_POINTS = {
        BookType.FICTION: 100,  # 1.0 point
        BookType.NONFICTION: 150,  # 1.5 points
        BookType.YA: 75,  # 0.75 points
        BookType.CHILDRENS: 50,  # 0.5 points
        BookType.COMIC: 50,  # 0.5 points (standalone comic volume)
        BookType.NOVELLA: 50,  # 0.5 points
        BookType.SHORT_STORY: 10,  # 0.1 points
        BookType.OTHER: 100,  # Default to 1.0 point
    }
    
    GRACE_BUFFER = 13  # 13-page grace buffer
    FIRST_THRESHOLD = 500  # First threshold for length add-ons
    ADDITIONAL_THRESHOLD = 100  # Every 100 pages after first threshold
    
    @classmethod
    def calculate_length_addons(cls, page_count: Optional[int]) -> int:
        """
        Calculate length add-ons based on page count
        Returns: points as integer * 100 (e.g., 200 = 2.0 points)
        """
        if not page_count or page_count <= 0:
            return 0
        
        # Apply grace buffer
        effective_pages = page_count + cls.GRACE_BUFFER
        
        # Calculate add-ons
        if effective_pages < cls.FIRST_THRESHOLD:
            return 0
        
        # First threshold gives +1 point
        addons = 100  # 1.0 point
        
        # Every additional 100 pages gives +1 point
        pages_over_first = effective_pages - cls.FIRST_THRESHOLD
        additional_addons = (pages_over_first // cls.ADDITIONAL_THRESHOLD) * 100
        
        return addons + additional_addons
    
    @classmethod
    def get_base_points(cls, book_type: Optional[BookType], overridden_base: Optional[int] = None) -> int:
        """
        Get base points for a book type
        Returns: points as integer * 100 (e.g., 100 = 1.0 point)
        """
        if overridden_base is not None:
            return overridden_base
        
        if not book_type:
            return 100  # Default to 1.0 point
        
        return cls.BASE_POINTS.get(book_type, 100)  # Default to 1.0 point
    
    @classmethod
    def calculate_bompyallegory(
        cls,
        book_type: Optional[BookType],
        page_count: Optional[int],
        is_reread: bool = False,
        overridden_base: Optional[int] = None
    ) -> int:
        """
        Calculate points using bompyallegory algorithm (with reread penalty)
        Formula: (Base Points + Length Add-ons) × Reread Multiplier
        Returns: points as integer * 100 (e.g., 150 = 1.50 points)
        """
        base = cls.get_base_points(book_type, overridden_base)
        length_addons = cls.calculate_length_addons(page_count)
        
        # Reread multiplier: 0.5 if reread, 1.0 if first read
        reread_multiplier = 50 if is_reread else 100  # 0.5 or 1.0 as integer * 100
        
        # Calculate: (base + length) * multiplier
        total = ((base + length_addons) * reread_multiplier) // 100
        
        return total
    
    @classmethod
    def calculate_bompyreasonable(
        cls,
        book_type: Optional[BookType],
        page_count: Optional[int],
        overridden_base: Optional[int] = None
    ) -> int:
        """
        Calculate points using bompyreasonable algorithm (no reread penalty)
        Formula: Base Points + Length Add-ons
        Returns: points as integer * 100 (e.g., 200 = 2.0 points)
        """
        base = cls.get_base_points(book_type, overridden_base)
        length_addons = cls.calculate_length_addons(page_count)
        
        return base + length_addons
    
    @classmethod
    def calculate_points(
        cls,
        book_type: Optional[BookType],
        page_count: Optional[int],
        is_reread: bool = False,
        overridden_base: Optional[int] = None
    ) -> tuple[int, int]:
        """
        Calculate both algorithms at once
        Returns: (bompyallegory_points, bompyreasonable_points) as integers * 100
        """
        allegory = cls.calculate_bompyallegory(book_type, page_count, is_reread, overridden_base)
        reasonable = cls.calculate_bompyreasonable(book_type, page_count, overridden_base)
        
        return (allegory, reasonable)
    
    @classmethod
    def format_points(cls, points_int: Optional[int]) -> float:
        """
        Convert integer * 100 to float
        Example: 150 -> 1.50
        """
        if points_int is None:
            return 0.0
        return points_int / 100.0
    
    @classmethod
    def parse_points(cls, points_float: float) -> int:
        """
        Convert float to integer * 100
        Example: 1.50 -> 150
        """
        return int(round(points_float * 100))

