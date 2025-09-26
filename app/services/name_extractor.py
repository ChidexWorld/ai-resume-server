"""
Name extraction component with general rules.
"""

import re
from typing import Optional


class NameExtractor:
    """Handles name extraction with general, flexible rules."""

    def extract_name(self, text: str) -> Optional[str]:
        """Extract name using general rules that work broadly."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if not lines:
            return None

        # Strategy 1: Check first 3 lines (most common location)
        for line in lines[:3]:
            cleaned_name = self._clean_name_line(line)
            if self._is_likely_name(cleaned_name):
                return cleaned_name

        # Strategy 2: Pattern-based search in first 10 lines
        name_patterns = [
            r'\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20})\b',  # First Last
            r'\b([A-Z][a-z]{1,20}\s+[A-Z]\.\s+[A-Z][a-z]{1,20})\b',  # First M. Last
            r'\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20})\b',  # First Middle Last
        ]

        for line in lines[:10]:
            for pattern in name_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if self._is_likely_name(match):
                        return match

        return None

    def _clean_name_line(self, line: str) -> str:
        """Clean a line to extract potential name."""
        if not line:
            return ""

        prefixes = ['mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'professor', 'sir', 'madam']
        suffixes = ['jr.', 'sr.', 'ii', 'iii', 'iv', 'phd', 'md', 'cpa', 'esq.']

        cleaned = line.strip()

        # Remove prefixes
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix + ' '):
                cleaned = cleaned[len(prefix):].strip()
                break

        # Remove suffixes
        for suffix in suffixes:
            if cleaned.lower().endswith(' ' + suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                break

        return ' '.join(cleaned.split())

    def _is_likely_name(self, candidate: str) -> bool:
        """Check if text is likely to be a person's name."""
        if not candidate or len(candidate.strip()) < 2:
            return False

        candidate = candidate.strip()

        # Must contain only letters, spaces, periods, hyphens, apostrophes
        if not re.match(r'^[A-Za-z\s\.\-\']+$', candidate):
            return False

        parts = [part.strip() for part in candidate.split() if part.strip()]

        # Must have 1-5 parts
        if len(parts) < 1 or len(parts) > 5:
            return False

        # If only one part, should be at least 3 characters
        if len(parts) == 1 and len(parts[0]) < 3:
            return False

        # Each part reasonable length
        for part in parts:
            if len(part) < 1 or len(part) > 25:
                return False

        # Reject obvious non-names
        rejected_patterns = [
            r'\b(resume|cv|curriculum|vitae)\b',
            r'\b(email|phone|tel|fax|address|website)\b',
            r'\b(contact|information|details)\b',
            r'\b(objective|summary|profile|about)\b',
            r'\b(experience|education|skills|projects)\b',
            r'\b(manager|engineer|developer|analyst|director)\b',
            r'\b(company|corporation|inc|ltd|llc)\b',
            r'\d+',
        ]

        candidate_lower = candidate.lower()
        for pattern in rejected_patterns:
            if re.search(pattern, candidate_lower):
                return False

        return True


# Global instance
name_extractor = NameExtractor()