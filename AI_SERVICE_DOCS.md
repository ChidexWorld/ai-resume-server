# AI Service - Complete Documentation

## Overview

The AI Service is the core intelligence component of the AI Resume Server, providing advanced machine learning capabilities for resume analysis, voice processing, and job matching. It integrates multiple AI models and leverages the Dataset Manager for industry-specific intelligence.

## Architecture

### Core Components

```
AIService
├── Document Processing
│   ├── PDF Text Extraction
│   ├── DOCX Processing
│   └── Plain Text Handling
├── Resume Analysis
│   ├── Contact Information Extraction
│   ├── Skills Detection
│   ├── Experience Analysis
│   ├── Education Parsing
│   ├── Certifications Identification
│   └── Industry Detection
├── Voice Analysis
│   ├── Audio Transcription (Whisper)
│   ├── Speech Feature Extraction
│   ├── Communication Assessment
│   └── Language Quality Analysis
├── Job Matching
│   ├── Skills Matching
│   ├── Experience Scoring
│   ├── Education Assessment
│   └── Overall Compatibility Rating
└── Model Management
    ├── Lazy Loading
    ├── Memory Optimization
    └── Error Handling
```

### Dependencies

#### Core ML Libraries
- **OpenAI Whisper**: Speech-to-text transcription
- **Transformers**: Sentence embeddings and NLP
- **Sentence-Transformers**: Semantic similarity
- **spaCy**: Named entity recognition and NLP
- **scikit-learn**: Feature extraction and similarity
- **TextBlob**: Sentiment analysis

#### Audio Processing
- **librosa**: Audio feature extraction
- **soundfile**: Audio file handling
- **pydub**: Audio format conversion

#### Document Processing
- **PyPDF2**: PDF text extraction
- **pdfplumber**: Enhanced PDF processing
- **python-docx**: Word document processing

#### Scientific Computing
- **numpy**: Numerical computations
- **pandas**: Data manipulation

## Model Management

### Lazy Loading System

The AI Service implements lazy loading for optimal performance:

```python
class AIService:
    def __init__(self, dataset_path: str = "datasets/"):
        self._whisper_model = None
        self._sentence_model = None
        self._nlp_model = None
        self.dataset_manager = DatasetManager(dataset_path)

    @property
    def whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None:
            self._whisper_model = whisper.load_model(settings.whisper_model)
        return self._whisper_model
```

### Model Specifications

#### Whisper Model
- **Purpose**: Audio transcription
- **Model Size**: Configurable (tiny, base, small, medium, large)
- **Languages**: 100+ languages supported
- **Memory Usage**: 1-10GB depending on model size
- **Load Time**: 5-30 seconds

#### Sentence Transformer
- **Model**: all-MiniLM-L6-v2
- **Purpose**: Text embeddings for similarity
- **Memory Usage**: ~400MB
- **Load Time**: 2-5 seconds

#### spaCy Model
- **Model**: en_core_web_sm
- **Purpose**: Named entity recognition
- **Memory Usage**: ~50MB
- **Load Time**: 1-3 seconds

## Document Processing

### Supported Formats

#### PDF Files
```python
def _extract_from_pdf(self, file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        # Primary: pdfplumber (better formatting)
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        # Fallback: PyPDF2
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    return text.strip()
```

#### DOCX Files
```python
def _extract_from_docx(self, file_path: str) -> str:
    """Extract text from DOCX file."""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()
```

#### Text Files
```python
def _extract_from_text(self, file_path: str) -> str:
    """Extract text from plain text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
```

### Usage
```python
from app.services import ai_service

# Extract text from any supported format
text = ai_service.extract_text_from_file(
    file_path="/path/to/resume.pdf",
    mime_type="application/pdf"
)
```

## Resume Analysis

### Complete Analysis Pipeline

