"""
FastAPI main application entry point.
Employee-Employer Matching System with AI-powered analysis.
"""
# CRITICAL: Import setup_nltk FIRST before any other imports
import setup_nltk

import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, create_tables

# Import all models first to register them with SQLAlchemy
from app.models import (
    User, UserType, JobPosting, JobStatus, ExperienceLevel, JobType,
    Resume, ResumeStatus, VoiceAnalysis, VoiceStatus, 
    Application, ApplicationStatus, JobMatch
)

# Import routers after models are registered
from app.routers import auth, employee, employer, admin
# Temporarily disabled matching import due to syntax issues
# from app.routers import matching

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## AI-Powered Employee-Employer Matching Platform
    
    This API provides comprehensive functionality for matching employees with employers using advanced AI analysis:
    
    ### 🎯 **Core Features**
    - **AI Resume Analysis**: Extract skills, experience, and education from uploaded documents
    - **Voice Analysis**: Assess communication skills through speech-to-text and pattern analysis
    - **Smart Matching**: AI-powered job-candidate compatibility scoring
    - **Dual User System**: Separate workflows for employees and employers
    - **Real-time Recommendations**: Dynamic job and candidate suggestions
    
    ### 🔐 **Authentication**
    All endpoints (except public ones) require JWT authentication via Bearer tokens.
    
    ### 📊 **Getting Started**
    1. Register as either an employee or employer using `/api/auth/register`
    2. Login to receive your access token via `/api/auth/login`
    3. Use the token in the Authorization header: `Bearer <your-token>`
    4. Explore endpoints based on your user type (employee/employer)
    
    ### 🚀 **Live Documentation**
    - **Interactive API Docs**: [/docs](/docs) (this page)
    - **Alternative Docs**: [/redoc](/redoc)
    - **Health Check**: [/api/health](/api/health)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AI Resume Server API",
        "url": "http://localhost:8000",
    },
    license_info={
        "name": "MIT License",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Create upload directories
os.makedirs(settings.upload_folder, exist_ok=True)
os.makedirs(os.path.join(settings.upload_folder, "resumes"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_folder, "voice"), exist_ok=True)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(employee.router, prefix="/api/employee", tags=["Employee"])
app.include_router(employer.router, prefix="/api/employer", tags=["Employer"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])

# Import and include matching router
try:
    from app.routers import matching
    app.include_router(matching.router, prefix="/api/matching", tags=["AI Matching"])
    print("✓ AI Matching router enabled")
except Exception as e:
    print(f"⚠️ AI Matching router could not be loaded: {e}")
    print("Basic matching functionality may be limited")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")

    # Create database tables
    create_tables()
    print("Database tables created/verified")

    # Create upload directories
    os.makedirs(settings.upload_folder, exist_ok=True)
    print(f"Upload directory ready: {settings.upload_folder}")

    # Initialize AI services
    try:
        from app.services import initialize_services
        print("Initializing AI services...")
        service_status = initialize_services()

        if service_status["errors"]:
            for error in service_status["errors"]:
                print(f"Warning: {error}")

        print("AI services initialization completed")

    except Exception as e:
        print(f"Warning: Failed to initialize AI services: {e}")
        print("The application will continue but AI features may not work properly")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "dashboards": {
            "employer_dashboard": "/employer-dashboard"
        },
        "endpoints": {
            "authentication": "/api/auth",
            "employee": "/api/employee",
            "employer": "/api/employer",
            "matching": "/api/matching",
            "admin": "/api/admin"
        }
    }


@app.get("/employer-dashboard")
async def employer_dashboard():
    """Serve the employer dashboard HTML file."""
    dashboard_path = os.path.join(os.getcwd(), "employer_dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return JSONResponse(
            status_code=404,
            content={"detail": "Employer dashboard not found"}
        )


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check AI services status
    ai_status = "unknown"
    try:
        from app.services import get_service_status
        service_status = get_service_status()
        ai_status = service_status
    except Exception as e:
        ai_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.app_version,
        "ai_services": ai_status
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )