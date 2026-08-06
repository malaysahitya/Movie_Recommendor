import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.config import settings

class TMDBFetchParams(BaseModel):
    year: int = Field(..., ge=1950, le=2026, description="Release year of the movies to search for (e.g., 2015)")
    genre: str = Field(..., description="Genre name (e.g. Action, Comedy, Drama, Sci-Fi, Animation)")
    industry: str = Field(..., description="Target cinema industry: 'Hollywood', 'Bollywood', or 'Anime'")
    limit: int = Field(default=20, ge=1, le=50, description="Maximum number of candidate movies to retrieve")

GENRE_MAP: Dict[str, int] = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
    "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
    "fantasy": 14, "history": 36, "horror": 27, "mystery": 9648,
    "romance": 10749, "sci-fi": 878, "science fiction": 878, "thriller": 53
}

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

async def fetch_movies_by_year_and_genre(
    year: int,
    genre: str,
    industry: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of candidate movies from TMDB for a specific year, genre, and industry.

    Args:
        year (int): Target release year (must be between 1950 and 2026).
        genre (str): Movie genre name (e.g., 'Action', 'Drama', 'Sci-Fi').
        industry (str): Regional industry ('Hollywood', 'Bollywood', or 'Anime').
        limit (int): Max candidate movies to fetch (default: 20).

    Returns:
        List[Dict[str, Any]]: List of dictionary items containing title, release date, ratings, vote count, synopsis, and poster URL.

    Raises:
        ValueError: If TMDB_API_KEY is missing or invalid.
    """
    if not settings.TMDB_API_KEY:
        # Guided recovery prompt for LLM
        return [{
            "error": "TMDB_API_KEY_MISSING",
            "recovery_instruction": "Please inform the user or configure TMDB_API_KEY in environment settings."
        }]

    genre_lower = genre.lower().strip()
    genre_id = GENRE_MAP.get(genre_lower, None)

    params: Dict[str, Any] = {
        "api_key": settings.TMDB_API_KEY,
        "primary_release_year": year,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "page": 1,
    }

    if genre_id:
        params["with_genres"] = genre_id

    industry_clean = industry.lower().strip()
    if industry_clean == "hollywood":
        params["with_original_language"] = "en"
    elif industry_clean == "bollywood":
        params["with_original_language"] = "hi"
        params["region"] = "IN"
        params["vote_count.gte"] = 10
    elif industry_clean == "anime":
        params["with_original_language"] = "ja"
        params["with_genres"] = 16
        params["vote_count.gte"] = 20

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
            if response.status_code != 200:
                params["vote_count.gte"] = 0
                response = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
                
            if response.status_code != 200:
                return []

            data = response.json()
            results = data.get("results", [])

            candidate_movies = []
            for item in results[:limit]:
                poster_path = item.get("poster_path")
                poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
                
                candidate_movies.append({
                    "id": str(item.get("id")),
                    "title": item.get("title") or item.get("original_title"),
                    "original_title": item.get("original_title"),
                    "release_year": year,
                    "release_date": item.get("release_date"),
                    "rating": float(item.get("vote_average", 0.0)),
                    "vote_count": int(item.get("vote_count", 0)),
                    "popularity_score": float(item.get("popularity", 0.0)),
                    "synopsis": item.get("overview") or "No overview available.",
                    "poster_url": poster_url,
                    "genre_ids": item.get("genre_ids", []),
                })

            return candidate_movies
        except Exception as e:
            return [{
                "error": str(e),
                "recovery_instruction": "Network error during TMDB API fetch. Retrying or falling back."
            }]
