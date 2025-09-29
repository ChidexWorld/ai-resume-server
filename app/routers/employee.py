"""
Employee router for resume upload, voice analysis, and job applications.
"""
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.database import get_db
from app.models import User, Resume, VoiceAnalysis, Application, JobPosting, UserType
from app.models.resume import ResumeStatus
from app.models.voice_analysis import VoiceStatus
from app.routers.auth import get_current_active_user
from app.services import ai_service, AI_SERVICE_AVAILABLE
from app.services.file_service import FileService
from app.schemas.employer import (
    ResumeResponse, VoiceAnalysisResponse, ApplicationCreate, ApplicationResponse
)
from app.schemas.matching import JobMatchResponse
from app.config import settings

# Create router
router = APIRouter()

# File service
file_service = FileService()


def verify_employee_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify that current user is an employee."""
    if current_user.user_type != UserType.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to employees"
        )
    return current_user


async def get_skill_based_recommendations(
    current_user: User,
    db: Session,
    limit: int,
    min_score: int,
    industry_filter: Optional[str]
):
    """Fast skill-based job recommendations without AI."""
    print(f"🔍 Getting skill-based recommendations for user {current_user.id}")

    # Get employee's latest resume
    latest_resume = db.query(Resume).filter(
        Resume.employee_id == current_user.id,
        Resume.status == ResumeStatus.ANALYZED,
        Resume.is_active == True
    ).order_by(desc(Resume.created_at)).first()

    if not latest_resume:
        print(f"⚠️ No analyzed resume found for user {current_user.id}")
        return []

    # Extract user skills
    resume_data = latest_resume.to_dict(include_analysis=True)
    user_skills = set()
    if "skills" in resume_data:
        for skill_category in resume_data["skills"].values():
            user_skills.update([s.lower().strip() for s in skill_category])

    # Get active job postings
    query = db.query(JobPosting).filter(JobPosting.status == "active")

    if industry_filter:
        query = query.filter(JobPosting.department.ilike(f"%{industry_filter}%"))

    jobs = query.limit(50).all()
    print(f"📊 Found {len(jobs)} active job postings")

    recommendations = []

    for job in jobs:
        try:
            # Calculate skill-based match score
            job_required_skills = set([s.lower().strip() for s in (job.required_skills or [])])
            job_preferred_skills = set([s.lower().strip() for s in (job.preferred_skills or [])])

            all_job_skills = job_required_skills.union(job_preferred_skills)

            if not all_job_skills:
                continue

            # Calculate match scores
            required_matches = len(job_required_skills.intersection(user_skills))
            preferred_matches = len(job_preferred_skills.intersection(user_skills))

            # Weighted scoring: required skills are more important
            required_score = (required_matches / max(len(job_required_skills), 1)) * 70
            preferred_score = (preferred_matches / max(len(job_preferred_skills), 1)) * 30

            total_score = min(100, int(required_score + preferred_score))

            if total_score >= min_score:
                recommendations.append({
                    "match_id": job.id,
                    "job": job.to_dict(),
                    "match_score": total_score,
                    "match_details": {
                        "matching_skills": list(user_skills.intersection(all_job_skills)),
                        "missing_skills": list(job_required_skills - user_skills),
                        "skill_match_ratio": len(user_skills.intersection(all_job_skills)) / len(all_job_skills)
                    },
                    "created_at": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Skill-based matching failed for job {job.id}: {e}")
            continue

    # Sort by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)

    print(f"✅ Returning {len(recommendations)} recommendations")
    return recommendations[:limit]


@router.post(
    "/resume/upload", 
    response_model=ResumeResponse,
    summary="Upload Resume",
    description="Upload resume file (PDF, DOCX, TXT) for AI analysis and skill extraction.",
    response_description="Resume analysis results including extracted skills, experience, and education"
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT format, max 25MB)"),
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a resume file.
    
    - **file**: Resume document in PDF, DOCX, or TXT format
    - **Max size**: 25MB
    
    AI analysis extracts:
    - Contact information (email, phone, location)  
    - Skills (technical and soft skills)
    - Work experience and job history
    - Education (degrees, institutions, certifications)
    - Professional summary
    
    Returns detailed analysis results and skill matching data.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_resume_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(settings.allowed_resume_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Save file
        file_info = file_service.save_file(
            file_content=file_content,
            original_filename=file.filename,
            user_id=current_user.id,
            file_type="resume"
        )
        
        # Create resume record
        resume = Resume(
            employee_id=current_user.id,
            original_filename=file.filename,
            stored_filename=file_info["stored_filename"],
            file_path=file_info["file_path"],
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Start AI analysis in background (for now, we'll do it synchronously)
        try:
            resume.update_status("processing")
            db.commit()

            # Check if AI service is available
            if not AI_SERVICE_AVAILABLE:
                resume.status = "failed"
                resume.analysis_error = "AI service not available - missing dependencies"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service not available. Please ensure all AI dependencies are installed."
                )

            # Extract text from file
            extracted_text = ai_service.extract_text_from_file(
                file_info["file_path"],
                resume.mime_type
            )
            resume.raw_text = extracted_text

            # Analyze resume with AI
            analysis_results = ai_service.analyze_resume_from_text(extracted_text)
            resume.set_analysis_results(analysis_results)

            db.commit()
            db.refresh(resume)

        except HTTPException:
            raise
        except Exception as e:
            # Mark analysis as failed but keep the resume record
            resume.status = "failed"
            resume.analysis_error = str(e)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resume analysis failed: {str(e)}"
            )
        
        return ResumeResponse.from_orm(resume)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume upload failed: {str(e)}"
        )


@router.post("/voice/upload", response_model=VoiceAnalysisResponse)
async def upload_voice_recording(
    file: UploadFile = File(...),
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a voice recording.
    Supports WAV, MP3, MP4, M4A, OGG formats.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_audio_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(settings.allowed_audio_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Save file
        file_info = file_service.save_file(
            file_content=file_content,
            original_filename=file.filename,
            user_id=current_user.id,
            file_type="voice"
        )
        
        # Get audio duration
        duration = file_service.get_audio_duration(file_info["file_path"])
        
        # Validate duration
        if duration and duration > settings.max_audio_duration:
            # Clean up file
            file_service.delete_file(file_info["file_path"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio duration exceeds maximum limit of {settings.max_audio_duration} seconds"
            )
        
        # Create voice analysis record
        voice_analysis = VoiceAnalysis(
            employee_id=current_user.id,
            original_filename=file.filename,
            stored_filename=file_info["stored_filename"],
            file_path=file_info["file_path"],
            file_size=file_size,
            mime_type=file.content_type or "audio/wav",
            duration=duration
        )
        
        db.add(voice_analysis)
        db.commit()
        db.refresh(voice_analysis)
        
        # Start AI analysis
        try:
            voice_analysis.update_status("transcribing")
            db.commit()

            # Check if AI service is available
            if not AI_SERVICE_AVAILABLE:
                voice_analysis.status = "failed"
                voice_analysis.analysis_error = "AI service not available - missing dependencies"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service not available. Please ensure all AI dependencies are installed."
                )

            # Transcribe audio
            transcript, confidence = ai_service.transcribe_audio(file_info["file_path"])
            voice_analysis.set_transcript(transcript, confidence)
            db.commit()

            # Analyze voice resume
            analysis_results = ai_service.analyze_voice_resume(file_info["file_path"])
            voice_analysis.set_analysis_results(analysis_results)

            db.commit()
            db.refresh(voice_analysis)

        except HTTPException:
            raise
        except Exception as e:
            # Mark analysis as failed
            voice_analysis.status = "failed"
            voice_analysis.analysis_error = str(e)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Voice analysis failed: {str(e)}"
            )
        
        return VoiceAnalysisResponse.from_orm(voice_analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice upload failed: {str(e)}"
        )


@router.get("/resumes", response_model=List[ResumeResponse])
async def get_my_resumes(
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current employee."""
    resumes = db.query(Resume).filter(
        Resume.employee_id == current_user.id,
        Resume.is_active == True
    ).order_by(desc(Resume.created_at)).all()
    
    return [ResumeResponse.from_orm(resume) for resume in resumes]


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.employee_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return ResumeResponse.from_orm(resume)


