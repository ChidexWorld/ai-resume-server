"""
Pydantic schemas for employee-related endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, HttpUrl, validator, Field
from enum import Enum


class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    FREELANCER = "freelancer"
    STUDENT = "student"
    LOOKING = "looking"


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    OTHER = "other"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Profile Schemas
class EmployeeProfileBase(BaseModel):
    """Base schema for employee profile."""
    headline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    desired_salary_min: Optional[float] = Field(None, ge=0)
    desired_salary_max: Optional[float] = Field(None, ge=0)
    willing_to_relocate: Optional[bool] = False
    preferred_job_types: Optional[List[JobType]] = []
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None

    @validator('desired_salary_max')
    def validate_salary_range(cls, v, values):
        if v and values.get('desired_salary_min') and v < values.get('desired_salary_min'):
            raise ValueError('Maximum salary must be greater than minimum salary')
        return v

    @validator('headline')
    def validate_headline(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Headline must be at least 10 characters long')
        return v.strip() if v else v

    @validator('years_of_experience')
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError('Years of experience cannot be negative')
        return v

    @validator('preferred_job_types')
    def validate_job_types(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 preferred job types allowed')
        return v


class EmployeeProfileCreate(EmployeeProfileBase):
    """Schema for creating employee profile."""
    pass


class EmployeeProfileUpdate(EmployeeProfileBase):
    """Schema for updating employee profile."""
    pass


class EmployeeProfileResponse(EmployeeProfileBase):
    """Schema for employee profile response."""
    id: int
    user_id: int
    profile_completion: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Education Schemas
class EducationBase(BaseModel):
    """Base schema for education."""
    institution: str = Field(..., max_length=200)
    degree: str = Field(..., max_length=200)
    field_of_study: str = Field(..., max_length=200)
    education_level: EducationLevel
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('end_date')
    def validate_dates(cls, v, values):
        if not values.get('is_current') and not v:
            raise ValueError('End date is required when not currently studying')
        if v and values.get('start_date') and v < values.get('start_date'):
            raise ValueError('End date must be after start date')
        return v


class EducationCreate(EducationBase):
    """Schema for creating education record."""
    pass


class EducationUpdate(EducationBase):
    """Schema for updating education record."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    start_date: Optional[date] = None


class EducationResponse(EducationBase):
    """Schema for education response."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Experience Schemas
class ExperienceBase(BaseModel):
    """Base schema for work experience."""
    company: str = Field(..., max_length=200)
    position: str = Field(..., max_length=200)
    location: Optional[str] = None
    job_type: JobType
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = Field(..., max_length=2000)
    achievements: Optional[List[str]] = []
    technologies: Optional[List[str]] = []

    @validator('end_date')
    def validate_dates(cls, v, values):
        if not values.get('is_current') and not v:
            raise ValueError('End date is required when not current position')
        if v and values.get('start_date') and v < values.get('start_date'):
            raise ValueError('End date must be after start date')
        return v


class ExperienceCreate(ExperienceBase):
    """Schema for creating experience record."""
    pass


class ExperienceUpdate(ExperienceBase):
    """Schema for updating experience record."""
    company: Optional[str] = None
    position: Optional[str] = None
    job_type: Optional[JobType] = None
    start_date: Optional[date] = None
    description: Optional[str] = None


class ExperienceResponse(ExperienceBase):
    """Schema for experience response."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Skills Schemas
class SkillBase(BaseModel):
    """Base schema for skills."""
    name: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    level: SkillLevel
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    is_certified: bool = False
    certification_name: Optional[str] = None

    @validator('certification_name')
    def validate_certification(cls, v, values):
        if values.get('is_certified') and not v:
            raise ValueError('Certification name is required when certified')
        return v


class SkillCreate(SkillBase):
    """Schema for creating skill."""
    pass


class SkillUpdate(BaseModel):
    """Schema for updating skill."""
    level: Optional[SkillLevel] = None
    years_of_experience: Optional[int] = None
    is_certified: Optional[bool] = None
    certification_name: Optional[str] = None


