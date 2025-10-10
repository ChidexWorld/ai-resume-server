"""
FastAPI application configuration for Employee-Employer Matching System.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = "Employee-Employer Matching API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 1440  # 24 hours
    algorithm: str = "HS256"

    # Database settings
    mysql_host: str 
    mysql_port: int 
    mysql_user: str
    mysql_password: str 
    mysql_database: str

    # File upload settings
    max_file_size: int = 25 * 1024 * 1024  # 25MB
    upload_folder: str = "uploads"
    allowed_resume_extensions: List[str] = ["pdf", "doc", "docx", "txt"]
    allowed_audio_extensions: List[str] = ["wav", "mp3", "mp4", "m4a", "ogg", "flac", "webm"]

    # AI/ML settings
    whisper_model: str = "base"
    max_audio_duration: int = 600  # 10 minutes
    similarity_threshold: float = 0.7

    # Matching settings
    default_match_limit: int = 50
    minimum_match_score: int = 70  # Add this field that's in your .env
    score_weights: dict = {
        "skills": 0.4,
        "experience": 0.3,
        "education": 0.2,
        "communication": 0.1
    }

    # CORS settings - use Field to map environment variable
    cors_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174, https://ai-resume-frontend-d44x.vercel.app",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Convert comma-separated CORS origins string to list."""
        if not self.cors_origins_str:
            return ["http://localhost:5173", "http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins_str.split(',') if origin.strip()]

    @property
    def database_url(self) -> str:
        """Construct MySQL database URL."""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore" 


# Global settings instance
settings = Settings()
