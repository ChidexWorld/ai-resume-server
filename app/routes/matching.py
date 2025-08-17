"""
AI matching system router for intelligent job-candidate matching.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime


from app.database import get_db
from app.models import User, JobPosting, Resume, VoiceAnalysis, JobMatch, UserType, JobStatus
from app.routers.auth import get_current_active_user
from app.services.ai_service import ai_service
from app.schemas.matching import (
    JobMatchResponse, CandidateMatchResponse, MatchingRequest,
    BatchMatchingResponse, MatchingStatsResponse
)
from app.config import settings

# Create router
router = APIRouter()


@router.post("/generate-matches/{job_id}", response_model=BatchMatchingResponse)
async def generate_job_matches(
    job_id: int,
    background_tasks: BackgroundTasks,
    limit: int = Query(50, le=200, description="Maximum matches to generate"),
    min_score: int = Query(70, ge=0, le=100, description="Minimum match score"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI matches for a job posting."""
    try:
        # Get job posting and verify access
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )
        
        # Verify access (job owner or admin)
        if current_user.user_type == UserType.EMPLOYER and job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job posting"
        )
    
    # Build query
    query = db.query(JobMatch).filter(JobMatch.job_posting_id == job_id, JobMatch.is_recommended == True)
    
    if min_score is not None:
        query = query.filter(JobMatch.match_score >= min_score)
    
    matches = query.order_by(desc(JobMatch.match_score)).offset(offset).limit(limit).all()
    
    # Prepare response with candidate data
    response_data = []
    for match in matches:
        # Get employee data
        employee = db.query(User).filter(User.id == match.employee_id).first()
        
        # Get resume data
        resume = db.query(Resume).filter(Resume.id == match.resume_id).first() if match.resume_id else None
        
        # Get voice analysis if available
        voice_analysis = db.query(VoiceAnalysis).filter(
            VoiceAnalysis.employee_id == match.employee_id,
            VoiceAnalysis.status == "completed",
            VoiceAnalysis.is_active == True
        ).order_by(desc(VoiceAnalysis.created_at)).first()
        
        # Mark as viewed by employer
        if not match.is_viewed_by_employer:
            match.mark_viewed_by_employer()
        
        response_data.append(CandidateMatchResponse(
            match_id=match.id,
            employee=employee.to_dict() if employee else None,
            resume_analysis=resume.to_dict(include_analysis=True) if resume else None,
            voice_analysis=voice_analysis.to_dict(include_analysis=True) if voice_analysis else None,
            match_score=match.match_score,
            match_details=match.match_details,
            created_at=match.created_at.isoformat()
        ))
    
    db.commit()  # Save viewed status
    return response_data


@router.get("/employee-matches", response_model=List[JobMatchResponse])
async def get_employee_job_matches(
    min_score: Optional[int] = Query(70, ge=0, le=100),
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job matches for the current employee."""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employees"
        )
    
    # Build query
    query = db.query(JobMatch).filter(
        JobMatch.employee_id == current_user.id,
        JobMatch.is_recommended == True,
        JobMatch.is_dismissed == False
    )
    
    if min_score is not None:
        query = query.filter(JobMatch.match_score >= min_score)
    
    matches = query.order_by(desc(JobMatch.match_score)).offset(offset).limit(limit).all()
    
    # Prepare response with job data
    response_data = []
    for match in matches:
        # Get job posting data
        job = db.query(JobPosting).filter(JobPosting.id == match.job_posting_id).first()
        
        if job and job.status == JobStatus.ACTIVE:
            # Mark as viewed by employee
            if not match.is_viewed_by_employee:
                match.mark_viewed_by_employee()
            
            response_data.append(JobMatchResponse(
                match_id=match.id,
                job=job.to_dict(),
                match_score=match.match_score,
                match_details=match.match_details,
                created_at=match.created_at.isoformat()
            ))
    
    db.commit()  # Save viewed status
    return response_data


@router.post("/calculate-match")
async def calculate_job_match(
    matching_request: MatchingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate match score between a resume and job requirements."""
    try:
        # Get resume
        resume = db.query(Resume).filter(Resume.id == matching_request.resume_id).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Verify access
        if current_user.user_type == UserType.EMPLOYEE and resume.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this resume"
            )
        
        # Get job if job_id provided, otherwise use custom requirements
        job_requirements = None
        if matching_request.job_id:
            job = db.query(JobPosting).filter(JobPosting.id == matching_request.job_id).first()
            if job:
                job_requirements = job.get_matching_criteria()
        
        if not job_requirements:
            job_requirements = matching_request.job_requirements
        
        if not job_requirements:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job requirements must be provided"
            )
        
        # Calculate match
        resume_data = resume.to_dict(include_analysis=True)
        match_result = ai_service.match_resume_to_job(resume_data, job_requirements)
        
        return {
            "resume_id": matching_request.resume_id,
            "job_id": matching_request.job_id,
            "match_score": match_result["overall_score"],
            "match_details": match_result["match_details"],
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match calculation failed: {str(e)}"
        )


