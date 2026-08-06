import time
from typing import List, Dict, Any
from app.models.request import RecommendationRequest
from app.models.movie import RecommendationResponse, MovieItem
from app.agent.planner_agent import PlannerAgent
from app.agent.researcher_agent import ResearcherAgent
from app.agent.analysis_agent import AnalysisAgent
from app.agent.explainer_agent import ExplainerAgent
from app.agent.guardrails import validate_input_guardrail, hitl_hook
from app.telemetry.tracer import get_tracer
from app.memory.sqlite_memory import save_user_query_async, get_context_prompt

async def run_agent_pipeline(request: RecommendationRequest) -> RecommendationResponse:
    """
    Orchestrates the LLM-Driven 4-Agent Pipeline with Human-In-The-Loop (HITL) 18+ Confirmation Stop:
      1. Guardrail Validation
      2. Context Management Loading
      3. Planner Agent -> Decomposes queries
      4. Researcher Agent -> Fetches candidates per year
      5. Analysis Agent -> Scores candidate movies & flags 18+ adult themes
      6. HUMAN-IN-THE-LOOP HALT CHECK:
         - If 18+ content detected AND user_confirmed_18_plus is False -> HALT pipeline & return AWAITING_18_PLUS_APPROVAL.
      7. Explainer Agent -> Generates Gemini LLM reasoning (when confirmed/safe)
      8. Non-blocking Background Memory Persistence
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
    p_inputs = {"genre": request.genre, "industry": request.industry, "year_range": f"{request.start_year}-{request.end_year}", "context": context_prompt}
    p_start = time.time()
    with tracer.span("PlannerAgent", "formulate_research_plan", p_inputs):
        planner = PlannerAgent()
        plan = planner.plan_execution(request)
    p_latency = (time.time() - p_start) * 1000
    tracer.log_outcome("PlannerAgent", "formulate_research_plan", p_inputs, plan, p_latency)

    # 4. Agent 2: Researcher
    r_inputs = {"years_queried": plan["target_years"]}
    r_start = time.time()
    with tracer.span("ResearcherAgent", "gather_year_by_year_candidates", r_inputs):
        researcher = ResearcherAgent()
        raw_candidates = await researcher.gather_candidates(plan)
    r_latency = (time.time() - r_start) * 1000
    tracer.log_outcome("ResearcherAgent", "gather_year_by_year_candidates", r_inputs, {"total_candidates_found": len(raw_candidates)}, r_latency)

    # 5. Agent 3: Analysis
    a_inputs = {"candidates_count": len(raw_candidates), "target_limit": request.limit}
    a_start = time.time()
    with tracer.span("AnalysisAgent", "rank_and_select_top_10_movies", a_inputs):
        analysis = AnalysisAgent()
        top_ranked = analysis.rank_and_select_top_movies(raw_candidates, limit=request.limit)
    a_latency = (time.time() - a_start) * 1000
    tracer.log_outcome("AnalysisAgent", "rank_and_select_top_10_movies", a_inputs, {"selected_top_count": len(top_ranked)}, a_latency)

    # 6. HUMAN-IN-THE-LOOP (HITL) 18+ HALT CHECK
    contains_18_plus = hitl_hook.check_18_plus_content(request.genre, top_ranked)
    
    if contains_18_plus and not request.user_confirmed_18_plus:
        count_18 = sum(1 for m in top_ranked if m.get("is_18_plus", False))
        hitl_payload = hitl_hook.trigger_hitl_halt(request.user_session_id, request.genre, count_18)
        
        tracer.log_outcome(
            agent_name="HITLGuardrail",
            action="halt_pipeline_for_18_plus_age_verification",
            inputs={"genre": request.genre, "user_confirmed_18_plus": request.user_confirmed_18_plus},
            outputs=hitl_payload,
            latency_ms=0.0
        )
        
        total_latency_ms = (time.time() - start_time) * 1000
        return RecommendationResponse(
            status="AWAITING_18_PLUS_APPROVAL",
            genre=request.genre,
            industry=request.industry,
            year_range=f"{request.start_year} - {request.end_year}",
            total_returned=0,
            movies=[],
            session_id=request.user_session_id,
            execution_time_ms=round(total_latency_ms, 2),
            hitl_status=hitl_payload["message"]
        )

    # 7. Agent 4: Explainer (Gemini LLM)
    e_inputs = {"movies_count": len(top_ranked)}
    e_start = time.time()
    with tracer.span("ExplainerAgent", "generate_movie_explanations_with_gemini", e_inputs):
        explainer = ExplainerAgent()
        final_movies = await explainer.generate_explanations(
            ranked_movies=top_ranked,
            genre=request.genre,
            industry=request.industry,
            context_prompt=context_prompt
        )
    e_latency = (time.time() - e_start) * 1000
    tracer.log_outcome("ExplainerAgent", "generate_movie_explanations_with_gemini", e_inputs, {"status": "completed"}, e_latency)

    # 8. Non-blocking Background Memory Saver
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
        execution_time_ms=round(total_latency_ms, 2),
        hitl_status="18+ Content Verified & Approved by User" if request.user_confirmed_18_plus else None
    )
