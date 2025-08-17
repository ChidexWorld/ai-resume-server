"""
Pydantic schemas for admin system endpoints.
"""
from typing import Dict, Any
from pydantic import BaseModel


class SystemStatsResponse(BaseModel):
    """Schema for system statistics."""
    total_users: int
    active_users: int
    total_employees: int
    total_employers: int
    total_job_postings: int
    active_job_postings: int
    total_resumes: int
    analyzed_resumes: int
    total_voice_analyses: int
    completed_voice_analyses: int
    total_applications: int
    pending_applications: int
    total_matches: int
    high_score_matches: int
    new_users_this_week: int
    new_resumes_this_week: int
    new_applications_this_week: int
    average_match_score: float
    average_applications_per_job: float


class UserManagementResponse(BaseModel):
    """Schema for user management data."""
    user: Dict[str, Any]
    activity_summary: Dict[str, Any]
    last_login: str
    account_status: str
    
    class Config:
        from_attributes = True


class ContentModerationResponse(BaseModel):
    """Schema for content moderation data."""
    content_id: int
    content_type: str
    user_id: int
    status: str
    flagged: bool
    created_at: str
    content_preview: str
    
    class Config:
        from_attributes = True