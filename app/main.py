import os
from fastapi import FastAPI, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.request import RecommendationRequest
from app.models.movie import RecommendationResponse, TracePayload
from app.agent.orchestrator import run_agent_pipeline
from app.telemetry.tracer import get_tracer
from app.memory.sqlite_memory import get_query_history, init_memory_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Google ADK powered Movie Recommender Agent with multi-agent orchestration and step tracing."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_memory_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.VERSION}

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_movies(request: RecommendationRequest):
    try:
        response = await run_agent_pipeline(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@app.get("/api/trace/{session_id}", response_model=TracePayload)
async def get_execution_trace(session_id: str = Path(..., description="User Session ID")):
    tracer = get_tracer(session_id)
    return tracer.get_payload()

@app.get("/api/history/{session_id}")
async def get_session_history(session_id: str = Path(..., description="User Session ID")):
    history = await get_query_history(session_id)
    return {"session_id": session_id, "history": history}

# Static file hosting for Web UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Movie Recommender Agent API is running."}