@router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Delete a resume (soft delete)."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.employee_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Soft delete
    resume.soft_delete()
    db.commit()
    
    return {"message": "Resume deleted successfully"}


@router.get("/voice-analyses", response_model=List[VoiceAnalysisResponse])
async def get_my_voice_analyses(
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get all voice analyses for the current employee."""
    voice_analyses = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.employee_id == current_user.id,
        VoiceAnalysis.is_active == True
    ).order_by(desc(VoiceAnalysis.created_at)).all()
    
    return [VoiceAnalysisResponse.from_orm(va) for va in voice_analyses]


@router.get("/voice-analyses/{voice_id}", response_model=VoiceAnalysisResponse)
async def get_voice_analysis(
    voice_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get a specific voice analysis by ID."""
    voice_analysis = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.id == voice_id,
        VoiceAnalysis.employee_id == current_user.id,
        VoiceAnalysis.is_active == True
    ).first()
    
    if not voice_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice analysis not found"
        )
    
    return VoiceAnalysisResponse.from_orm(voice_analysis)


@router.delete("/voice-analyses/{voice_id}")
async def delete_voice_analysis(
    voice_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Delete a voice analysis (soft delete)."""
    voice_analysis = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.id == voice_id,
        VoiceAnalysis.employee_id == current_user.id,
        VoiceAnalysis.is_active == True
    ).first()
    
    if not voice_analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice analysis not found"
        )
    
    # Soft delete
    voice_analysis.soft_delete()
    db.commit()
    
    return {"message": "Voice analysis deleted successfully"}


@router.post("/apply/{job_id}", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: int,
    application_data: ApplicationCreate,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Apply to a job posting."""
    try:
        # Check if job exists and is active
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.status == "active"
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found or not active"
            )
        
        # Check if already applied
        existing_application = db.query(Application).filter(
            Application.employee_id == current_user.id,
            Application.job_posting_id == job_id
        ).first()
        
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already applied to this job"
            )
        
        # Verify resume exists if provided
        resume = None
        if application_data.resume_id:
            resume = db.query(Resume).filter(
                Resume.id == application_data.resume_id,
                Resume.employee_id == current_user.id,
                Resume.status == ResumeStatus.ANALYZED
            ).first()
            
            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resume not found or not analyzed"
                )
        
        # Verify voice analysis exists if provided
        voice_analysis = None
        if application_data.voice_analysis_id:
            voice_analysis = db.query(VoiceAnalysis).filter(
                VoiceAnalysis.id == application_data.voice_analysis_id,
                VoiceAnalysis.employee_id == current_user.id,
                VoiceAnalysis.status == VoiceStatus.COMPLETED
            ).first()
            
            if not voice_analysis:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Voice analysis not found or not completed"
                )
        
        # Create application
        application = Application(
            employee_id=current_user.id,
            job_posting_id=job_id,
            resume_id=application_data.resume_id,
            voice_analysis_id=application_data.voice_analysis_id,
            cover_letter=application_data.cover_letter
        )
        
        db.add(application)
        
        # Calculate match score if resume is provided and AI service is available
        if resume and AI_SERVICE_AVAILABLE:
            try:
                job_requirements = job.get_matching_criteria()
                resume_data = resume.to_dict(include_analysis=True)

                match_result = await ai_service.match_resume_to_job(resume_data, job_requirements)

                application.set_match_results(
                    match_score=match_result["overall_match_score"],
                    match_details=match_result["matching_details"],
                    recommendation=f"Match score: {match_result['overall_match_score']}%"
                )

            except Exception as e:
                print(f"Match calculation failed: {e}")
                # Continue without match score
        elif resume and not AI_SERVICE_AVAILABLE:
            print("AI service not available - skipping match calculation")
        
        # Update job application count
        job.increment_applications()
        
        db.commit()
        db.refresh(application)
        
        app_dict = {
            "id": application.id,
            "employee_id": application.employee_id,
            "job_posting_id": application.job_posting_id,
            "resume_id": application.resume_id,
            "voice_analysis_id": application.voice_analysis_id,
            "cover_letter": application.cover_letter,
            "status": application.status.value,
            "match_score": application.match_score,
            "match_details": application.match_details,
            "recommendation": application.ai_recommendation,
            "applied_at": application.applied_at.isoformat(),
            "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
            "interview_scheduled_at": application.interview_scheduled.isoformat() if application.interview_scheduled else None,
            "notes": application.employer_notes
        }
        return ApplicationResponse.model_validate(app_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application failed: {str(e)}"
        )


