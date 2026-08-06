from typing import Dict, Any, List
from app.models.request import RecommendationRequest

class PlannerAgent:
    """
    Sub-Agent 1: Planner / Orchestrator
    Validates user request, decomposes multi-year range, and creates execution directives.
    """
    def __init__(self):
        self.name = "PlannerAgent"

    def plan_execution(self, request: RecommendationRequest) -> Dict[str, Any]:
        years = list(range(request.start_year, request.end_year + 1))
        
        plan = {
            "genre": request.genre,
            "industry": request.industry,
            "start_year": request.start_year,
            "end_year": request.end_year,
            "target_years": years,
            "total_years_span": len(years),
            "target_limit": request.limit,
            "directives": f"Research {request.genre} movies in {request.industry} across years {request.start_year}-{request.end_year} to select the top {request.limit} overall."
        }
        return plan
