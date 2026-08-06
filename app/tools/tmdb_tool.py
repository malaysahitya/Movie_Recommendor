import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

# TMDB Genre ID Map
GENRE_MAP: Dict[str, int] = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "fantasy": 14,
    "history": 36,
    "horror": 27,
    "mystery": 9648,
    "romance": 10749,
    "sci-fi": 878,
    "science fiction": 878,
    "thriller": 53,
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
    Fetches candidate movies from TMDB API for a specific year, genre, and industry.
    
    Args:
        year: Release year (e.g. 2015)
        genre: Target genre (e.g. Action)
        industry: Hollywood, Bollywood, or Anime
        limit: Max candidates to return
        
    Returns:
        List of candidate movie dictionaries.
    """
    if not settings.TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY is missing. Please add TMDB_API_KEY to your .env file.")

    genre_lower = genre.lower().strip()
    genre_id = GENRE_MAP.get(genre_lower, None)

    # Base parameters for TMDB Discover API
    params: Dict[str, Any] = {
        "api_key": settings.TMDB_API_KEY,
        "primary_release_year": year,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,  # Ensure quality filter
        "page": 1,
    }

    if genre_id:
        params["with_genres"] = genre_id

    industry_clean = industry.lower().strip()

    if industry_clean == "hollywood":
        params["with_original_language"] = "en"
    elif industry_clean == "bollywood":
        # Include Hindi language or Indian origin releases
        params["with_original_language"] = "hi"
        params["region"] = "IN"
        params["vote_count.gte"] = 10  # Lower threshold for regional hits
    elif industry_clean == "anime":
        params["with_original_language"] = "ja"
        params["with_genres"] = 16  # Force Animation genre for Anime
        params["vote_count.gte"] = 20

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
        
        if response.status_code != 200:
            # Fallback query if strict vote count returns empty
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