```python
def analyze_resume(self, text: str, target_industry: Optional[str] = None) -> Dict:
    """Enhanced resume analysis with industry detection and manual datasets."""
    doc = self.nlp_model(text)

    # Detect industry if not provided
    if not target_industry:
        target_industry = self.dataset_manager.detect_industry(text)

    analysis = {
        "detected_industry": target_industry,
        "contact_info": self._extract_contact_info(text, doc),
        "skills": self._extract_skills_enhanced(text, target_industry),
        "experience": self._extract_experience_enhanced(text, doc),
        "education": self._extract_education_enhanced(text, doc),
        "certifications": self._extract_certifications_enhanced(text),
        "languages": self._extract_languages(text),
        "professional_summary": self._generate_professional_summary(text),
        "experience_level": self._determine_experience_level(text),
        "total_experience_years": self._calculate_experience_years(text),
        "job_titles": self._extract_job_titles(text),
        "achievements": self._extract_achievements(text),
        "soft_skills": self._extract_soft_skills(text),
    }

    return analysis
```

### Contact Information Extraction

#### Features Detected
- **Email**: Multiple pattern matching
- **Phone**: International and domestic formats
- **Name**: NER + heuristic extraction
- **Location**: Geographic entities
- **LinkedIn**: URL pattern matching

#### Implementation
```python
def _extract_contact_info(self, text: str, doc) -> Dict:
    contact_info = {}

    # Email extraction
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info["email"] = emails[0]

    # Phone extraction (multiple patterns)
    phone_patterns = [
        r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
        r"(?:\+?[0-9]{1,3}[-.\s]?)?(?:\(?[0-9]{2,4}\)?[-.\s]?)?[0-9]{3,4}[-.\s]?[0-9]{3,4}",
    ]

    # Name extraction using NER
    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    if persons:
        # Prefer names in first few lines
        first_lines = "\n".join(text.split("\n")[:5])
        for person in persons:
            if person in first_lines:
                contact_info["name"] = person
                break

    return contact_info
```

### Skills Extraction

#### Enhanced Algorithm
1. **Industry Detection**: Automatically detect resume industry
2. **Industry-Specific Matching**: Prioritize relevant skills
3. **Category Organization**: Group skills by type
4. **Comprehensive Coverage**: Include skills from all industries

```python
def _extract_skills_enhanced(self, text: str, industry: str) -> Dict[str, List[str]]:
    text_lower = text.lower()
    found_skills = {}

    # Get industry-specific skills
    industry_skills = self.dataset_manager.get_skills_by_industry(industry)
    all_skills = self.dataset_manager.get_all_skills()

    # Check for skills presence
    for skill in set(industry_skills + all_skills):
        if skill.lower() in text_lower:
            category = self._find_skill_category(skill, industry)
            if category not in found_skills:
                found_skills[category] = []
            found_skills[category].append(skill.title())

    # Remove duplicates
    for category in found_skills:
        found_skills[category] = list(set(found_skills[category]))

    return found_skills
```

### Experience Analysis

#### Features Extracted
- **Job Titles**: Industry-specific title recognition
- **Companies**: Organization entity recognition
- **Duration**: Date range parsing
- **Responsibilities**: Bullet point extraction
- **Achievements**: Quantified accomplishments

```python
def _extract_experience_enhanced(self, text: str, doc) -> List[Dict]:
    experience = []
    lines = text.split("\n")

    # Get all job titles from dataset
    all_job_titles = self.dataset_manager.get_all_job_titles()

    # Extract organizations and dates
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

    current_job = {}
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 5:
            continue

        # Check if line contains a job title
        line_lower = line.lower()
        is_job_title = any(title.lower() in line_lower for title in all_job_titles)

        if is_job_title:
            if current_job and "title" in current_job:
                experience.append(current_job)
            current_job = {"title": line}

        # Extract company, duration, responsibilities
        # ... (detailed implementation)

    return experience[:5]  # Return top 5 experiences
```

### Education Parsing

#### Supported Formats
- **Degrees**: bachelor, master, phd, mba, associate, etc.
- **Institutions**: university, college, institute, school
- **Fields**: computer science, business, engineering, etc.
- **GPAs**: Automatic extraction
- **Graduation Years**: Date pattern matching

