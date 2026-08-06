import math
from typing import Dict, Any

def calculate_composite_score(
    rating: float,
    vote_count: int,
    popularity: float
) -> float:
    """
    Calculates a normalized composite quality score (0.0 to 100.0) combining rating, vote volume, and popularity.
    
    Formula:
      Weighted Rating Score (70%): (rating / 10.0) * 70.0
      Popularity & Vote Volume Score (30%): Log-scaled vote confidence & popularity percentile * 30.0
    """
    if rating <= 0:
        return 0.0

    # 1. Base Rating Score (0 to 70 points)
    rating_component = (rating / 10.0) * 70.0

    # 2. Vote Confidence & Popularity (0 to 30 points)
    # Use log scale so 1000 votes vs 100000 votes scales smoothly
    vote_weight = min(1.0, math.log10(max(vote_count, 1)) / 5.0)  # capped at ~100k votes
    pop_weight = min(1.0, math.log10(max(popularity, 1.0) + 1) / 3.0)
    
    volume_component = ((vote_weight * 0.6) + (pop_weight * 0.4)) * 30.0

    composite = rating_component + volume_component
    return round(min(100.0, max(0.0, composite)), 2)
