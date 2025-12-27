"""Time-related utility functions."""

from datetime import datetime, time, timedelta
from typing import List, Optional
from src.models import TimeWindow


def is_open_at(
    opening_hours: List[TimeWindow],
    check_time: datetime,
) -> bool:
    """Check if a place is open at a given time.
    
    Args:
        opening_hours: List of time windows with opening hours.
        check_time: Time to check.
        
    Returns:
        True if open at the given time.
    """
    if not opening_hours:
        return True  # Assume always open if no hours specified
    
    day_name = check_time.strftime("%A")
    check_time_only = check_time.time()
    
    for window in opening_hours:
        # Check if day matches
        if window.days and day_name not in window.days:
            continue
        
        # Check if time is within window
        if window.start <= check_time_only <= window.end:
            return True
    
    return False


def get_next_available_time(
    opening_hours: List[TimeWindow],
    after_time: datetime,
) -> Optional[datetime]:
    """Get the next time a place opens after a given time.
    
    Args:
        opening_hours: List of time windows.
        after_time: Starting time to search from.
        
    Returns:
        Next opening datetime, or None if not found in next 7 days.
    """
    if not opening_hours:
        return after_time
    
    # Search for next 7 days
    for day_offset in range(7):
        check_date = after_time.date() + timedelta(days=day_offset)
        day_name = (after_time + timedelta(days=day_offset)).strftime("%A")
        
        for window in opening_hours:
            # Skip if this window doesn't apply to this day
            if window.days and day_name not in window.days:
                continue
            
            # Combine date and start time
            opening_datetime = datetime.combine(check_date, window.start)
            
            # Only return if it's after the requested time
            if opening_datetime > after_time:
                return opening_datetime
    
    return None


def calculate_duration(start: datetime, end: datetime) -> int:
    """Calculate duration between two times in minutes.
    
    Args:
        start: Start time.
        end: End time.
        
    Returns:
        Duration in minutes.
    """
    delta = end - start
    return int(delta.total_seconds() / 60)


def is_seasonal_match(
    seasonal: Optional[List[str]],
    date: datetime,
) -> bool:
    """Check if an activity is appropriate for the given season.
    
    Args:
        seasonal: List of seasons (e.g., ["spring", "summer"]).
        date: Date to check.
        
    Returns:
        True if appropriate or no seasonal restriction.
    """
    if not seasonal:
        return True  # No restriction
    
    # Simple season detection (Northern Hemisphere)
    month = date.month
    
    if month in [3, 4, 5]:
        current_season = "spring"
    elif month in [6, 7, 8]:
        current_season = "summer"
    elif month in [9, 10, 11]:
        current_season = "autumn"
    else:
        current_season = "winter"
    
    return current_season in seasonal


def split_into_time_blocks(
    start_time: datetime,
    end_time: datetime,
    block_duration_minutes: int = 180,
) -> List[tuple[datetime, datetime]]:
    """Split a day into time blocks.
    
    Args:
        start_time: Start of day.
        end_time: End of day.
        block_duration_minutes: Duration of each block in minutes.
        
    Returns:
        List of (start, end) tuples for each block.
    """
    blocks = []
    current = start_time
    
    while current < end_time:
        block_end = min(current + timedelta(minutes=block_duration_minutes), end_time)
        blocks.append((current, block_end))
        current = block_end
    
    return blocks