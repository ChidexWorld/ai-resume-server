"""
User model for both employees and employers.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserType(str, enum.Enum):
    """User type enumeration."""
    EMPLOYEE = "employee"
    EMPLOYER = "employer"


class User(Base):
    """
    User model for authentication and profile management.
    Supports both employees and employers.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # User type and status
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Company information (for employers)
    company_name = Column(String(255), nullable=True)
    company_website = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # For employees
    resumes = relationship("Resume", back_populates="employee", cascade="all, delete-orphan")
    voice_analyses = relationship("VoiceAnalysis", back_populates="employee", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="employee", cascade="all, delete-orphan")
    
    # For employers
    job_postings = relationship("JobPosting", back_populates="employer", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_employee(self) -> bool:
        """Check if user is an employee."""
        return self.user_type == UserType.EMPLOYEE
    
    @property
    def is_employer(self) -> bool:
        """Check if user is an employer."""
        return self.user_type == UserType.EMPLOYER
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary."""
        user_data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "user_type": self.user_type.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        # Add employer-specific fields
        if self.is_employer:
            user_data.update({
                "company_name": self.company_name,
                "company_website": self.company_website,
                "company_size": self.company_size
            })
        
        if include_sensitive:
            user_data["password_hash"] = self.password_hash
        
        return user_data
    
    def __repr__(self):
        return f"<User {self.email} ({self.user_type.value})>"