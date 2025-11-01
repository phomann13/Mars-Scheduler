"""
Configuration settings for the UMD AI Scheduling Assistant backend.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "UMD AI Scheduling Assistant"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/umd_scheduler"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Store Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "umd-courses"
    
    # External API Keys
    PLANET_TERP_API_URL: str = "https://api.planetterp.com/v1"
    RATE_MY_PROFESSOR_API_URL: str = "https://www.ratemyprofessors.com/graphql"
    UMD_SCHEDULE_API_URL: str = "https://api.umd.io/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

