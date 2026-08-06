from typing import List, Dict, Any
import asyncio
from app.tools.tmdb_tool import fetch_movies_by_year_and_genre

class ResearcherAgent:
    """
    Sub-Agent 2: Researcher
    Executes tool queries across each year in the plan to gather raw candidate movies.
    """
    def __init__(self):
        self.name = "ResearcherAgent"

    async def gather_candidates(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        genre = plan["genre"]
        industry = plan["industry"]
        target_years = plan["target_years"]

        all_candidates: List[Dict[str, Any]] = []

        # Execute queries for each year
        for year in target_years:
            try:
                candidates = await fetch_movies_by_year_and_genre(
                    year=year,
                    genre=genre,
                    industry=industry,
                    limit=15
                )
                all_candidates.extend(candidates)
            except Exception as e:
                # Continue gracefully if a single year API query fails
                continue

        return all_candidates