```python
def _extract_education_enhanced(self, text: str, doc) -> List[Dict]:
    education = []
    degree_keywords = self.dataset_manager.education_keywords.get("degree_types", [])
    field_keywords = self.dataset_manager.education_keywords.get("fields", [])

    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()

        # Check for degree and field keywords
        has_degree = any(degree.lower() in line_lower for degree in degree_keywords)
        has_field = any(field.lower() in line_lower for field in field_keywords)

        if has_degree or has_field:
            edu_entry = {"degree": line}

            # Extract GPA
            gpa_match = re.search(r"gpa:?\s*(\d+\.?\d*)", line_lower)
            if gpa_match:
                edu_entry["gpa"] = gpa_match.group(1)

            # Extract year
            year_match = re.search(r"\b(19|20)\d{2}\b", line)
            if year_match:
                edu_entry["year"] = year_match.group()

            education.append(edu_entry)

    return education[:3]
```

### Professional Summary Generation

```python
def _generate_professional_summary(self, text: str) -> str:
    sentences = re.split(r"[.!?]+", text)
    summary_sentences = []

    # Look for summary/objective section first
    text_lower = text.lower()
    summary_keywords = ["summary", "objective", "profile", "about", "overview"]

    for keyword in summary_keywords:
        keyword_index = text_lower.find(keyword)
        if keyword_index != -1:
            remaining_text = text[keyword_index:keyword_index + 500]
            summary_sentences = re.split(r"[.!?]+", remaining_text)[:3]
            break

    if not summary_sentences:
        # Fallback: meaningful sentences from beginning
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            if (len(sentence) > 30 and len(sentence) < 200 and
                not sentence.lower().startswith(("email", "phone", "address"))):
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 3:
                    break

    return ". ".join(s.strip() for s in summary_sentences if s.strip()) + "."
```

### Experience Level Determination

```python
def _determine_experience_level(self, text: str) -> str:
    text_lower = text.lower()

    # Senior level indicators
    senior_indicators = [
        "senior", "lead", "principal", "director", "manager",
        "10+ years", "expert", "architect", "executive"
    ]

    # Mid-level indicators
    mid_indicators = [
        "5+ years", "experienced", "proficient", "advanced",
        "specialist", "several years"
    ]

    # Junior level indicators
    junior_indicators = [
        "junior", "entry", "associate", "assistant",
        "1-2 years", "recent graduate"
    ]

    senior_count = sum(1 for indicator in senior_indicators if indicator in text_lower)
    mid_count = sum(1 for indicator in mid_indicators if indicator in text_lower)
    junior_count = sum(1 for indicator in junior_indicators if indicator in text_lower)

    # Also consider years of experience
    years = self._calculate_experience_years(text)

    if senior_count >= 2 or years >= 10:
        return "senior"
    elif mid_count >= 1 or years >= 5:
        return "mid"
    elif junior_count >= 1 or years <= 2:
        return "junior"
    else:
        return "mid"  # Default to mid-level
```

## Voice Analysis

### Audio Transcription

```python
def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
    """Transcribe audio file to text."""
    try:
        result = self.whisper_model.transcribe(file_path)
        transcript = result["text"]
        confidence = self._estimate_transcript_confidence(transcript)
        return transcript, confidence
    except Exception as e:
        raise Exception(f"Audio transcription failed: {str(e)}")
```

### Speech Feature Extraction

```python
def _extract_speech_features(self, file_path: str) -> Dict:
    """Extract technical speech features from audio."""
    try:
        y, sr = librosa.load(file_path, sr=None)

        features = {
            "duration": float(librosa.get_duration(y=y, sr=sr)),
            "speaking_rate": len(y) / librosa.get_duration(y=y, sr=sr),
            "pitch_mean": self._safe_pitch_mean(y),
            "energy_mean": float(np.mean(librosa.feature.rms(y=y)[0])),
            "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0])),
            "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y)[0])),
        }

        return features
    except Exception as e:
        return {"error": f"Failed to extract speech features: {str(e)}"}
```

### Communication Analysis

