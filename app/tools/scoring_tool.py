import math
from typing import Dict, Any

def calculate_composite_score(
    rating: float,
    vote_count: int,
    popularity: float
) -> float:
    """
    Calculates a normalized composite quality score (0.0 to 100.0) combining rating, vote volume, and popularity.

    Args:
        rating (float): Average audience rating score out of 10.0.
        vote_count (int): Total number of audience votes recorded.
        popularity (float): Popularity index metric.

    Returns:
        float: Composite quality index score between 0.0 and 100.0 rounded to 2 decimal places.

    Raises:
        ValueError: If rating is negative.
    """
    if rating < 0:
        raise ValueError("Rating score cannot be negative.")

    if rating == 0:
        return 0.0

    # 1. Base Rating Score (0 to 70 points)
    rating_component = (rating / 10.0) * 70.0

    # 2. Vote Confidence & Popularity (0 to 30 points)
    vote_weight = min(1.0, math.log10(max(vote_count, 1)) / 5.0)
    pop_weight = min(1.0, math.log10(max(popularity, 1.0) + 1) / 3.0)
    
    volume_component = ((vote_weight * 0.6) + (pop_weight * 0.4)) * 30.0

    composite = rating_component + volume_component
    return round(min(100.0, max(0.0, composite)), 2)
