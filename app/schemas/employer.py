"""
Pydantic schemas for employer endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator
from app.models.application import ApplicationStatus
from app.models.job_posting import JobStatus, ExperienceLevel, JobType


class ResumeResponse(BaseModel):
    """Schema for resume data in responses."""
    id: int
    employee_id: int
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    is_analyzed: bool
    analysis_status: str
    extracted_text: Optional[str]
    analysis_results: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    analyzed_at: Optional[str]
    
    class Config:
        from_attributes = True


class VoiceAnalysisResponse(BaseModel):
    """Schema for voice analysis data in responses."""
    id: int
    employee_id: int
    original_filename: str
    file_path: str
    file_size: int
    content_type: str
    is_analyzed: bool
    analysis_status: str
    transcription: Optional[str]
    analysis_results: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    analyzed_at: Optional[str]
    
    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    """Schema for creating job applications."""
    job_id: int
    resume_id: Optional[int] = None
    voice_analysis_id: Optional[int] = None
    cover_letter: Optional[str] = None
    expected_salary: Optional[int] = None  # In cents
    availability_date: Optional[datetime] = None
    additional_notes: Optional[str] = None
    
    @validator('cover_letter')
    def validate_cover_letter(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Cover letter must be at least 10 characters long if provided')
        return v.strip() if v else v
    
    @validator('expected_salary')
    def validate_expected_salary(cls, v):
        if v is not None and v < 0:
            raise ValueError('Expected salary must be a positive number')
        return v


class ApplicationResponse(BaseModel):
    """Schema for job application data in responses."""
    id: int
    employee_id: int
    job_id: int
    status: str
    cover_letter: Optional[str]
    expected_salary: Optional[int]
    expected_salary_formatted: Optional[str]
    availability_date: Optional[str]
    additional_notes: Optional[str]
    applied_at: str
    updated_at: str
    
    # Related data
    job: Optional[Dict[str, Any]]
    employer: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ApplicationUpdate(BaseModel):
    """Schema for updating job applications."""
    cover_letter: Optional[str] = None
    expected_salary: Optional[int] = None
    availability_date: Optional[datetime] = None
    additional_notes: Optional[str] = None
    
    @validator('cover_letter')
    def validate_cover_letter(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Cover letter must be at least 10 characters long if provided')
        return v.strip() if v else v


class ProfileUpdate(BaseModel):
    """Schema for updating employee profile."""
    bio: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[Dict[str, Any]] = None
    
    @validator('bio')
    def validate_bio(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Bio must be at least 10 characters long if provided')
        return v.strip() if v else v
    
    @validator('experience_years')
    def validate_experience_years(cls, v):
        if v is not None and (v < 0 or v > 60):
            raise ValueError('Experience years must be between 0 and 60')
        return v


class EmployeeProfileResponse(BaseModel):
    """Schema for employee profile data in responses."""
    id: int
    user_id: int
    bio: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]
    skills: Optional[List[str]]
    experience_years: Optional[int]
    education: Optional[Dict[str, Any]]
    is_active: bool
    is_seeking_job: bool
    resume_count: int
    voice_analysis_count: int
    applications_count: int
    matches_count: int
    created_at: str
    updated_at: str
    
    # Related data
    user: Optional[Dict[str, Any]]
    latest_resume: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


# Job Posting Schemas
class JobPostingCreate(BaseModel):
    """Schema for creating job postings."""
    title: str
    description: str
    department: Optional[str] = None
    location: str
    remote_allowed: bool = False
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = "USD"
    benefits: Optional[str] = None

    # Requirements
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = None
    required_experience: Optional[Dict[str, Any]] = None
    required_education: Optional[Dict[str, Any]] = None

    # Matching criteria
    communication_requirements: Optional[Dict[str, Any]] = None
    matching_weights: Optional[Dict[str, Any]] = None
    minimum_match_score: int = 70

    # Additional settings
    is_urgent: bool = False
    max_applications: Optional[int] = None
    auto_match_enabled: bool = True
    expires_at: Optional[datetime] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Job title must be at least 3 characters long')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Job description must be at least 50 characters long')
        return v.strip()


class JobPostingUpdate(BaseModel):
    """Schema for updating job postings."""
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    remote_allowed: Optional[bool] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    benefits: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    status: Optional[JobStatus] = None
    minimum_match_score: Optional[int] = None


class JobPostingResponse(BaseModel):
    """Schema for job posting data in responses."""
    id: int
    employer_id: int
    title: str
    description: str
    department: Optional[str]
    location: str
    remote_allowed: bool
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: Optional[int]
    salary_max: Optional[int]
    benefits: Optional[str]
    required_skills: List[str]
    preferred_skills: Optional[List[str]]
    required_experience: Optional[Dict[str, Any]]
    required_education: Optional[Dict[str, Any]]
    communication_requirements: Optional[Dict[str, Any]]
    minimum_match_score: int
    status: JobStatus
    applications_count: int
    matches_count: int
    created_at: str
    updated_at: str
    
    # Related data
    employer: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ApplicationReviewResponse(BaseModel):
    """Schema for application review data."""
    application: Dict[str, Any]
    employee: Optional[Dict[str, Any]]
    resume_analysis: Optional[Dict[str, Any]]
    voice_analysis: Optional[Dict[str, Any]]


class CandidateSearchResponse(BaseModel):
    """Schema for candidate search results."""
    employee: Dict[str, Any]
    resume_analysis: Optional[Dict[str, Any]]
    voice_analysis: Optional[Dict[str, Any]]
    match_summary: Optional[Dict[str, Any]]


class InterviewSchedule(BaseModel):
    """Schema for scheduling interviews."""
    application_id: int
    interview_date: datetime
    interview_type: str  # "video", "phone", "in_person"
    location_or_link: Optional[str] = None
    notes: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status."""
    status: ApplicationStatus
    notes: Optional[str] = None