@router.get("/applications", response_model=List[ApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get all applications for the current employee."""
    applications = db.query(Application).filter(
        Application.employee_id == current_user.id
    ).order_by(desc(Application.applied_at)).all()
    
    result = []
    for app in applications:
        app_dict = {
            "id": app.id,
            "employee_id": app.employee_id,
            "job_posting_id": app.job_posting_id,
            "resume_id": app.resume_id,
            "voice_analysis_id": app.voice_analysis_id,
            "cover_letter": app.cover_letter,
            "status": app.status.value,
            "match_score": app.match_score,
            "match_details": app.match_details,
            "recommendation": app.ai_recommendation,
            "applied_at": app.applied_at.isoformat(),
            "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
            "interview_scheduled_at": app.interview_scheduled.isoformat() if app.interview_scheduled else None,
            "notes": app.employer_notes
        }
        result.append(ApplicationResponse.model_validate(app_dict))
    return result


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get a specific application by ID."""
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.employee_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    app_dict = {
        "id": application.id,
        "employee_id": application.employee_id,
        "job_posting_id": application.job_posting_id,
        "resume_id": application.resume_id,
        "voice_analysis_id": application.voice_analysis_id,
        "cover_letter": application.cover_letter,
        "status": application.status.value,
        "match_score": application.match_score,
        "match_details": application.match_details,
        "recommendation": application.ai_recommendation,
        "applied_at": application.applied_at.isoformat(),
        "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
        "interview_scheduled_at": application.interview_scheduled.isoformat() if application.interview_scheduled else None,
        "notes": application.employer_notes
    }
    return ApplicationResponse.model_validate(app_dict)


@router.get("/job-recommendations", response_model=List[JobMatchResponse])
async def get_job_recommendations(
    limit: int = 20,
    min_score: int = 70,
    industry_filter: Optional[str] = None,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered job recommendations for the employee."""
    try:
        # Always use AI service if available
        if not AI_SERVICE_AVAILABLE:
            return await get_skill_based_recommendations(
                current_user, db, limit, min_score, industry_filter
            )

        # Get employee's latest resume
        latest_resume = db.query(Resume).filter(
            Resume.employee_id == current_user.id,
            Resume.status == ResumeStatus.ANALYZED,
            Resume.is_active == True
        ).order_by(desc(Resume.created_at)).first()

        if not latest_resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analyzed resume found. Please upload and analyze a resume first."
            )

        # Get active job postings with improved query
        query = db.query(JobPosting).filter(JobPosting.status == "active")

        # Apply industry filter if provided
        if industry_filter:
            query = query.filter(JobPosting.department.ilike(f"%{industry_filter}%"))

        # Limit to reasonable number for AI processing
        jobs = query.limit(30).all()  # Reduced from 100 to 30 for faster processing

        recommendations = []
        resume_data = latest_resume.to_dict(include_analysis=True)

        # Process jobs in smaller batches for better performance
        for job in jobs:
            try:
                # Quick skill-based pre-filtering before expensive AI call
                job_skills = set((job.required_skills or []) + (job.preferred_skills or []))
                resume_skills = set()
                if "skills" in resume_data:
                    for skill_category in resume_data["skills"].values():
                        resume_skills.update([s.lower() for s in skill_category])

                # Calculate basic skill overlap ratio
                if job_skills:
                    skill_overlap = len(job_skills.intersection(resume_skills)) / len(job_skills)
                    # Skip jobs with very low skill overlap to save AI calls
                    if skill_overlap < 0.1:  # Less than 10% skill match
                        continue

                # Only do expensive AI calculation for promising matches
                job_requirements = job.get_matching_criteria()
                match_result = await ai_service.match_resume_to_job(resume_data, job_requirements)
                match_score = match_result["overall_match_score"]

                if match_score >= min_score:
                    recommendations.append({
                        "job": job,
                        "match_score": match_score,
                        "match_details": match_result["matching_details"]
                    })

                # Stop after finding enough good matches
                if len(recommendations) >= limit:
                    break

            except Exception as e:
                print(f"Match calculation failed for job {job.id}: {e}")
                continue

        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        # Return top recommendations
        return [
            JobMatchResponse(
                match_id=i+1,  # Generate temporary ID
                job=rec["job"].to_dict(),
                match_score=rec["match_score"],
                match_details=rec["match_details"],
                created_at=datetime.now().isoformat()
            )
            for i, rec in enumerate(recommendations[:limit])
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.post("/analyze-job-match/{job_id}")
async def analyze_job_match(
    job_id: int,
    resume_id: Optional[int] = None,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get detailed match analysis between user's resume and a specific job."""
    try:
        # Check if AI service is available
        if not AI_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not available. Match analysis requires AI service."
            )

        # Get job posting
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.status == "active"
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found or not active"
            )

        # Get resume (use provided ID or latest)
        if resume_id:
            resume = db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.employee_id == current_user.id,
                Resume.status == ResumeStatus.ANALYZED,
                Resume.is_active == True
            ).first()
        else:
            resume = db.query(Resume).filter(
                Resume.employee_id == current_user.id,
                Resume.status == ResumeStatus.ANALYZED,
                Resume.is_active == True
            ).order_by(desc(Resume.created_at)).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analyzed resume found. Please upload and analyze a resume first."
            )

        # Calculate detailed match
        job_requirements = job.get_matching_criteria()
        resume_data = resume.to_dict(include_analysis=True)

        match_result = await ai_service.match_resume_to_job(resume_data, job_requirements)

        return {
            "job": job.to_dict(),
            "resume": {
                "id": resume.id,
                "filename": resume.original_filename,
                "detected_industry": resume_data.get("detected_industry"),
                "experience_level": resume_data.get("experience_level"),
                "total_experience_years": resume_data.get("total_experience_years")
            },
            "match_analysis": {
                "overall_score": match_result["overall_match_score"],
                "match_details": match_result["matching_details"],
                "strengths": match_result["matching_details"].get("matching_skills", []),
                "gaps": match_result["matching_details"].get("missing_skills", []),
                "recommendations": match_result["matching_details"].get("recommendations", [])
            },
            "analysis_date": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match analysis failed: {str(e)}"
        )


