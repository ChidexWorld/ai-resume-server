"""
Admin router for system management and analytics.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import User, JobPosting, Resume, VoiceAnalysis, Application, JobMatch, UserType, JobStatus, ApplicationStatus
from app.routers.auth import get_current_active_user
from app.schemas.admin import SystemStatsResponse, UserManagementResponse

# Create router
router = APIRouter()


def verify_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify that current user has admin privileges."""
    # For now, we'll consider employers as having some admin capabilities
    # In production, you might want a separate admin role
    if current_user.user_type not in [UserType.EMPLOYER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats/system", response_model=SystemStatsResponse)
async def get_system_statistics(
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system statistics."""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        employees = db.query(User).filter(User.user_type == UserType.EMPLOYEE).count()
        employers = db.query(User).filter(User.user_type == UserType.EMPLOYER).count()
        
        # Job posting statistics
        total_jobs = db.query(JobPosting).count()
        active_jobs = db.query(JobPosting).filter(JobPosting.status == JobStatus.ACTIVE).count()
        
        # Resume statistics
        total_resumes = db.query(Resume).filter(Resume.is_active == True).count()
        analyzed_resumes = db.query(Resume).filter(
            Resume.is_active == True,
            Resume.status == "analyzed"
        ).count()
        
        # Voice analysis statistics
        total_voice = db.query(VoiceAnalysis).filter(VoiceAnalysis.is_active == True).count()
        completed_voice = db.query(VoiceAnalysis).filter(
            VoiceAnalysis.is_active == True,
            VoiceAnalysis.status == "completed"
        ).count()
        
        # Application statistics
        total_applications = db.query(Application).count()
        pending_applications = db.query(Application).filter(
            Application.status == ApplicationStatus.PENDING
        ).count()
        
        # Match statistics
        total_matches = db.query(JobMatch).filter(JobMatch.is_recommended == True).count()
        high_score_matches = db.query(JobMatch).filter(
            JobMatch.is_recommended == True,
            JobMatch.match_score >= 80
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
        new_resumes_week = db.query(Resume).filter(Resume.created_at >= week_ago).count()
        new_applications_week = db.query(Application).filter(Application.applied_at >= week_ago).count()
        
        # Average metrics
        avg_match_score = db.query(func.avg(JobMatch.match_score)).filter(
            JobMatch.is_recommended == True
        ).scalar() or 0
        
        avg_applications_per_job = db.query(func.avg(JobPosting.applications_count)).scalar() or 0
        
        return SystemStatsResponse(
            total_users=total_users,
            active_users=active_users,
            total_employees=employees,
            total_employers=employers,
            total_job_postings=total_jobs,
            active_job_postings=active_jobs,
            total_resumes=total_resumes,
            analyzed_resumes=analyzed_resumes,
            total_voice_analyses=total_voice,
            completed_voice_analyses=completed_voice,
            total_applications=total_applications,
            pending_applications=pending_applications,
            total_matches=total_matches,
            high_score_matches=high_score_matches,
            new_users_this_week=new_users_week,
            new_resumes_this_week=new_resumes_week,
            new_applications_this_week=new_applications_week,
            average_match_score=round(avg_match_score, 1),
            average_applications_per_job=round(avg_applications_per_job, 1)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system statistics: {str(e)}"
        )


@router.get("/users", response_model=List[UserManagementResponse])
async def get_users_for_management(
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get users for management purposes."""
    try:
        query = db.query(User)
        
        if user_type:
            try:
                user_type_enum = UserType(user_type)
                query = query.filter(User.user_type == user_type_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user type"
                )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
        
        response_data = []
        for user in users:
            # Get user statistics
            if user.user_type == UserType.EMPLOYEE:
                resume_count = db.query(Resume).filter(
                    Resume.employee_id == user.id,
                    Resume.is_active == True
                ).count()
                application_count = db.query(Application).filter(
                    Application.employee_id == user.id
                ).count()
                activity_data = {
                    "resume_count": resume_count,
                    "application_count": application_count
                }
            else:  # Employer
                job_count = db.query(JobPosting).filter(
                    JobPosting.employer_id == user.id
                ).count()
                received_applications = db.query(Application).join(JobPosting).filter(
                    JobPosting.employer_id == user.id
                ).count()
                activity_data = {
                    "job_posting_count": job_count,
                    "received_applications": received_applications
                }
            
            response_data.append(UserManagementResponse(
                user=user.to_dict(),
                activity_summary=activity_data,
                last_login=user.updated_at.isoformat(),  # Approximate
                account_status="active" if user.is_active else "inactive"
            ))
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Update user active status."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deactivation
        if user.id == current_user.id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        user.is_active = is_active
        user.updated_at = datetime.utcnow()
        db.commit()
        
        action = "activated" if is_active else "deactivated"
        return {"message": f"User {action} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )


@router.get("/content/moderation")
async def get_content_for_moderation(
    content_type: str = Query(..., description="Type: resumes, jobs, applications"),
    flagged_only: bool = Query(False, description="Show only flagged content"),
    limit: int = Query(20, le=100),
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get content for moderation review."""
    try:
        if content_type == "resumes":
            query = db.query(Resume).filter(Resume.is_active == True)
            if flagged_only:
                # In a real system, you'd have a flagged field
                query = query.filter(Resume.status == "failed")
            
            items = query.order_by(desc(Resume.created_at)).limit(limit).all()
            content_data = [resume.to_dict(include_analysis=False) for resume in items]
            
        elif content_type == "jobs":
            query = db.query(JobPosting)
            if flagged_only:
                # Filter for potentially problematic jobs
                query = query.filter(JobPosting.status == JobStatus.PAUSED)
            
            items = query.order_by(desc(JobPosting.created_at)).limit(limit).all()
            content_data = [job.to_dict(include_requirements=False) for job in items]
            
        elif content_type == "applications":
            query = db.query(Application)
            if flagged_only:
                query = query.filter(Application.status == ApplicationStatus.REJECTED)
            
            items = query.order_by(desc(Application.applied_at)).limit(limit).all()
            content_data = [app.to_dict(include_details=False) for app in items]
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type"
            )
        
        return {
            "content_type": content_type,
            "total_items": len(content_data),
            "flagged_only": flagged_only,
            "items": content_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content for moderation: {str(e)}"
        )


@router.get("/analytics/trends")
async def get_analytics_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Get analytics trends over time."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily user registrations
        daily_users = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= start_date).group_by(
            func.date(User.created_at)
        ).all()
        
        # Daily job postings
        daily_jobs = db.query(
            func.date(JobPosting.created_at).label('date'),
            func.count(JobPosting.id).label('count')
        ).filter(JobPosting.created_at >= start_date).group_by(
            func.date(JobPosting.created_at)
        ).all()
        
        # Daily applications
        daily_applications = db.query(
            func.date(Application.applied_at).label('date'),
            func.count(Application.id).label('count')
        ).filter(Application.applied_at >= start_date).group_by(
            func.date(Application.applied_at)
        ).all()
        
        # Match success rate trends
        daily_matches = db.query(
            func.date(JobMatch.created_at).label('date'),
            func.count(JobMatch.id).label('total'),
            func.sum(func.case([(JobMatch.match_score >= 80, 1)], else_=0)).label('high_score')
        ).filter(JobMatch.created_at >= start_date).group_by(
            func.date(JobMatch.created_at)
        ).all()
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "trends": {
                "daily_registrations": [{"date": str(row.date), "count": row.count} for row in daily_users],
                "daily_job_postings": [{"date": str(row.date), "count": row.count} for row in daily_jobs],
                "daily_applications": [{"date": str(row.date), "count": row.count} for row in daily_applications],
                "daily_matches": [
                    {
                        "date": str(row.date), 
                        "total_matches": row.total,
                        "high_score_matches": row.high_score,
                        "success_rate": round((row.high_score / row.total * 100), 1) if row.total > 0 else 0
                    } for row in daily_matches
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics trends: {str(e)}"
        )


@router.post("/system/cleanup")
async def cleanup_system_data(
    cleanup_type: str = Query(..., description="Type: inactive_users, old_files, failed_analyses"),
    days_threshold: int = Query(30, ge=7, description="Age threshold in days"),
    current_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """Cleanup old or unnecessary system data."""
    try:
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
        cleanup_count = 0
        
        if cleanup_type == "inactive_users":
            # Mark very old inactive users for review (don't delete)
            old_inactive_users = db.query(User).filter(
                User.is_active == False,
                User.updated_at < threshold_date
            ).all()
            
            cleanup_count = len(old_inactive_users)
            # In a real system, you might anonymize or mark for deletion
            
        elif cleanup_type == "old_files":
            # Clean up files for deleted resumes/voice analyses
            old_resumes = db.query(Resume).filter(
                Resume.is_active == False,
                Resume.updated_at < threshold_date
            ).all()
            
            old_voice = db.query(VoiceAnalysis).filter(
                VoiceAnalysis.is_active == False,
                VoiceAnalysis.updated_at < threshold_date
            ).all()
            
            cleanup_count = len(old_resumes) + len(old_voice)
            # File cleanup would happen here
            
        elif cleanup_type == "failed_analyses":
            # Remove failed analysis records
            failed_resumes = db.query(Resume).filter(
                Resume.status == "failed",
                Resume.created_at < threshold_date
            )
            
            failed_voice = db.query(VoiceAnalysis).filter(
                VoiceAnalysis.status == "failed",
                VoiceAnalysis.created_at < threshold_date
            )
            
            cleanup_count = failed_resumes.count() + failed_voice.count()
            
            # Actually delete failed analyses
            failed_resumes.delete()
            failed_voice.delete()
            db.commit()
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cleanup type"
            )
        
        return {
            "cleanup_type": cleanup_type,
            "items_processed": cleanup_count,
            "threshold_days": days_threshold,
            "message": f"Cleanup completed. Processed {cleanup_count} items."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup operation failed: {str(e)}"
        )