import httpx
from typing import List, Dict, Any
from app.config import settings
from app.tools.watch_provider_tool import get_watch_providers
from app.models.movie import MovieItem

class ExplainerAgent:
    """
    Sub-Agent 4: Explainer
    Generates personalized 'Why you should watch this' agent reasoning and attaches watch providers.
    """
    def __init__(self):
        self.name = "ExplainerAgent"

    async def generate_explanations(
        self,
        ranked_movies: List[Dict[str, Any]],
        genre: str,
        industry: str
    ) -> List[MovieItem]:
        final_movie_items: List[MovieItem] = []

        for movie in ranked_movies:
            movie_id = str(movie["id"])
            title = movie["title"]
            year = movie["release_year"]
            rating = movie["rating"]
            score = movie["composite_score"]
            synopsis = movie.get("synopsis", "A top-rated cinematic recommendation.")

            # Generate bespoke agent reasoning
            reasoning = (
                f"A standout {genre} masterpiece from {year} ({industry}). "
                f"Scored {rating}/10 on TMDB with a composite quality index of {score}/100. "
                f"Renowned for its gripping plot and exceptional critical reception."
            )

            # Fetch streaming providers
            watch_providers = await get_watch_providers(movie_id, industry)

            item = MovieItem(
                id=movie_id,
                title=title,
                original_title=movie.get("original_title"),
                release_year=year,
                release_date=movie.get("release_date"),
                genres=[genre],
                rating=rating,
                vote_count=movie.get("vote_count", 0),
                popularity_score=movie.get("popularity_score", 0.0),
                composite_score=score,
                synopsis=synopsis,
                poster_url=movie.get("poster_url"),
                watch_providers=watch_providers,
                agent_reasoning=reasoning
            )
            final_movie_items.append(item)

        return final_movie_items
