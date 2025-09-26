"""
Voice analysis component for audio processing.
"""

from typing import Dict, Tuple
from .resume_analyzer import resume_analyzer


class VoiceAnalyzer:
    """Handles voice/audio analysis and transcription."""

    def __init__(self):
        self._whisper_model = None

    @property
    def whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None:
            try:
                import whisper
                self._whisper_model = whisper.load_model("base")
            except ImportError:
                raise Exception("Whisper not installed. Please install openai-whisper.")
        return self._whisper_model

    def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
        """Transcribe audio file to text."""
        try:
            result = self.whisper_model.transcribe(file_path)
            transcript = result["text"]
            confidence = self._estimate_confidence(transcript)
            return transcript, confidence
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")

    def _estimate_confidence(self, transcript: str) -> float:
        """Estimate transcript confidence based on text quality."""
        if not transcript or len(transcript.strip()) < 10:
            return 0.3

        word_count = len(transcript.split())

        # Check quality indicators
        coherence_score = 0
        if word_count > 20:
            coherence_score += 0.3
        if any(char in transcript for char in ".!?"):
            coherence_score += 0.2
        if len([w for w in transcript.split() if len(w) > 3]) / word_count > 0.5:
            coherence_score += 0.3

        base_confidence = 0.5 + coherence_score
        return min(0.95, max(0.3, base_confidence))

    def analyze_voice_resume(self, audio_file_path: str) -> Dict:
        """Complete voice resume analysis."""
        try:
            # Transcribe audio
            transcript, confidence = self.transcribe_audio(audio_file_path)

            # Analyze transcribed text
            resume_data = resume_analyzer.analyze_resume_from_text(transcript)

            # Add voice-specific data
            resume_data.update({
                "transcript": transcript,
                "transcription_confidence": confidence,
                "input_type": "voice",
                "communication_scores": {
                    "clarity_score": 70,
                    "confidence_score": 70,
                    "fluency_score": 70,
                    "vocabulary_score": 70
                }
            })

            return resume_data
        except Exception as e:
            raise Exception(f"Voice resume analysis failed: {str(e)}")


# Global instance
voice_analyzer = VoiceAnalyzer()