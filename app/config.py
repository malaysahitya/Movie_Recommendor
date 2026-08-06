import os
from pydantic_settings import BaseSettings
from pydantic import Field

def get_secret_from_manager_or_env(secret_name: str, default_val: str = "") -> str:
    """
    Secret Manager Integration:
    Attempts to retrieve sensitive API keys from Google Cloud Secret Manager.
    Falls back seamlessly to local environment variables if GCP Secret Manager is unconfigured.
    """
    # 1. First check environment variables
    env_val = os.getenv(secret_name)
    if env_val:
        return env_val

    # 2. Secret Manager Integration fallback
    project_id = os.getenv("GCP_PROJECT_ID", "striking-retina-503305-j2")
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_payload = response.payload.data.decode("UTF-8")
        if secret_payload:
            return secret_payload
    except Exception:
        pass

    return default_val

class Settings(BaseSettings):
    APP_NAME: str = "Movie Recommender Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys with Secret Manager Integration
    GEMINI_API_KEY: str = Field(default_factory=lambda: get_secret_from_manager_or_env("GEMINI_API_KEY"))
    TMDB_API_KEY: str = Field(default_factory=lambda: get_secret_from_manager_or_env("TMDB_API_KEY"))
    OMDB_API_KEY: str = Field(default_factory=lambda: get_secret_from_manager_or_env("OMDB_API_KEY"))
    
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