```python
def analyze_voice(self, file_path: str, transcript: str) -> Dict:
    """Enhanced voice analysis with industry-specific insights."""
    # Detect industry from transcript
    industry = self.dataset_manager.detect_industry(transcript)

    speech_features = self._extract_speech_features(file_path)
    communication_analysis = self._analyze_communication_enhanced(transcript, industry)
    language_analysis = self._analyze_language_quality(transcript)

    scores = self._calculate_communication_scores(
        speech_features, communication_analysis, language_analysis
    )
    insights = self._generate_communication_insights(
        scores, communication_analysis, industry
    )

    return {
        "detected_industry": industry,
        "speech_features": speech_features,
        "communication_analysis": communication_analysis,
        "language_analysis": language_analysis,
        **scores,
        **insights,
    }
```

### Communication Scoring

#### Metrics Calculated
- **Clarity Score**: Based on energy and pitch consistency
- **Confidence Score**: Sentiment and professional language usage
- **Fluency Score**: Sentence structure and filler word analysis
- **Vocabulary Score**: Diversity and complexity of language
- **Industry Knowledge Score**: Use of industry-specific terminology

```python
def _calculate_communication_scores(self, speech_features: Dict,
                                   comm_analysis: Dict, lang_analysis: Dict) -> Dict:
    scores = {}

    # Clarity score (energy and pitch)
    if "energy_mean" in speech_features and "pitch_mean" in speech_features:
        energy_score = min(100, speech_features["energy_mean"] * 2000)
        pitch_score = min(100, abs(speech_features.get("pitch_mean", 100) - 150) * -2 + 100)
        clarity_score = (energy_score + pitch_score) / 2
        scores["clarity_score"] = int(max(30, min(100, clarity_score)))

    # Confidence score (sentiment + professional language)
    if comm_analysis:
        sentiment_score = (comm_analysis.get("sentiment_polarity", 0) + 1) * 50
        professional_score = comm_analysis.get("professional_language_ratio", 0) * 100
        industry_score = comm_analysis.get("industry_terminology_usage", 0) * 100

        confidence_score = (sentiment_score * 0.4 + professional_score * 0.4 +
                           industry_score * 0.2)
        scores["confidence_score"] = int(max(30, min(100, confidence_score)))

    # Overall communication score
    scores["overall_communication_score"] = int(
        (scores.get("clarity_score", 70) * 0.3 +
         scores.get("confidence_score", 70) * 0.3 +
         scores.get("fluency_score", 70) * 0.2 +
         scores.get("vocabulary_score", 70) * 0.2)
    )

    return scores
```

## Job Matching

### Enhanced Matching Algorithm

```python
def match_resume_to_job(self, resume_data: Dict, job_requirements: Dict) -> Dict:
    """Enhanced job matching with industry context."""
    # Get industry context
    resume_industry = resume_data.get("detected_industry", "general")
    job_industry = job_requirements.get("industry", resume_industry)

    # Extract matching data
    resume_skills = self._flatten_skills(resume_data.get("skills", {}))
    job_required_skills = job_requirements.get("required_skills", [])
    job_preferred_skills = job_requirements.get("preferred_skills", [])

    # Calculate detailed scores
    skills_score = self._calculate_skills_match_enhanced(
        resume_skills, job_required_skills, job_preferred_skills, job_industry
    )
    experience_score = self._calculate_experience_match_enhanced(
        resume_data.get("experience", []),
        job_requirements.get("required_experience", {}),
        resume_data.get("total_experience_years", 0),
    )

    # Weighted overall score
    weights = job_requirements.get("matching_weights", {
        "skills": 0.35,
        "experience": 0.25,
        "education": 0.15,
        "certifications": 0.15,
        "industry_fit": 0.10,
    })

    overall_score = int(
        skills_score * weights.get("skills", 0.35) +
        experience_score * weights.get("experience", 0.25) +
        # ... other components
    )

    return {
        "overall_score": overall_score,
        "match_details": {
            "skills_score": skills_score,
            "experience_score": experience_score,
            "matching_skills": self._get_matching_skills(resume_skills, job_required_skills),
            "missing_skills": self._get_missing_skills(resume_skills, job_required_skills),
            "recommendations": self._generate_improvement_recommendations(resume_data, job_requirements)
        }
    }
```

### Skills Matching with Industry Bonus

