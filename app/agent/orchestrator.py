import time
from typing import List, Dict, Any
from app.models.request import RecommendationRequest
from app.models.movie import RecommendationResponse, MovieItem
from app.agent.planner_agent import PlannerAgent
from app.agent.researcher_agent import ResearcherAgent
from app.agent.analysis_agent import AnalysisAgent
from app.agent.explainer_agent import ExplainerAgent
from app.telemetry.tracer import get_tracer
from app.memory.sqlite_memory import save_user_query

async def run_agent_pipeline(request: RecommendationRequest) -> RecommendationResponse:
    """
    Orchestrates the 4-Agent Pipeline:
      1. Planner Agent -> Decomposes multi-year range
      2. Researcher Agent -> Queries TMDB for candidates per year
      3. Analysis Agent -> Computes quality scores & selects top 10 overall
      4. Explainer Agent -> Generates reasoning & attaches streaming availability
    """
    start_time = time.time()
    tracer = get_tracer(request.user_session_id)

    # Agent 1: Planner
    p_start = time.time()
    planner = PlannerAgent()
    plan = planner.plan_execution(request)
    p_latency = (time.time() - p_start) * 1000
    tracer.add_step(
        agent_name="PlannerAgent",
        action="formulate_research_plan",
        inputs={"genre": request.genre, "industry": request.industry, "year_range": f"{request.start_year}-{request.end_year}"},
        outputs=plan,
        latency_ms=p_latency
    )

    # Agent 2: Researcher
    r_start = time.time()
    researcher = ResearcherAgent()
    raw_candidates = await researcher.gather_candidates(plan)
    r_latency = (time.time() - r_start) * 1000
    tracer.add_step(
        agent_name="ResearcherAgent",
        action="gather_year_by_year_candidates",
        inputs={"years_queried": plan["target_years"]},
        outputs={"total_candidates_found": len(raw_candidates)},
        latency_ms=r_latency
    )

    # Agent 3: Analysis & Ranking
    a_start = time.time()
    analysis = AnalysisAgent()
    top_ranked = analysis.rank_and_select_top_movies(raw_candidates, limit=request.limit)
    a_latency = (time.time() - a_start) * 1000
    tracer.add_step(
        agent_name="AnalysisAgent",
        action="rank_and_select_top_10_movies",
        inputs={"candidates_count": len(raw_candidates), "target_limit": request.limit},
        outputs={"selected_top_count": len(top_ranked)},
        latency_ms=a_latency
    )

    # Agent 4: Explainer
    e_start = time.time()
    explainer = ExplainerAgent()
    final_movies = await explainer.generate_explanations(top_ranked, request.genre, request.industry)
    e_latency = (time.time() - e_start) * 1000
    tracer.add_step(
        agent_name="ExplainerAgent",
        action="generate_movie_explanations",
        inputs={"movies_count": len(final_movies)},
        outputs={"status": "completed"},
        latency_ms=e_latency
    )

    # Persist to SQLite Memory
    movie_ids = [m.id for m in final_movies]
    await save_user_query(
        session_id=request.user_session_id,
        genre=request.genre,
        industry=request.industry,
        start_year=request.start_year,
        end_year=request.end_year,
        movie_ids=movie_ids
    )

    total_latency_ms = (time.time() - start_time) * 1000

    return RecommendationResponse(
        status="success",
        genre=request.genre,
        industry=request.industry,
        year_range=f"{request.start_year} - {request.end_year}",
        total_returned=len(final_movies),
        movies=final_movies,
        session_id=request.user_session_id,
        execution_time_ms=round(total_latency_ms, 2)
    )
