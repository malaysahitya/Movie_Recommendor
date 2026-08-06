import time
from typing import List, Dict, Any
from app.models.request import RecommendationRequest
from app.models.movie import RecommendationResponse, MovieItem
from app.agent.planner_agent import PlannerAgent
from app.agent.researcher_agent import ResearcherAgent
from app.agent.analysis_agent import AnalysisAgent
from app.agent.explainer_agent import ExplainerAgent
from app.agent.guardrails import validate_input_guardrail
from app.telemetry.tracer import get_tracer
from app.memory.sqlite_memory import save_user_query_async, get_context_prompt

async def run_agent_pipeline(request: RecommendationRequest) -> RecommendationResponse:
    """
    Orchestrates the LLM-Driven 4-Agent Pipeline:
      1. Guardrail Validation & Context Loading
      2. Planner Agent -> Formulates execution plan
      3. Researcher Agent -> Executes TMDB tool search queries
      4. Analysis Agent -> Computes quality scores & selects top 10 movies
      5. Explainer Agent -> Generates Gemini LLM reasoning & streaming availability
      6. Non-blocking Background Memory Persistence
    """
    start_time = time.time()
    tracer = get_tracer(request.user_session_id)

    # 1. Input Guardrail Check
    is_valid, guardrail_msg = validate_input_guardrail(
        genre=request.genre,
        industry=request.industry,
        start_year=request.start_year,
        end_year=request.end_year
    )
    if not is_valid:
        raise ValueError(f"Guardrail Flagged Request: {guardrail_msg}")

    # 2. Context Management Loading
    context_prompt = await get_context_prompt(request.user_session_id)

    # 3. Agent 1: Planner
    p_start = time.time()
    planner = PlannerAgent()
    plan = planner.plan_execution(request)
    p_latency = (time.time() - p_start) * 1000
    tracer.add_step(
        agent_name="PlannerAgent",
        action="formulate_research_plan",
        inputs={"genre": request.genre, "industry": request.industry, "year_range": f"{request.start_year}-{request.end_year}", "context": context_prompt},
        outputs=plan,
        latency_ms=p_latency
    )

    # 4. Agent 2: Researcher
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

    # 5. Agent 3: Analysis
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

    # 6. Agent 4: Explainer (Gemini LLM)
    e_start = time.time()
    explainer = ExplainerAgent()
    final_movies = await explainer.generate_explanations(
        ranked_movies=top_ranked,
        genre=request.genre,
        industry=request.industry,
        context_prompt=context_prompt
    )
    e_latency = (time.time() - e_start) * 1000
    tracer.add_step(
        agent_name="ExplainerAgent",
        action="generate_movie_explanations_with_gemini",
        inputs={"movies_count": len(final_movies)},
        outputs={"status": "completed"},
        latency_ms=e_latency
    )

    # 7. Non-blocking Memory Saver (asynchronous background task)
    movie_ids = [m.id for m in final_movies]
    save_user_query_async(
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