```python
def _calculate_skills_match_enhanced(self, resume_skills: List[str],
                                   required_skills: List[str],
                                   preferred_skills: List[str],
                                   industry: str) -> int:
    if not required_skills and not preferred_skills:
        return 80

    # Calculate basic matches
    required_matches = sum(1 for skill in required_skills if skill.lower() in resume_skills)
    preferred_matches = sum(1 for skill in preferred_skills if skill.lower() in resume_skills)

    # Calculate scores
    required_score = (required_matches / max(len(required_skills), 1)) * 100 if required_skills else 100
    preferred_score = (preferred_matches / max(len(preferred_skills), 1)) * 100 if preferred_skills else 0

    # Industry bonus for relevant skills
    industry_skills = self.dataset_manager.get_skills_by_industry(industry)
    industry_matches = sum(1 for skill in resume_skills
                          if skill in [s.lower() for s in industry_skills])
    industry_bonus = min(10, industry_matches * 2)  # Up to 10 bonus points

    base_score = required_score * 0.8 + preferred_score * 0.2 if required_skills else preferred_score
    return int(min(100, base_score + industry_bonus))
```

## API Usage Examples

### Basic Resume Analysis

```python
from app.services import ai_service

# Extract and analyze resume
resume_text = ai_service.extract_text_from_file(
    file_path="/path/to/resume.pdf",
    mime_type="application/pdf"
)

analysis = ai_service.analyze_resume(resume_text)

print(f"Detected Industry: {analysis['detected_industry']}")
print(f"Experience Level: {analysis['experience_level']}")
print(f"Total Experience: {analysis['total_experience_years']} years")
print(f"Skills Found: {len(analysis['skills'])}")
```

### Voice Analysis

```python
# Transcribe and analyze voice recording
transcript, confidence = ai_service.transcribe_audio("/path/to/audio.wav")
print(f"Transcription Confidence: {confidence:.2f}")

voice_analysis = ai_service.analyze_voice("/path/to/audio.wav", transcript)
print(f"Communication Score: {voice_analysis['overall_communication_score']}")
print(f"Strengths: {voice_analysis['strengths']}")
```

### Job Matching

```python
# Define job requirements
job_requirements = {
    "industry": "technology",
    "required_skills": ["python", "aws", "docker"],
    "preferred_skills": ["kubernetes", "terraform", "react"],
    "required_experience": {
        "min_years": 5,
        "preferred_roles": ["software engineer", "devops engineer"]
    },
    "required_education": {"min_degree": "bachelor"},
    "matching_weights": {
        "skills": 0.4,
        "experience": 0.3,
        "education": 0.2,
        "certifications": 0.1
    }
}

# Match resume to job
match_result = ai_service.match_resume_to_job(resume_analysis, job_requirements)
print(f"Overall Match Score: {match_result['overall_score']}%")
print(f"Matching Skills: {match_result['match_details']['matching_skills']}")
print(f"Missing Skills: {match_result['match_details']['missing_skills']}")
```

## Configuration

### Model Settings

Configure models in your `.env` file:

```env
# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=base

# Model paths (optional, for custom models)
SENTENCE_MODEL_PATH=all-MiniLM-L6-v2
SPACY_MODEL_PATH=en_core_web_sm
```

### Performance Tuning

```python
# Configure in app/config.py
class Settings(BaseSettings):
    # Model configurations
    whisper_model: str = "base"  # Balance between speed and accuracy
    max_audio_duration: int = 300  # 5 minutes max

    # Text processing
    max_resume_length: int = 50000  # Characters
    similarity_threshold: float = 0.7

    # Matching parameters
    minimum_match_score: int = 30
    max_recommendations: int = 5
```

## Error Handling

### Graceful Degradation

```python
try:
    analysis = ai_service.analyze_resume(resume_text)
except Exception as e:
    # Fallback to basic text analysis
    analysis = {
        "error": str(e),
        "basic_analysis": basic_text_analysis(resume_text),
        "detected_industry": "general"
    }
```

### Common Error Scenarios