class SkillResponse(SkillBase):
    """Schema for skill response."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resume Schemas
class ResumeBase(BaseModel):
    """Base schema for resume."""
    title: str = Field(..., max_length=200)
    template: Optional[str] = "default"
    is_primary: bool = False
    summary: Optional[str] = Field(None, max_length=1000)
    custom_sections: Optional[Dict[str, Any]] = {}


class ResumeCreate(ResumeBase):
    """Schema for creating resume."""
    education_ids: Optional[List[int]] = []
    experience_ids: Optional[List[int]] = []
    skill_ids: Optional[List[int]] = []


class ResumeUpdate(ResumeBase):
    """Schema for updating resume."""
    title: Optional[str] = None
    education_ids: Optional[List[int]] = None
    experience_ids: Optional[List[int]] = None
    skill_ids: Optional[List[int]] = None


class ResumeResponse(ResumeBase):
    """Schema for resume response."""
    id: int
    employee_id: int
    file_url: Optional[str] = None
    ai_score: Optional[float] = None
    education: List[EducationResponse] = []
    experience: List[ExperienceResponse] = []
    skills: List[SkillResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Application Schemas
class JobApplicationBase(BaseModel):
    """Base schema for job application."""
    job_id: int
    resume_id: int
    cover_letter: Optional[str] = Field(None, max_length=3000)
    expected_salary: Optional[float] = Field(None, ge=0)
    available_from: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating job application."""
    pass


class JobApplicationUpdate(BaseModel):
    """Schema for updating job application."""
    cover_letter: Optional[str] = None
    expected_salary: Optional[float] = None
    available_from: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None


class JobApplicationResponse(JobApplicationBase):
    """Schema for job application response."""
    id: int
    employee_id: int
    status: ApplicationStatus
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    interview_scheduled_at: Optional[datetime] = None
    employer_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Voice Assessment Schemas
class VoiceAssessmentBase(BaseModel):
    """Base schema for voice assessment."""
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    language: str = Field(default="english", max_length=50)
    duration_seconds: Optional[int] = Field(None, ge=0)


class VoiceAssessmentCreate(VoiceAssessmentBase):
    """Schema for creating voice assessment."""
    file_path: str


class VoiceAssessmentResponse(VoiceAssessmentBase):
    """Schema for voice assessment response."""
    id: int
    employee_id: int
    file_url: str
    analysis_results: Optional[Dict[str, Any]] = None
    clarity_score: Optional[float] = Field(None, ge=0, le=100)
    fluency_score: Optional[float] = Field(None, ge=0, le=100)
    pronunciation_score: Optional[float] = Field(None, ge=0, le=100)
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    feedback: Optional[str] = None
    analyzed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Search and Filter Schemas
class EmployeeSearchFilter(BaseModel):
    """Schema for searching/filtering employees."""
    keywords: Optional[str] = None
    skills: Optional[List[str]] = []
    education_level: Optional[EducationLevel] = None
    min_experience: Optional[int] = Field(None, ge=0)
    max_experience: Optional[int] = Field(None, ge=0)
    location: Optional[str] = None
    job_types: Optional[List[JobType]] = []
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    willing_to_relocate: Optional[bool] = None

    @validator('max_experience')
    def validate_experience_range(cls, v, values):
        if v and values.get('min_experience') and v < values.get('min_experience'):
            raise ValueError('Maximum experience must be greater than minimum')
        return v


# Notification Schemas
class NotificationType(str, Enum):
    APPLICATION_UPDATE = "application_update"
    JOB_MATCH = "job_match"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    MESSAGE = "message"
    PROFILE_VIEW = "profile_view"
    SYSTEM = "system"


class NotificationBase(BaseModel):
    """Base schema for notifications."""
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    type: NotificationType
    priority: Optional[str] = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    action_url: Optional[str] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: int
    employee_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Certification Schemas
class CertificationBase(BaseModel):
    """Base schema for professional certifications."""
    name: str = Field(..., max_length=200)
    issuing_organization: str = Field(..., max_length=200)
    credential_id: Optional[str] = Field(None, max_length=100)
    issue_date: date
    expiry_date: Optional[date] = None
    is_verified: bool = False
    verification_url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, max_length=500)

    @validator('expiry_date')
    def validate_dates(cls, v, values):
        if v and values.get('issue_date') and v <= values.get('issue_date'):
            raise ValueError('Expiry date must be after issue date')
        return v


