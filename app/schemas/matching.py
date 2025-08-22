"""
Pydantic schemas for matching system endpoints.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class MatchingRequest(BaseModel):
    """Schema for match calculation requests."""
    resume_id: int
    job_id: Optional[int] = None
    job_requirements: Optional[Dict[str, Any]] = None


class JobMatchResponse(BaseModel):
    """Schema for job match recommendations (employee view)."""
    match_id: int
    job: Dict[str, Any]
    match_score: int
    match_details: Dict[str, Any]
    created_at: str
    
    class Config:
        from_attributes = True


class CandidateMatchResponse(BaseModel):
    """Schema for candidate match recommendations (employer view)."""
    match_id: int
    employee: Optional[Dict[str, Any]]
    resume_analysis: Optional[Dict[str, Any]]
    voice_analysis: Optional[Dict[str, Any]]
    match_score: int
    match_details: Dict[str, Any]
    created_at: str
    
    class Config:
        from_attributes = True


class BatchMatchingResponse(BaseModel):
    """Schema for batch matching operation results."""
    job_id: int
    total_candidates_analyzed: int
    matches_created: int
    min_score_threshold: int
    message: str


class MatchingStatsResponse(BaseModel):
    """Schema for matching statistics."""
    user_type: str
    total_matches: int
    viewed_matches: int
    high_score_matches: int
    average_match_score: float
    dismissed_matches: Optional[int] = None
    active_job_postings: Optional[int] = None   