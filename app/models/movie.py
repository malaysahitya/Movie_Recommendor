from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class WatchProvider(BaseModel):
    provider_name: str
    logo_path: Optional[str] = None
    type: str = "flatrate"

class MovieItem(BaseModel):
    id: str = Field(..., description="Unique movie ID")
    title: str = Field(..., description="Movie title")
    original_title: Optional[str] = Field(None, description="Original title for Anime/Bollywood")
    release_year: int = Field(..., description="Release year")
    release_date: Optional[str] = Field(None, description="Full release date YYYY-MM-DD")
    genres: List[str] = Field(default_factory=list, description="Genre list")
    rating: float = Field(..., ge=0.0, le=10.0, description="Normalized rating score out of 10")
    vote_count: int = Field(default=0, description="Total vote count")
    popularity_score: float = Field(default=0.0, description="Popularity score")
    composite_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Quality score out of 100")
    synopsis: str = Field(..., description="Short plot overview")
    director: Optional[str] = Field(None, description="Director name")
    cast: List[str] = Field(default_factory=list, description="Top cast members")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    trailer_url: Optional[str] = Field(None, description="Trailer URL")
    watch_providers: List[WatchProvider] = Field(default_factory=list, description="Streaming platforms")
    agent_reasoning: str = Field(..., description="Agent's 'Why you should watch this' explanation")
    is_18_plus: bool = Field(default=False, description="Flag indicating if movie contains 18+ adult themes")

class RecommendationResponse(BaseModel):
    status: str = "success"  # success or AWAITING_18_PLUS_APPROVAL
    genre: str
    industry: str
    year_range: str
    total_returned: int
    movies: List[MovieItem] = Field(default_factory=list)
    session_id: str
    execution_time_ms: float
    hitl_status: Optional[str] = Field(None, description="Human-in-the-loop status message if execution is paused")

class TraceStep(BaseModel):
    step_number: int
    agent_name: str
    action: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    latency_ms: float
    timestamp: str

class TracePayload(BaseModel):
    session_id: str
    total_steps: int
    steps: List[TraceStep]
