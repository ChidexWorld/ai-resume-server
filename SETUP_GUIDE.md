# AI Resume Server - Setup Guide

## 🎯 Overview

The AI Resume Server is a FastAPI-based application that provides an intelligent employee-employer matching platform with AI-powered resume analysis, voice analysis, and job matching capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ 
- MySQL database (configured in .env)
- At least 4GB RAM (for AI models)

### 1. Environment Setup

Configure your `.env` file with:
```env
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=your-database-name

# Security Settings
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# File Upload Settings
MAX_FILE_SIZE=26214400
UPLOAD_FOLDER=uploads

# AI/ML Model Settings
WHISPER_MODEL=base
MAX_AUDIO_DURATION=600
SIMILARITY_THRESHOLD=0.7

# Matching Algorithm Settings
DEFAULT_MATCH_LIMIT=50
MINIMUM_MATCH_SCORE=70

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

### 2. Install Dependencies

```bash
# Activate virtual environment (already created)
source venv/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
# Run migrations (this will create all necessary tables)
python -m alembic upgrade head
```

### 4. Start the Application

**Option 1: Using the startup script (recommended)**
```bash
# Make script executable (first time only)
chmod +x start_server.sh

# Start the server with clean environment
./start_server.sh
```

**Option 2: Using uvicorn directly**
```bash
# Clear any conflicting environment variables first
unset MAX_FILE_SIZE MAX_AUDIO_DURATION SIMILARITY_THRESHOLD MINIMUM_MATCH_SCORE

# Start server
uvicorn main:app --reload
```

**Option 3: Using uvicorn command with custom host/port**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Application URLs

Once running, access these URLs:

- **Main App**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Run tests with pytest (install if needed)
pip install pytest pytest-asyncio httpx
pytest

# Or run tests with coverage
pytest --cov=app tests/
```

## 📁 Project Structure

```
ai-resume-server/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── routers/         # FastAPI route handlers
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic services
│   ├── config.py        # Configuration management
│   └── database.py      # Database connection setup
├── alembic/             # Database migration files
├── uploads/             # File upload storage
├── main.py              # Application entry point
├── start_server.sh      # Server startup script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
└── .env.example        # Environment variables template
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile

### Employee Endpoints
- `POST /api/employee/resume/upload` - Upload and analyze resume
- `POST /api/employee/voice/upload` - Upload and analyze voice recording
- `GET /api/employee/resumes` - Get user's resumes
- `POST /api/employee/apply/{job_id}` - Apply to job
- `GET /api/employee/applications` - Get user's applications
- `GET /api/employee/job-recommendations` - Get AI job recommendations

### Employer Endpoints
- `POST /api/employer/jobs` - Create job posting
- `GET /api/employer/jobs` - Get employer's job postings
- `PUT /api/employer/jobs/{job_id}` - Update job posting
- `GET /api/employer/jobs/{job_id}/applications` - Get job applications
- `PUT /api/employer/applications/{id}/status` - Update application status
- `GET /api/employer/candidates/search` - Search candidates

### AI Matching
- `POST /api/matching/generate-matches/{job_id}` - Generate AI matches
- `GET /api/matching/job-matches/{job_id}` - Get job matches
- `GET /api/matching/employee-matches` - Get employee matches
- `POST /api/matching/calculate-match` - Calculate match score

### Admin
- `GET /api/admin/stats` - System statistics
- `GET /api/admin/users` - User management
- `GET /api/admin/content` - Content moderation

## 🤖 AI Features

### Resume Analysis
- **Text Extraction**: PDF, DOCX, TXT support
- **Contact Information**: Email, phone, location extraction
- **Skills Analysis**: Technical and soft skills identification
- **Experience Parsing**: Work history and career progression
- **Education Extraction**: Degrees, institutions, certifications
- **Professional Summary**: AI-generated summaries

### Voice Analysis
- **Speech-to-Text**: Using OpenAI Whisper
- **Communication Scoring**: Clarity, confidence, fluency
- **Language Analysis**: Vocabulary, professional language usage
- **Speaking Patterns**: Pace, tone, articulation analysis

### Job Matching
- **Skill Matching**: Required vs. candidate skills
- **Experience Matching**: Years and domain experience
- **Education Matching**: Degree requirements
- **Communication Fit**: Voice analysis integration
- **Custom Weights**: Employer-defined matching criteria

## 📊 Database Schema

The application uses the following main entities:

- **Users**: Employee and employer profiles
- **Job Postings**: Job requirements and details
- **Resumes**: Uploaded files and AI analysis results
- **Voice Analyses**: Audio files and communication analysis
- **Applications**: Job applications with match scores
- **Job Matches**: AI-generated recommendations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt password protection  
- **File Validation**: Upload size and type limits
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **CORS Configuration**: Cross-origin request handling

## 🚨 Troubleshooting

### Common Issues

**1. Environment Variable Parsing Errors**
```bash
# Error: ValidationError for Settings (int_parsing, float_parsing)
# Solution: Clear conflicting system environment variables
unset MAX_FILE_SIZE MAX_AUDIO_DURATION SIMILARITY_THRESHOLD MINIMUM_MATCH_SCORE

# Or use the startup script which handles this automatically
./start_server.sh
```

**2. Database Connection Error**
```bash
# Check if MySQL service is running
# Verify .env database credentials
python -c "from app.config import settings; print('Database configured:', settings.mysql_host)"
```

**2. AI Model Loading Issues**
```bash
# Install required models
python -c "import whisper; whisper.load_model('base')"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**3. Import Errors**
```bash
# Run the test suite
pytest

# Check specific imports
python -c "from app.config import settings; from main import app; print('✅ Application loads successfully')"
```

**4. Migration Issues**
```bash
# Reset migrations (caution: drops data)
python -m alembic downgrade base
python -m alembic upgrade head

# Or create tables directly
python -c "from app.database import create_tables; create_tables()"
```

## 🔄 Development Workflow

### Making Changes

1. **Models**: Edit files in `app/models/`
2. **API Routes**: Edit files in `app/routers/`  
3. **Business Logic**: Edit files in `app/services/`
4. **Schemas**: Edit files in `app/schemas/`

### Database Changes

1. **Create Migration**:
```bash
python -m alembic revision --autogenerate -m "Description of changes"
```

2. **Apply Migration**:
```bash
python -m alembic upgrade head
```

### Testing Changes

```bash
# Run tests
pytest

# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/docs
```

## 📈 Production Deployment

For production deployment:

1. **Environment Variables**: Set secure values
2. **Database**: Use production MySQL instance
3. **File Storage**: Consider cloud storage (S3, etc.)
4. **Load Balancer**: Use nginx or similar
5. **Process Manager**: Use gunicorn or similar
6. **Monitoring**: Add logging and monitoring
7. **SSL**: Configure HTTPS certificates

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🎉 Success!

Your AI Resume Server is now fully configured and ready to use! The application provides:

- ✅ Complete user authentication system
- ✅ AI-powered resume analysis  
- ✅ Voice recording analysis
- ✅ Intelligent job matching
- ✅ RESTful API with documentation
- ✅ Database migrations
- ✅ File upload handling
- ✅ Admin management tools

Visit http://localhost:8000/docs to explore the full API!