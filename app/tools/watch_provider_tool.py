import httpx
from typing import List, Dict, Any
from app.config import settings
from app.models.movie import WatchProvider

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w92"

async def get_watch_providers(movie_id: str, industry: str = "Hollywood") -> List[WatchProvider]:
    """
    Fetches streaming availability for a movie from TMDB Watch Providers API.

    Args:
        movie_id (str): Unique movie identifier (TMDB ID or numeric string).
        industry (str): Regional cinema category ('Hollywood', 'Bollywood', or 'Anime').

    Returns:
        List[WatchProvider]: List of WatchProvider models containing provider name and type.

    Raises:
        ValueError: If movie_id is empty.
    """
    if not movie_id:
        raise ValueError("movie_id parameter cannot be empty.")

    providers: List[WatchProvider] = []
    
    if settings.TMDB_API_KEY and movie_id.isdigit():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
                    params={"api_key": settings.TMDB_API_KEY}
                )
                if res.status_code == 200:
                    data = res.json().get("results", {})
                    region_data = data.get("IN") or data.get("US") or {}
                    flatrate = region_data.get("flatrate", [])
                    
                    for provider in flatrate[:3]:
                        logo = provider.get("logo_path")
                        logo_url = f"{TMDB_IMAGE_BASE}{logo}" if logo else None
                        providers.append(WatchProvider(
                            provider_name=provider.get("provider_name", "Streaming"),
                            logo_path=logo_url,
                            type="flatrate"
                        ))
        except Exception:
            pass

    # Default fallback streaming options based on industry
    if not providers:
        ind_clean = industry.lower()
        if "anime" in ind_clean:
            providers = [
                WatchProvider(provider_name="Crunchyroll", type="flatrate"),
                WatchProvider(provider_name="Netflix", type="flatrate")
            ]
        elif "bollywood" in ind_clean:
            providers = [
                WatchProvider(provider_name="Disney+ Hotstar / JioCinema", type="flatrate"),
                WatchProvider(provider_name="Amazon Prime Video", type="flatrate")
            ]
        else:
            providers = [
                WatchProvider(provider_name="Netflix", type="flatrate"),
                WatchProvider(provider_name="Amazon Prime Video", type="flatrate")
            ]

    return providers
