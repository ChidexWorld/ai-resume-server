"""
Job matching component for resume-job compatibility analysis.
"""

from typing import Dict, List


class JobMatcher:
    """Handles job matching and compatibility analysis."""

    def __init__(self):
        self._sentence_model = None

    @property
    def sentence_model(self):
        """Lazy load sentence transformer model."""
        if self._sentence_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                raise Exception("sentence-transformers not installed. Please install it for job matching.")
        return self._sentence_model

    async def match_resume_to_job(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Match resume to job requirements."""
        try:
            # Extract skills and experience
            resume_skills = resume_data.get("skills", [])
            resume_experience = resume_data.get("experience", [])

            # Get job requirements
            required_skills = job_requirements.get("required_skills", [])
            preferred_skills = job_requirements.get("preferred_skills", [])

            # Calculate scores
            skills_score = self._calculate_skills_match(resume_skills, required_skills, preferred_skills)
            experience_score = self._calculate_experience_match(resume_experience, job_requirements)

            # Overall score
            overall_score = int((skills_score * 0.6) + (experience_score * 0.4))

            # Generate analysis
            matching_details = self._generate_match_details(
                resume_data, job_requirements, skills_score, experience_score
            )

            return {
                "overall_match_score": overall_score,
                "matching_details": matching_details
            }

        except Exception as e:
            raise Exception(f"Job matching failed: {str(e)}")

    def _calculate_skills_match(self, resume_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> int:
        """Calculate skills matching score."""
        if not required_skills and not preferred_skills:
            return 75

        resume_skills_lower = [skill.lower() for skill in resume_skills]

        # Required skills match
        required_matches = 0
        for skill in required_skills:
            if skill.lower() in resume_skills_lower:
                required_matches += 1

        required_score = (required_matches / max(len(required_skills), 1)) * 100 if required_skills else 100

        # Preferred skills match
        preferred_matches = 0
        for skill in preferred_skills:
            if skill.lower() in resume_skills_lower:
                preferred_matches += 1

        preferred_score = (preferred_matches / max(len(preferred_skills), 1)) * 100 if preferred_skills else 0

        # Weighted score
        if required_skills:
            final_score = (required_score * 0.8) + (preferred_score * 0.2)
        else:
            final_score = preferred_score

        return int(min(100, max(0, final_score)))

    def _calculate_experience_match(self, resume_experience: List, job_requirements: Dict) -> int:
        """Calculate experience matching score."""
        # Basic experience scoring
        if not resume_experience:
            return 50

        # Look for years in job requirements
        min_years = job_requirements.get("min_years", 0)

        # Estimate experience from resume
        experience_years = 0
        for exp in resume_experience:
            if isinstance(exp, str) and "year" in exp.lower():
                # Extract years from text
                import re
                years_match = re.search(r'(\d+)', exp)
                if years_match:
                    experience_years = max(experience_years, int(years_match.group(1)))

        if experience_years >= min_years:
            return min(100, 80 + (experience_years - min_years) * 5)
        else:
            return max(30, int((experience_years / max(min_years, 1)) * 80))

    def _generate_match_details(self, resume_data: Dict, job_requirements: Dict, skills_score: int, experience_score: int) -> Dict:
        """Generate detailed matching analysis."""
        resume_skills = resume_data.get("skills", [])
        required_skills = job_requirements.get("required_skills", [])

        # Find matching skills
        matching_skills = []
        missing_skills = []

        resume_skills_lower = [skill.lower() for skill in resume_skills]

        for skill in required_skills:
            if skill.lower() in resume_skills_lower:
                matching_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Generate strengths and concerns
        strengths = []
        concerns = []

        if skills_score >= 80:
            strengths.append("Excellent skills match")
        elif skills_score >= 60:
            strengths.append("Good skills alignment")

        if experience_score >= 80:
            strengths.append("Strong experience background")

        if skills_score < 60:
            concerns.append("Some required skills missing")

        if experience_score < 60:
            concerns.append("May need more experience")

        # Recommendations
        recommendations = []
        if missing_skills:
            recommendations.append(f"Consider learning: {', '.join(missing_skills[:3])}")

        if experience_score < 70:
            recommendations.append("Gain more relevant experience")

        return {
            "skills_score": skills_score,
            "experience_score": experience_score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "concerns": concerns,
            "recommendations": recommendations
        }


# Global instance
job_matcher = JobMatcher()