# 🤖 AI-Powered Employee-Employer Matching System

A comprehensive FastAPI backend that uses AI to match employees with employers based on resume analysis, voice communication assessment, and job requirements.

## 🎯 **System Overview**

### **How It Works**
1. **Employers** create job postings with specific requirements (skills, experience, education, communication needs)
2. **Employees** upload resumes (PDF/Word) and/or voice recordings 
3. **AI analyzes** employee profiles and matches them against job requirements
4. **Smart matching** provides scored recommendations for both parties
5. **Application tracking** manages the hiring process

### **Key Features**
- 🧠 **AI Resume Analysis** - Extract skills, experience, education from documents
- 🎤 **Voice Communication Assessment** - Analyze speech patterns, clarity, confidence
- 🎯 **Smart Job Matching** - AI-powered compatibility scoring
- 👥 **Dual User System** - Separate interfaces for employees and employers
- 📊 **Detailed Analytics** - Match breakdowns and improvement suggestions
- 🔐 **Secure Authentication** - JWT-based user management

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Python 3.8+
- MySQL 8.0+
- 4GB+ RAM (for AI models)
- 2GB+ free storage

### **1. Clone and Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd ai-resume-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### **2. Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### **3. Database Setup**
```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE your_database_name;
CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### **4. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required .env settings:**
```env
# Database
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=your-database-name

# Security
SECRET_KEY=your-super-secret-key-here
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

# Development
DEBUG=True
```

### **5. Run Application**
```bash
# Recommended: Use the startup script
chmod +x start_server.sh
./start_server.sh

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **6. Verify Installation**
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Root**: http://localhost:8000/

## 📚 **API Documentation**

### **Authentication Endpoints**

#### **Register User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "employee",  // or "employer"
  "phone": "+1234567890",
  
  // For employers only:
  "company_name": "Tech Corp",
  "company_website": "https://techcorp.com",
  "company_size": "50-100"
}
```

#### **Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### **Employer Endpoints**

#### **Create Job Posting**
```http
POST /api/employer/jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "location": "San Francisco, CA",
  "remote_allowed": true,
  "job_type": "full_time",
  "experience_level": "senior",
  "salary_min": 12000000,  // $120,000 in cents
  "salary_max": 15000000,  // $150,000 in cents
  
  "required_skills": ["python", "django", "postgresql", "docker"],
  "preferred_skills": ["kubernetes", "aws", "react"],
  "required_experience": {
    "min_years": 5,
    "areas": ["web development", "api design"]
  },
  "required_education": {
    "min_degree": "bachelor",
    "field": "computer science"
  },
  "communication_requirements": {
    "presentation_skills": true,
    "client_interaction": true,
    "min_communication_score": 75
  },
  "minimum_match_score": 70
}
```

#### **Get Job Applications**
```http
GET /api/employer/jobs/{job_id}/applications
Authorization: Bearer <token>
```

### **Employee Endpoints**

#### **Upload Resume**
```http
POST /api/employee/resume/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <resume.pdf>
```

#### **Upload Voice Recording**
```http
POST /api/employee/voice/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <voice_recording.wav>
```

#### **Apply to Job**
```http
POST /api/employee/apply/{job_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_id": 1,
  "voice_analysis_id": 2,
  "cover_letter": "I am excited to apply for this position..."
}
```

### **Matching Endpoints**

#### **Get Job Matches for Employee**
```http
GET /api/matching/jobs
Authorization: Bearer <token>
Query Parameters:
- limit: 20 (optional)
- min_score: 70 (optional)
```

#### **Get Employee Matches for Job**
```http
GET /api/matching/candidates/{job_id}
Authorization: Bearer <token>
Query Parameters:
- limit: 50 (optional)
- min_score: 70 (optional)
```

## 🗃️ **Database Schema**

### **Core Tables**

#### **Users**
- Stores both employees and employers
- Fields: id, email, password_hash, first_name, last_name, user_type, company_info

#### **Job Postings**
- Employer job requirements and criteria
- Fields: id, employer_id, title, description, requirements (JSON), matching_weights

#### **Resumes** 
- Employee resume files and AI analysis results
- Fields: id, employee_id, file_info, analysis_results (JSON), skills, experience

#### **Voice Analyses**
- Employee voice recordings and communication assessment
- Fields: id, employee_id, file_info, transcript, communication_scores

#### **Applications**
- Links employees to jobs with match scores
- Fields: id, employee_id, job_id, resume_id, voice_id, match_score, status

#### **Job Matches**
- AI-generated proactive matches
- Fields: id, employee_id, job_id, match_score, match_details (JSON)

## 🤖 **AI/ML Components**

### **Resume Analysis Pipeline**
1. **Text Extraction** - PyPDF2, pdfplumber, python-docx
2. **NLP Processing** - spaCy for named entity recognition
3. **Skills Extraction** - Keyword matching + semantic analysis
4. **Experience Parsing** - Pattern recognition for job history
5. **Education Analysis** - Degree and institution extraction

### **Voice Analysis Pipeline**
1. **Speech-to-Text** - OpenAI Whisper (runs locally)
2. **Audio Features** - Librosa for speech characteristics
3. **Communication Analysis** - TextBlob for sentiment and language quality
4. **Professional Assessment** - Custom scoring algorithms

### **Matching Algorithm**
1. **Skills Matching** - TF-IDF + semantic similarity
2. **Experience Scoring** - Years and relevance analysis
3. **Education Matching** - Degree level and field comparison
4. **Communication Fit** - Voice analysis vs job requirements
5. **Weighted Scoring** - Customizable importance weights

## 🛠️ **Project Structure**

```
ai-resume-server/
├── app/
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py         # User model (employees & employers)
│   │   ├── job_posting.py  # Job posting model
│   │   ├── resume.py       # Resume analysis model
│   │   ├── voice_analysis.py # Voice analysis model
│   │   └── application.py  # Application tracking model
│   ├── routers/            # FastAPI route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── employer.py     # Employer-specific endpoints
│   │   ├── employee.py     # Employee-specific endpoints
│   │   └── matching.py     # AI matching endpoints
│   ├── services/           # Business logic layer
│   │   ├── ai_service.py   # AI/ML processing service
│   │   ├── auth_service.py # Authentication service
│   │   └── file_service.py # File handling service
│   ├── schemas/            # Pydantic models for validation
│   ├── utils/              # Utility functions
│   ├── config.py          # Configuration settings
│   └── database.py        # Database connection setup
├── uploads/               # File storage directory
├── tests/                # Test files
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── main.py              # FastAPI application entry point
└── README.md            # This documentation
```

## ⚙️ **Configuration Options**

### **AI Model Settings**
```python
# In .env file
WHISPER_MODEL=base          # tiny, base, small, medium, large
SIMILARITY_THRESHOLD=0.7    # 0.0 to 1.0
MAX_AUDIO_DURATION=600     # seconds (10 minutes)
```

### **Matching Weights**
```python
# Customize in job posting or config
SCORE_WEIGHTS = {
    "skills": 0.4,          # 40% weight
    "experience": 0.3,      # 30% weight  
    "education": 0.2,       # 20% weight
    "communication": 0.1    # 10% weight
}
```

### **File Upload Limits**
```python
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
ALLOWED_RESUME_EXTENSIONS = ["pdf", "doc", "docx", "txt"]
ALLOWED_AUDIO_EXTENSIONS = ["wav", "mp3", "mp4", "m4a", "ogg"]
```

## 🧪 **Testing**

### **Run Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

### **API Testing**
Use the interactive docs at `/docs` or test with curl:

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","first_name":"John","last_name":"Doe","user_type":"employee"}'
```

## 🚀 **Deployment**

### **Production Setup**
1. **Use Production Database**
   ```env
   MYSQL_HOST=your-production-host
   MYSQL_PASSWORD=your-secure-production-password
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ```

2. **Run with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Environment Variables**
   ```env
   SECRET_KEY=your-production-secret-key
   MYSQL_PASSWORD=your-secure-production-password
   CORS_ORIGINS=https://yourdomain.com
   ```

### **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

#### **"MySQL connection failed"**
- Verify MySQL is running
- Check credentials in .env
- Ensure database exists

#### **"Whisper model download fails"**
- Ensure stable internet connection
- Check available disk space (models are 100MB+)
- Try smaller model: `WHISPER_MODEL=tiny`

#### **"File upload fails"**
- Check file size limits
- Verify upload directory permissions
- Ensure supported file format

### **Performance Optimization**

#### **For Large Scale**
- Use Redis for caching
- Implement background job queue
- Optimize database queries
- Use CDN for file storage

#### **Memory Management**
```python
# Reduce model memory usage
WHISPER_MODEL=tiny        # Smallest model
torch.set_num_threads(2)  # Limit CPU threads
```

## 📊 **Monitoring & Analytics**

### **Key Metrics to Track**
- User registration rates (employees vs employers)
- Resume/voice upload success rates  
- AI analysis completion times
- Match accuracy feedback
- Application conversion rates

### **Health Monitoring**
```bash
# Check system health
curl http://localhost:8000/api/health

# Monitor database performance
curl http://localhost:8000/api/admin/stats
```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

- **Documentation**: http://localhost:8000/docs
- **Issues**: Create GitHub issue
- **Email**: support@yourcompany.com

---

## 🎉 **You're Ready!**

Your AI-powered employee-employer matching system is now ready to use. The system provides:

✅ **Complete user management** for employees and employers  
✅ **AI-powered resume analysis** with skill extraction  
✅ **Voice communication assessment** with detailed scoring  
✅ **Smart job matching** with customizable criteria  
✅ **Full application tracking** and management  
✅ **RESTful API** with comprehensive documentation  
✅ **Production-ready** with proper error handling  

Start by registering users and creating job postings to see the AI matching in action!