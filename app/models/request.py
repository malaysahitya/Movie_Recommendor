from typing import Optional, List
from pydantic import BaseModel, Field, validator

class RecommendationRequest(BaseModel):
    genre: str = Field(..., description="Target movie genre (e.g. Action, Drama, Sci-Fi, Horror, Animation)")
    industry: str = Field(..., description="Target industry: 'Hollywood', 'Bollywood', or 'Anime'")
    start_year: int = Field(..., ge=1950, le=2026, description="Start year of the release range (e.g. 2010)")
    end_year: int = Field(..., ge=1950, le=2026, description="End year of the release range (e.g. 2020)")
    limit: int = Field(default=10, ge=1, le=50, description="Total top movies to return across the range (default 10)")
    user_session_id: Optional[str] = Field(default="default_session", description="Session ID for context and memory persistence")
    user_confirmed_18_plus: bool = Field(default=False, description="Human-in-the-loop explicit confirmation flag for 18+ content")

    @validator("industry")
    def validate_industry(cls, v):
        allowed = ["hollywood", "bollywood", "anime"]
        if v.lower() not in allowed:
            raise ValueError(f"Industry must be one of {allowed}, got '{v}'")
        return v.lower().capitalize()

    @validator("end_year")
    def validate_year_range(cls, v, values):
        if "start_year" in values and v < values["start_year"]:
            raise ValueError("end_year must be greater than or equal to start_year")
        return v
