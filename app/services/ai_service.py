"""
AI service for resume parsing, voice analysis, and job matching.
All AI processing logic centralized here.
"""
import os
import re
import json
import whisper
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from textblob import TextBlob
import PyPDF2
import pdfplumber
from docx import Document
from app.config import settings


class AIService:
    """Centralized AI service for all ML/NLP operations."""
    
    def __init__(self):
        """Initialize AI models and tools."""
        self._whisper_model = None
        self._sentence_model = None
        self._nlp_model = None
        self._skills_keywords = self._load_skills_keywords()
    
    @property
    def whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None:
            self._whisper_model = whisper.load_model(settings.whisper_model)
        return self._whisper_model
    
    @property
    def sentence_model(self):
        """Lazy load sentence transformer model."""
        if self._sentence_model is None:
            self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._sentence_model
    
    @property
    def nlp_model(self):
        """Lazy load spaCy model."""
        if self._nlp_model is None:
            try:
                self._nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                # Download model if not available
                os.system("python -m spacy download en_core_web_sm")
                self._nlp_model = spacy.load("en_core_web_sm")
        return self._nlp_model
    
    def _load_skills_keywords(self) -> Dict[str, List[str]]:
        """Load predefined skills keywords for extraction."""
        return {
            "programming": [
                "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
                "typescript", "kotlin", "swift", "scala", "r", "matlab", "sql", "html", "css"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "laravel", "rails",
                "express", "fastapi", "bootstrap", "tailwind", "jquery", "node.js"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
                "oracle", "sqlite", "dynamodb", "firebase"
            ],
            "cloud": [
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
                "gitlab", "github", "ci/cd", "devops"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving", "analytical",
                "creative", "adaptable", "organized", "detail oriented", "time management"
            ],
            "tools": [
                "git", "jira", "confluence", "slack", "figma", "photoshop", "excel",
                "powerpoint", "tableau", "power bi", "salesforce"
            ]
        }
    
    # === DOCUMENT PROCESSING ===
    
    def extract_text_from_file(self, file_path: str, mime_type: str) -> str:
        """Extract text from various file types."""
        try:
            if mime_type == "application/pdf":
                return self._extract_from_pdf(file_path)
            elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                return self._extract_from_docx(file_path)
            elif mime_type.startswith("text/"):
                return self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    # === RESUME ANALYSIS ===
    
    def analyze_resume(self, text: str) -> Dict:
        """Complete resume analysis pipeline."""
        try:
            doc = self.nlp_model(text)
            
            analysis = {
                "contact_info": self._extract_contact_info(text, doc),
                "skills": self._extract_skills(text),
                "experience": self._extract_experience(text, doc),
                "education": self._extract_education(text, doc),
                "certifications": self._extract_certifications(text),
                "languages": self._extract_languages(text),
                "professional_summary": self._generate_professional_summary(text),
                "experience_level": self._determine_experience_level(text),
                "total_experience_years": self._calculate_experience_years(text)
            }
            
            return analysis
        except Exception as e:
            raise Exception(f"Resume analysis failed: {str(e)}")
    
    def _extract_contact_info(self, text: str, doc) -> Dict:
        """Extract contact information from resume."""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]
        
        # Extract phone
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
        
        # Extract name (use NER)
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if persons:
            contact_info["name"] = persons[0]
        
        # Extract location
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        if locations:
            contact_info["location"] = locations[0]
        
        return contact_info
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills."""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self._skills_keywords.items():
            category_skills = []
            for skill in skills:
                if skill.lower() in text_lower:
                    category_skills.append(skill.title())
            
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills
    
    def _extract_experience(self, text: str, doc) -> List[Dict]:
        """Extract work experience information."""
        experience = []
        
        # Find organizations
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Find dates
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        
        # Simple experience extraction (can be enhanced)
        lines = text.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for job titles (contains common title words)
            title_keywords = ["manager", "developer", "engineer", "analyst", "specialist", "coordinator", "director", "officer", "assistant"]
            if any(keyword in line.lower() for keyword in title_keywords):
                if current_job:
                    experience.append(current_job)
                current_job = {"title": line}
            
            # Look for companies (if we have org entities)
            elif any(org in line for org in orgs[:5]):  # Limit to first 5 orgs
                current_job["company"] = line
            
            # Look for dates
            elif any(date_part in line for date_part in dates[:10]):  # Limit to first 10 dates
                current_job["duration"] = line
        
        if current_job:
            experience.append(current_job)
        
        return experience[:5]  # Return top 5 experiences
    
    def _extract_education(self, text: str, doc) -> List[Dict]:
        """Extract education information."""
        education = []
        
        # Common degree keywords
        degree_keywords = ["bachelor", "master", "phd", "doctorate", "associate", "diploma", "certificate"]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(degree in line_lower for degree in degree_keywords):
                education.append({"degree": line.strip()})
        
        return education[:3]  # Return top 3 education entries
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract professional certifications."""
        cert_keywords = ["certified", "certification", "certificate", "license"]
        certifications = []
        
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in cert_keywords):
                certifications.append(line.strip())
        
        return certifications[:5]  # Return top 5 certifications
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract language skills."""
        language_keywords = ["english", "spanish", "french", "german", "chinese", "japanese", "italian", "portuguese"]
        languages = []
        
        text_lower = text.lower()
        for lang in language_keywords:
            if lang in text_lower:
                languages.append(lang.title())
        
        return list(set(languages))  # Remove duplicates
    
    def _generate_professional_summary(self, text: str) -> str:
        """Generate a professional summary using TextBlob."""
        # Simple extractive summarization
        sentences = text.split('.')
        # Get first few meaningful sentences
        summary_sentences = []
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 3:
                    break
        
        return '. '.join(summary_sentences) + '.' if summary_sentences else "Professional summary not available."
    
    def _determine_experience_level(self, text: str) -> str:
        """Determine experience level based on text analysis."""
        text_lower = text.lower()
        
        # Count experience indicators
        senior_indicators = ["senior", "lead", "principal", "director", "manager", "10+ years", "15+ years"]
        mid_indicators = ["5+ years", "experienced", "proficient", "advanced"]
        junior_indicators = ["junior", "entry", "graduate", "intern", "1-2 years", "recent graduate"]
        
        senior_count = sum(1 for indicator in senior_indicators if indicator in text_lower)
        mid_count = sum(1 for indicator in mid_indicators if indicator in text_lower)
        junior_count = sum(1 for indicator in junior_indicators if indicator in text_lower)
        
        if senior_count >= 2:
            return "senior"
        elif mid_count >= 1:
            return "mid"
        elif junior_count >= 1:
            return "junior"
        else:
            return "entry"
    
    def _calculate_experience_years(self, text: str) -> int:
        """Calculate total years of experience."""
        # Look for patterns like "5 years", "10+ years"
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|work)',
            r'(\d+)\+?\s*years?\s*in',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0
    
    # === VOICE ANALYSIS ===
    
    def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
        """Transcribe audio file to text."""
        try:
            result = self.whisper_model.transcribe(file_path)
            transcript = result["text"]
            
            # Calculate confidence (Whisper doesn't provide confidence directly)
            # We'll use a simple heuristic based on text quality
            confidence = self._estimate_transcript_confidence(transcript)
            
            return transcript, confidence
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")
    
    def _estimate_transcript_confidence(self, transcript: str) -> float:
        """Estimate transcript confidence based on text quality."""
        if not transcript:
            return 0.0
        
        # Simple heuristics for confidence
        word_count = len(transcript.split())
        avg_word_length = sum(len(word) for word in transcript.split()) / max(word_count, 1)
        
        # Higher confidence for longer words and more words
        confidence = min(0.9, (word_count * 0.01) + (avg_word_length * 0.1))
        return max(0.3, confidence)  # Minimum 30% confidence
    
    def analyze_voice(self, file_path: str, transcript: str) -> Dict:
        """Complete voice analysis pipeline."""
        try:
            # Extract audio features
            speech_features = self._extract_speech_features(file_path)
            
            # Analyze communication
            communication_analysis = self._analyze_communication(transcript)
            
            # Analyze language
            language_analysis = self._analyze_language_quality(transcript)
            
            # Calculate scores
            scores = self._calculate_communication_scores(speech_features, communication_analysis, language_analysis)
            
            # Generate insights
            insights = self._generate_communication_insights(scores, communication_analysis)
            
            return {
                "speech_features": speech_features,
                "communication_analysis": communication_analysis,
                "language_analysis": language_analysis,
                **scores,
                **insights
            }
        except Exception as e:
            raise Exception(f"Voice analysis failed: {str(e)}")
    
    def _safe_pitch_mean(self, y) -> float:
        """Safely calculate pitch mean handling NaN values."""
        try:
            pitch_values = librosa.yin(y, fmin=50, fmax=300, threshold=0.1)
            # Filter out NaN values and calculate mean
            valid_pitch = pitch_values[~np.isnan(pitch_values)]
            if len(valid_pitch) > 0:
                return float(np.mean(valid_pitch))
            else:
                return 150.0  # Default pitch value
        except:
            return 150.0  # Default pitch value on error

    def _extract_speech_features(self, file_path: str) -> Dict:
        """Extract technical speech features from audio."""
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=None)

            # Extract features
            features = {
                "duration": float(librosa.get_duration(y=y, sr=sr)),
                "speaking_rate": len(y) / librosa.get_duration(y=y, sr=sr),
                "pitch_mean": self._safe_pitch_mean(y),
                "energy_mean": float(np.mean(librosa.feature.rms(y=y)[0])),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0])),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y)[0]))
            }

            return features
        except Exception as e:
            return {"error": f"Failed to extract speech features: {str(e)}"}
    
    def _analyze_communication(self, transcript: str) -> Dict:
        """Analyze communication patterns from transcript."""
        if not transcript:
            return {}
        
        blob = TextBlob(transcript)
        
        # Basic communication analysis
        analysis = {
            "word_count": len(transcript.split()),
            "sentence_count": len(blob.sentences),
            "avg_sentence_length": len(transcript.split()) / max(len(blob.sentences), 1),
            "sentiment_polarity": blob.sentiment.polarity,
            "sentiment_subjectivity": blob.sentiment.subjectivity
        }
        
        # Professional language indicators
        professional_words = [
            "experience", "achieved", "managed", "developed", "led", "improved",
            "created", "implemented", "successful", "responsibility", "team", "project"
        ]
        
        professional_count = sum(1 for word in professional_words if word in transcript.lower())
        analysis["professional_language_ratio"] = professional_count / max(len(transcript.split()), 1)
        
        return analysis
    
    def _analyze_language_quality(self, transcript: str) -> Dict:
        """Analyze language quality and vocabulary."""
        if not transcript:
            return {}
        
        words = transcript.split()
        unique_words = set(word.lower().strip('.,!?;:"()[]') for word in words)
        
        return {
            "vocabulary_diversity": len(unique_words) / max(len(words), 1),
            "avg_word_length": sum(len(word) for word in words) / max(len(words), 1),
            "complex_words_ratio": sum(1 for word in words if len(word) > 6) / max(len(words), 1)
        }
    
    def _calculate_communication_scores(self, speech_features: Dict, comm_analysis: Dict, lang_analysis: Dict) -> Dict:
        """Calculate communication scores (0-100 scale)."""
        scores = {}
        
        # Clarity score (based on speech features)
        if "energy_mean" in speech_features and "pitch_mean" in speech_features:
            clarity_score = min(100, (speech_features["energy_mean"] * 1000 + speech_features.get("pitch_mean", 100)) / 2)
            scores["clarity_score"] = int(max(30, clarity_score))
        else:
            scores["clarity_score"] = 70  # Default
        
        # Confidence score (based on sentiment and professional language)
        if comm_analysis:
            confidence_base = max(0, comm_analysis.get("sentiment_polarity", 0)) * 50 + 50
            professional_boost = comm_analysis.get("professional_language_ratio", 0) * 30
            scores["confidence_score"] = int(min(100, confidence_base + professional_boost))
        else:
            scores["confidence_score"] = 70
        
        # Fluency score (based on speaking rate and sentence structure)
        if speech_features and comm_analysis:
            ideal_sentence_length = 15  # words
            sentence_length_score = 100 - abs(comm_analysis.get("avg_sentence_length", 15) - ideal_sentence_length) * 2
            scores["fluency_score"] = int(max(40, min(100, sentence_length_score)))
        else:
            scores["fluency_score"] = 70
        
        # Vocabulary score (based on language analysis)
        if lang_analysis:
            vocab_score = (lang_analysis.get("vocabulary_diversity", 0.5) * 60 + 
                          lang_analysis.get("complex_words_ratio", 0.2) * 40)
            scores["vocabulary_score"] = int(min(100, max(30, vocab_score * 100)))
        else:
            scores["vocabulary_score"] = 70
        
        # Overall communication score (weighted average)
        scores["overall_communication_score"] = int(
            (scores["clarity_score"] * 0.3 +
             scores["confidence_score"] * 0.3 +
             scores["fluency_score"] * 0.2 +
             scores["vocabulary_score"] * 0.2)
        )
        
        # Professional language usage score
        if comm_analysis:
            scores["professional_language_usage"] = int(min(100, comm_analysis.get("professional_language_ratio", 0) * 200))
        else:
            scores["professional_language_usage"] = 70
        
        return scores
    
    def _generate_communication_insights(self, scores: Dict, comm_analysis: Dict) -> Dict:
        """Generate communication insights and recommendations."""
        strengths = []
        improvements = []
        
        # Analyze strengths
        if scores.get("clarity_score", 0) >= 80:
            strengths.append("Clear and articulate speech")
        if scores.get("confidence_score", 0) >= 80:
            strengths.append("Confident communication style")
        if scores.get("vocabulary_score", 0) >= 80:
            strengths.append("Rich vocabulary usage")
        if scores.get("professional_language_usage", 0) >= 70:
            strengths.append("Professional language skills")
        
        # Analyze areas for improvement
        if scores.get("clarity_score", 0) < 60:
            improvements.append("Work on speech clarity and articulation")
        if scores.get("confidence_score", 0) < 60:
            improvements.append("Build confidence in communication")
        if scores.get("fluency_score", 0) < 60:
            improvements.append("Improve speech fluency and pace")
        if scores.get("vocabulary_score", 0) < 60:
            improvements.append("Expand professional vocabulary")
        
        # Determine speaking pace
        speaking_pace = "normal"
        if comm_analysis.get("avg_sentence_length", 15) > 20:
            speaking_pace = "slow"
        elif comm_analysis.get("avg_sentence_length", 15) < 10:
            speaking_pace = "fast"
        
        # Determine emotional tone
        sentiment = comm_analysis.get("sentiment_polarity", 0)
        if sentiment > 0.3:
            emotional_tone = "positive"
        elif sentiment < -0.3:
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"
        
        return {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "speaking_pace": speaking_pace,
            "emotional_tone": emotional_tone
        }
    
    # === JOB MATCHING ===
    
    def match_resume_to_job(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Match resume data against job requirements."""
        try:
            # Extract data for matching
            resume_skills = self._flatten_skills(resume_data.get("skills", {}))
            resume_experience = resume_data.get("experience", [])
            resume_education = resume_data.get("education", [])
            
            job_required_skills = job_requirements.get("required_skills", [])
            job_preferred_skills = job_requirements.get("preferred_skills", [])
            job_experience_req = job_requirements.get("required_experience", {})
            job_education_req = job_requirements.get("required_education", {})
            
            # Calculate individual scores
            skills_score = self._calculate_skills_match(resume_skills, job_required_skills, job_preferred_skills)
            experience_score = self._calculate_experience_match(resume_experience, job_experience_req)
            education_score = self._calculate_education_match(resume_education, job_education_req)
            
            # Get custom weights or use defaults
            weights = job_requirements.get("matching_weights", settings.score_weights)
            
            # Calculate overall score
            overall_score = int(
                skills_score * weights.get("skills", 0.4) +
                experience_score * weights.get("experience", 0.3) +
                education_score * weights.get("education", 0.2)
            )
            
            # Generate detailed match breakdown
            match_details = {
                "skills_score": skills_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "matching_skills": self._get_matching_skills(resume_skills, job_required_skills + job_preferred_skills),
                "missing_skills": self._get_missing_skills(resume_skills, job_required_skills),
                "strengths": self._identify_strengths(resume_data, job_requirements),
                "concerns": self._identify_concerns(resume_data, job_requirements)
            }
            
            return {
                "overall_score": overall_score,
                "match_details": match_details
            }
        except Exception as e:
            raise Exception(f"Job matching failed: {str(e)}")
    
    def _flatten_skills(self, skills_dict: Dict) -> List[str]:
        """Flatten skills dictionary into a list."""
        all_skills = []
        if isinstance(skills_dict, dict):
            for category, skills in skills_dict.items():
                if isinstance(skills, list):
                    all_skills.extend([skill.lower() for skill in skills])
                elif isinstance(skills, str):
                    all_skills.append(skills.lower())
        elif isinstance(skills_dict, list):
            all_skills = [skill.lower() for skill in skills_dict]
        
        return list(set(all_skills))  # Remove duplicates
    
    def _calculate_skills_match(self, resume_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> int:
        """Calculate skills matching score."""
        if not required_skills and not preferred_skills:
            return 80  # Default score if no skills specified
        
        required_skills_lower = [skill.lower() for skill in required_skills]
        preferred_skills_lower = [skill.lower() for skill in preferred_skills]
        
        # Calculate required skills match
        required_matches = sum(1 for skill in required_skills_lower if skill in resume_skills)
        required_score = (required_matches / max(len(required_skills_lower), 1)) * 100 if required_skills_lower else 100
        
        # Calculate preferred skills match
        preferred_matches = sum(1 for skill in preferred_skills_lower if skill in resume_skills)
        preferred_score = (preferred_matches / max(len(preferred_skills_lower), 1)) * 100 if preferred_skills_lower else 0
        
        # Weighted combination (required skills are more important)
        if required_skills_lower:
            return int(required_score * 0.8 + preferred_score * 0.2)
        else:
            return int(preferred_score)
    
    def _calculate_experience_match(self, resume_experience: List[Dict], job_experience_req: Dict) -> int:
        """Calculate experience matching score."""
        if not job_experience_req:
            return 80  # Default score if no experience requirements
        
        # Simple experience matching based on years and job titles
        required_years = job_experience_req.get("min_years", 0)
        resume_total_years = sum(self._extract_years_from_experience(exp) for exp in resume_experience)
        
        if resume_total_years >= required_years:
            return min(100, 80 + (resume_total_years - required_years) * 5)
        else:
            return max(30, int((resume_total_years / max(required_years, 1)) * 80))
    
    def _calculate_education_match(self, resume_education: List[Dict], job_education_req: Dict) -> int:
        """Calculate education matching score."""
        if not job_education_req:
            return 80  # Default score if no education requirements
        
        # Simple education matching
        required_degree = job_education_req.get("min_degree", "").lower()
        
        if not required_degree:
            return 80
        
        degree_hierarchy = {
            "phd": 5, "doctorate": 5, "master": 4, "bachelor": 3, "associate": 2, "diploma": 1, "certificate": 1
        }
        
        required_level = 0
        for degree, level in degree_hierarchy.items():
            if degree in required_degree:
                required_level = level
                break
        
        max_resume_level = 0
        for edu in resume_education:
            degree_text = edu.get("degree", "").lower()
            for degree, level in degree_hierarchy.items():
                if degree in degree_text:
                    max_resume_level = max(max_resume_level, level)
        
        if max_resume_level >= required_level:
            return min(100, 80 + (max_resume_level - required_level) * 10)
        else:
            return max(40, int((max_resume_level / max(required_level, 1)) * 80))
    
    def _extract_years_from_experience(self, experience: Dict) -> int:
        """Extract years from experience entry."""
        duration = experience.get("duration", "")
        if not duration:
            return 1  # Default 1 year if no duration specified
        
        # Look for year patterns
        year_match = re.search(r'(\d+)\s*years?', duration.lower())
        if year_match:
            return int(year_match.group(1))
        
        return 1  # Default
    
    def _get_matching_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get skills that match between resume and job."""
        job_skills_lower = [skill.lower() for skill in job_skills]
        return [skill for skill in resume_skills if skill in job_skills_lower]
    
    def _get_missing_skills(self, resume_skills: List[str], required_skills: List[str]) -> List[str]:
        """Get required skills that are missing from resume."""
        required_skills_lower = [skill.lower() for skill in required_skills]
        return [skill for skill in required_skills if skill.lower() not in resume_skills]
    
    def _identify_strengths(self, resume_data: Dict, job_requirements: Dict) -> List[str]:
        """Identify candidate strengths for this position."""
        strengths = []
        
        # Check for strong skill matches
        resume_skills = self._flatten_skills(resume_data.get("skills", {}))
        job_skills = job_requirements.get("required_skills", []) + job_requirements.get("preferred_skills", [])
        matching_skills = self._get_matching_skills(resume_skills, job_skills)
        
        if len(matching_skills) >= 3:
            strengths.append(f"Strong technical skills match ({len(matching_skills)} matching skills)")
        
        # Check experience level
        total_years = resume_data.get("total_experience_years", 0)
        if total_years >= 5:
            strengths.append("Experienced professional")
        
        return strengths
    
    def _identify_concerns(self, resume_data: Dict, job_requirements: Dict) -> List[str]:
        """Identify potential concerns for this position."""
        concerns = []
        
        # Check for missing required skills
        resume_skills = self._flatten_skills(resume_data.get("skills", {}))
        missing_skills = self._get_missing_skills(resume_skills, job_requirements.get("required_skills", []))
        
        if len(missing_skills) > 2:
            concerns.append(f"Missing {len(missing_skills)} required skills")
        
        # Check experience gap
        required_years = job_requirements.get("required_experience", {}).get("min_years", 0)
        total_years = resume_data.get("total_experience_years", 0)
        
        if required_years > 0 and total_years < required_years * 0.8:
            concerns.append("Below preferred experience level")
        
        return concerns


# Global AI service instance
ai_service = AIService()