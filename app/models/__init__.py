"""
Model imports for the application.
Makes all models available from the models package.
"""
# Import database instance first
from app.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, UserType
from app.models.job_posting import JobPosting, JobStatus, ExperienceLevel, JobType
from app.models.resume import Resume, ResumeStatus
from app.models.voice_analysis import VoiceAnalysis, VoiceStatus
from app.models.application import Application, ApplicationStatus, JobMatch

# Make models available at package level
__all__ = [
    'Base',
    'User',
    'UserType',
    'JobPosting',
    'JobStatus',
    'ExperienceLevel',
    'JobType',
    'Resume',
    'ResumeStatus',
    'VoiceAnalysis',
    'VoiceStatus',
    'Application',
    'ApplicationStatus',
    'JobMatch'
]