"""
Employer router for job posting management and candidate review.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.database import get_db
from app.models import User, JobPosting, Application, Resume, VoiceAnalysis, UserType, JobStatus, ApplicationStatus
from app.routers.auth import get_current_active_user
from app.services import ai_service, AI_SERVICE_AVAILABLE
from app.schemas.employer import (
    JobPostingCreate, JobPostingUpdate, JobPostingResponse,
    ApplicationReviewResponse, CandidateSearchResponse,
    InterviewSchedule, ApplicationStatusUpdate
)
from app.config import settings

# Create router
router = APIRouter()


def verify_employer_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify that current user is an employer."""
    if current_user.user_type != UserType.EMPLOYER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employers"
        )
    return current_user


@router.post(
    "/jobs", 
    response_model=JobPostingResponse,
    summary="Create Job Posting",
    description="Create a new job posting with requirements and matching criteria for AI-powered candidate matching.",
    response_description="Created job posting with unique ID and matching configuration"
)
async def create_job_posting(
    job_data: JobPostingCreate,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting.
    
    Define job requirements and AI matching criteria:
    - **Basic Info**: Title, description, location, salary range
    - **Required Skills**: Technical skills candidates must have
    - **Experience**: Minimum years and relevant areas
    - **Education**: Degree requirements and preferred fields
    - **Communication**: Voice analysis requirements for role
    
    The AI system will use these criteria to automatically match and rank candidates.
    """
    try:
        # Create job posting
        job_posting = JobPosting(
            employer_id=current_user.id,
            title=job_data.title,
            description=job_data.description,
            department=job_data.department,
            location=job_data.location,
            remote_allowed=job_data.remote_allowed,
            job_type=job_data.job_type,
            experience_level=job_data.experience_level,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            currency=job_data.currency,
            required_skills=job_data.required_skills,
            preferred_skills=job_data.preferred_skills,
            required_education=job_data.required_education,
            required_experience=job_data.required_experience,
            communication_requirements=job_data.communication_requirements,
            matching_weights=job_data.matching_weights,
            is_urgent=job_data.is_urgent,
            max_applications=job_data.max_applications,
            auto_match_enabled=job_data.auto_match_enabled,
            minimum_match_score=job_data.minimum_match_score,
            expires_at=job_data.expires_at
        )
        
        db.add(job_posting)
        db.commit()
        db.refresh(job_posting)

        try:
            job_dict = job_posting.to_dict()
            return JobPostingResponse.model_validate(job_dict)
        except Exception as dict_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert job posting to dict: {str(dict_error)}"
            )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job posting: {str(e)}"
        )


@router.get("/jobs", response_model=List[JobPostingResponse])
async def get_my_job_postings(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, paused, closed"),
    limit: int = Query(50, le=100, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Get all job postings for the current employer."""
    query = db.query(JobPosting).filter(JobPosting.employer_id == current_user.id)
    
    if status_filter:
        try:
            job_status = JobStatus(status_filter)
            query = query.filter(JobPosting.status == job_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )
    
    jobs = query.order_by(desc(JobPosting.created_at)).offset(offset).limit(limit).all()
    
    return [JobPostingResponse.model_validate(job.to_dict()) for job in jobs]


@router.get("/jobs/{job_id}", response_model=JobPostingResponse)
async def get_job_posting(
    job_id: int,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Get a specific job posting by ID."""
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.employer_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    return JobPostingResponse.model_validate(job.to_dict())


@router.put("/jobs/{job_id}", response_model=JobPostingResponse)
async def update_job_posting(
    job_id: int,
    job_update: JobPostingUpdate,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Update a job posting."""
    try:
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.employer_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )
        
        # Update fields
        update_data = job_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        
        return JobPostingResponse.model_validate(job.to_dict())
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job posting: {str(e)}"
        )