class CertificationCreate(CertificationBase):
    """Schema for creating certification."""
    pass


class CertificationUpdate(CertificationBase):
    """Schema for updating certification."""
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None


class CertificationResponse(CertificationBase):
    """Schema for certification response."""
    id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Language Schemas
class LanguageProficiency(str, Enum):
    NATIVE = "native"
    FLUENT = "fluent"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    BASIC = "basic"


class LanguageBase(BaseModel):
    """Base schema for language skills."""
    language: str = Field(..., max_length=100)
    proficiency: LanguageProficiency
    is_primary: bool = False
    can_read: bool = True
    can_write: bool = True
    can_speak: bool = True
    certification: Optional[str] = Field(None, max_length=200)


class LanguageCreate(LanguageBase):
    """Schema for creating language skill."""
    pass


class LanguageUpdate(BaseModel):
    """Schema for updating language skill."""
    proficiency: Optional[LanguageProficiency] = None
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    can_speak: Optional[bool] = None
    certification: Optional[str] = None


class LanguageResponse(LanguageBase):
    """Schema for language response."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Reference Schemas
class ReferenceBase(BaseModel):
    """Base schema for professional references."""
    name: str = Field(..., max_length=200)
    title: str = Field(..., max_length=200)
    company: str = Field(..., max_length=200)
    relationship: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    phone: Optional[str] = Field(None, max_length=20)
    years_known: Optional[int] = Field(None, ge=0, le=50)
    permission_to_contact: bool = False
    notes: Optional[str] = Field(None, max_length=500)


class ReferenceCreate(ReferenceBase):
    """Schema for creating reference."""
    pass


class ReferenceUpdate(ReferenceBase):
    """Schema for updating reference."""
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    relationship: Optional[str] = None


class ReferenceResponse(ReferenceBase):
    """Schema for reference response."""
    id: int
    employee_id: int
    has_been_contacted: bool = False
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Portfolio Schemas
class ProjectBase(BaseModel):
    """Base schema for portfolio projects."""
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    role: str = Field(..., max_length=100)
    team_size: Optional[int] = Field(None, ge=1, le=1000)
    start_date: date
    end_date: Optional[date] = None
    is_ongoing: bool = False
    project_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    technologies: List[str] = []
    key_achievements: List[str] = []
    images: Optional[List[str]] = []

    @validator('end_date')
    def validate_dates(cls, v, values):
        if not values.get('is_ongoing') and not v:
            raise ValueError('End date is required for completed projects')
        if v and values.get('start_date') and v < values.get('start_date'):
            raise ValueError('End date must be after start date')
        return v

    @validator('technologies', 'key_achievements')
    def validate_list_length(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 items allowed')
        return v

    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return v.strip()

    @validator('title', 'role')
    def validate_required_fields(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Field must be at least 2 characters long')
        return v.strip()


class ProjectCreate(ProjectBase):
    """Schema for creating project."""
    pass


class ProjectUpdate(ProjectBase):
    """Schema for updating project."""
    title: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    employee_id: int
    view_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    TRANSCRIPT = "transcript"
    CERTIFICATE = "certificate"
    PORTFOLIO = "portfolio"
    REFERENCE_LETTER = "reference_letter"
    OTHER = "other"


class DocumentBase(BaseModel):
    """Base schema for documents."""
    title: str = Field(..., max_length=200)
    document_type: DocumentType
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = False
    tags: Optional[List[str]] = []

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 5:
            raise ValueError('Maximum 5 tags allowed')
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating document."""
    file_path: str


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    employee_id: int
    file_url: str
    file_size: int
    mime_type: str
    download_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Achievement/Award Schemas
class AchievementBase(BaseModel):
    """Base schema for achievements and awards."""
    title: str = Field(..., max_length=200)
    issuer: str = Field(..., max_length=200)
    date_received: date
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., max_length=50)
    url: Optional[HttpUrl] = None
    is_featured: bool = False


class AchievementCreate(AchievementBase):
    """Schema for creating achievement."""
    pass


class AchievementResponse(AchievementBase):
    """Schema for achievement response."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True