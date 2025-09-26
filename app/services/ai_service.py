"""
Main AI service that combines all components.
Modular design with separated concerns for resume analysis, voice processing, and job matching.
"""

from typing import Dict, Optional
from .resume_analyzer import resume_analyzer
from .voice_analyzer import voice_analyzer
from .job_matcher import job_matcher


class AIService:
    """Main AI service combining all analysis components."""

    def __init__(self):
        """Initialize AI service with all components."""
        self.resume_analyzer = resume_analyzer
        self.voice_analyzer = voice_analyzer
        self.job_matcher = job_matcher

    # === FILE PROCESSING (for routes) ===

    def extract_text_from_file(self, file_path: str, mime_type: str) -> str:
        """Extract text from files - delegates to resume analyzer."""
        return self.resume_analyzer.extract_text_from_file(file_path, mime_type)

    # === RESUME ANALYSIS (for routes) ===

    def analyze_resume(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume from text - sync version."""
        return self.resume_analyzer.analyze_resume(text, target_industry)

    def analyze_resume_from_text(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume from text - synchronous for route compatibility."""
        return self.resume_analyzer.analyze_resume_from_text(text, target_industry)

    async def analyze_resume_from_text_async(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume from text - async version."""
        return self.resume_analyzer.analyze_resume_from_text_async(text, target_industry)

    # === VOICE ANALYSIS (for routes) ===

    def analyze_voice_resume(self, audio_file_path: str) -> Dict:
        """Analyze voice resume - delegates to voice analyzer."""
        return self.voice_analyzer.analyze_voice_resume(audio_file_path)

    def transcribe_audio(self, file_path: str):
        """Transcribe audio file."""
        return self.voice_analyzer.transcribe_audio(file_path)

    # === JOB MATCHING (for routes) ===

    async def match_resume_to_job(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Match resume to job - delegates to job matcher."""
        return await self.job_matcher.match_resume_to_job(resume_data, job_requirements)

    # === UTILITY METHODS (for backward compatibility) ===

    def get_resume_summary(self, resume_data: Dict) -> Dict:
        """Get quick resume summary."""
        contact_info = resume_data.get("contact_info", {})
        return {
            "name": contact_info.get("name", "Unknown"),
            "email": contact_info.get("email", "Not provided"),
            "phone": contact_info.get("phone", "Not provided"),
            "total_skills": len(resume_data.get("skills", [])),
            "experience_years": resume_data.get("total_experience_years", 0),
            "has_contact_info": bool(contact_info.get("name") or contact_info.get("email")),
        }


# Global AI service instance
ai_service = AIService()