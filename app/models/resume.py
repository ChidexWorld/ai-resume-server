"""
Resume model for employee document uploads and AI analysis.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ResumeStatus(str, enum.Enum):
    """Resume processing status enumeration."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class Resume(Base):
    """
    Resume model for storing employee resumes and AI analysis results.
    """
    
    __tablename__ = "resumes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to employee
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Processing status
    status = Column(Enum(ResumeStatus), default=ResumeStatus.UPLOADED, nullable=False)
    
    # Extracted content
    raw_text = Column(Text, nullable=True)
    
    # AI Analysis Results (JSON fields for structured data)
    contact_info = Column(JSON, nullable=True)  # Name, email, phone, address
    skills = Column(JSON, nullable=True)  # Technical and soft skills
    experience = Column(JSON, nullable=True)  # Work experience details
    education = Column(JSON, nullable=True)  # Educational background
    certifications = Column(JSON, nullable=True)  # Professional certifications
    languages = Column(JSON, nullable=True)  # Language skills
    
    # AI-generated summary and analysis
    professional_summary = Column(Text, nullable=True)
    experience_level = Column(String(20), nullable=True)  # entry, junior, mid, senior, etc.
    total_experience_years = Column(Integer, nullable=True)
    
    # Matching scores (updated when matched against jobs)
    latest_match_score = Column(Integer, nullable=True)  # 0-100 percentage
    match_details = Column(JSON, nullable=True)  # Detailed matching breakdown
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Active status (for soft deletion)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employee = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")
    matches = relationship("JobMatch", back_populates="resume")
    
    @property
    def is_analyzed(self) -> bool:
        """Check if resume has been successfully analyzed."""
        return self.status == ResumeStatus.ANALYZED
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
    
    def update_status(self, status: ResumeStatus):
        """Update the processing status."""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == ResumeStatus.ANALYZED:
            self.analyzed_at = datetime.utcnow()
    
    def set_analysis_results(self, analysis_data: dict):
        """Set the AI analysis results."""
        # Extract structured data from analysis
        self.contact_info = analysis_data.get("contact_info", {})
        self.skills = analysis_data.get("skills", {})
        self.experience = analysis_data.get("experience", [])
        self.education = analysis_data.get("education", [])
        self.certifications = analysis_data.get("certifications", [])
        self.languages = analysis_data.get("languages", [])
        
        # Set summary information
        self.professional_summary = analysis_data.get("professional_summary")
        self.experience_level = analysis_data.get("experience_level")
        self.total_experience_years = analysis_data.get("total_experience_years")
        
        # Update status
        self.update_status(ResumeStatus.ANALYZED)
    
    def get_skills_list(self) -> list:
        """Get flattened list of all skills."""
        if not self.skills:
            return []
        
        all_skills = []
        if isinstance(self.skills, dict):
            for category, skills in self.skills.items():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.append(skills)
        elif isinstance(self.skills, list):
            all_skills = self.skills
        
        return list(set(all_skills))  # Remove duplicates
    
    def get_experience_summary(self) -> dict:
        """Get summarized experience information."""
        if not self.experience:
            return {"total_years": 0, "companies": [], "positions": []}

        # Handle case where experience is stored as string (parse JSON)
        experience_data = self.experience
        if isinstance(experience_data, str):
            try:
                import json
                experience_data = json.loads(experience_data)
            except (json.JSONDecodeError, ValueError):
                return {"total_years": self.total_experience_years or 0, "companies": [], "positions": []}

        if not isinstance(experience_data, list):
            return {"total_years": self.total_experience_years or 0, "companies": [], "positions": []}

        companies = []
        positions = []

        for exp in experience_data:
            if isinstance(exp, dict):
                if exp.get("company"):
                    companies.append(exp["company"])
                if exp.get("position") or exp.get("title"):
                    positions.append(exp.get("position") or exp.get("title"))

        return {
            "total_years": self.total_experience_years or 0,
            "companies": list(set(companies)),
            "positions": list(set(positions))
        }
    
    def get_education_summary(self) -> dict:
        """Get summarized education information."""
        if not self.education:
            return {"highest_degree": None, "institutions": [], "fields": []}

        # Handle case where education is stored as string (parse JSON)
        education_data = self.education
        if isinstance(education_data, str):
            try:
                import json
                education_data = json.loads(education_data)
            except (json.JSONDecodeError, ValueError):
                return {"highest_degree": None, "institutions": [], "fields": []}

        if not isinstance(education_data, list):
            return {"highest_degree": None, "institutions": [], "fields": []}

        degrees = []
        institutions = []
        fields = []

        for edu in education_data:
            if isinstance(edu, dict):
                if edu.get("degree"):
                    degrees.append(edu["degree"])
                if edu.get("institution"):
                    institutions.append(edu["institution"])
                if edu.get("field") or edu.get("major"):
                    fields.append(edu.get("field") or edu.get("major"))
        
        # Determine highest degree (simplified logic)
        degree_hierarchy = ["phd", "doctorate", "master", "bachelor", "associate", "diploma", "certificate"]
        highest_degree = None
        
        for degree_level in degree_hierarchy:
            for degree in degrees:
                if degree_level in degree.lower():
                    highest_degree = degree
                    break
            if highest_degree:
                break
        
        return {
            "highest_degree": highest_degree,
            "institutions": list(set(institutions)),
            "fields": list(set(fields))
        }
    
    def soft_delete(self):
        """Soft delete the resume."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_analysis: bool = True) -> dict:
        """Convert resume to dictionary."""
        resume_data = {
            "id": self.id,
            "employee_id": self.employee_id,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "mime_type": self.mime_type,
            "status": self.status.value,
            "is_analyzed": self.is_analyzed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "latest_match_score": self.latest_match_score
        }
        
        if include_analysis and self.is_analyzed:
            def safe_json_parse(data):
                """Safely parse JSON data that might be stored as string."""
                if isinstance(data, str):
                    try:
                        import json
                        return json.loads(data)
                    except (json.JSONDecodeError, ValueError):
                        return data
                return data

            resume_data.update({
                "contact_info": safe_json_parse(self.contact_info),
                "skills": safe_json_parse(self.skills),
                "experience": safe_json_parse(self.experience),
                "education": safe_json_parse(self.education),
                "certifications": safe_json_parse(self.certifications),
                "languages": safe_json_parse(self.languages),
                "professional_summary": self.professional_summary,
                "experience_level": self.experience_level,
                "total_experience_years": self.total_experience_years,
                "skills_list": self.get_skills_list(),
                "experience_summary": self.get_experience_summary(),
                "education_summary": self.get_education_summary()
            })
        
        return resume_data
    
    def __repr__(self):
        return f"<Resume {self.original_filename} (Employee: {self.employee_id})>"