"""
FastAPI application configuration for Employee-Employer Matching System.
"""
import os
from pydantic_settings import BaseSettings
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
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "employee_employer_matching"
    
    # File upload settings
    max_file_size: int = 25 * 1024 * 1024  # 25MB
    upload_folder: str = "uploads"
    allowed_resume_extensions: List[str] = ["pdf", "doc", "docx", "txt"]
    allowed_audio_extensions: List[str] = ["wav", "mp3", "mp4", "m4a", "ogg", "flac"]
    
    # AI/ML settings
    whisper_model: str = "base"
    max_audio_duration: int = 600  # 10 minutes
    similarity_threshold: float = 0.7
    
    # Matching settings
    default_match_limit: int = 50
    score_weights: dict = {
        "skills": 0.4,
        "experience": 0.3,
        "education": 0.2,
        "communication": 0.1
    }
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    @property
    def database_url(self) -> str:
        """Construct MySQL database URL."""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()