@router.post("/dismiss-match/{match_id}")
async def dismiss_job_match(
    match_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dismiss a job match recommendation."""
    try:
        # Get match
        match = db.query(JobMatch).filter(JobMatch.id == match_id).first()
        
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Verify access
        if current_user.user_type == UserType.EMPLOYEE and match.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this match"
            )
        elif current_user.user_type == UserType.EMPLOYER:
            job = db.query(JobPosting).filter(JobPosting.id == match.job_posting_id).first()
            if not job or job.employer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this match"
                )
        
        # Dismiss match
        match.dismiss()
        db.commit()
        
        return {"message": "Match dismissed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dismiss match: {str(e)}"
        )


@router.get("/matching-stats", response_model=MatchingStatsResponse)
async def get_matching_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get matching statistics for the current user."""
    try:
        if current_user.user_type == UserType.EMPLOYEE:
            # Employee stats
            total_matches = db.query(JobMatch).filter(
                JobMatch.employee_id == current_user.id,
                JobMatch.is_recommended == True
            ).count()
            
            viewed_matches = db.query(JobMatch).filter(
                JobMatch.employee_id == current_user.id,
                JobMatch.is_recommended == True,
                JobMatch.is_viewed_by_employee == True
            ).count()
            
            high_score_matches = db.query(JobMatch).filter(
                JobMatch.employee_id == current_user.id,
                JobMatch.is_recommended == True,
                JobMatch.match_score >= 80
            ).count()
            
            # Get average match score
            from sqlalchemy import func
            avg_score_result = db.query(func.avg(JobMatch.match_score)).filter(
                JobMatch.employee_id == current_user.id,
                JobMatch.is_recommended == True
            ).scalar()
            
            avg_match_score = round(avg_score_result, 1) if avg_score_result else 0
            
            return MatchingStatsResponse(
                user_type="employee",
                total_matches=total_matches,
                viewed_matches=viewed_matches,
                high_score_matches=high_score_matches,
                average_match_score=avg_match_score,
                dismissed_matches=db.query(JobMatch).filter(
                    JobMatch.employee_id == current_user.id,
                    JobMatch.is_dismissed == True
                ).count()
            )
            
        else:  # Employer
            # Get all matches for employer's jobs
            from sqlalchemy import func
            
            employer_matches = db.query(JobMatch).join(JobPosting).filter(
                JobPosting.employer_id == current_user.id
            )
            
            total_matches = employer_matches.count()
            viewed_matches = employer_matches.filter(JobMatch.is_viewed_by_employer == True).count()
            high_score_matches = employer_matches.filter(JobMatch.match_score >= 80).count()
            
            # Average match score across all employer's jobs
            avg_score_result = employer_matches.with_entities(func.avg(JobMatch.match_score)).scalar()
            avg_match_score = round(avg_score_result, 1) if avg_score_result else 0
            
            return MatchingStatsResponse(
                user_type="employer",
                total_matches=total_matches,
                viewed_matches=viewed_matches,
                high_score_matches=high_score_matches,
                average_match_score=avg_match_score,
                active_job_postings=db.query(JobPosting).filter(
                    JobPosting.employer_id == current_user.id,
                    JobPosting.status == JobStatus.ACTIVE
                ).count()
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matching statistics: {str(e)}"
        )


@router.post("/bulk-match-generation")
async def generate_bulk_matches(
    background_tasks: BackgroundTasks,
    employer_id: Optional[int] = Query(None, description="Generate matches for specific employer"),
    min_score: int = Query(70, ge=0, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate matches for multiple jobs (admin or system use)."""
    # This endpoint could be restricted to admin users in production
    try:
        # Get active job postings
        query = db.query(JobPosting).filter(JobPosting.status == JobStatus.ACTIVE)
        
        if employer_id:
            query = query.filter(JobPosting.employer_id == employer_id)
        
        jobs = query.limit(50).all()  # Limit for performance
        
        total_matches = 0
        jobs_processed = 0
        
        for job in jobs:
            try:
                # Generate matches for this job
                job_requirements = job.get_matching_criteria()
                
                # Get candidates
                resumes = db.query(Resume).join(User).filter(
                    User.user_type == UserType.EMPLOYEE,
                    User.is_active == True,
                    Resume.status == "analyzed",
                    Resume.is_active == True
                ).limit(100).all()
                
                job_matches = 0
                
                for resume in resumes:
                    # Skip existing matches
                    existing = db.query(JobMatch).filter(
                        JobMatch.employee_id == resume.employee_id,
                        JobMatch.job_posting_id == job.id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Calculate match
                    resume_data = resume.to_dict(include_analysis=True)
                    match_result = ai_service.match_resume_to_job(resume_data, job_requirements)
                    
                    if match_result["overall_score"] >= min_score:
                        match = JobMatch(
                            employee_id=resume.employee_id,
                            job_posting_id=job.id,
                            resume_id=resume.id,
                            match_score=match_result["overall_score"],
                            match_details=match_result["match_details"]
                        )
                        
                        db.add(match)
                        job_matches += 1
                        total_matches += 1
                
                jobs_processed += 1
                
                # Commit periodically
                if jobs_processed % 10 == 0:
                    db.commit()
                    
            except Exception as e:
                print(f"Error processing job {job.id}: {e}")
                continue
        
        db.commit()
        
        return {
            "message": "Bulk match generation completed",
            "jobs_processed": jobs_processed,
            "total_matches_created": total_matches,
            "min_score_threshold": min_score
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk match generation failed: {str(e)}"
        )_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this job posting"
            )
        
        # Get job requirements
        job_requirements = job.get_matching_criteria()
        
        # Get all active resumes for matching
        resumes = db.query(Resume).join(User).filter(
            User.user_type == UserType.EMPLOYEE,
            User.is_active == True,
            Resume.status == "analyzed",
            Resume.is_active == True
        ).limit(500).all()  # Limit for performance
        
        matches_created = 0
        total_candidates = len(resumes)
        
        for resume in resumes:
            try:
                # Skip if already matched
                existing_match = db.query(JobMatch).filter(
                    JobMatch.employee_id == resume.employee_id,
                    JobMatch.job_posting_id == job_id
                ).first()
                
                if existing_match:
                    continue
                
                # Calculate match score
                resume_data = resume.to_dict(include_analysis=True)
                match_result = ai_service.match_resume_to_job(resume_data, job_requirements)
                match_score = match_result["overall_score"]
                
                # Create match if score is above threshold
                if match_score >= min_score:
                    job_match = JobMatch(
                        employee_id=resume.employee_id,
                        job_posting_id=job_id,
                        resume_id=resume.id,
                        match_score=match_score,
                        match_details=match_result["match_details"]
                    )
                    
                    db.add(job_match)
                    matches_created += 1
                    
                    if matches_created >= limit:
                        break
                        
            except Exception as e:
                print(f"Error matching resume {resume.id}: {e}")
                continue
        
        db.commit()
        
        return BatchMatchingResponse(
            job_id=job_id,
            total_candidates_analyzed=total_candidates,
            matches_created=matches_created,
            min_score_threshold=min_score,
            message=f"Generated {matches_created} matches from {total_candidates} candidates"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match generation failed: {str(e)}"
        )


@router.get("/job-matches/{job_id}", response_model=List[CandidateMatchResponse])
async def get_job_matches(
    job_id: int,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get AI-generated matches for a job posting."""
    # Verify job access
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    if current_user.user_type == UserType.EMPLOYER and job.employer