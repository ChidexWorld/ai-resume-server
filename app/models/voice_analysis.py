"""
Voice analysis model for employee audio uploads and speech analysis.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class VoiceStatus(str, enum.Enum):
    """Voice analysis processing status enumeration."""
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceAnalysis(Base):
    """
    Voice analysis model for storing employee voice recordings and AI analysis results.
    """
    
    __tablename__ = "voice_analyses"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to employee
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Processing status
    status = Column(Enum(VoiceStatus), default=VoiceStatus.UPLOADED, nullable=False)
    
    # Speech-to-text results
    transcript = Column(Text, nullable=True)
    transcript_confidence = Column(Float, nullable=True)  # 0-1 confidence score
    
    # Speech analysis results (JSON fields)
    speech_features = Column(JSON, nullable=True)  # Technical speech analysis
    communication_analysis = Column(JSON, nullable=True)  # Communication skills analysis
    language_analysis = Column(JSON, nullable=True)  # Language and vocabulary analysis
    
    # Computed scores (0-100 scale)
    clarity_score = Column(Integer, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    fluency_score = Column(Integer, nullable=True)
    vocabulary_score = Column(Integer, nullable=True)
    overall_communication_score = Column(Integer, nullable=True)
    
    # Communication insights
    strengths = Column(JSON, nullable=True)  # List of communication strengths
    areas_for_improvement = Column(JSON, nullable=True)  # Areas to improve
    speaking_pace = Column(String(20), nullable=True)  # slow, normal, fast
    
    # Professional assessment
    professional_language_usage = Column(Integer, nullable=True)  # 0-100 score
    emotional_tone = Column(String(50), nullable=True)  # confident, nervous, enthusiastic, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    transcribed_at = Column(DateTime, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Active status (for soft deletion)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employee = relationship("User", back_populates="voice_analyses")
    
    @property
    def is_completed(self) -> bool:
        """Check if voice analysis is completed."""
        return self.status == VoiceStatus.COMPLETED
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration string (MM:SS)."""
        if not self.duration:
            return "Unknown"
        
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def speaking_rate_wpm(self) -> float:
        """Calculate speaking rate in words per minute."""
        if not self.transcript or not self.duration:
            return 0.0
        
        word_count = len(self.transcript.split())
        minutes = self.duration / 60
        return round(word_count / minutes, 1) if minutes > 0 else 0.0
    
    def update_status(self, status: VoiceStatus):
        """Update the processing status."""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == VoiceStatus.COMPLETED:
            self.analyzed_at = datetime.utcnow()
    
    def set_transcript(self, transcript: str, confidence: float = None):
        """Set the speech-to-text transcript."""
        self.transcript = transcript
        self.transcript_confidence = confidence
        self.transcribed_at = datetime.utcnow()
        self.update_status(VoiceStatus.ANALYZING)
    
    def set_analysis_results(self, analysis_data: dict):
        """Set the complete voice analysis results."""
        # Set technical analysis
        self.speech_features = analysis_data.get("speech_features", {})
        self.communication_analysis = analysis_data.get("communication_analysis", {})
        self.language_analysis = analysis_data.get("language_analysis", {})
        
        # Set computed scores
        self.clarity_score = analysis_data.get("clarity_score")
        self.confidence_score = analysis_data.get("confidence_score")
        self.fluency_score = analysis_data.get("fluency_score")
        self.vocabulary_score = analysis_data.get("vocabulary_score")
        self.overall_communication_score = analysis_data.get("overall_communication_score")
        
        # Set insights
        self.strengths = analysis_data.get("strengths", [])
        self.areas_for_improvement = analysis_data.get("areas_for_improvement", [])
        self.speaking_pace = analysis_data.get("speaking_pace")
        self.professional_language_usage = analysis_data.get("professional_language_usage")
        self.emotional_tone = analysis_data.get("emotional_tone")
        
        # Update status
        self.update_status(VoiceStatus.COMPLETED)
    
    def get_communication_summary(self) -> dict:
        """Get summarized communication assessment."""
        return {
            "overall_score": self.overall_communication_score,
            "clarity": self.clarity_score,
            "confidence": self.confidence_score,
            "fluency": self.fluency_score,
            "vocabulary": self.vocabulary_score,
            "professional_language": self.professional_language_usage,
            "speaking_rate": self.speaking_rate_wpm,
            "speaking_pace": self.speaking_pace,
            "emotional_tone": self.emotional_tone,
            "strengths": self.strengths or [],
            "improvements": self.areas_for_improvement or []
        }
    
    def get_transcript_stats(self) -> dict:
        """Get transcript statistics."""
        if not self.transcript:
            return {"word_count": 0, "sentence_count": 0, "avg_words_per_sentence": 0}
        
        words = self.transcript.split()
        sentences = self.transcript.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_words_per_sentence": round(len(words) / max(len(sentences), 1), 1),
            "speaking_rate_wpm": self.speaking_rate_wpm
        }
    
    def soft_delete(self):
        """Soft delete the voice analysis."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_analysis: bool = True) -> dict:
        """Convert voice analysis to dictionary."""
        voice_data = {
            "id": self.id,
            "employee_id": self.employee_id,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "duration": self.duration,
            "duration_formatted": self.duration_formatted,
            "mime_type": self.mime_type,
            "status": self.status.value,
            "is_completed": self.is_completed,
            "transcript_confidence": self.transcript_confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "transcribed_at": self.transcribed_at.isoformat() if self.transcribed_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }
        
        if include_analysis and self.is_completed:
            voice_data.update({
                "transcript": self.transcript,
                "speech_features": self.speech_features,
                "communication_analysis": self.communication_analysis,
                "language_analysis": self.language_analysis,
                "communication_summary": self.get_communication_summary(),
                "transcript_stats": self.get_transcript_stats()
            })
        
        return voice_data
    
    def __repr__(self):
        return f"<VoiceAnalysis {self.original_filename} (Employee: {self.employee_id})>"