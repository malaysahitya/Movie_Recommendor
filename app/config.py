import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Movie Recommender Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys
    GEMINI_API_KEY: str = ""
    TMDB_API_KEY: str = ""
    OMDB_API_KEY: str = ""
    
    # Application Defaults
    DEFAULT_RESULT_LIMIT: int = 10
    MIN_YEAR: int = 1950
    MAX_YEAR: int = 2026
    
    # Database URL
    DATABASE_URL: str = "sqlite+aiosqlite:///./movie_agent.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
