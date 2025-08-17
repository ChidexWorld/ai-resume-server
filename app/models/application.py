"""
Application model for tracking employee applications to job postings.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration."""
    PENDING = "pending"
    REVIEWING = "reviewing"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    """
    Application model for tracking employee applications to job postings.
    Links employees, their resumes/voice analyses, and job postings.
    """
    
    __tablename__ = "applications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True, index=True)
    voice_analysis_id = Column(Integer, ForeignKey("voice_analyses.id"), nullable=True, index=True)
    
    # Application details
    cover_letter = Column(Text, nullable=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    
    # AI matching results
    match_score = Column(Integer, nullable=True)  # 0-100 percentage
    match_details = Column(JSON, nullable=True)  # Detailed matching breakdown
    ai_recommendation = Column(Text, nullable=True)  # AI-generated recommendation
    
    # Employer feedback
    employer_notes = Column(Text, nullable=True)
    interview_scheduled = Column(DateTime, nullable=True)
    interview_feedback = Column(Text, nullable=True)
    
    # Timestamps
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    decision_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("User", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    voice_analysis = relationship("VoiceAnalysis")
    
    @property
    def is_active(self) -> bool:
        """Check if application is still active (not decided)."""
        return self.status not in [
            ApplicationStatus.ACCEPTED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.WITHDRAWN
        ]
    
    @property
    def has_resume(self) -> bool:
        """Check if application includes a resume."""
        return self.resume_id is not None
    
    @property
    def has_voice_analysis(self) -> bool:
        """Check if application includes voice analysis."""
        return self.voice_analysis_id is not None
    
    def update_status(self, status: ApplicationStatus, notes: str = None):
        """Update application status."""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if notes:
            self.employer_notes = notes
        
        # Set decision timestamp for final statuses
        if status in [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]:
            self.decision_at = datetime.utcnow()
        
        # Set reviewed timestamp
        if status != ApplicationStatus.PENDING and not self.reviewed_at:
            self.reviewed_at = datetime.utcnow()
    
    def set_match_results(self, match_score: int, match_details: dict, recommendation: str = None):
        """Set AI matching results."""
        self.match_score = match_score
        self.match_details = match_details
        self.ai_recommendation = recommendation
        self.updated_at = datetime.utcnow()
    
    def schedule_interview(self, interview_date: datetime, notes: str = None):
        """Schedule an interview."""
        self.interview_scheduled = interview_date
        self.update_status(ApplicationStatus.INTERVIEWED, notes)
    
    def add_interview_feedback(self, feedback: str):
        """Add interview feedback."""
        self.interview_feedback = feedback
        self.updated_at = datetime.utcnow()
    
    def get_match_breakdown(self) -> dict:
        """Get detailed match score breakdown."""
        if not self.match_details:
            return {}
        
        return {
            "overall_score": self.match_score,
            "skills_match": self.match_details.get("skills_score", 0),
            "experience_match": self.match_details.get("experience_score", 0),
            "education_match": self.match_details.get("education_score", 0),
            "communication_match": self.match_details.get("communication_score", 0),
            "missing_skills": self.match_details.get("missing_skills", []),
            "matching_skills": self.match_details.get("matching_skills", []),
            "strengths": self.match_details.get("strengths", []),
            "concerns": self.match_details.get("concerns", [])
        }
    
    def to_dict(self, include_details: bool = True) -> dict:
        """Convert application to dictionary."""
        app_data = {
            "id": self.id,
            "employee_id": self.employee_id,
            "job_posting_id": self.job_posting_id,
            "resume_id": self.resume_id,
            "voice_analysis_id": self.voice_analysis_id,
            "status": self.status.value,
            "is_active": self.is_active,
            "has_resume": self.has_resume,
            "has_voice_analysis": self.has_voice_analysis,
            "match_score": self.match_score,
            "applied_at": self.applied_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "decision_at": self.decision_at.isoformat() if self.decision_at else None,
            "interview_scheduled": self.interview_scheduled.isoformat() if self.interview_scheduled else None
        }
        
        if include_details:
            app_data.update({
                "cover_letter": self.cover_letter,
                "match_details": self.match_details,
                "match_breakdown": self.get_match_breakdown(),
                "ai_recommendation": self.ai_recommendation,
                "employer_notes": self.employer_notes,
                "interview_feedback": self.interview_feedback
            })
        
        return app_data
    
    def __repr__(self):
        return f"<Application {self.id} (Employee: {self.employee_id}, Job: {self.job_posting_id})>"


# Job matching model for storing AI match results
class JobMatch(Base):
    """
    Job match model for storing AI-generated matches between employees and jobs.
    Used for proactive matching and recommendations.
    """
    
    __tablename__ = "job_matches"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True, index=True)
    
    # Match results
    match_score = Column(Integer, nullable=False)  # 0-100 percentage
    match_details = Column(JSON, nullable=False)  # Detailed matching analysis
    
    # Status tracking
    is_recommended = Column(Boolean, default=True, nullable=False)  # Show to employee
    is_viewed_by_employee = Column(Boolean, default=False, nullable=False)
    is_viewed_by_employer = Column(Boolean, default=False, nullable=False)
    is_dismissed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id])
    job_posting = relationship("JobPosting", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
    
    def mark_viewed_by_employee(self):
        """Mark as viewed by employee."""
        self.is_viewed_by_employee = True
        self.updated_at = datetime.utcnow()
    
    def mark_viewed_by_employer(self):
        """Mark as viewed by employer."""
        self.is_viewed_by_employer = True
        self.updated_at = datetime.utcnow()
    
    def dismiss(self):
        """Dismiss this match recommendation."""
        self.is_dismissed = True
        self.is_recommended = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert job match to dictionary."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "job_posting_id": self.job_posting_id,
            "resume_id": self.resume_id,
            "match_score": self.match_score,
            "match_details": self.match_details,
            "is_recommended": self.is_recommended,
            "is_viewed_by_employee": self.is_viewed_by_employee,
            "is_viewed_by_employer": self.is_viewed_by_employer,
            "is_dismissed": self.is_dismissed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f"<JobMatch {self.match_score}% (Employee: {self.employee_id}, Job: {self.job_posting_id})>"