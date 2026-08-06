from typing import List, Dict, Any
from app.tools.scoring_tool import calculate_composite_score

ADULT_GENRE_IDS = [27, 80, 53]  # Horror, Crime, Thriller

class AnalysisAgent:
    """
    Sub-Agent 3: Analysis & Ranking
    Deduplicates candidates, computes composite quality scores, detects 18+ adult themes, and selects top movies overall.
    """
    def __init__(self):
        self.name = "AnalysisAgent"

    def rank_and_select_top_movies(
        self,
        raw_candidates: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        # 1. Deduplicate by title or ID
        seen_ids = set()
        unique_candidates = []
        for movie in raw_candidates:
            movie_id = movie["id"]
            if movie_id not in seen_ids:
                seen_ids.add(movie_id)
                unique_candidates.append(movie)

        # 2. Compute composite quality score and flag 18+ content
        for movie in unique_candidates:
            composite = calculate_composite_score(
                rating=movie.get("rating", 0.0),
                vote_count=movie.get("vote_count", 0),
                popularity=movie.get("popularity_score", 0.0)
            )
            movie["composite_score"] = composite
            
            # Check for 18+ adult content themes
            g_ids = movie.get("genre_ids", [])
            movie["is_18_plus"] = any(gid in ADULT_GENRE_IDS for gid in g_ids)

        # 3. Sort by composite quality score descending
        sorted_candidates = sorted(
            unique_candidates,
            key=lambda x: (x["composite_score"], x["rating"], x["vote_count"]),
            reverse=True
        )

        return sorted_candidates[:limit]
