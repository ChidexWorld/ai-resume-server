"""
Model imports and database table creation.
"""
from app.models.user import User, UserType
from app.models.job_posting import JobPosting, JobStatus, ExperienceLevel, JobType
from app.models.resume import Resume, ResumeStatus
from app.models.voice_analysis import VoiceAnalysis, VoiceStatus
from app.models.application import Application, ApplicationStatus, JobMatch

# Export all models
__all__ = [
    "User",
    "UserType", 
    "JobPosting",
    "JobStatus",
    "ExperienceLevel", 
    "JobType",
    "Resume",
    "ResumeStatus",
    "VoiceAnalysis", 
    "VoiceStatus",
    "Application",
    "ApplicationStatus",
    "JobMatch"
]