#### Model Loading Failures
```python
@property
def whisper_model(self):
    if self._whisper_model is None:
        try:
            self._whisper_model = whisper.load_model(settings.whisper_model)
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            raise Exception("Voice analysis unavailable - model loading failed")
    return self._whisper_model
```

#### Audio Processing Errors
```python
def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
    try:
        # Validate audio file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Check file size and duration
        file_size = os.path.getsize(file_path)
        if file_size > settings.max_file_size:
            raise ValueError("Audio file too large")

        result = self.whisper_model.transcribe(file_path)
        return result["text"], self._estimate_confidence(result["text"])
    except Exception as e:
        raise Exception(f"Audio transcription failed: {str(e)}")
```

## Performance Optimization

### Memory Management

```python
# Implement model cleanup for long-running processes
def cleanup_models(self):
    """Free model memory when not in use."""
    if hasattr(self, '_whisper_model') and self._whisper_model:
        del self._whisper_model
        self._whisper_model = None

    if hasattr(self, '_sentence_model') and self._sentence_model:
        del self._sentence_model
        self._sentence_model = None

    # Force garbage collection
    import gc
    gc.collect()
```

### Batch Processing

```python
def analyze_multiple_resumes(self, resume_files: List[str]) -> List[Dict]:
    """Efficiently process multiple resumes."""
    results = []

    # Load models once
    _ = self.nlp_model  # Trigger lazy loading

    for file_path in resume_files:
        try:
            text = self.extract_text_from_file(file_path, self._detect_mime_type(file_path))
            analysis = self.analyze_resume(text)
            results.append(analysis)
        except Exception as e:
            results.append({"error": str(e), "file": file_path})

    return results
```

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def _cached_industry_detection(self, text_hash: str) -> str:
    """Cache industry detection results."""
    return self.dataset_manager.detect_industry(text)

def detect_industry_cached(self, text: str) -> str:
    """Industry detection with caching."""
    text_hash = hash(text[:1000])  # Hash first 1000 chars
    return self._cached_industry_detection(text_hash)
```

## Monitoring and Debugging

### Performance Metrics

```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logging.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper

# Apply to key methods
@performance_monitor
def analyze_resume(self, text: str, target_industry: Optional[str] = None) -> Dict:
    # ... implementation
```

### Health Checks

```python
def get_service_health(self) -> Dict:
    """Comprehensive health check for AI service."""
    health = {
        "status": "healthy",
        "models": {},
        "performance": {},
        "errors": []
    }

    # Check model availability
    try:
        health["models"]["whisper"] = self._whisper_model is not None
        health["models"]["sentence_transformer"] = self._sentence_model is not None
        health["models"]["spacy"] = self._nlp_model is not None
    except Exception as e:
        health["errors"].append(f"Model check failed: {e}")

    # Test basic functionality
    try:
        test_text = "Software engineer with Python experience"
        industry = self.dataset_manager.detect_industry(test_text)
        health["performance"]["industry_detection"] = industry == "technology"
    except Exception as e:
        health["errors"].append(f"Industry detection test failed: {e}")

    if health["errors"]:
        health["status"] = "degraded"

    return health
```

## Integration with FastAPI

### Service Endpoints

```python
from fastapi import FastAPI, UploadFile, HTTPException
from app.services import ai_service, AI_SERVICE_AVAILABLE

@app.post("/api/analyze-resume")
async def analyze_resume_endpoint(file: UploadFile):
    if not AI_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract and analyze
        text = ai_service.extract_text_from_file(temp_path, file.content_type)
        analysis = ai_service.analyze_resume(text)

        # Cleanup
        os.unlink(temp_path)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-voice")
async def analyze_voice_endpoint(audio: UploadFile, transcript: str = None):
    if not AI_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    try:
        temp_path = f"/tmp/{audio.filename}"
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Transcribe if transcript not provided
        if not transcript:
            transcript, confidence = ai_service.transcribe_audio(temp_path)

        # Analyze voice
        analysis = ai_service.analyze_voice(temp_path, transcript)

        os.unlink(temp_path)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

This comprehensive AI Service provides powerful machine learning capabilities for resume analysis, voice processing, and intelligent job matching while maintaining robust error handling and performance optimization.