@router.get("/skills-analysis")
async def get_skills_analysis(
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive skills analysis from user's latest resume."""
    try:
        # Check if AI service is available
        if not AI_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not available. Skills analysis requires AI service."
            )

        # Get latest analyzed resume
        latest_resume = db.query(Resume).filter(
            Resume.employee_id == current_user.id,
            Resume.status == ResumeStatus.ANALYZED,
            Resume.is_active == True
        ).order_by(desc(Resume.created_at)).first()

        if not latest_resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analyzed resume found. Please upload and analyze a resume first."
            )

        resume_data = latest_resume.to_dict(include_analysis=True)

        # Get industry-specific insights from dataset manager
        from app.services import dataset_manager
        detected_industry = resume_data.get("detected_industry", "general")
        industry_skills = dataset_manager.get_skills_by_industry(detected_industry)
        all_skills = dataset_manager.get_all_skills()

        # Analyze skill coverage
        resume_skills = []
        if "skills" in resume_data:
            for _, skills in resume_data["skills"].items():
                resume_skills.extend(skills)

        resume_skills_lower = [skill.lower() for skill in resume_skills]
        industry_skills_lower = [skill.lower() for skill in industry_skills]

        matching_industry_skills = [
            skill for skill in industry_skills
            if skill.lower() in resume_skills_lower
        ]

        missing_industry_skills = [
            skill for skill in industry_skills
            if skill.lower() not in resume_skills_lower
        ][:10]  # Top 10 missing skills

        return {
            "detected_industry": detected_industry,
            "total_skills_found": len(resume_skills),
            "industry_skill_coverage": {
                "matching_skills": matching_industry_skills,
                "missing_skills": missing_industry_skills,
                "coverage_percentage": round(
                    (len(matching_industry_skills) / max(len(industry_skills), 1)) * 100, 1
                )
            },
            "skills_by_category": resume_data.get("skills", {}),
            "experience_level": resume_data.get("experience_level"),
            "total_experience_years": resume_data.get("total_experience_years"),
            "recommendations": {
                "skills_to_develop": missing_industry_skills[:5],
                "career_level": resume_data.get("experience_level"),
                "industry_focus": detected_industry
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skills analysis failed: {str(e)}"
        )

@router.get("/jobs/search",
           summary="Search Jobs",
           description="Search and filter job postings with various criteria. Returns all active jobs if no filters are applied.",
           response_description="List of job postings matching the search criteria",
           tags=["Jobs"])
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query for job title, description, or company"),
    location: Optional[str] = Query(None, description="Location filter"),
    job_type: Optional[str] = Query(None, description="Job type filter (full_time, part_time, contract, etc.)"),
    experience_level: Optional[str] = Query(None, description="Experience level filter (entry, mid, senior, executive)"),
    remote_allowed: Optional[bool] = Query(None, description="Filter for remote-allowed jobs"),
    min_salary: Optional[int] = Query(None, ge=0, description="Minimum salary filter"),
    max_salary: Optional[int] = Query(None, ge=0, description="Maximum salary filter"),
    skills: Optional[str] = Query(None, description="Comma-separated skills to search for"),
    department: Optional[str] = Query(None, description="Department filter"),
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """
    Search for jobs based on various criteria.

    This endpoint allows employees to search for job postings using multiple filters:
    - Text search in job title, description, and company name
    - Location-based filtering
    - Job type and experience level filtering
    - Salary range filtering
    - Skills-based matching
    - Remote work preferences

    Returns a list of matching job postings with basic information.
    """
    try:
        # Start with base query for active job postings
        # current_user is required for authentication but not used in filtering
        query = db.query(JobPosting).filter(JobPosting.status == "active")

        # Apply text search filter
        if q and q.strip():
            search_term = f"%{q.lower()}%"
            query = query.filter(
                or_(
                    JobPosting.title.ilike(search_term),
                    JobPosting.description.ilike(search_term),
                    JobPosting.department.ilike(search_term)
                )
            )

        # Apply location filter
        if location and location.strip():
            location_term = f"%{location.lower()}%"
            query = query.filter(JobPosting.location.ilike(location_term))

        # Apply job type filter
        if job_type and job_type.strip():
            query = query.filter(JobPosting.job_type == job_type)

        # Apply experience level filter
        if experience_level and experience_level.strip():
            query = query.filter(JobPosting.experience_level == experience_level)

        # Apply remote allowed filter
        if remote_allowed is not None:
            query = query.filter(JobPosting.remote_allowed == remote_allowed)

        # Apply salary filters
        if min_salary is not None and min_salary > 0:
            query = query.filter(
                or_(
                    JobPosting.salary_min >= min_salary,
                    JobPosting.salary_max >= min_salary
                )
            )

        if max_salary is not None and max_salary > 0:
            query = query.filter(
                or_(
                    JobPosting.salary_min <= max_salary,
                    JobPosting.salary_max <= max_salary
                )
            )

        # Apply department filter
        if department and department.strip():
            dept_term = f"%{department.lower()}%"
            query = query.filter(JobPosting.department.ilike(dept_term))

        # Apply skills filter (search in required_skills and preferred_skills JSON fields)
        if skills and skills.strip():
            skills_list = [skill.strip().lower() for skill in skills.split(',') if skill.strip()]
            skills_conditions = []

            for skill in skills_list:
                # Search in required_skills JSON array
                skills_conditions.extend([
                    JobPosting.required_skills.contains([skill]),
                    JobPosting.preferred_skills.contains([skill])
                ])

                # Also search as case-insensitive partial match in JSON
                skills_conditions.extend([
                    JobPosting.required_skills.op('::text')(f'%{skill}%'),
                    JobPosting.preferred_skills.op('::text')(f'%{skill}%')
                ])

            if skills_conditions:
                query = query.filter(or_(*skills_conditions))

        # Apply ordering (most recent first)
        query = query.order_by(desc(JobPosting.created_at))

        # Apply pagination
        total_count = query.count()
        jobs = query.offset(offset).limit(limit).all()

        # Convert to response format
        job_results = []
        for job in jobs:
            # Get employer information
            employer = db.query(User).filter(User.id == job.employer_id).first()
            company_name = "Unknown Company"
            if employer:
                if hasattr(employer, 'company_name') and employer.company_name:
                    company_name = employer.company_name
                else:
                    company_name = f"{employer.first_name} {employer.last_name}".strip() or employer.email

            # Format salary range
            salary_range = "Salary not specified"
            if job.salary_min and job.salary_max:
                salary_range = f"{job.currency} {job.salary_min:,} - {job.salary_max:,}"
            elif job.salary_min:
                salary_range = f"From {job.currency} {job.salary_min:,}"
            elif job.salary_max:
                salary_range = f"Up to {job.currency} {job.salary_max:,}"

            job_data = {
                "id": job.id,
                "employer_id": job.employer_id,
                "title": job.title,
                "description": job.description,
                "department": job.department,
                "location": job.location,
                "remote_allowed": job.remote_allowed,
                "job_type": job.job_type.value,
                "experience_level": job.experience_level.value,
                "salary_range": salary_range,
                "currency": job.currency,
                "status": job.status.value,
                "is_urgent": job.is_urgent,
                "is_active": job.is_active,
                "applications_count": job.applications_count,
                "max_applications": job.max_applications,
                "auto_match_enabled": job.auto_match_enabled,
                "minimum_match_score": job.minimum_match_score,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
                "expires_at": job.expires_at.isoformat() if job.expires_at else None,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "required_education": job.required_education,
                "required_experience": job.required_experience,
                "communication_requirements": job.communication_requirements,
                "matching_weights": job.matching_weights,
                "company_name": company_name
            }
            job_results.append(job_data)

        return {
            "jobs": job_results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job search failed: {str(e)}"
        )
@router.get("/jobs/{job_id}",
           summary="Get Job Details",
           description="Get detailed information about a specific job posting including match analysis",
           response_description="Complete job details with match analysis and application status",
           tags=["Jobs"])
async def get_job_details(
    job_id: int,
    current_user: User = Depends(verify_employee_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific job posting.

    Returns comprehensive job details including:
    - Job description and requirements
    - Company information
    - Salary and benefits
    - Application status (if already applied)
    - Match analysis (if resume is available)
    """
    try:
        # Get job posting
        job = db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.status == "active"
        ).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job posting not found or not active"
            )

        # Get employer information
        employer = db.query(User).filter(User.id == job.employer_id).first()
        company_name = "Unknown Company"
        if employer:
            if hasattr(employer, 'company_name') and employer.company_name:
                company_name = employer.company_name
            else:
                company_name = f"{employer.first_name} {employer.last_name}".strip() or employer.email

        # Check if user has already applied
        existing_application = db.query(Application).filter(
            Application.employee_id == current_user.id,
            Application.job_posting_id == job_id
        ).first()

        # Get match analysis if available
        match_analysis = None
        if AI_SERVICE_AVAILABLE:
            try:
                # Get user's latest analyzed resume
                latest_resume = db.query(Resume).filter(
                    Resume.employee_id == current_user.id,
                    Resume.status == ResumeStatus.ANALYZED,
                    Resume.is_active == True
                ).order_by(desc(Resume.created_at)).first()

                if latest_resume:
                    job_requirements = job.get_matching_criteria()
                    resume_data = latest_resume.to_dict(include_analysis=True)

                    match_result = await ai_service.match_resume_to_job(resume_data, job_requirements)
                    match_analysis = {
                        "overall_score": match_result["overall_match_score"],
                        "match_details": match_result["matching_details"],
                        "strengths": match_result["matching_details"].get("matching_skills", []),
                        "gaps": match_result["matching_details"].get("missing_skills", []),
                        "recommendations": match_result["matching_details"].get("recommendations", [])
                    }
            except Exception as e:
                print(f"Match analysis failed: {e}")
                # Continue without match analysis

        # Format salary range
        salary_range = "Salary not specified"
        if job.salary_min and job.salary_max:
            salary_range = f"{job.currency} {job.salary_min:,} - {job.salary_max:,}"
        elif job.salary_min:
            salary_range = f"From {job.currency} {job.salary_min:,}"
        elif job.salary_max:
            salary_range = f"Up to {job.currency} {job.salary_max:,}"

        job_data = {
            "id": job.id,
            "employer_id": job.employer_id,
            "title": job.title,
            "description": job.description,
            "department": job.department,
            "location": job.location,
            "remote_allowed": job.remote_allowed,
            "job_type": job.job_type.value,
            "experience_level": job.experience_level.value,
            "salary_range": salary_range,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "currency": job.currency,
            "status": job.status.value,
            "is_urgent": job.is_urgent,
            "is_active": job.is_active,
            "applications_count": job.applications_count,
            "max_applications": job.max_applications,
            "auto_match_enabled": job.auto_match_enabled,
            "minimum_match_score": job.minimum_match_score,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "expires_at": job.expires_at.isoformat() if job.expires_at else None,
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "required_education": job.required_education,
            "required_experience": job.required_experience,
            "communication_requirements": job.communication_requirements,
            "matching_weights": job.matching_weights,
            "company_name": company_name,
            "application_status": existing_application.status.value if existing_application else None,
            "applied_at": existing_application.applied_at.isoformat() if existing_application else None,
            "match_analysis": match_analysis
        }

        return job_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job details: {str(e)}"
        )


