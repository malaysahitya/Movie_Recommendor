import google.generativeai as genai
from typing import List, Dict, Any
from app.config import settings
from app.tools.watch_provider_tool import get_watch_providers
from app.models.movie import MovieItem
from app.agent.guardrails import model_router

class ExplainerAgent:
    """
    Sub-Agent 4: Explainer Agent (Gemini LLM Driven)
    Uses System Instructions and Gemini LLM reasoning to craft bespoke 'Why you should watch this' explanations.
    """
    def __init__(self):
        self.name = "ExplainerAgent"
        self.model_name = model_router("explainer")
        self.system_instruction = (
            "You are an expert film critic and cinema concierge AI. "
            "Your role is to explain succinctly and persuasively why a selected movie stands out "
            "for its release year, genre, and industry."
        )

    async def generate_explanations(
        self,
        ranked_movies: List[Dict[str, Any]],
        genre: str,
        industry: str,
        context_prompt: str = ""
    ) -> List[MovieItem]:
        final_movie_items: List[MovieItem] = []

        # Configure Gemini if API key is present
        llm_available = False
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                llm_model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=self.system_instruction
                )
                llm_available = True
            except Exception:
                llm_available = False

        for movie in ranked_movies:
            movie_id = str(movie["id"])
            title = movie["title"]
            year = movie["release_year"]
            rating = movie["rating"]
            score = movie["composite_score"]
            synopsis = movie.get("synopsis", "A top-rated cinematic recommendation.")

            # Default fallback reasoning
            reasoning = (
                f"A standout {genre} masterpiece from {year} ({industry}). "
                f"Scored {rating}/10 on TMDB with a composite quality index of {score}/100. "
                f"Renowned for its gripping plot and exceptional critical reception."
            )

            # Generate Gemini LLM reasoning if available
            if llm_available:
                try:
                    prompt = (
                        f"Context: {context_prompt}\n"
                        f"Movie: {title} ({year})\nIndustry: {industry} | Genre: {genre}\n"
                        f"Rating: {rating}/10 | Synopsis: {synopsis}\n"
                        f"Write 2 compelling sentences explaining why this movie is a must-watch choice for {year}."
                    )
                    llm_response = llm_model.generate_content(prompt)
                    if llm_response and llm_response.text:
                        reasoning = llm_response.text.strip()
                except Exception:
                    pass  # Gracefully fall back to structured reasoning

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
