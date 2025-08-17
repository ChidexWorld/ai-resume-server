"""
Job posting model for employers to define requirements.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class JobStatus(str, enum.Enum):
    """Job posting status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    EXPIRED = "expired"


class ExperienceLevel(str, enum.Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class JobPosting(Base):
    """
    Job posting model where employers define their requirements.
    This is what the AI will match employee profiles against.
    """
    
    __tablename__ = "job_postings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to employer
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic job information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    department = Column(String(100), nullable=True)
    location = Column(String(255), nullable=False)
    remote_allowed = Column(Boolean, default=False, nullable=False)
    
    # Job details
    job_type = Column(Enum(JobType), nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=False)
    salary_min = Column(Integer, nullable=True)  # In cents to avoid decimal issues
    salary_max = Column(Integer, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # AI Matching Requirements (JSON fields for flexibility)
    required_skills = Column(JSON, nullable=False)  # List of required skills
    preferred_skills = Column(JSON, nullable=True)  # List of preferred skills
    required_education = Column(JSON, nullable=True)  # Education requirements
    required_experience = Column(JSON, nullable=False)  # Experience requirements
    
    # Communication requirements (for voice analysis matching)
    communication_requirements = Column(JSON, nullable=True)  # Communication criteria
    
    # Matching criteria weights (customize importance of different factors)
    matching_weights = Column(JSON, nullable=True)  # Custom weights for this job
    
    # Status and settings
    status = Column(Enum(JobStatus), default=JobStatus.ACTIVE, nullable=False)
    is_urgent = Column(Boolean, default=False, nullable=False)
    applications_count = Column(Integer, default=0, nullable=False)
    max_applications = Column(Integer, nullable=True)  # Limit applications
    
    # Auto-matching settings
    auto_match_enabled = Column(Boolean, default=True, nullable=False)
    minimum_match_score = Column(Integer, default=70, nullable=False)  # Percentage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Job posting expiration
    
    # Relationships
    employer = relationship("User", back_populates="job_postings")
    applications = relationship("Application", back_populates="job_posting", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job_posting", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """Check if job posting is active and not expired."""
        if self.status != JobStatus.ACTIVE:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        if self.max_applications and self.applications_count >= self.max_applications:
            return False
        
        return True
    
    @property
    def salary_range(self) -> str:
        """Get formatted salary range."""
        if not self.salary_min and not self.salary_max:
            return "Salary not specified"
        
        def format_salary(amount):
            if amount:
                return f"{self.currency} {amount // 100:,}"
            return "Not specified"
        
        min_sal = format_salary(self.salary_min)
        max_sal = format_salary(self.salary_max)
        
        if self.salary_min and self.salary_max:
            return f"{min_sal} - {max_sal}"
        elif self.salary_min:
            return f"From {min_sal}"
        else:
            return f"Up to {max_sal}"
    
    def get_matching_criteria(self) -> dict:
        """Get the complete matching criteria for AI processing."""
        return {
            "required_skills": self.required_skills or [],
            "preferred_skills": self.preferred_skills or [],
            "required_education": self.required_education or {},
            "required_experience": self.required_experience or {},
            "communication_requirements": self.communication_requirements or {},
            "experience_level": self.experience_level.value,
            "job_type": self.job_type.value,
            "location": self.location,
            "remote_allowed": self.remote_allowed,
            "minimum_match_score": self.minimum_match_score,
            "matching_weights": self.matching_weights or {}
        }
    
    def increment_applications(self):
        """Increment the applications count."""
        self.applications_count += 1
    
    def to_dict(self, include_requirements: bool = True) -> dict:
        """Convert job posting to dictionary."""
        job_data = {
            "id": self.id,
            "employer_id": self.employer_id,
            "title": self.title,
            "description": self.description,
            "department": self.department,
            "location": self.location,
            "remote_allowed": self.remote_allowed,
            "job_type": self.job_type.value,
            "experience_level": self.experience_level.value,
            "salary_range": self.salary_range,
            "currency": self.currency,
            "status": self.status.value,
            "is_urgent": self.is_urgent,
            "is_active": self.is_active,
            "applications_count": self.applications_count,
            "max_applications": self.max_applications,
            "auto_match_enabled": self.auto_match_enabled,
            "minimum_match_score": self.minimum_match_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
        
        if include_requirements:
            job_data.update({
                "required_skills": self.required_skills,
                "preferred_skills": self.preferred_skills,
                "required_education": self.required_education,
                "required_experience": self.required_experience,
                "communication_requirements": self.communication_requirements,
                "matching_weights": self.matching_weights
            })
        
        return job_data
    
    def __repr__(self):
        return f"<JobPosting {self.title} ({self.status.value})>"