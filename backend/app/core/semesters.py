"""
Semester calculation utilities for CookBomPy

Semester Definition:
- Semester 1: May 15, 2005 - November 14, 2005
- Semester 2: November 15, 2005 - May 14, 2006
- Pattern continues in 6-month cycles
"""
from datetime import date, datetime
from typing import Tuple, Optional


# The epoch: first semester starts May 15, 2005
EPOCH_YEAR = 2005
EPOCH_MONTH = 5
EPOCH_DAY = 15

# Semester boundaries within a year
# Semester type 1 (odd semesters): May 15 - November 14
# Semester type 2 (even semesters): November 15 - May 14


def calculate_semester_number(check_date: date) -> int:
    """
    Given a date, return the semester number.
    
    Semester 1: May 15, 2005 - November 14, 2005
    Semester 2: November 15, 2005 - May 14, 2006
    Semester 3: May 15, 2006 - November 14, 2006
    ...and so on
    
    Args:
        check_date: The date to check
        
    Returns:
        Semester number (1-based)
        
    Raises:
        ValueError: If date is before the epoch (May 15, 2005)
    """
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    
    epoch = date(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY)
    
    if check_date < epoch:
        raise ValueError(f"Date {check_date} is before the epoch (May 15, 2005)")
    
    # Calculate years since epoch
    year_diff = check_date.year - EPOCH_YEAR
    
    # Determine which half of the year we're in
    month = check_date.month
    day = check_date.day
    
    # May 15 - November 14: Type 1 (odd semesters in first year pattern)
    # November 15 - May 14: Type 2 (even semesters)
    
    if month < 5 or (month == 5 and day < 15):
        # Before May 15 of this year - we're in the second half of a semester
        # that started in November of the previous year
        semester_year_offset = (year_diff - 1) * 2
        semester_number = semester_year_offset + 2  # Even semester
    elif month < 11 or (month == 11 and day < 15):
        # May 15 to November 14 - odd semester
        semester_year_offset = year_diff * 2
        semester_number = semester_year_offset + 1  # Odd semester
    else:
        # November 15 onwards - even semester
        semester_year_offset = year_diff * 2
        semester_number = semester_year_offset + 2  # Even semester
    
    return semester_number


def get_semester_date_range(semester_number: int) -> Tuple[date, date]:
    """
    Given a semester number, return the (start_date, end_date) tuple.
    
    Args:
        semester_number: The semester number (1-based)
        
    Returns:
        Tuple of (start_date, end_date)
        
    Raises:
        ValueError: If semester_number is less than 1
    """
    if semester_number < 1:
        raise ValueError("Semester number must be at least 1")
    
    # Calculate the year offset (0-indexed pairs of semesters per year)
    # Semester 1,2 -> year offset 0
    # Semester 3,4 -> year offset 1
    # etc.
    year_offset = (semester_number - 1) // 2
    
    # Is this an odd (type 1) or even (type 2) semester?
    is_odd = semester_number % 2 == 1
    
    if is_odd:
        # Odd semester: May 15 - November 14 of the same year
        start_year = EPOCH_YEAR + year_offset
        start_date = date(start_year, 5, 15)
        end_date = date(start_year, 11, 14)
    else:
        # Even semester: November 15 of one year - May 14 of the next
        start_year = EPOCH_YEAR + year_offset
        end_year = start_year + 1
        start_date = date(start_year, 11, 15)
        end_date = date(end_year, 5, 14)
    
    return (start_date, end_date)


def get_current_semester() -> int:
    """
    Return the current semester number based on today's date.
    
    Returns:
        Current semester number
    """
    return calculate_semester_number(date.today())


def format_semester_date_range(semester_number: int) -> str:
    """
    Format the date range for display.
    
    Args:
        semester_number: The semester number
        
    Returns:
        Formatted string like "May 15, 2005 - Nov 14, 2005"
    """
    start_date, end_date = get_semester_date_range(semester_number)
    return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"


def get_semester_display_name(semester_number: int, custom_name: Optional[str] = None) -> str:
    """
    Get display name for a semester.
    
    Args:
        semester_number: The semester number
        custom_name: Optional custom name set by user
        
    Returns:
        Custom name if set, otherwise "Semester {number}"
    """
    if custom_name:
        return custom_name
    return f"Semester {semester_number}"

