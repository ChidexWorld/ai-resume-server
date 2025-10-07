# AI-Powered Employee-Employer Matching Platform - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Backend Documentation](#backend-documentation)
6. [Frontend Documentation](#frontend-documentation)
7. [AI/ML Components](#aiml-components)
8. [Database Schema](#database-schema)
9. [API Reference](#api-reference)
10. [Setup & Installation](#setup--installation)
11. [Configuration](#configuration)
12. [User Workflows](#user-workflows)
13. [Security & Authentication](#security--authentication)
14. [Deployment Guide](#deployment-guide)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)
17. [Future Enhancements](#future-enhancements)

---

## Project Overview

### What is this System?

The AI-Powered Employee-Employer Matching Platform is a comprehensive full-stack web application that revolutionizes the job hiring process by leveraging artificial intelligence to match job seekers with employers based on skills, experience, education, and communication abilities.

### Core Purpose

- **For Employees**: Upload resumes and voice recordings to create comprehensive profiles, discover matching job opportunities, and apply to positions with AI-enhanced applications
- **For Employers**: Post job openings with detailed requirements, receive AI-scored candidate matches, and streamline the hiring process
- **For the System**: Utilize advanced AI/ML models to analyze resumes, assess communication skills via voice analysis, and provide intelligent matching scores

### Key Features

#### 🧠 **Intelligent Resume Analysis**
- Multi-format support (PDF, DOCX, TXT)
- Automatic extraction of skills, experience, education, certifications
- Industry-specific keyword matching
- Contact information extraction
- Job title and achievement recognition
- PyResParser integration for enhanced accuracy

#### 🎤 **Voice Communication Assessment**
- OpenAI Whisper-based speech-to-text transcription
- Communication quality scoring (clarity, confidence, fluency, vocabulary)
- Automatic resume creation from voice recordings
- Support for multiple audio formats (WAV, MP3, M4A, FLAC, OGG)

#### 🎯 **Smart Job Matching Algorithm**
- Multi-dimensional scoring system (skills, experience, education, communication)
- Customizable matching weights per job posting
- Semantic similarity analysis using sentence transformers
- Minimum score thresholds for quality control
- Detailed match breakdowns with strengths and improvement areas

#### 👥 **Dual User System**
- **Employee Portal**: Profile management, job search, application tracking, skill assessments
- **Employer Portal**: Job posting management, candidate search, application review, analytics
- **Admin Portal**: System oversight and user management

#### 📊 **Comprehensive Analytics**
- Match score breakdowns
- Skills gap analysis
- Application status tracking
- Employer dashboard with candidate metrics
- Employee dashboard with job recommendations

### System Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REGISTRATION                         │
│  Employees & Employers register with role-specific information  │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────▼─────────┐              ┌───────────▼──────────┐
│  EMPLOYEE FLOW    │              │   EMPLOYER FLOW      │
├───────────────────┤              ├──────────────────────┤
│ 1. Upload Resume  │              │ 1. Create Job Post   │
│ 2. Upload Voice   │              │ 2. Set Requirements  │
│ 3. AI Analysis    │              │ 3. Set Match Weights │
│ 4. Profile Created│              │ 4. Post Job          │
└─────────┬─────────┘              └───────────┬──────────┘
          │                                    │
          │         ┌──────────────────┐       │
          └────────►│  AI MATCHING     │◄──────┘
                    │  ENGINE          │
                    ├──────────────────┤
                    │ • Skills Match   │
                    │ • Experience     │
                    │ • Education      │
                    │ • Communication  │
                    │ • Weighted Score │
                    └────────┬─────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────▼─────────┐              ┌───────────▼──────────┐
│ Job Recommendations│              │Candidate Matches     │
│ for Employees      │              │for Employers         │
├────────────────────┤              ├──────────────────────┤
│ • Browse Matches   │              │ • Review Candidates  │
│ • View Details     │              │ • View Match Details │
│ • Apply to Jobs    │              │ • Shortlist/Reject   │
└────────────────────┘              └──────────────────────┘
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│  React 19 + TypeScript + Vite + TailwindCSS + Zustand          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Employee   │  │   Employer   │  │    Admin     │         │
│  │     App      │  │     App      │  │     App      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API (Axios)
┌──────────────────────────▼──────────────────────────────────────┐
│                        API GATEWAY LAYER                         │
│              FastAPI + CORS + JWT Authentication                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     Auth     │  │   Employee   │  │   Employer   │         │
│  │    Router    │  │    Router    │  │    Router    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   Matching   │  │    Admin     │                            │
│  │    Router    │  │    Router    │                            │
│  └──────────────┘  └──────────────┘                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                        │
│                         (Services)                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │              AI Service (Main Coordinator)         │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│         │
│  │  │   Resume     │  │    Voice     │  │   Job    ││         │
│  │  │   Analyzer   │  │   Analyzer   │  │  Matcher ││         │
│  │  └──────────────┘  └──────────────┘  └──────────┘│         │
│  └────────────────────────────────────────────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     Auth     │  │     File     │  │   Dataset    │         │
│  │   Service    │  │   Service    │  │   Manager    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                       DATA ACCESS LAYER                          │
│                   SQLAlchemy ORM + MySQL                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Users     │  │  Job Posts   │  │   Resumes    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Voice     │  │Applications  │  │ Job Matches  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                        DATABASE LAYER                            │
│                         MySQL 8.0+                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      AI/ML MODELS LAYER                          │
│  • OpenAI Whisper (Speech-to-Text)                              │
│  • Sentence Transformers (Semantic Similarity)                   │
│  • PyResParser (Resume Parsing - Optional)                       │
│  • spaCy NLP Models (Named Entity Recognition)                   │
│  • Custom Pattern Matching (Skills, Education, Experience)       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      FILE STORAGE LAYER                          │
│  uploads/                                                        │
│    ├── resumes/    (PDF, DOCX, TXT files)                       │
│    └── voice/      (Audio files)                                │
└──────────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

#### 1. **Factory Pattern**
- `AIServiceFactory` creates different implementations of AI services
- Allows switching between simple, original, lightweight, and enhanced analyzers

#### 2. **Singleton Pattern**
- Global instances for AI services to prevent multiple model loads
- Database connection pooling

#### 3. **Repository Pattern**
- SQLAlchemy models act as repositories for data access
- Abstraction between business logic and database operations

#### 4. **Dependency Injection**
- FastAPI's dependency injection for database sessions, authentication
- Makes testing and modularity easier

#### 5. **Lazy Loading**
- AI models loaded on-demand to optimize memory usage
- Whisper and SentenceTransformer models only initialized when needed

#### 6. **MVC (Model-View-Controller)**
- **Models**: SQLAlchemy database models
- **Views**: React components
- **Controllers**: FastAPI routers + services

---

## Technology Stack

### Backend Stack

#### **Core Framework**
- **FastAPI 0.104.1**: Modern, high-performance web framework
  - Automatic OpenAPI documentation
  - Built-in request validation with Pydantic
  - Async support
  - Type hints support

#### **Database**
- **MySQL 8.0+**: Relational database
- **SQLAlchemy 2.0.23**: ORM for database operations
- **PyMySQL 1.1.0**: MySQL connector
- **Alembic 1.12.1**: Database migration tool

#### **Authentication & Security**
- **python-jose[cryptography] 3.3.0**: JWT token handling
- **passlib 1.7.4**: Password hashing
- **bcrypt 4.0.1**: Secure password hashing algorithm

#### **AI/ML Libraries**
- **openai-whisper 20231117**: Speech-to-text transcription
- **PyTorch 2.2.0+cpu**: Deep learning framework
- **transformers 4.35.0**: Hugging Face transformers
- **sentence-transformers 2.2.2**: Semantic text similarity
- **scikit-learn >=1.3.2**: Machine learning utilities
- **numpy >=1.26.0**: Numerical computing
- **pandas 2.0.3**: Data manipulation

#### **NLP & Resume Parsing**
- **pyresparser 1.0.6**: Resume parsing library
- **spaCy 3.7.2**: NLP library for entity recognition
- **nltk 3.8.1**: Natural language toolkit

#### **Document Processing**
- **PyPDF2 3.0.1**: PDF text extraction
- **pdfplumber 0.9.0**: Advanced PDF parsing
- **python-docx 1.0.1**: DOCX file processing

#### **Server & Runtime**
- **uvicorn[standard] 0.24.0**: ASGI server
- **python-dotenv 1.0.0**: Environment variable management
- **python-multipart 0.0.6**: File upload handling
- **aiofiles 23.2.0**: Async file operations

### Frontend Stack

#### **Core Framework**
- **React 19.1.1**: UI library
- **TypeScript 5.8.3**: Type-safe JavaScript
- **Vite 7.1.2**: Build tool and dev server

#### **Routing & State Management**
- **react-router-dom 7.9.1**: Client-side routing
- **zustand 5.0.8**: Lightweight state management
- **@tanstack/react-query 5.89.0**: Server state management

#### **UI & Styling**
- **TailwindCSS 3.4.17**: Utility-first CSS framework
- **framer-motion 12.23.13**: Animation library
- **lucide-react 0.544.0**: Icon library
- **react-hot-toast 2.6.0**: Toast notifications

#### **Forms & Data Visualization**
- **react-hook-form 7.62.0**: Form management
- **@hookform/resolvers 5.2.2**: Form validation
- **yup 1.7.0**: Schema validation
- **recharts 3.2.1**: Charting library

#### **HTTP Client**
- **axios 1.12.2**: Promise-based HTTP client

#### **Development Tools**
- **ESLint 9.33.0**: Code linting
- **TypeScript ESLint**: TypeScript linting
- **PostCSS 8.5.6**: CSS transformation
- **Autoprefixer 10.4.21**: CSS vendor prefixes

### Development & Testing

- **pytest 7.4.3**: Python testing framework
- **pytest-asyncio 0.21.1**: Async test support
- **httpx 0.25.2**: HTTP client for testing

### System Requirements

#### **Minimum**
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- 4GB RAM
- 2GB storage

#### **Recommended**
- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- 8GB RAM
- 5GB storage (for AI models)

---

## Project Structure

### Complete Directory Tree

```
ai resume/
│
├── ai-resume-server/                    # Backend FastAPI Application
│   ├── app/
│   │   ├── models/                      # SQLAlchemy Database Models
│   │   │   ├── __init__.py             # Model exports
│   │   │   ├── user.py                 # User model (employees & employers)
│   │   │   ├── job_posting.py          # Job posting model
│   │   │   ├── resume.py               # Resume analysis model
│   │   │   ├── voice_analysis.py       # Voice analysis model
│   │   │   └── application.py          # Application tracking model
│   │   │
│   │   ├── routers/                     # FastAPI Route Handlers
│   │   │   ├── __init__.py             # Router exports
│   │   │   ├── auth.py                 # Authentication endpoints
│   │   │   ├── employee.py             # Employee-specific endpoints
│   │   │   ├── employer.py             # Employer-specific endpoints
│   │   │   ├── matching.py             # AI matching endpoints
│   │   │   └── admin.py                # Admin endpoints
│   │   │
│   │   ├── services/                    # Business Logic Layer
│   │   │   ├── __init__.py             # Service exports
│   │   │   ├── ai_service.py           # Main AI coordinator
│   │   │   ├── ai_service_factory.py   # Service factory pattern
│   │   │   ├── resume_analyzer.py      # Resume text/file analysis
│   │   │   ├── voice_analyzer.py       # Audio processing & transcription
│   │   │   ├── job_matcher.py          # Job-resume matching
│   │   │   ├── name_extractor.py       # Name extraction utilities
│   │   │   ├── auth_service.py         # Authentication service
│   │   │   ├── file_service.py         # File handling service
│   │   │   ├── dataset_manager.py      # Industry datasets management
│   │   │   └── datasets/               # JSON datasets
│   │   │       ├── skills.json         # Skills database
│   │   │       ├── industries.json     # Industry definitions
│   │   │       ├── certifications.json # Certification database
│   │   │       ├── job_titles.json     # Job title patterns
│   │   │       └── education_keywords.json
│   │   │
│   │   ├── schemas/                     # Pydantic Validation Schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # Authentication schemas
│   │   │   ├── employee.py             # Employee schemas
│   │   │   ├── employer.py             # Employer schemas
│   │   │   ├── matching.py             # Matching schemas
│   │   │   └── admin.py                # Admin schemas
│   │   │
│   │   ├── config.py                    # Application configuration
│   │   ├── database.py                  # Database connection setup
│   │   └── __init__.py
│   │
│   ├── uploads/                         # File Storage Directory
│   │   ├── resumes/                     # Uploaded resume files
│   │   └── voice/                       # Uploaded audio files
│   │
│   ├── nltk_data/                       # NLTK data files
│   │   ├── tokenizers/punkt/
│   │   └── corpora/stopwords/
│   │
│   ├── datasets/                        # Root-level datasets (backup)
│   │   ├── skills.json
│   │   ├── industries.json
│   │   ├── certifications.json
│   │   ├── job_titles.json
│   │   └── education_keywords.json
│   │
│   ├── main.py                          # FastAPI application entry point
│   ├── setup_nltk.py                    # NLTK setup script
│   ├── requirements-dev.txt             # Python dependencies
│   ├── .env.example                     # Environment template
│   ├── .env                             # Environment variables (gitignored)
│   ├── README.md                        # Backend documentation
│   ├── AI_SERVICE_DOCUMENTATION.md      # AI service detailed docs
│   ├── DATASET_MANAGER_DOCUMENTATION.md # Dataset manager docs
│   ├── test_ai_service.py               # AI service tests
│   ├── test_dataset_enhancements.py     # Dataset tests
│   └── venv/                            # Python virtual environment
│
├── ai-resume-frontend/                  # Frontend React Application
│   ├── src/
│   │   ├── components/                  # Reusable React Components
│   │   │   ├── auth/                    # Authentication components
│   │   │   │   ├── ProtectedRoute.tsx
│   │   │   │   └── LoginForm.tsx
│   │   │   ├── common/                  # Common UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   ├── dashboard/               # Dashboard components
│   │   │   │   ├── StatCard.tsx
│   │   │   │   ├── RecentActivity.tsx
│   │   │   │   └── QuickActions.tsx
│   │   │   ├── employer/                # Employer components
│   │   │   │   ├── JobPostForm.tsx
│   │   │   │   ├── CandidateCard.tsx
│   │   │   │   └── ApplicationList.tsx
│   │   │   ├── jobs/                    # Job components
│   │   │   │   ├── JobCard.tsx
│   │   │   │   ├── JobList.tsx
│   │   │   │   └── JobFilters.tsx
│   │   │   ├── matching/                # Matching components
│   │   │   │   ├── MatchScore.tsx
│   │   │   │   └── MatchDetails.tsx
│   │   │   └── resume/                  # Resume components
│   │   │       ├── ResumeUpload.tsx
│   │   │       ├── ResumeView.tsx
│   │   │       └── SkillsDisplay.tsx
│   │   │
│   │   ├── pages/                       # Page Components
│   │   │   ├── auth/                    # Auth pages
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   └── RegisterPage.tsx
│   │   │   ├── employee/                # Employee pages
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── ResumePage.tsx
│   │   │   │   ├── JobsPage.tsx
│   │   │   │   ├── JobDetailsPage.tsx
│   │   │   │   ├── JobApplicationPage.tsx
│   │   │   │   ├── ApplicationsPage.tsx
│   │   │   │   ├── AssessmentsPage.tsx
│   │   │   │   ├── ProfilePage.tsx
│   │   │   │   ├── SkillsAnalysisPage.tsx
│   │   │   │   ├── SettingsPage.tsx
│   │   │   │   └── JobMatches.tsx
│   │   │   ├── employer/                # Employer pages
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── SearchPage.tsx
│   │   │   │   ├── InterviewsPage.tsx
│   │   │   │   ├── JobPostingsPage.tsx
│   │   │   │   └── ProfilePage.tsx
│   │   │   ├── admin/                   # Admin pages
│   │   │   │   └── Dashboard.tsx
│   │   │   └── LandingPage.tsx          # Public landing page
│   │   │
│   │   ├── layouts/                     # Layout Components
│   │   │   └── DashboardLayout.tsx
│   │   │
│   │   ├── store/                       # Zustand State Management
│   │   │   ├── authStore.ts            # Authentication state
│   │   │   └── themeStore.ts           # Theme state
│   │   │
│   │   ├── services/                    # API Services
│   │   │   └── api.ts                  # Axios instance & API calls
│   │   │
│   │   ├── types/                       # TypeScript Type Definitions
│   │   │   └── index.ts
│   │   │
│   │   ├── hooks/                       # Custom React Hooks
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── utils/                       # Utility Functions
│   │   │   └── formatters.ts
│   │   │
│   │   ├── App.tsx                      # Main App component
│   │   ├── App.css                      # App styles
│   │   ├── main.tsx                     # React entry point
│   │   └── index.css                    # Global styles
│   │
│   ├── public/                          # Static Assets
│   │   └── index.html
│   │
│   ├── node_modules/                    # NPM packages
│   ├── package.json                     # NPM dependencies
│   ├── package-lock.json                # NPM lock file
│   ├── tsconfig.json                    # TypeScript config
│   ├── vite.config.ts                   # Vite config
│   ├── tailwind.config.js               # TailwindCSS config
│   ├── postcss.config.js                # PostCSS config
│   └── eslint.config.js                 # ESLint config
│
├── .claude/                             # Claude Code settings
│   └── settings.local.json
│
├── datasets/                            # Shared datasets
├── PROJECT_DOCUMENTATION.md             # This file
└── README.md                            # Project root readme
```

---

## Backend Documentation

### Models (Database Layer)

#### 1. **User Model** (`app/models/user.py`)

Stores both employee and employer accounts with role-specific fields.

**Fields:**
- `id` (Integer, Primary Key)
- `email` (String, Unique, Indexed)
- `password_hash` (String)
- `first_name` (String)
- `last_name` (String)
- `user_type` (Enum: employee, employer, admin)
- `phone` (String, Optional)
- `is_active` (Boolean)
- `is_verified` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Employer-specific fields:**
- `company_name` (String)
- `company_website` (String)
- `company_size` (String)
- `company_description` (Text)

**Relationships:**
- One-to-Many with `Resume` (for employees)
- One-to-Many with `VoiceAnalysis` (for employees)
- One-to-Many with `JobPosting` (for employers)
- One-to-Many with `Application`

#### 2. **Job Posting Model** (`app/models/job_posting.py`)

Stores employer job postings with detailed requirements.

**Fields:**
- `id` (Integer, Primary Key)
- `employer_id` (Foreign Key → User)
- `title` (String)
- `description` (Text)
- `location` (String)
- `remote_allowed` (Boolean)
- `job_type` (Enum: full_time, part_time, contract, internship)
- `experience_level` (Enum: entry, mid, senior, executive)
- `salary_min` (Integer, in cents)
- `salary_max` (Integer, in cents)
- `status` (Enum: draft, active, paused, closed, filled)
- `required_skills` (JSON Array)
- `preferred_skills` (JSON Array)
- `required_experience` (JSON Object)
- `required_education` (JSON Object)
- `communication_requirements` (JSON Object)
- `matching_weights` (JSON Object)
- `minimum_match_score` (Integer)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `expires_at` (DateTime)

**Relationships:**
- Many-to-One with `User` (employer)
- One-to-Many with `Application`
- One-to-Many with `JobMatch`

#### 3. **Resume Model** (`app/models/resume.py`)

Stores uploaded resumes and AI analysis results.

**Fields:**
- `id` (Integer, Primary Key)
- `employee_id` (Foreign Key → User)
- `file_path` (String)
- `file_name` (String)
- `file_size` (Integer)
- `mime_type` (String)
- `status` (Enum: pending, processing, completed, failed)
- `analysis_results` (JSON Object)
  - Contains: skills, experience, education, certifications, etc.
- `extracted_text` (Text)
- `upload_date` (DateTime)
- `analyzed_at` (DateTime)
- `is_primary` (Boolean)

**Relationships:**
- Many-to-One with `User` (employee)
- One-to-Many with `Application`

#### 4. **Voice Analysis Model** (`app/models/voice_analysis.py`)

Stores voice recordings and communication assessments.

**Fields:**
- `id` (Integer, Primary Key)
- `employee_id` (Foreign Key → User)
- `file_path` (String)
- `file_name` (String)
- `file_size` (Integer)
- `duration` (Integer, seconds)
- `status` (Enum: pending, processing, completed, failed)
- `transcript` (Text)
- `transcription_confidence` (Float)
- `communication_scores` (JSON Object)
  - clarity_score, confidence_score, fluency_score, vocabulary_score
- `analyzed_at` (DateTime)
- `created_at` (DateTime)

**Relationships:**
- Many-to-One with `User` (employee)
- One-to-Many with `Application`

#### 5. **Application Model** (`app/models/application.py`)

Tracks job applications from employees to job postings.

**Fields:**
- `id` (Integer, Primary Key)
- `employee_id` (Foreign Key → User)
- `job_id` (Foreign Key → JobPosting)
- `resume_id` (Foreign Key → Resume)
- `voice_analysis_id` (Foreign Key → VoiceAnalysis, Optional)
- `cover_letter` (Text)
- `status` (Enum: pending, reviewed, shortlisted, interview, offered, rejected, accepted, declined)
- `match_score` (Integer, 0-100)
- `match_details` (JSON Object)
- `applied_at` (DateTime)
- `updated_at` (DateTime)
- `employer_notes` (Text)

**Relationships:**
- Many-to-One with `User` (employee)
- Many-to-One with `JobPosting`
- Many-to-One with `Resume`
- Many-to-One with `VoiceAnalysis`

#### 6. **Job Match Model** (Implied from matching router)

Stores AI-generated proactive job-employee matches.

**Fields:**
- `id` (Integer, Primary Key)
- `employee_id` (Foreign Key → User)
- `job_id` (Foreign Key → JobPosting)
- `match_score` (Integer, 0-100)
- `match_details` (JSON Object)
  - skills_score, experience_score, education_score, communication_score
  - matching_skills, missing_skills, strengths, concerns, recommendations
- `created_at` (DateTime)
- `viewed_by_employee` (Boolean)
- `viewed_by_employer` (Boolean)

### Routers (API Endpoints)

#### 1. **Authentication Router** (`app/routers/auth.py`)

**Endpoints:**

```
POST /api/auth/register
- Register new user (employee or employer)
- Body: { email, password, first_name, last_name, user_type, phone, company_name?, ... }
- Returns: { user, access_token }

POST /api/auth/login
- Authenticate user and get token
- Body: { email, password }
- Returns: { user, access_token, token_type: "bearer" }

POST /api/auth/logout
- Logout user (client-side token removal)
- Requires: Bearer token
- Returns: { message }

GET /api/auth/me
- Get current user profile
- Requires: Bearer token
- Returns: User object

PUT /api/auth/me
- Update current user profile
- Requires: Bearer token
- Body: { first_name?, last_name?, phone?, ... }
- Returns: Updated user object
```

#### 2. **Employee Router** (`app/routers/employee.py`)

**Endpoints:**

```
POST /api/employee/resume/upload
- Upload resume file (PDF, DOCX, TXT)
- Requires: Bearer token (employee)
- Content-Type: multipart/form-data
- Body: file
- Returns: { resume_id, status, analysis_results }

GET /api/employee/resume
- Get all resumes for current employee
- Requires: Bearer token (employee)
- Returns: Array of resume objects

GET /api/employee/resume/{resume_id}
- Get specific resume details
- Requires: Bearer token (employee)
- Returns: Resume object with analysis

DELETE /api/employee/resume/{resume_id}
- Delete resume
- Requires: Bearer token (employee)
- Returns: { message }

POST /api/employee/voice/upload
- Upload voice recording (WAV, MP3, M4A, etc.)
- Requires: Bearer token (employee)
- Content-Type: multipart/form-data
- Body: file
- Returns: { voice_id, status, transcript, communication_scores }

GET /api/employee/voice
- Get all voice analyses
- Requires: Bearer token (employee)
- Returns: Array of voice analysis objects

POST /api/employee/apply/{job_id}
- Apply to job posting
- Requires: Bearer token (employee)
- Body: { resume_id, voice_analysis_id?, cover_letter }
- Returns: Application object with match score

GET /api/employee/applications
- Get all applications
- Requires: Bearer token (employee)
- Query: ?status=pending&limit=20
- Returns: Array of application objects

GET /api/employee/applications/{application_id}
- Get specific application details
- Requires: Bearer token (employee)
- Returns: Application object with job and match details
```

#### 3. **Employer Router** (`app/routers/employer.py`)

**Endpoints:**

```
POST /api/employer/jobs
- Create new job posting
- Requires: Bearer token (employer)
- Body: { title, description, location, required_skills, ... }
- Returns: JobPosting object

GET /api/employer/jobs
- Get all job postings for employer
- Requires: Bearer token (employer)
- Query: ?status=active&limit=50
- Returns: Array of job posting objects

GET /api/employer/jobs/{job_id}
- Get specific job posting
- Requires: Bearer token (employer)
- Returns: JobPosting object

PUT /api/employer/jobs/{job_id}
- Update job posting
- Requires: Bearer token (employer)
- Body: { title?, description?, status?, ... }
- Returns: Updated job posting

DELETE /api/employer/jobs/{job_id}
- Delete/close job posting
- Requires: Bearer token (employer)
- Returns: { message }

GET /api/employer/jobs/{job_id}/applications
- Get all applications for job
- Requires: Bearer token (employer)
- Query: ?status=pending&min_score=70
- Returns: Array of applications with employee details

PUT /api/employer/applications/{application_id}
- Update application status
- Requires: Bearer token (employer)
- Body: { status, employer_notes? }
- Returns: Updated application

GET /api/employer/applications/{application_id}
- Get detailed application view
- Requires: Bearer token (employer)
- Returns: Application with full employee profile, resume, voice analysis

GET /api/employer/analytics
- Get employer analytics dashboard data
- Requires: Bearer token (employer)
- Returns: { total_jobs, total_applications, avg_match_score, ... }
```

#### 4. **Matching Router** (`app/routers/matching.py`)

**Endpoints:**

```
GET /api/matching/jobs
- Get job matches for employee
- Requires: Bearer token (employee)
- Query: ?limit=20&min_score=70
- Returns: Array of job postings with match scores

GET /api/matching/candidates/{job_id}
- Get candidate matches for job
- Requires: Bearer token (employer)
- Query: ?limit=50&min_score=70
- Returns: Array of employees with match scores and details

POST /api/matching/calculate
- Calculate match score for specific employee-job pair
- Requires: Bearer token
- Body: { employee_id, job_id }
- Returns: { match_score, match_details }

GET /api/matching/recommendations
- Get AI recommendations based on user type
- Requires: Bearer token
- Returns: Job recommendations for employees, candidate recommendations for employers
```

#### 5. **Admin Router** (`app/routers/admin.py`)

**Endpoints:**

```
GET /api/admin/users
- Get all users
- Requires: Bearer token (admin)
- Query: ?user_type=employee&limit=100
- Returns: Array of user objects

GET /api/admin/stats
- Get system-wide statistics
- Requires: Bearer token (admin)
- Returns: { total_users, total_jobs, total_applications, ... }

PUT /api/admin/users/{user_id}
- Update user (activate/deactivate)
- Requires: Bearer token (admin)
- Body: { is_active?, is_verified? }
- Returns: Updated user

DELETE /api/admin/users/{user_id}
- Delete user
- Requires: Bearer token (admin)
- Returns: { message }
```

### Services (Business Logic)

#### 1. **AI Service** (`app/services/ai_service.py`)

Main coordinator for all AI operations.

**Methods:**
- `extract_text_from_file(file_path, mime_type)` - Extract text from PDF/DOCX/TXT
- `analyze_resume(text, target_industry)` - Analyze resume text
- `analyze_resume_from_text(text, target_industry)` - Sync wrapper
- `analyze_resume_from_text_async(text, target_industry)` - Async version
- `analyze_voice_resume(audio_file_path)` - Complete voice analysis pipeline
- `transcribe_audio(file_path)` - Audio to text transcription
- `match_resume_to_job(resume_data, job_requirements)` - Calculate job match
- `get_resume_summary(resume_data)` - Quick resume summary

#### 2. **Resume Analyzer** (`app/services/resume_analyzer.py`)

Handles resume parsing and analysis.

**Methods:**
- `extract_text_from_file(file_path, mime_type)` - File text extraction
- `analyze_resume(text, target_industry)` - Main analysis
- `analyze_resume_from_file(file_path, target_industry)` - File-based analysis
- `_extract_contact_info(text)` - Extract name, email, phone
- `_extract_enhanced_skills(text)` - Extract skills using datasets
- `extract_global_experience(text)` - Extract experience with years calculation
- `_extract_enhanced_education(text)` - Extract education
- `_extract_enhanced_certifications(text)` - Extract certifications
- `_extract_enhanced_job_titles(text, industry)` - Extract job titles
- `_extract_achievements(text)` - Extract accomplishments
- `_analyze_with_pyresparser(file_path, target_industry)` - PyResParser integration

#### 3. **Voice Analyzer** (`app/services/voice_analyzer.py`)

Processes audio files and analyzes communication.

**Methods:**
- `transcribe_audio(file_path)` - Whisper transcription
- `analyze_voice_resume(audio_file_path)` - Complete analysis
- `_estimate_confidence(transcript)` - Confidence scoring

#### 4. **Job Matcher** (`app/services/job_matcher.py`)

Matches resumes to job requirements.

**Methods:**
- `match_resume_to_job(resume_data, job_requirements)` - Main matching
- `_calculate_skills_match(resume_skills, required_skills, preferred_skills)` - Skills scoring
- `_calculate_experience_match(resume_experience, job_requirements)` - Experience scoring
- `_generate_match_details(...)` - Detailed analysis generation

#### 5. **Dataset Manager** (`app/services/dataset_manager.py`)

Manages industry-specific datasets for extraction.

**Methods:**
- `load_datasets()` - Load all JSON datasets
- `extract_skills(text, industry)` - Extract skills from text
- `extract_job_titles(text, industry)` - Extract job titles
- `extract_certifications(text)` - Extract certifications
- `detect_industry(text)` - Detect target industry
- `get_education_keywords()` - Get education patterns

#### 6. **Auth Service** (`app/services/auth_service.py`)

Handles authentication and authorization.

**Methods:**
- `create_access_token(data, expires_delta)` - Create JWT token
- `verify_password(plain_password, hashed_password)` - Password verification
- `get_password_hash(password)` - Hash password
- `get_current_user(token, db)` - Extract user from token

#### 7. **File Service** (`app/services/file_service.py`)

Manages file uploads and storage.

**Methods:**
- `save_uploaded_file(file, upload_type)` - Save file to disk
- `validate_file(file, allowed_extensions, max_size)` - File validation
- `delete_file(file_path)` - Delete file
- `get_file_info(file)` - Get file metadata

---

## Frontend Documentation

### Pages

#### **Authentication Pages** (`src/pages/auth/`)

1. **LoginPage.tsx**
   - User login form
   - Email and password validation
   - Redirect to dashboard on success
   - Link to registration

2. **RegisterPage.tsx**
   - User registration form
   - Role selection (employee/employer)
   - Conditional fields based on role
   - Form validation with Yup
   - Company information for employers

#### **Employee Pages** (`src/pages/employee/`)

1. **Dashboard.tsx**
   - Overview statistics
   - Recent job matches
   - Application status
   - Quick actions (upload resume, browse jobs)

2. **ResumePage.tsx**
   - Resume upload form
   - List of uploaded resumes
   - Resume analysis results display
   - Primary resume selection
   - Delete resume functionality

3. **JobsPage.tsx**
   - Browse all available jobs
   - Filter by location, type, experience level
   - Search functionality
   - Job cards with match scores
   - Pagination

4. **JobDetailsPage.tsx**
   - Detailed job information
   - Requirements breakdown
   - Match score and analysis
   - Apply button
   - Employer information

5. **JobApplicationPage.tsx**
   - Application form
   - Resume selection
   - Voice analysis selection (optional)
   - Cover letter editor
   - Submit application

6. **ApplicationsPage.tsx**
   - List of all applications
   - Status tracking
   - Filter by status
   - Application details modal

7. **AssessmentsPage.tsx**
   - Voice recordings list
   - Upload voice recording
   - Communication scores display
   - Transcript view

8. **JobMatches.tsx**
   - AI-recommended jobs
   - Match score visualization
   - Match details breakdown
   - Quick apply

9. **SkillsAnalysisPage.tsx**
   - Skills breakdown from resume
   - Skills gap analysis
   - Skill recommendations
   - Industry trends

10. **ProfilePage.tsx**
    - View/edit personal information
    - Account settings
    - Contact information

11. **SettingsPage.tsx**
    - Account preferences
    - Notification settings
    - Privacy settings
    - Theme toggle

#### **Employer Pages** (`src/pages/employer/`)

1. **Dashboard.tsx**
   - Posted jobs overview
   - Application statistics
   - Recent applicants
   - Analytics charts (with Recharts)

2. **JobPostingsPage.tsx**
   - Create new job posting
   - List of all posted jobs
   - Edit job postings
   - Job status management (active/paused/closed)
   - Delete jobs

3. **SearchPage.tsx**
   - Search for candidates
   - Filter by skills, experience, education
   - Candidate cards with match scores
   - View candidate profiles

4. **InterviewsPage.tsx**
   - Schedule interviews
   - Interview tracking
   - Candidate shortlisting
   - Notes and feedback

5. **ProfilePage.tsx**
   - Company information
   - Edit company profile
   - Contact details

#### **Admin Pages** (`src/pages/admin/`)

1. **Dashboard.tsx**
   - System-wide statistics
   - User management
   - Job management
   - Analytics

#### **Public Pages**

1. **LandingPage.tsx**
   - Marketing content
   - Feature highlights
   - Call-to-action (Register/Login)
   - How it works section

### Components

#### **Authentication Components** (`src/components/auth/`)

1. **ProtectedRoute.tsx**
   - Route guard for authenticated users
   - Role-based access control
   - Redirect to login if not authenticated

#### **Common Components** (`src/components/common/`)

1. **Button.tsx** - Reusable button with variants
2. **Card.tsx** - Container component
3. **Input.tsx** - Form input with validation
4. **Modal.tsx** - Modal dialog
5. **LoadingSpinner.tsx** - Loading indicator

#### **Dashboard Components** (`src/components/dashboard/`)

1. **StatCard.tsx** - Statistics display card
2. **RecentActivity.tsx** - Activity feed
3. **QuickActions.tsx** - Quick action buttons

#### **Job Components** (`src/components/jobs/`)

1. **JobCard.tsx** - Job listing card
2. **JobList.tsx** - Grid of job cards
3. **JobFilters.tsx** - Filter controls

#### **Matching Components** (`src/components/matching/`)

1. **MatchScore.tsx** - Match score visualization
2. **MatchDetails.tsx** - Detailed match breakdown

#### **Resume Components** (`src/components/resume/`)

1. **ResumeUpload.tsx** - File upload component
2. **ResumeView.tsx** - Resume display
3. **SkillsDisplay.tsx** - Skills visualization

### State Management

#### **Zustand Stores** (`src/store/`)

1. **authStore.ts**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
}
```

2. **themeStore.ts**
```typescript
interface ThemeState {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

### Services

#### **API Service** (`src/services/api.ts`)

Axios instance with interceptors for authentication and error handling.

**Configuration:**
- Base URL from environment variable
- Auto-attach JWT token to requests
- Response error handling
- Request/response logging (dev mode)

**Methods:**
- `api.get(url, config)`
- `api.post(url, data, config)`
- `api.put(url, data, config)`
- `api.delete(url, config)`

**Endpoints exported:**
- Auth: `login`, `register`, `logout`, `getMe`
- Employee: `uploadResume`, `getResumes`, `uploadVoice`, `applyJob`
- Employer: `createJob`, `getJobs`, `getApplications`
- Matching: `getJobMatches`, `getCandidateMatches`

### Types

#### **TypeScript Interfaces** (`src/types/index.ts`)

```typescript
interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'employee' | 'employer' | 'admin';
  phone?: string;
  company_name?: string;
  company_website?: string;
  created_at: string;
}

interface JobPosting {
  id: number;
  employer_id: number;
  title: string;
  description: string;
  location: string;
  remote_allowed: boolean;
  job_type: 'full_time' | 'part_time' | 'contract' | 'internship';
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  salary_min?: number;
  salary_max?: number;
  status: 'draft' | 'active' | 'paused' | 'closed' | 'filled';
  required_skills: string[];
  preferred_skills: string[];
  created_at: string;
}

interface Resume {
  id: number;
  employee_id: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_results: ResumeAnalysis;
  upload_date: string;
  is_primary: boolean;
}

interface ResumeAnalysis {
  contact_info: {
    name: string;
    email: string;
    phone: string;
  };
  skills: {
    technical_skills: string[];
    soft_skills: string[];
    languages: string[];
  };
  experience: any[];
  education: string[];
  certifications: string[];
  total_experience_years: number;
  experience_level: string;
}

interface Application {
  id: number;
  employee_id: number;
  job_id: number;
  resume_id: number;
  voice_analysis_id?: number;
  cover_letter: string;
  status: 'pending' | 'reviewed' | 'shortlisted' | 'interview' | 'offered' | 'rejected' | 'accepted' | 'declined';
  match_score: number;
  match_details: MatchDetails;
  applied_at: string;
}

interface MatchDetails {
  skills_score: number;
  experience_score: number;
  education_score: number;
  communication_score: number;
  matching_skills: string[];
  missing_skills: string[];
  strengths: string[];
  concerns: string[];
  recommendations: string[];
}
```

---

## AI/ML Components

### Overview

The AI/ML system consists of multiple specialized components working together:

```
User Upload (Resume/Voice)
         ↓
   File Service
         ↓
    AI Service (Coordinator)
         ↓
    ┌────┴────┐
    ↓         ↓
Resume      Voice
Analyzer    Analyzer
    ↓         ↓
 Extracted  Transcript
  Data       + Scores
    └────┬────┘
         ↓
   Database Storage
         ↓
   Job Matcher
         ↓
   Match Scores
```

### 1. Resume Analyzer

**Technology:** PyPDF2, python-docx, spaCy, pyresparser, custom regex

**Process:**
1. **File Extraction**: Extract text from PDF/DOCX/TXT
2. **Contact Extraction**: Name, email, phone via regex patterns
3. **Skills Extraction**: Match against 10,000+ skills database
4. **Experience Parsing**: Extract job positions with dates
5. **Education Extraction**: Degrees, institutions, fields
6. **Certification Matching**: 500+ known certifications
7. **Industry Detection**: Classify resume into industry categories

**Skills Database Categories:**
- Programming Languages (Python, Java, JavaScript, etc.)
- Frameworks (React, Django, Spring, etc.)
- Tools (Git, Docker, Kubernetes, etc.)
- Soft Skills (Leadership, Communication, etc.)
- Domain-Specific (Healthcare, Finance, etc.)

**Experience Calculation:**
- Parse date ranges (2020-2023, Jan 2020 - Present, etc.)
- Calculate total years
- Determine experience level (Entry/Mid/Senior/Executive)

### 2. Voice Analyzer

**Technology:** OpenAI Whisper, custom scoring algorithms

**Process:**
1. **Audio Loading**: Load audio file (WAV, MP3, M4A, FLAC)
2. **Transcription**: Whisper "base" model transcribes speech to text
3. **Confidence Estimation**: Based on word count, punctuation, word length
4. **Communication Scoring**:
   - Clarity: Speech clarity and enunciation
   - Confidence: Speech patterns and assertiveness
   - Fluency: Smoothness and coherence
   - Vocabulary: Word diversity and complexity
5. **Resume Creation**: Transcribed text analyzed as resume

**Whisper Model Sizes:**
- Tiny: Fastest, lowest accuracy
- Base: Balanced (used by default)
- Small: Better accuracy, slower
- Medium/Large: Production quality, requires more resources

### 3. Job Matcher

**Technology:** Sentence Transformers (all-MiniLM-L6-v2), custom algorithms

**Matching Algorithm:**

```python
overall_score = (
    skills_score * 0.6 +           # 60% weight
    experience_score * 0.4          # 40% weight
)

# Can be customized per job:
overall_score = (
    skills_score * weights['skills'] +
    experience_score * weights['experience'] +
    education_score * weights['education'] +
    communication_score * weights['communication']
)
```

**Skills Matching:**
- Required skills: 80% weight
- Preferred skills: 20% weight
- Semantic similarity for partial matches
- Bonus for exceeding requirements

**Experience Matching:**
- Years of experience vs. minimum required
- Penalty for under-qualified (<70%)
- Bonus for over-qualified (up to 20%)

**Match Details Generated:**
- Matching skills (what candidate has)
- Missing skills (what candidate lacks)
- Strengths (high scores)
- Concerns (low scores)
- Recommendations (improvement suggestions)

### 4. Dataset Manager

**Purpose:** Centralized management of industry-specific data

**Datasets:**

1. **skills.json** (~10,000 entries)
   ```json
   {
     "technology": {
       "programming_languages": ["Python", "Java", ...],
       "frameworks": ["React", "Django", ...],
       "tools": ["Git", "Docker", ...]
     },
     "healthcare": { ... },
     "finance": { ... }
   }
   ```

2. **job_titles.json** (~2,000 entries)
   ```json
   {
     "technology": ["Software Engineer", "Data Scientist", ...],
     "healthcare": ["Registered Nurse", "Medical Doctor", ...],
     ...
   }
   ```

3. **certifications.json** (~500 entries)
   ```json
   [
     "AWS Certified Solutions Architect",
     "Certified Public Accountant (CPA)",
     "Project Management Professional (PMP)",
     ...
   ]
   ```

4. **industries.json**
   ```json
   [
     "technology",
     "healthcare",
     "finance",
     "education",
     "manufacturing",
     ...
   ]
   ```

5. **education_keywords.json**
   ```json
   {
     "degrees": ["Bachelor", "Master", "PhD", "MBA", ...],
     "fields": ["Computer Science", "Engineering", ...],
     "institutions": ["University", "College", "Institute", ...]
   }
   ```

### AI Service Factory

**Purpose:** Manage multiple AI service implementations

**Implementations:**

1. **Simple AI Service**: Basic regex-based extraction, fast
2. **Original AI Service**: Standard implementation with spaCy
3. **Lightweight AI Service**: Enhanced patterns, no heavy dependencies
4. **Enhanced AI Service**: Full featured with PyResParser and Kaggle datasets

**Usage:**
```python
from app.services.ai_service_factory import AIServiceFactory

# Create specific implementation
service = AIServiceFactory.create_service("enhanced")

# Or use environment variable
os.environ["AI_SERVICE_TYPE"] = "lightweight"
service = AIServiceFactory.create_service()
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│       Users         │
├─────────────────────┤
│ id (PK)            │
│ email              │◄────────┐
│ password_hash      │         │
│ user_type          │         │
│ first_name         │         │
│ last_name          │         │
│ phone              │         │
│ company_name       │         │
│ ...                │         │
└──────┬──────────────┘         │
       │                        │
       │ employee_id            │ employer_id
       │                        │
       ├────────────────────────┼──────────────┐
       │                        │              │
       │                        │              │
┌──────▼──────────┐   ┌─────────▼────────┐  ┌▼──────────────┐
│    Resumes      │   │   Job Postings   │  │ Applications  │
├─────────────────┤   ├──────────────────┤  ├───────────────┤
│ id (PK)        │   │ id (PK)         │  │ id (PK)       │
│ employee_id FK │   │ employer_id FK  │  │ employee_id FK│
│ file_path      │   │ title           │  │ job_id FK     │
│ analysis_results│   │ description     │  │ resume_id FK  │
│ status         │   │ required_skills │  │ voice_id FK   │
│ ...            │   │ status          │  │ status        │
└────────┬────────┘   │ ...             │  │ match_score   │
         │            └─────────┬────────┘  │ match_details │
         │                      │           └───────────────┘
         │                      │
         │                      │
┌────────▼────────┐   ┌─────────▼────────┐
│ Voice Analyses  │   │   Job Matches    │
├─────────────────┤   ├──────────────────┤
│ id (PK)        │   │ id (PK)         │
│ employee_id FK │   │ employee_id FK  │
│ transcript     │   │ job_id FK       │
│ comm_scores    │   │ match_score     │
│ status         │   │ match_details   │
│ ...            │   │ ...             │
└─────────────────┘   └──────────────────┘
```

### SQL Schema (Simplified)

```sql
-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('employee', 'employer', 'admin') NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    company_name VARCHAR(255),
    company_website VARCHAR(255),
    company_size VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_user_type (user_type)
);

-- Job postings table
CREATE TABLE job_postings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employer_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    remote_allowed BOOLEAN DEFAULT FALSE,
    job_type ENUM('full_time', 'part_time', 'contract', 'internship'),
    experience_level ENUM('entry', 'mid', 'senior', 'executive'),
    salary_min INT,
    salary_max INT,
    status ENUM('draft', 'active', 'paused', 'closed', 'filled') DEFAULT 'draft',
    required_skills JSON,
    preferred_skills JSON,
    required_experience JSON,
    required_education JSON,
    communication_requirements JSON,
    matching_weights JSON,
    minimum_match_score INT DEFAULT 70,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_employer (employer_id)
);

-- Resumes table
CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_size INT,
    mime_type VARCHAR(100),
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    analysis_results JSON,
    extracted_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id),
    INDEX idx_status (status)
);

-- Voice analyses table
CREATE TABLE voice_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_size INT,
    duration INT,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    transcript TEXT,
    transcription_confidence FLOAT,
    communication_scores JSON,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id)
);

-- Applications table
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    job_id INT NOT NULL,
    resume_id INT NOT NULL,
    voice_analysis_id INT,
    cover_letter TEXT,
    status ENUM('pending', 'reviewed', 'shortlisted', 'interview', 'offered', 'rejected', 'accepted', 'declined') DEFAULT 'pending',
    match_score INT,
    match_details JSON,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    employer_notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    FOREIGN KEY (voice_analysis_id) REFERENCES voice_analyses(id) ON DELETE SET NULL,
    UNIQUE KEY unique_application (employee_id, job_id),
    INDEX idx_employee (employee_id),
    INDEX idx_job (job_id),
    INDEX idx_status (status)
);

-- Job matches table (AI-generated)
CREATE TABLE job_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    job_id INT NOT NULL,
    match_score INT NOT NULL,
    match_details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewed_by_employee BOOLEAN DEFAULT FALSE,
    viewed_by_employer BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
    INDEX idx_employee (employee_id),
    INDEX idx_job (job_id),
    INDEX idx_score (match_score)
);
```

### Indexing Strategy

**Optimized Queries:**
- User lookups by email (unique index)
- Job filtering by status and employer
- Application filtering by employee, job, status
- Match lookups by score

**Composite Indexes:**
- (employee_id, job_id) for preventing duplicate applications
- (status, created_at) for filtering and sorting

---

## API Reference

### Authentication Flow

```
1. Register
POST /api/auth/register
→ User created in database
→ JWT token generated
→ Token returned to client

2. Login
POST /api/auth/login
→ Credentials verified
→ JWT token generated
→ Token returned to client

3. Authenticated Requests
GET /api/employee/resume
Header: Authorization: Bearer <token>
→ Token validated
→ User extracted from token
→ Request processed
→ Response returned

4. Logout
Client-side: Remove token from storage
```

### Request/Response Examples

#### **Register Employee**

**Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "employee",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "employee",
    "phone": "+1234567890",
    "is_active": true,
    "created_at": "2025-01-10T10:00:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### **Upload Resume**

**Request:**
```http
POST /api/employee/resume/upload
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

file: john_doe_resume.pdf (binary data)
```

**Response:**
```json
{
  "resume_id": 1,
  "status": "completed",
  "file_name": "john_doe_resume.pdf",
  "file_size": 524288,
  "analysis_results": {
    "contact_info": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890"
    },
    "skills": {
      "technical_skills": ["Python", "JavaScript", "React", "Django", "SQL"],
      "soft_skills": ["Leadership", "Communication", "Problem Solving"],
      "languages": ["English", "Spanish"]
    },
    "experience": [
      {
        "job_title": "Senior Software Engineer",
        "company": "Tech Corp",
        "duration": "2020-2023",
        "description": "Led development team..."
      }
    ],
    "education": [
      "Bachelor of Science in Computer Science - Stanford University (2016)"
    ],
    "certifications": [
      "AWS Certified Solutions Architect",
      "Certified Scrum Master"
    ],
    "total_experience_years": 7,
    "experience_level": "senior",
    "professional_summary": "Experienced software engineer with expertise in...",
    "achievements": [
      "Increased system performance by 40%",
      "Led team of 5 developers"
    ]
  },
  "upload_date": "2025-01-10T11:00:00",
  "analyzed_at": "2025-01-10T11:00:15"
}
```

#### **Create Job Posting**

**Request:**
```http
POST /api/employer/jobs
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Senior Full Stack Developer",
  "description": "We are seeking an experienced full stack developer...",
  "location": "San Francisco, CA",
  "remote_allowed": true,
  "job_type": "full_time",
  "experience_level": "senior",
  "salary_min": 12000000,
  "salary_max": 15000000,
  "required_skills": ["Python", "React", "PostgreSQL", "Docker"],
  "preferred_skills": ["Kubernetes", "AWS", "GraphQL"],
  "required_experience": {
    "min_years": 5,
    "areas": ["web development", "API design", "database design"]
  },
  "required_education": {
    "min_degree": "bachelor",
    "field": "computer science or related"
  },
  "communication_requirements": {
    "presentation_skills": true,
    "client_interaction": true,
    "min_communication_score": 75
  },
  "matching_weights": {
    "skills": 0.4,
    "experience": 0.35,
    "education": 0.15,
    "communication": 0.1
  },
  "minimum_match_score": 70
}
```

**Response:**
```json
{
  "id": 1,
  "employer_id": 2,
  "title": "Senior Full Stack Developer",
  "description": "We are seeking an experienced full stack developer...",
  "location": "San Francisco, CA",
  "remote_allowed": true,
  "job_type": "full_time",
  "experience_level": "senior",
  "salary_min": 12000000,
  "salary_max": 15000000,
  "status": "active",
  "required_skills": ["Python", "React", "PostgreSQL", "Docker"],
  "preferred_skills": ["Kubernetes", "AWS", "GraphQL"],
  "required_experience": { ... },
  "required_education": { ... },
  "communication_requirements": { ... },
  "matching_weights": { ... },
  "minimum_match_score": 70,
  "created_at": "2025-01-10T12:00:00",
  "updated_at": "2025-01-10T12:00:00"
}
```

#### **Get Job Matches for Employee**

**Request:**
```http
GET /api/matching/jobs?limit=10&min_score=75
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "job": {
      "id": 1,
      "title": "Senior Full Stack Developer",
      "description": "We are seeking...",
      "location": "San Francisco, CA",
      "remote_allowed": true,
      "job_type": "full_time",
      "experience_level": "senior",
      "salary_min": 12000000,
      "salary_max": 15000000,
      "required_skills": ["Python", "React", "PostgreSQL", "Docker"],
      "employer": {
        "company_name": "Tech Innovations Inc",
        "company_website": "https://techinnovations.com"
      }
    },
    "match_score": 87,
    "match_details": {
      "skills_score": 90,
      "experience_score": 85,
      "education_score": 80,
      "communication_score": 88,
      "matching_skills": ["Python", "React", "PostgreSQL", "Docker"],
      "missing_skills": [],
      "strengths": [
        "Strong skills match (90%)",
        "Excellent experience level",
        "Good communication scores"
      ],
      "concerns": [],
      "recommendations": [
        "Consider learning Kubernetes for an edge",
        "AWS certification would be valuable"
      ]
    }
  },
  {
    "job": { ... },
    "match_score": 78,
    "match_details": { ... }
  }
]
```

#### **Apply to Job**

**Request:**
```http
POST /api/employee/apply/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "resume_id": 1,
  "voice_analysis_id": 1,
  "cover_letter": "Dear Hiring Manager,\n\nI am excited to apply..."
}
```

**Response:**
```json
{
  "id": 1,
  "employee_id": 1,
  "job_id": 1,
  "resume_id": 1,
  "voice_analysis_id": 1,
  "cover_letter": "Dear Hiring Manager...",
  "status": "pending",
  "match_score": 87,
  "match_details": {
    "skills_score": 90,
    "experience_score": 85,
    "education_score": 80,
    "communication_score": 88,
    "matching_skills": ["Python", "React", "PostgreSQL", "Docker"],
    "missing_skills": [],
    "strengths": ["Strong skills match (90%)", ...],
    "concerns": [],
    "recommendations": ["Consider learning Kubernetes for an edge", ...]
  },
  "applied_at": "2025-01-10T14:00:00"
}
```

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Setup & Installation

### Backend Setup

#### 1. **Prerequisites**
```bash
# Install Python 3.8+
python --version

# Install MySQL 8.0+
mysql --version

# Install Git
git --version
```

#### 2. **Clone Repository**
```bash
git clone <repository-url>
cd ai-resume-server
```

#### 3. **Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 4. **Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements-dev.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data (handled automatically by setup_nltk.py)
```

#### 5. **Database Setup**
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE ai_resume_db;

# Create user
CREATE USER 'ai_resume_user'@'localhost' IDENTIFIED BY 'secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON ai_resume_db.* TO 'ai_resume_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 6. **Environment Configuration**
```bash
# Copy .env.example
cp .env.example .env

# Edit .env file
nano .env
```

**`.env` Configuration:**
```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ai_resume_user
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=ai_resume_db

# Application
APP_NAME=Employee-Employer Matching API
APP_VERSION=1.0.0
DEBUG=True

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# File Upload
MAX_FILE_SIZE=26214400
UPLOAD_FOLDER=uploads

# AI/ML Models
WHISPER_MODEL=base
MAX_AUDIO_DURATION=600
SIMILARITY_THRESHOLD=0.7

# Matching
DEFAULT_MATCH_LIMIT=50
MINIMUM_MATCH_SCORE=70

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 7. **Run Server**
```bash
# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or use the startup script (if available)
chmod +x start_server.sh
./start_server.sh
```

#### 8. **Verify Installation**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health
- Root: http://localhost:8000/

### Frontend Setup

#### 1. **Prerequisites**
```bash
# Install Node.js 16+
node --version
npm --version
```

#### 2. **Navigate to Frontend**
```bash
cd ai-resume-frontend
```

#### 3. **Install Dependencies**
```bash
npm install
```

#### 4. **Environment Configuration**
```bash
# Create .env file
nano .env
```

**`.env` Configuration:**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Resume Matcher
```

#### 5. **Run Development Server**
```bash
npm run dev
```

#### 6. **Verify Installation**
- Open browser: http://localhost:5173/
- Landing page should load
- Navigation to login/register should work

---

## Configuration

### Backend Configuration Options

#### **Database Settings**
```env
MYSQL_HOST=localhost              # Database host
MYSQL_PORT=3306                   # Database port
MYSQL_USER=ai_resume_user         # Database username
MYSQL_PASSWORD=secure_password    # Database password
MYSQL_DATABASE=ai_resume_db       # Database name
```

#### **Security Settings**
```env
SECRET_KEY=your-secret-key        # JWT signing key (CHANGE IN PRODUCTION!)
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # Token expiry (24 hours)
ALGORITHM=HS256                   # JWT algorithm
```

#### **File Upload Settings**
```env
MAX_FILE_SIZE=26214400            # Max file size in bytes (25MB)
UPLOAD_FOLDER=uploads             # Upload directory path
```

#### **AI/ML Model Settings**
```env
WHISPER_MODEL=base                # Whisper model: tiny, base, small, medium, large
MAX_AUDIO_DURATION=600            # Max audio duration in seconds (10 min)
SIMILARITY_THRESHOLD=0.7          # Semantic similarity threshold (0.0-1.0)
AI_SERVICE_TYPE=simple            # AI service type: simple, original, lightweight, enhanced
```

#### **Matching Algorithm Settings**
```env
DEFAULT_MATCH_LIMIT=50            # Default number of matches to return
MINIMUM_MATCH_SCORE=70            # Minimum match score threshold (0-100)
```

**Score Weights** (in code, `app/config.py`):
```python
score_weights = {
    "skills": 0.4,          # 40% weight
    "experience": 0.3,      # 30% weight
    "education": 0.2,       # 20% weight
    "communication": 0.1    # 10% weight
}
```

#### **CORS Settings**
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

### Frontend Configuration Options

#### **API Configuration**
```env
VITE_API_BASE_URL=http://localhost:8000    # Backend API URL
VITE_APP_NAME=AI Resume Matcher            # Application name
```

#### **Build Configuration** (`vite.config.ts`):
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### Production Configuration

#### **Backend Production Settings**
```env
DEBUG=False
SECRET_KEY=super-secure-production-key-min-32-chars
MYSQL_HOST=production-db-host.example.com
MYSQL_PASSWORD=super-secure-production-password
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### **Frontend Production Build**
```bash
npm run build
# Output: dist/ directory
```

**Environment for Production:**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## User Workflows

### Employee Workflow

```
1. REGISTRATION
   ↓
   Register as Employee
   ↓
   Email, Password, Name, Phone
   ↓
   Account Created
   ↓
   JWT Token Issued

2. PROFILE SETUP
   ↓
   Upload Resume (PDF/DOCX)
   ↓
   AI Analysis (Skills, Experience, Education)
   ↓
   Optional: Upload Voice Recording
   ↓
   Voice Transcription & Communication Scoring
   ↓
   Profile Complete

3. JOB DISCOVERY
   ↓
   View Dashboard
   ↓
   See AI-Recommended Jobs (Match Scores)
   ↓
   Browse All Jobs
   ↓
   Filter by Location, Type, Experience
   ↓
   View Job Details & Match Breakdown

4. APPLICATION
   ↓
   Select Job to Apply
   ↓
   Choose Resume (if multiple)
   ↓
   Choose Voice Analysis (optional)
   ↓
   Write Cover Letter
   ↓
   Submit Application
   ↓
   Application Created with Match Score

5. TRACKING
   ↓
   View Applications Page
   ↓
   See Application Status
   ↓
   Pending → Reviewed → Shortlisted → Interview → Offered
   ↓
   Employer Updates Status
   ↓
   Employee Notified
```

### Employer Workflow

```
1. REGISTRATION
   ↓
   Register as Employer
   ↓
   Email, Password, Name, Company Info
   ↓
   Account Created
   ↓
   JWT Token Issued

2. JOB POSTING
   ↓
   Create Job Posting
   ↓
   Enter Job Details (Title, Description, Location)
   ↓
   Set Requirements (Skills, Experience, Education)
   ↓
   Set Communication Requirements
   ↓
   Customize Matching Weights
   ↓
   Set Minimum Match Score Threshold
   ↓
   Publish Job (Status: Active)

3. CANDIDATE DISCOVERY
   ↓
   View Dashboard
   ↓
   See Applications for Jobs
   ↓
   View AI-Recommended Candidates
   ↓
   Filter by Match Score, Skills
   ↓
   View Candidate Profiles

4. CANDIDATE REVIEW
   ↓
   Select Candidate
   ↓
   View Resume Analysis
   ↓
   View Voice Analysis & Communication Scores
   ↓
   View Match Breakdown
   ↓
   See Matching Skills, Missing Skills
   ↓
   Read Strengths, Concerns, Recommendations

5. HIRING PROCESS
   ↓
   Update Application Status
   ↓
   Pending → Reviewed → Shortlisted
   ↓
   Schedule Interview
   ↓
   Interview → Offered / Rejected
   ↓
   Employee Accepts/Declines Offer
   ↓
   Job Filled or Continue Search
```

### Admin Workflow

```
1. SYSTEM OVERSIGHT
   ↓
   Login as Admin
   ↓
   View System Dashboard
   ↓
   See All Users, Jobs, Applications
   ↓
   View System Statistics

2. USER MANAGEMENT
   ↓
   View All Users
   ↓
   Filter by User Type
   ↓
   Activate/Deactivate Users
   ↓
   Verify Users
   ↓
   Delete Users (if necessary)

3. CONTENT MODERATION
   ↓
   Review Job Postings
   ↓
   Monitor for Inappropriate Content
   ↓
   Pause/Close Jobs
   ↓
   Review User Reports

4. ANALYTICS
   ↓
   View System Statistics
   ↓
   User Growth Metrics
   ↓
   Job Posting Trends
   ↓
   Application Conversion Rates
   ↓
   Average Match Scores
```

---

## Security & Authentication

### JWT Authentication

**Token Structure:**
```
Header.Payload.Signature

Header: { "alg": "HS256", "typ": "JWT" }
Payload: {
  "sub": "user@example.com",
  "user_id": 1,
  "user_type": "employee",
  "exp": 1704988800
}
Signature: HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

**Token Flow:**
1. User logs in with email/password
2. Server validates credentials
3. Server creates JWT with user data and expiration
4. Token sent to client
5. Client stores token (localStorage/sessionStorage)
6. Client includes token in Authorization header for all requests
7. Server validates token and extracts user info
8. Request processed with user context

**Token Expiry:**
- Default: 24 hours (1440 minutes)
- Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- After expiry, user must re-authenticate

### Password Security

**Hashing:**
- Algorithm: bcrypt
- Cost factor: 12 (default)
- Salted automatically by bcrypt

**Password Requirements (Frontend validation):**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Password Storage:**
- Plain passwords NEVER stored
- Only bcrypt hashes stored in database
- Hash comparison for authentication

### CORS (Cross-Origin Resource Sharing)

**Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # From .env
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

**Allowed Origins:**
- Development: http://localhost:5173, http://localhost:3000
- Production: https://yourdomain.com

### Role-Based Access Control (RBAC)

**User Roles:**
- `employee`: Can upload resumes, apply to jobs, view matches
- `employer`: Can post jobs, view applications, review candidates
- `admin`: Can manage users, view all data, moderate content

**Endpoint Protection:**
```python
# Employee-only endpoint
@router.get("/employee/resume")
async def get_resumes(
    current_user: User = Depends(get_current_employee)  # Checks user_type
):
    ...

# Employer-only endpoint
@router.get("/employer/jobs")
async def get_jobs(
    current_user: User = Depends(get_current_employer)
):
    ...

# Admin-only endpoint
@router.get("/admin/users")
async def get_users(
    current_user: User = Depends(get_current_admin)
):
    ...
```

### File Upload Security

**Validation:**
- File size limits (25MB default)
- Extension whitelist (PDF, DOCX, TXT, WAV, MP3, etc.)
- MIME type verification
- Filename sanitization

**Storage:**
- Files stored outside web root
- Unique filenames (UUID-based)
- Separate directories for resumes and voice files

**Access Control:**
- Files not directly accessible via URL
- Served only to authenticated users
- Ownership verification before serving

### SQL Injection Prevention

**Protection via SQLAlchemy:**
- Parameterized queries
- ORM escapes user input
- No raw SQL with user input

**Example:**
```python
# Safe (SQLAlchemy ORM)
user = db.query(User).filter(User.email == email).first()

# Unsafe (avoid)
db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### XSS (Cross-Site Scripting) Prevention

**Frontend:**
- React automatically escapes output
- No `dangerouslySetInnerHTML` without sanitization

**Backend:**
- Pydantic validates and sanitizes input
- HTML content stripped from user input

### CSRF (Cross-Site Request Forgery) Protection

**Not applicable** for JWT-based APIs:
- No session cookies
- Tokens must be manually included in requests
- Same-origin policy enforced by browsers

### Data Privacy

**PII (Personally Identifiable Information):**
- Encrypted in transit (HTTPS in production)
- Encrypted at rest (database encryption)
- Access logged for audit trails

**Data Retention:**
- Users can delete their data
- CASCADE deletes for user deletion
- Soft deletes for audit purposes

---

## Deployment Guide

### Production Deployment Options

#### **Option 1: Traditional Server (VPS)**

**1. Server Setup (Ubuntu 20.04+)**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Install MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Install Nginx
sudo apt install nginx -y

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**2. Backend Deployment**
```bash
# Clone repository
git clone <repository-url>
cd ai-resume-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm

# Setup environment
cp .env.example .env
nano .env  # Edit with production values

# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/ai-resume-api.service
```

**Systemd Service (`ai-resume-api.service`):**
```ini
[Unit]
Description=AI Resume API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-resume-server
Environment="PATH=/home/ubuntu/ai-resume-server/venv/bin"
ExecStart=/home/ubuntu/ai-resume-server/venv/bin/gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/ai-resume-api/access.log \
    --error-logfile /var/log/ai-resume-api/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/ai-resume-api
sudo chown ubuntu:ubuntu /var/log/ai-resume-api

# Start service
sudo systemctl daemon-reload
sudo systemctl start ai-resume-api
sudo systemctl enable ai-resume-api

# Check status
sudo systemctl status ai-resume-api
```

**3. Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/ai-resume-api
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 25M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-resume-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**4. SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

**5. Frontend Deployment**
```bash
cd ai-resume-frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with Nginx
sudo nano /etc/nginx/sites-available/ai-resume-frontend
```

**Nginx Frontend Config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /home/ubuntu/ai-resume-frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-resume-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### **Option 2: Docker Deployment**

**1. Backend Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt && \
    python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Frontend Dockerfile**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**3. Docker Compose**
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: ai_resume_db
      MYSQL_USER: ai_resume_user
      MYSQL_PASSWORD: userpassword
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  backend:
    build: ./ai-resume-server
    environment:
      MYSQL_HOST: db
      MYSQL_PORT: 3306
      MYSQL_USER: ai_resume_user
      MYSQL_PASSWORD: userpassword
      MYSQL_DATABASE: ai_resume_db
      SECRET_KEY: production-secret-key
      DEBUG: "False"
    volumes:
      - ./ai-resume-server/uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./ai-resume-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### **Option 3: Cloud Platform (AWS)**

**AWS Services Used:**
- **EC2**: Application hosting
- **RDS**: MySQL database
- **S3**: File storage
- **CloudFront**: CDN
- **Route 53**: DNS
- **Certificate Manager**: SSL

**Steps:**
1. Launch RDS MySQL instance
2. Launch EC2 instance
3. Deploy backend to EC2 (same as VPS steps)
4. Create S3 bucket for uploads
5. Update file service to use S3 instead of local storage
6. Build frontend and upload to S3
7. Configure CloudFront for frontend S3 bucket
8. Configure Route 53 DNS records

### Environment Variables for Production

**Backend `.env` (Production):**
```env
DEBUG=False
SECRET_KEY=super-secure-production-key-change-this-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

MYSQL_HOST=production-db-host.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=super-secure-production-password
MYSQL_DATABASE=ai_resume_production

MAX_FILE_SIZE=26214400
UPLOAD_FOLDER=/var/uploads

WHISPER_MODEL=base
SIMILARITY_THRESHOLD=0.7
DEFAULT_MATCH_LIMIT=50
MINIMUM_MATCH_SCORE=70

CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Frontend `.env` (Production):**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=AI Resume Matcher
```

### Security Checklist for Production

- [ ] Change `SECRET_KEY` to strong random value (min 32 chars)
- [ ] Set `DEBUG=False`
- [ ] Use strong database password
- [ ] Configure CORS to only allow your domain
- [ ] Enable SSL/HTTPS (Let's Encrypt or AWS Certificate Manager)
- [ ] Set up firewall (UFW on Ubuntu or AWS Security Groups)
- [ ] Configure regular database backups
- [ ] Set up log rotation
- [ ] Enable rate limiting (via Nginx or application layer)
- [ ] Monitor error logs
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom, etc.)

### Performance Optimization

**Backend:**
- Use Gunicorn with multiple workers (4-8 workers)
- Enable database connection pooling
- Implement caching (Redis) for frequently accessed data
- Optimize database queries with indexes
- Use background jobs (Celery) for long-running tasks

**Frontend:**
- Build with production mode (`npm run build`)
- Enable gzip compression in Nginx
- Use CDN for static assets
- Implement lazy loading for routes
- Optimize images and assets

**Database:**
- Create indexes on frequently queried columns
- Regular ANALYZE and OPTIMIZE TABLE
- Monitor slow queries
- Use read replicas for scaling

### Monitoring & Logging

**Application Logs:**
```bash
# Backend logs
tail -f /var/log/ai-resume-api/access.log
tail -f /var/log/ai-resume-api/error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

**Monitoring Tools:**
- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **New Relic**: APM
- **AWS CloudWatch**: AWS services monitoring

---

## Testing

### Backend Testing

**Test Structure:**
```
ai-resume-server/tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_auth.py             # Authentication tests
├── test_employee.py         # Employee endpoint tests
├── test_employer.py         # Employer endpoint tests
├── test_matching.py         # Matching algorithm tests
├── test_ai_service.py       # AI service tests
└── test_models.py           # Database model tests
```

**Run Tests:**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_register_employee -v
```

**Example Test (`tests/test_auth.py`):**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_employee():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "first_name": "John",
            "last_name": "Doe",
            "user_type": "employee"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_login():
    # First register
    client.post("/api/auth/register", json={...})

    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_protected_endpoint():
    # Login first
    login_response = client.post("/api/auth/login", json={...})
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/employee/resume",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Frontend Testing

**Test Structure:**
```
ai-resume-frontend/src/tests/
├── components/
│   ├── Button.test.tsx
│   ├── JobCard.test.tsx
│   └── ...
├── pages/
│   ├── LoginPage.test.tsx
│   └── ...
└── utils/
    └── formatters.test.tsx
```

**Setup (if implementing):**
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

**Example Test:**
```typescript
import { render, screen } from '@testing-library/react';
import { Button } from '../components/common/Button';

describe('Button Component', () => {
  it('renders button with text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  it('calls onClick handler', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    screen.getByText('Click Me').click();
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### Manual Testing Checklist

**Authentication:**
- [ ] Register as employee
- [ ] Register as employer
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout
- [ ] Protected routes redirect to login when not authenticated

**Employee Flow:**
- [ ] Upload PDF resume
- [ ] Upload DOCX resume
- [ ] View resume analysis results
- [ ] Upload voice recording
- [ ] View voice transcription
- [ ] View communication scores
- [ ] Browse jobs
- [ ] Filter jobs
- [ ] View job details
- [ ] Apply to job
- [ ] View applications
- [ ] View match scores

**Employer Flow:**
- [ ] Create job posting
- [ ] Edit job posting
- [ ] Delete job posting
- [ ] View applications for job
- [ ] View candidate details
- [ ] Update application status
- [ ] View match scores and details
- [ ] Search candidates

**Matching:**
- [ ] Job matches generated for employee
- [ ] Candidate matches generated for employer
- [ ] Match scores calculated correctly
- [ ] Match details show strengths/concerns
- [ ] Recommendations provided

---

## Troubleshooting

### Common Backend Issues

#### **1. "spaCy model not found"**
**Error:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

#### **2. "MySQL connection failed"**
**Error:**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```

**Solutions:**
- Verify MySQL is running: `sudo systemctl status mysql`
- Check credentials in `.env`
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`
- Check MySQL port: `sudo netstat -tlnp | grep 3306`

#### **3. "Whisper model download fails"**
**Error:**
```
Exception: Failed to download Whisper model
```

**Solutions:**
- Check internet connection
- Check available disk space: `df -h`
- Try smaller model: `WHISPER_MODEL=tiny` in `.env`
- Download manually:
  ```python
  import whisper
  whisper.load_model("base")
  ```

#### **4. "File upload fails"**
**Error:**
```
413 Request Entity Too Large
```

**Solutions:**
- Increase `MAX_FILE_SIZE` in `.env`
- If using Nginx, increase `client_max_body_size`:
  ```nginx
  client_max_body_size 25M;
  ```

#### **5. "Permission denied" for uploads directory**
**Error:**
```
PermissionError: [Errno 13] Permission denied: 'uploads/resumes/...'
```

**Solution:**
```bash
sudo chown -R $USER:$USER uploads/
chmod -R 755 uploads/
```

#### **6. "JWT token expired"**
**Error:**
```
401 Unauthorized: Token has expired
```

**Solution:**
- User needs to re-login
- Increase token expiry in `.env`: `ACCESS_TOKEN_EXPIRE_MINUTES=2880` (48 hours)

#### **7. "NLTK data not found"**
**Error:**
```
LookupError: Resource 'corpora/stopwords' not found
```

**Solution:**
```bash
python setup_nltk.py
```
Or manually:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### Common Frontend Issues

#### **1. "CORS error"**
**Error:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**
- Add frontend URL to `CORS_ORIGINS` in backend `.env`
- Restart backend server
- Check browser console for exact blocked origin

#### **2. "Module not found"**
**Error:**
```
Cannot find module 'axios'
```

**Solution:**
```bash
cd ai-resume-frontend
npm install
```

#### **3. "API connection error"**
**Error:**
```
Network Error / Failed to fetch
```

**Solutions:**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check `VITE_API_BASE_URL` in frontend `.env`
- Check browser network tab for exact error

#### **4. "Build fails"**
**Error:**
```
TypeScript errors in build
```

**Solutions:**
```bash
# Check for type errors
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# If desperate (not recommended)
# Disable type checking temporarily in vite.config.ts
```

### Performance Issues

#### **1. Slow resume analysis**
**Causes:**
- Large PDF files
- PyResParser processing
- First-time model loading

**Solutions:**
- Limit file size
- Use simpler AI service type: `AI_SERVICE_TYPE=simple`
- Implement caching for analyzed resumes

#### **2. Slow voice transcription**
**Causes:**
- Large audio files
- Whisper model size

**Solutions:**
- Limit audio duration: `MAX_AUDIO_DURATION=300` (5 min)
- Use smaller Whisper model: `WHISPER_MODEL=tiny`
- Implement background job queue (Celery)

#### **3. Slow matching**
**Causes:**
- Large number of candidates/jobs
- Semantic similarity calculations

**Solutions:**
- Implement pagination
- Use caching (Redis)
- Pre-calculate matches in background
- Optimize database queries with indexes

### Database Issues

#### **1. Table doesn't exist**
**Error:**
```
sqlalchemy.exc.ProgrammingError: Table 'ai_resume_db.users' doesn't exist
```

**Solution:**
```python
# Run in Python shell
from app.database import create_tables
create_tables()
```

#### **2. Migration needed**
**Error:**
```
Database schema out of sync
```

**Solution:**
```bash
# If using Alembic
alembic upgrade head

# Or recreate tables (WARNING: deletes data)
# In Python shell:
from app.database import drop_tables, create_tables
drop_tables()
create_tables()
```

---

## Future Enhancements

### Planned Features

#### **1. Enhanced AI Capabilities**
- **Resume Parsing Improvements**
  - Support for more file formats (RTF, ODT)
  - Multi-language resume support
  - Better handling of non-traditional resumes
  - Skills endorsement verification via LinkedIn API

- **Advanced Voice Analysis**
  - Emotion detection in speech
  - Personality assessment
  - Language proficiency scoring
  - Accent neutrality scoring

- **Improved Matching Algorithm**
  - Machine learning model for match scoring
  - Historical match success tracking
  - Feedback loop for improving matches
  - Cultural fit analysis
  - Salary expectation matching

#### **2. User Experience Enhancements**
- **For Employees:**
  - Resume builder/editor
  - Interview preparation tools
  - Skill gap recommendations with learning resources
  - Career path suggestions
  - Application tracking with reminders
  - Salary negotiation tips

- **For Employers:**
  - Bulk candidate screening
  - Interview scheduling integration (Calendly, Google Calendar)
  - Video interview integration (Zoom, Teams)
  - Candidate pipeline visualization
  - Team collaboration features
  - Offer letter generation

#### **3. Communication Features**
- **Messaging System**
  - In-app messaging between employers and candidates
  - Automated email notifications
  - Interview scheduling via chat
  - Document sharing

- **Notifications**
  - Real-time push notifications
  - Email digests
  - SMS alerts for important updates
  - Customizable notification preferences

#### **4. Analytics & Reporting**
- **For Employees:**
  - Profile views analytics
  - Application success rate
  - Skills demand trends
  - Salary insights

- **For Employers:**
  - Candidate funnel analytics
  - Time-to-hire metrics
  - Source of hire tracking
  - Diversity hiring reports
  - Cost-per-hire analysis

#### **5. Integration & APIs**
- **Third-Party Integrations**
  - LinkedIn profile import
  - Indeed/Glassdoor job posting sync
  - Applicant Tracking Systems (ATS) integration
  - Background check services (Checkr, HireRight)
  - Payment gateway for premium features

- **Public API**
  - RESTful API for third-party apps
  - Webhooks for events
  - OAuth2 for authentication
  - API rate limiting

#### **6. Premium Features**
- **Employee Premium:**
  - Priority job recommendations
  - Resume optimization tips
  - Direct employer messaging
  - Application tracking insights
  - Career coaching

- **Employer Premium:**
  - Unlimited job postings
  - Advanced search filters
  - Priority candidate access
  - Dedicated account manager
  - Custom branding

#### **7. Mobile Application**
- **Native Apps (iOS/Android)**
  - React Native or Flutter
  - Push notifications
  - Resume upload via camera
  - Voice recording on mobile
  - Job browsing and application

#### **8. Accessibility**
- **WCAG 2.1 Compliance**
  - Screen reader support
  - Keyboard navigation
  - High contrast mode
  - Font size adjustments
  - Alt text for images

#### **9. Localization**
- **Multi-language Support**
  - Spanish, French, German, Mandarin
  - Right-to-left language support
  - Currency localization
  - Date/time format localization

#### **10. Security Enhancements**
- **Advanced Security**
  - Two-factor authentication (2FA)
  - OAuth2 social login (Google, LinkedIn)
  - IP whitelisting for employers
  - Data encryption at rest
  - GDPR compliance tools
  - Right to be forgotten implementation

### Technical Improvements

#### **1. Performance**
- **Caching Layer**
  - Redis for session storage
  - Cache frequently accessed data
  - CDN for static assets

- **Background Jobs**
  - Celery for async task processing
  - Queue for resume analysis
  - Scheduled job for match generation

- **Database Optimization**
  - Read replicas for scaling
  - Partitioning large tables
  - Full-text search with Elasticsearch

#### **2. Scalability**
- **Microservices Architecture**
  - Separate services for AI, matching, notifications
  - Message queue (RabbitMQ, Kafka)
  - Service mesh (Istio)

- **Load Balancing**
  - Multiple application instances
  - Database load balancing
  - File storage on S3/CDN

#### **3. DevOps**
- **CI/CD Pipeline**
  - Automated testing
  - Automated deployments
  - Blue-green deployments
  - Rollback mechanisms

- **Monitoring**
  - Application performance monitoring (APM)
  - Error tracking (Sentry)
  - Log aggregation (ELK stack)
  - Uptime monitoring

#### **4. Code Quality**
- **Testing**
  - Increase test coverage to 80%+
  - Integration tests
  - End-to-end tests (Playwright, Cypress)
  - Load testing (Locust, k6)

- **Code Standards**
  - Linting enforcement
  - Pre-commit hooks
  - Code review process
  - Documentation standards

### Business Features

#### **1. Monetization**
- **Subscription Plans**
  - Free tier with limitations
  - Premium tiers for employees
  - Business plans for employers
  - Enterprise plans with custom features

- **Pay-per-use**
  - Pay per job posting
  - Pay per candidate search
  - Pay per resume analysis

#### **2. Marketing**
- **SEO Optimization**
  - Meta tags for all pages
  - Sitemap generation
  - Schema markup
  - Blog/content marketing

- **Analytics**
  - Google Analytics integration
  - Conversion tracking
  - A/B testing framework
  - User behavior tracking

#### **3. Compliance**
- **Legal**
  - Terms of service
  - Privacy policy
  - Cookie policy
  - GDPR compliance
  - CCPA compliance
  - Equal opportunity employment compliance

---

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Write/update tests**
5. **Ensure tests pass**: `pytest` (backend), `npm test` (frontend)
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Code Style Guidelines

**Backend (Python):**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions small and focused
- Use meaningful variable names

**Frontend (TypeScript/React):**
- Follow Airbnb style guide
- Use functional components
- Use TypeScript types/interfaces
- Keep components small and reusable
- Use meaningful prop names

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build process or auxiliary tool changes

**Example:**
```
feat(matching): Add semantic similarity for job matching

Implement sentence-transformers for better skill matching.
Uses all-MiniLM-L6-v2 model for semantic similarity.

Closes #123
```

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 AI Resume Matcher

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Support & Contact

### Documentation
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Alternative API Docs**: http://localhost:8000/redoc
- **AI Service Documentation**: See `AI_SERVICE_DOCUMENTATION.md`
- **Dataset Manager Documentation**: See `DATASET_MANAGER_DOCUMENTATION.md`

### Getting Help
- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Email**: support@yourcompany.com (replace with actual support email)

### Useful Links
- **Repository**: https://github.com/your-org/ai-resume-matcher
- **Documentation**: https://docs.yourcompany.com
- **Website**: https://yourcompany.com

---

## Acknowledgments

### Technologies
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **OpenAI Whisper** - Speech-to-text
- **spaCy** - NLP library
- **SQLAlchemy** - ORM
- **TailwindCSS** - CSS framework

### Libraries & Tools
- **PyResParser** - Resume parsing
- **Sentence Transformers** - Semantic similarity
- **Zustand** - State management
- **React Query** - Server state management
- **Recharts** - Data visualization

### Contributors
- **Lead Developer**: [Your Name]
- **AI Engineer**: [Name]
- **Frontend Developer**: [Name]
- **Backend Developer**: [Name]

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Employee registration and profile management
- Employer registration and job posting
- Resume upload and AI analysis
- Voice recording and communication assessment
- AI-powered job matching
- Application tracking
- Admin dashboard

### Upcoming (Version 1.1.0)
- Enhanced matching algorithm with ML
- Messaging system
- Mobile responsive improvements
- Performance optimizations

---

## FAQ

**Q: What file formats are supported for resumes?**
A: PDF, DOCX, and TXT files up to 25MB.

**Q: What audio formats are supported for voice recordings?**
A: WAV, MP3, M4A, FLAC, and OGG files up to 25MB.

**Q: How is the match score calculated?**
A: The match score is a weighted combination of skills match (60%) and experience match (40%), customizable per job posting.

**Q: Can I upload multiple resumes?**
A: Yes, you can upload multiple resumes and set one as primary.

**Q: How long does resume analysis take?**
A: Typically 5-15 seconds depending on file size and complexity.

**Q: Is my data secure?**
A: Yes, all data is encrypted in transit (HTTPS) and at rest. We follow industry best practices for security.

**Q: Can I delete my account and data?**
A: Yes, you can delete your account and all associated data from the settings page.

**Q: How do I report a bug?**
A: Please create an issue on our GitHub repository with detailed steps to reproduce.

**Q: Is there a mobile app?**
A: Not yet, but it's on our roadmap for future development.

**Q: Can I integrate this with my existing ATS?**
A: Custom integrations are available for enterprise plans. Contact us for details.

---

**Last Updated:** October 5, 2025
**Documentation Version:** 1.0.0
**Project Version:** 1.0.0