@router.delete("/jobs/{job_id}")
async def delete_job_posting(
    job_id: int,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting."""
    try:
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.employer_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )
        
        # Actually delete the job posting
        db.delete(job)
        db.commit()

        return {"message": "Job posting deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job posting: {str(e)}"
        )


@router.get("/jobs/{job_id}/applications", response_model=List[ApplicationReviewResponse])
async def get_job_applications(
    job_id: int,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum match score"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Get all applications for a specific job posting."""
    # Verify job belongs to employer
    job = db.query(JobPosting).filter(
        JobPosting.id == job_id,
        JobPosting.employer_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    # Build query
    query = db.query(Application).filter(Application.job_posting_id == job_id)
    
    if status_filter:
        try:
            app_status = ApplicationStatus(status_filter)
            query = query.filter(Application.status == app_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )
    
    if min_score is not None:
        query = query.filter(Application.match_score >= min_score)

    # Enhanced sorting: AI match score (if available) + recency + original match score
    applications = query.order_by(
        desc(Application.match_score),  # Primary: AI-calculated match score
        desc(Application.applied_at)    # Secondary: Most recent applications
    ).offset(offset).limit(limit).all()

    # Prepare response with employee and analysis data
    response_data = []
    for app in applications:
        # Get employee data
        employee = db.query(User).filter(User.id == app.employee_id).first()

        # Get resume data if available
        resume_data = None
        if app.resume_id:
            resume = db.query(Resume).filter(Resume.id == app.resume_id).first()
            if resume:
                resume_data = resume.to_dict(include_analysis=True)

        # Get voice analysis data if available
        voice_data = None
        if app.voice_analysis_id:
            voice = db.query(VoiceAnalysis).filter(VoiceAnalysis.id == app.voice_analysis_id).first()
            if voice:
                voice_data = voice.to_dict(include_analysis=True)

        # Calculate AI-powered match score if AI service is available
        ai_match_data = None
        if AI_SERVICE_AVAILABLE and ai_service and resume_data:
            try:
                job_requirements = {
                    "required_skills": job.required_skills or [],
                    "preferred_skills": job.preferred_skills or [],
                    "required_experience": {
                        "min_years": job.required_experience or 0
                    },
                    "required_education": job.required_education or {},
                    "industry": job.department,
                    "matching_weights": job.matching_weights or {}
                }
                ai_match_data = await ai_service.match_resume_to_job(resume_data, job_requirements)

                # Update application match score if it's outdated
                if app.match_score != ai_match_data.get("overall_match_score", app.match_score):
                    app.match_score = ai_match_data.get("overall_match_score", app.match_score)
                    db.commit()

            except Exception as e:
                print(f"AI matching failed for application {app.id}: {e}")

        app_data = app.to_dict()
        if ai_match_data:
            app_data["ai_match_analysis"] = ai_match_data

        response_data.append(ApplicationReviewResponse(
            application=app_data,
            employee=employee.to_dict() if employee else None,
            resume_analysis=resume_data,
            voice_analysis=voice_data
        ))
    
    return response_data


@router.put("/applications/{application_id}/status", response_model=ApplicationReviewResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Update application status and add employer notes."""
    try:
        # Get application and verify it belongs to employer's job
        application = db.query(Application).join(JobPosting).filter(
            Application.id == application_id,
            JobPosting.employer_id == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update application
        application.update_status(status_update.status, status_update.notes)
        db.commit()
        db.refresh(application)
        
        # Get related data for response
        employee = db.query(User).filter(User.id == application.employee_id).first()
        resume_data = None
        voice_data = None

        if application.resume_id:
            resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
            if resume:
                resume_data = resume.to_dict(include_analysis=True)

        if application.voice_analysis_id:
            voice = db.query(VoiceAnalysis).filter(VoiceAnalysis.id == application.voice_analysis_id).first()
            if voice:
                voice_data = voice.to_dict(include_analysis=True)

        # Generate AI analysis for the application
        ai_match_data = None
        if AI_SERVICE_AVAILABLE and ai_service and resume_data:
            try:
                job = db.query(JobPosting).filter(JobPosting.id == application.job_posting_id).first()
                if job:
                    job_requirements = {
                        "required_skills": job.required_skills or [],
                        "preferred_skills": job.preferred_skills or [],
                        "required_experience": {
                            "min_years": job.required_experience or 0
                        },
                        "required_education": job.required_education or {},
                        "industry": job.department,
                        "matching_weights": job.matching_weights or {}
                    }
                    ai_match_data = await ai_service.match_resume_to_job(resume_data, job_requirements)
            except Exception as e:
                print(f"AI analysis failed for application {application.id}: {e}")

        app_data = application.to_dict()
        if ai_match_data:
            app_data["ai_match_analysis"] = ai_match_data

        return ApplicationReviewResponse(
            application=app_data,
            employee=employee.to_dict() if employee else None,
            resume_analysis=resume_data,
            voice_analysis=voice_data
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application status: {str(e)}"
        )


@router.post("/applications/{application_id}/interview")
async def schedule_interview(
    application_id: int,
    interview_data: InterviewSchedule,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Schedule an interview for an application."""
    try:
        # Get application and verify it belongs to employer's job
        application = db.query(Application).join(JobPosting).filter(
            Application.id == application_id,
            JobPosting.employer_id == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Schedule interview
        application.schedule_interview(
            interview_date=interview_data.interview_date,
            interview_type=interview_data.interview_type,
            interview_location=interview_data.location_or_link,
            notes=interview_data.notes
        )
        db.commit()

        return {
            "message": "Interview scheduled successfully",
            "interview_date": interview_data.interview_date.isoformat(),
            "interview_type": interview_data.interview_type,
            "location_or_link": interview_data.location_or_link,
            "notes": interview_data.notes
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule interview: {str(e)}"
        )


@router.get("/candidates/search", response_model=List[CandidateSearchResponse])
async def search_candidates(
    skills: Optional[str] = Query(None, description="Comma-separated skills to search for"),
    experience_level: Optional[str] = Query(None, description="Minimum experience level"),
    min_experience_years: Optional[int] = Query(None, ge=0, description="Minimum years of experience"),
    location: Optional[str] = Query(None, description="Location filter"),
    min_communication_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum communication score"),
    limit: int = Query(20, le=100),
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Search for candidates based on criteria."""
    try:
        # Base query for employees with analyzed resumes
        query = db.query(Resume).join(User).filter(
            User.user_type == UserType.EMPLOYEE.value,
            User.is_active == True,
            Resume.status == "analyzed",
            Resume.is_active == True
        )
        
        # Apply filters
        if min_experience_years is not None:
            query = query.filter(Resume.total_experience_years >= min_experience_years)
        
        if experience_level:
            query = query.filter(Resume.experience_level == experience_level)
        
        resumes = query.order_by(desc(Resume.total_experience_years)).limit(limit * 2).all()  # Get more for filtering
        
        candidates = []
        for resume in resumes:
            # Get employee
            employee = resume.employee
            
            # Get latest voice analysis if available
            voice_analysis = db.query(VoiceAnalysis).filter(
                VoiceAnalysis.employee_id == employee.id,
                VoiceAnalysis.status == "completed",
                VoiceAnalysis.is_active == True
            ).order_by(desc(VoiceAnalysis.created_at)).first()
            
            # Apply communication score filter
            if min_communication_score and voice_analysis:
                if not voice_analysis.overall_communication_score or voice_analysis.overall_communication_score < min_communication_score:
                    continue
            
            # Apply skills filter with AI-powered semantic matching
            matching_skills = []
            if skills:
                required_skills = [s.strip().lower() for s in skills.split(',')]
                resume_skills = resume.get_skills_list()
                resume_skills_lower = [s.lower() for s in resume_skills]

                # Basic keyword matching
                matching_skills = [s for s in required_skills if s in resume_skills_lower]

                # Enhanced AI semantic matching if available
                if AI_SERVICE_AVAILABLE and ai_service and not matching_skills:
                    try:
                        # Create a simple job requirements object for AI matching
                        job_requirements = {
                            "required_skills": [s.strip() for s in skills.split(',')],
                            "preferred_skills": [],
                            "required_experience": {"min_years": min_experience_years or 0},
                            "industry": "general"
                        }
                        resume_data = resume.to_dict(include_analysis=True)
                        ai_match = await ai_service.match_resume_to_job(resume_data, job_requirements)

                        # Use AI match score to determine relevance
                        if ai_match.get("overall_match_score", 0) >= 60:  # 60% threshold
                            matching_skills = ai_match.get("matching_details", {}).get("matching_skills", [])

                    except Exception as e:
                        print(f"AI semantic matching failed for resume {resume.id}: {e}")

                # Skip if no skills match found
                if not matching_skills:
                    continue
            
            # Apply location filter (basic string matching)
            if location and resume.contact_info:
                candidate_location = resume.contact_info.get('location', '').lower()
                if location.lower() not in candidate_location:
                    continue
            
            # Calculate AI match score for search results
            ai_match_score = None
            ai_matching_details = None
            if AI_SERVICE_AVAILABLE and ai_service and skills:
                try:
                    job_requirements = {
                        "required_skills": [s.strip() for s in skills.split(',')],
                        "preferred_skills": [],
                        "required_experience": {"min_years": min_experience_years or 0},
                        "industry": "general"
                    }
                    resume_data = resume.to_dict(include_analysis=True)
                    ai_match = await ai_service.match_resume_to_job(resume_data, job_requirements)
                    ai_match_score = ai_match.get("overall_match_score")
                    ai_matching_details = ai_match.get("matching_details")
                except Exception as e:
                    print(f"AI match scoring failed for resume {resume.id}: {e}")

            candidates.append(CandidateSearchResponse(
                employee=employee.to_dict(),
                resume_analysis=resume.to_dict(include_analysis=True),
                voice_analysis=voice_analysis.to_dict(include_analysis=True) if voice_analysis else None,
                match_summary={
                    "skills_match": matching_skills if skills else [],
                    "experience_years": resume.total_experience_years,
                    "communication_score": voice_analysis.overall_communication_score if voice_analysis else None,
                    "ai_match_score": ai_match_score,
                    "ai_matching_details": ai_matching_details
                }
            ))
            
            if len(candidates) >= limit:
                break

        # Sort candidates by AI match score if available, otherwise by experience
        if AI_SERVICE_AVAILABLE and any(c.match_summary.get("ai_match_score") for c in candidates):
            candidates.sort(key=lambda x: x.match_summary.get("ai_match_score", 0), reverse=True)
        else:
            candidates.sort(key=lambda x: x.match_summary.get("experience_years", 0), reverse=True)

        return candidates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Candidate search failed: {str(e)}"
        )


@router.post("/jobs/{job_id}/auto-score-applications")
async def auto_score_applications(
    job_id: int,
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Automatically score all applications for a job using AI matching."""
    try:
        # Verify job belongs to employer
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.employer_id == current_user.id
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )

        if not AI_SERVICE_AVAILABLE or not ai_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not available"
            )

        # Get all applications for this job
        applications = db.query(Application).filter(
            Application.job_posting_id == job_id
        ).all()

        updated_count = 0
        job_requirements = {
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "required_experience": {
                "min_years": job.required_experience or 0
            },
            "required_education": job.required_education or {},
            "industry": job.department,
            "matching_weights": job.matching_weights or {}
        }

        for app in applications:
            try:
                if app.resume_id:
                    resume = db.query(Resume).filter(Resume.id == app.resume_id).first()
                    if resume:
                        resume_data = resume.to_dict(include_analysis=True)
                        ai_match = await ai_service.match_resume_to_job(resume_data, job_requirements)

                        # Update match score
                        new_score = ai_match.get("overall_match_score", app.match_score)
                        if app.match_score != new_score:
                            app.match_score = new_score
                            updated_count += 1

            except Exception as e:
                print(f"Failed to score application {app.id}: {e}")
                continue

        db.commit()

        return {
            "message": f"Successfully updated {updated_count} application scores",
            "total_applications": len(applications),
            "updated_applications": updated_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-score applications: {str(e)}"
        )


@router.get("/jobs/{job_id}/ai-recommendations", response_model=List[CandidateSearchResponse])
async def get_ai_candidate_recommendations(
    job_id: int,
    limit: int = Query(10, le=50, description="Maximum number of candidates to recommend"),
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered candidate recommendations for a specific job."""
    try:
        # Verify job belongs to employer
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.employer_id == current_user.id
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found"
            )

        if not AI_SERVICE_AVAILABLE or not ai_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not available"
            )

        # Get job requirements
        job_requirements = {
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "required_experience": {
                "min_years": job.required_experience or 0
            },
            "required_education": job.required_education or {},
            "industry": job.department,
            "matching_weights": job.matching_weights or {}
        }

        # Get all active employees with analyzed resumes
        resumes = db.query(Resume).join(User).filter(
            User.user_type == UserType.EMPLOYEE.value,
            User.is_active == True,
            Resume.status == "analyzed",
            Resume.is_active == True
        ).limit(limit * 3).all()  # Get more for better filtering

        candidates = []
        for resume in resumes:
            try:
                resume_data = resume.to_dict(include_analysis=True)
                ai_match = await ai_service.match_resume_to_job(resume_data, job_requirements)

                # Only include high-scoring candidates
                if ai_match.get("overall_match_score", 0) >= 70:  # 70% threshold for recommendations
                    employee = resume.employee

                    # Get voice analysis if available
                    voice_analysis = db.query(VoiceAnalysis).filter(
                        VoiceAnalysis.employee_id == employee.id,
                        VoiceAnalysis.status == "completed",
                        VoiceAnalysis.is_active == True
                    ).order_by(desc(VoiceAnalysis.created_at)).first()

                    candidates.append(CandidateSearchResponse(
                        employee=employee.to_dict(),
                        resume_analysis=resume_data,
                        voice_analysis=voice_analysis.to_dict(include_analysis=True) if voice_analysis else None,
                        match_summary={
                            "ai_match_score": ai_match.get("overall_match_score"),
                            "matching_skills": ai_match.get("matching_details", {}).get("matching_skills", []),
                            "experience_years": resume.total_experience_years,
                            "communication_score": voice_analysis.overall_communication_score if voice_analysis else None,
                            "strengths": ai_match.get("matching_details", {}).get("strengths", []),
                            "concerns": ai_match.get("matching_details", {}).get("concerns", []),
                            "recommendations": ai_match.get("matching_details", {}).get("recommendations", [])
                        }
                    ))

            except Exception as e:
                print(f"AI recommendation failed for resume {resume.id}: {e}")
                continue

        # Sort by AI match score
        candidates.sort(key=lambda x: x.match_summary.get("ai_match_score", 0), reverse=True)

        return candidates[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI recommendations: {str(e)}"
        )


@router.get("/dashboard/stats")
async def get_employer_dashboard_stats(
    current_user: User = Depends(verify_employer_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for employer."""
    try:
        # Get job posting stats
        total_jobs = db.query(JobPosting).filter(JobPosting.employer_id == current_user.id).count()
        active_jobs = db.query(JobPosting).filter(
            JobPosting.employer_id == current_user.id,
            JobPosting.status == JobStatus.ACTIVE
        ).count()
        
        # Get application stats
        total_applications = db.query(Application).join(JobPosting).filter(
            JobPosting.employer_id == current_user.id
        ).count()
        
        pending_applications = db.query(Application).join(JobPosting).filter(
            JobPosting.employer_id == current_user.id,
            Application.status == ApplicationStatus.PENDING
        ).count()
        
        # Get recent applications (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_applications = db.query(Application).join(JobPosting).filter(
            JobPosting.employer_id == current_user.id,
            Application.applied_at >= thirty_days_ago
        ).count()
        
        return {
            "company_name": current_user.company_name,
            "total_job_postings": total_jobs,
            "active_job_postings": active_jobs,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "recent_applications_30d": recent_applications,
            "average_applications_per_job": round(total_applications / max(total_jobs, 1), 1)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )