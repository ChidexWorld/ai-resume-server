# AI Resume Server - Services Guide

This document explains the separated service architecture and how to work with the AI and dataset management services.

## Architecture Overview

The AI Resume Server now has a modular service architecture:

### 🗂️ Dataset Manager (`app/services/dataset_manager.py`)
- **Purpose**: Manages manual datasets for skills, job titles, industries, certifications, and education keywords
- **Dependencies**: None (lightweight, Python standard library only)
- **Features**:
  - Industry-specific skill categorization
  - Job title management
  - Certification tracking
  - Education keyword detection
  - Export/import functionality
  - Automatic fallback data creation

### 🤖 AI Service (`app/services/ai_service.py`)
- **Purpose**: Handles AI-powered resume analysis, voice processing, and job matching
- **Dependencies**: Heavy ML libraries (whisper, transformers, spacy, etc.)
- **Features**:
  - Resume text extraction and analysis
  - Voice analysis and transcription
  - Job matching algorithms
  - Industry detection
  - Lazy model loading

### 🚀 Service Initialization (`app/services/__init__.py`)
- **Purpose**: Centralized service management with graceful error handling
- **Features**:
  - Graceful dependency handling
  - Service status monitoring
  - Initialization coordination

## Getting Started

### 1. Check Service Status
```bash
# Check current service status
python3 check_services.py
```

### 2. Start the Server
```bash
# Using the enhanced startup script
./start_server.sh

# Or directly
python3 run_with_services.py
```

### 3. Install Dependencies (if needed)
```bash
# Activate virtual environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

## Service Status Monitoring

### Health Check Endpoint
The `/api/health` endpoint now includes service status:

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "ai_services": {
    "dataset_manager": {
      "status": "ready",
      "stats": {
        "skills": {
          "total_skills": 148,
          "total_industries": 9
        }
      }
    },
    "ai_service": {
      "status": "ready|unavailable",
      "models_loaded": {
        "whisper": false,
        "sentence_transformer": false,
        "spacy": false
      }
    }
  }
}
```

## Working with Services

### Dataset Manager

#### Access the Dataset Manager
```python
from app.services import dataset_manager

# Get statistics
stats = dataset_manager.get_dataset_stats()

# Add new skills
dataset_manager.add_skills_to_dataset(
    industry="retail",
    category="customer_service",
    skills=["customer support", "pos systems"]
)

# Detect industry from text
industry = dataset_manager.detect_industry("python developer with react experience")
```

#### Dataset Structure
```
datasets/
├── skills.json           # Skills by industry and category
├── job_titles.json       # Job titles by industry
├── industries.json       # Industry keywords
├── certifications.json   # Certifications by industry
└── education_keywords.json # Education-related terms
```

### AI Service

#### Access the AI Service (when available)
```python
from app.services import ai_service, AI_SERVICE_AVAILABLE

if AI_SERVICE_AVAILABLE:
    # Analyze resume
    analysis = ai_service.analyze_resume(resume_text)

    # Match job requirements
    match_result = ai_service.match_resume_to_job(resume_data, job_requirements)

    # Voice analysis
    voice_analysis = ai_service.analyze_voice(audio_file, transcript)
```

## Graceful Degradation

The system is designed to work even when AI dependencies are missing:

1. **Dataset Manager Always Available**: Core functionality for managing datasets works without ML dependencies
2. **Graceful AI Fallback**: If AI libraries aren't installed, the service reports unavailable status but doesn't crash
3. **Clear Error Messages**: Users get informative messages about what's available and what's missing

## Development Workflow

### Adding New Industries
```python
# Add to dataset manager
dataset_manager.add_skills_to_dataset("new_industry", "category", ["skill1", "skill2"])
dataset_manager.add_job_titles_to_dataset("new_industry", ["title1", "title2"])
dataset_manager.add_certifications_to_dataset("new_industry", ["cert1", "cert2"])
```

### Testing Services
```bash
# Test dataset manager only
python3 -c "from app.services.dataset_manager import dataset_manager; print(dataset_manager.get_dataset_stats())"

# Test full service initialization
python3 -c "from app.services import initialize_services; initialize_services()"

# Check service status
python3 check_services.py
```

## Production Deployment

### Environment Setup
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Configure environment variables in `.env`
3. Use the enhanced startup script: `./start_server.sh`

### Service Monitoring
- Monitor the `/api/health` endpoint for service status
- Check logs for service initialization messages
- Use `check_services.py` for detailed status reports

### Performance Considerations
- **Dataset Manager**: Lightweight, loads quickly
- **AI Service**: Heavy models load lazily on first use
- **Memory Usage**: Models are only loaded when needed
- **Startup Time**: Dataset manager initializes quickly, AI models load on demand

## Troubleshooting

### Common Issues

#### "AI service dependencies not available"
- **Cause**: ML libraries not installed
- **Solution**: `pip install -r requirements.txt`
- **Workaround**: Dataset functionality still works

#### "Dataset files not found"
- **Cause**: First run or missing dataset files
- **Solution**: Automatic - default datasets are created automatically

#### "Models not loading"
- **Cause**: Insufficient memory or corrupted model files
- **Solution**: Check available memory, reinstall model dependencies

### Debug Commands
```bash
# Verbose service checking
python3 -c "from app.services import get_service_status; import json; print(json.dumps(get_service_status(), indent=2))"

# Test dataset creation
python3 -c "from app.services.dataset_manager import DatasetManager; dm = DatasetManager('test_datasets'); print('Test datasets created')"

# Check model loading
python3 -c "from app.services.ai_service import AIService; ai = AIService(); print('AI service created')"
```

## File Structure

```
app/
├── services/
│   ├── __init__.py           # Service coordination and initialization
│   ├── dataset_manager.py    # Dataset management (lightweight)
│   └── ai_service.py         # AI processing (heavy dependencies)
├── main.py                   # FastAPI app with service initialization
check_services.py             # Service status checker
run_with_services.py          # Enhanced startup script
start_server.sh               # Shell startup script
datasets/                     # Auto-created dataset files
└── requirements.txt          # All dependencies
```

This architecture ensures your AI Resume Server is modular, maintainable, and gracefully handles missing dependencies while providing powerful AI functionality when available.