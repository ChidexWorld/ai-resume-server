"""
Pydantic schemas for employer endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator
from app.models.job_posting import JobType, ExperienceLevel, JobStatus
from app.models.application import ApplicationStatus


class JobPostingCreate(BaseModel):
    """Schema for creating a job posting."""
    title: str
    description: str
    department: Optional[str] = None
    location: str
    remote_allowed: bool = False
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: Optional[int] = None  # In cents
    salary_max: Optional[int] = None  # In cents
    currency: str = "USD"
    
    # AI matching requirements
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = None
    required_education: Optional[Dict[str, Any]] = None
    required_experience: Optional[Dict[str, Any]] = None
    communication_requirements: Optional[Dict[str, Any]] = None
    
    # Matching settings
    matching_weights: Optional[Dict[str, float]] = None
    is_urgent: bool = False
    max_applications: Optional[int] = None
    auto_match_enabled: bool = True
    minimum_match_score: int = 70
    expires_at: Optional[datetime] = None
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 50:
            raise ValueError('Description must be at least 50 characters long')
        return v.strip()
    
    @validator('required_skills')
    def validate_required_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one required skill must be specified')
        return [skill.strip() for skill in v]
    
    @validator('minimum_match_score')
    def validate_match_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Match score must be between 0 and 100')
        return v


class JobPostingUpdate(BaseModel):
    """Schema for updating a job posting."""
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    remote_allowed: Optional[bool] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = None
    status: Optional[JobStatus] = None
    
    # AI matching requirements
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    required_education: Optional[Dict[str, Any]] = None
    required_experience: Optional[Dict[str, Any]] = None
    communication_requirements: Optional[Dict[str, Any]] = None
    
    # Matching settings
    matching_weights: Optional[Dict[str, float]] = None
    is_urgent: Optional[bool] = None
    max_applications: Optional[int] = None
    auto_match_enabled: Optional[bool] = None
    minimum_match_score: Optional[int] = None
    expires_at: Optional[datetime] = None


class JobPostingResponse(BaseModel):
    """Schema for job posting data in responses."""
    id: int
    employer_id: int
    title: str
    description: str
    department: Optional[str]
    location: str
    remote_allowed: bool
    job_type: str
    experience_level: str
    salary_range: str
    currency: str
    status: str
    is_urgent: bool
    is_active: bool
    applications_count: int
    max_applications: Optional[int]
    auto_match_enabled: bool
    minimum_match_score: int
    created_at: str
    updated_at: str
    expires_at: Optional[str]
    
    # AI matching requirements
    required_skills: List[str]
    preferred_skills: Optional[List[str]]
    required_education: Optional[Dict[str, Any]]
    required_experience: Optional[Dict[str, Any]]
    communication_requirements: Optional[Dict[str, Any]]
    matching_weights: Optional[Dict[str, float]]
    
    class Config:
        from_attributes = True


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status."""
    status: ApplicationStatus
    notes: Optional[str] = None


class InterviewSchedule(BaseModel):
    """Schema for scheduling interviews."""
    interview_date: datetime
    notes: Optional[str] = None


class ApplicationReviewResponse(BaseModel):
    """Schema for application review data."""
    application: Dict[str, Any]
    employee: Optional[Dict[str, Any]]
    resume_analysis: Optional[Dict[str, Any]]
    voice_analysis: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class CandidateSearchResponse(BaseModel):
    """Schema for candidate search results."""
    employee: Dict[str, Any]
    resume_analysis: Dict[str, Any]
    voice_analysis: Optional[Dict[str, Any]]
    match_summary: Dict[str, Any]
    
    class Config:
        from_attributes = True