"""
AI service for resume parsing, voice analysis, and job matching.
Enhanced to support manual datasets and general industries beyond software engineering.
"""

import os
import re
import json
import whisper
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from textblob import TextBlob
import PyPDF2
import pdfplumber
from docx import Document
from app.config import settings
from app.services.dataset_manager import DatasetManager


class AIService:
    """Enhanced AI service for all industries with manual dataset support."""

    def __init__(self, dataset_path: str = "datasets/"):
        """Initialize AI models and dataset manager."""
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

    @property
    def sentence_model(self):
        """Lazy load sentence transformer model."""
        if self._sentence_model is None:
            self._sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._sentence_model

    @property
    def nlp_model(self):
        """Lazy load spaCy model."""
        if self._nlp_model is None:
            try:
                self._nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                os.system("python -m spacy download en_core_web_sm")
                self._nlp_model = spacy.load("en_core_web_sm")
        return self._nlp_model

    # === DOCUMENT PROCESSING === (Same as before)

    def extract_text_from_file(self, file_path: str, mime_type: str) -> str:
        """Extract text from various file types."""
        try:
            if mime_type == "application/pdf":
                return self._extract_from_pdf(file_path)
            elif mime_type in [
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]:
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
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            with open(file_path, "rb") as file:
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
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    # === ENHANCED RESUME ANALYSIS ===

    def analyze_resume(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Enhanced resume analysis with industry detection and manual datasets."""
        try:
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
        except Exception as e:
            raise Exception(f"Resume analysis failed: {str(e)}")

    def _extract_contact_info(self, text: str, doc) -> Dict:
        """Extract contact information from resume."""
        contact_info = {}

        # --- Extract email ---
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]

        # --- Extract phone (enhanced patterns for international) ---
        phone_patterns = [
            # US format
            r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            # Nigerian format (e.g., 09125189296, +234-912-518-9296)
            r"(?:\+?234[-.\s]?)?(?:0)?([0-9]{1,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})",
            # General international format
            r"(?:\+?[0-9]{1,3}[-.\s]?)?(?:\(?[0-9]{2,4}\)?[-.\s]?)?[0-9]{3,4}[-.\s]?[0-9]{3,4}",
            # Nigerian 11-digit format
            r"(0[789][01][0-9]{8})",
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                if isinstance(phones[0], tuple):
                    contact_info["phone"] = (
                        f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
                    )
                else:
                    contact_info["phone"] = phones[0]
                break

        # --- Extract name using NER and heuristics ---
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        if persons:
            # Look only in the first few lines (common place for names, e.g., resumes, forms)
            first_lines = "\n".join(text.split("\n")[:5])

            for person in persons:
                if person in first_lines:
                    contact_info["name"] = person
                    break

            # If no person found in first lines → fallback to first detected person
            if "name" not in contact_info:
                contact_info["name"] = persons[0]

        else:
            # --- Heuristic fallback ---
            tokens = text.split()
            for i, token in enumerate(tokens):
                # Check for titles like Mr., Mrs., Dr.
                if token in ["Mr.", "Mrs.", "Dr."] and i + 1 < len(tokens):
                    possible_name = " ".join(tokens[i + 1 : i + 3])
                    contact_info["name"] = possible_name
                    break

                # Check for "Name:" keyword
                if token.lower().startswith("name:") and i + 1 < len(tokens):
                    possible_name = " ".join(tokens[i + 1 : i + 3])
                    contact_info["name"] = possible_name
                    break

        # --- Extract location ---
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        if locations:
            contact_info["location"] = locations[0]
        else:
            # Enhanced location detection for African addresses
            location_patterns = [
                r"([A-Z][a-z]+,?\s*[A-Z][a-z]+\s*(?:STATE|State)?)",  # City, State
                r"(\d+\s+[A-Z][a-z\s]+(?:Street|St|Road|Rd|Avenue|Ave)),?\s*([A-Z][a-z]+)",  # Address pattern
                r"([A-Z][a-z]+),?\s*([A-Z]{2}\s*\d{5,6})",  # City, PostalCode
            ]
            for pattern in location_patterns:
                location_match = re.search(pattern, text)
                if location_match:
                    contact_info["location"] = location_match.group(0).strip()
                    break

        # --- Extract LinkedIn ---
        linkedin_pattern = r"linkedin\.com/in/[\w-]+"
        linkedin_matches = re.findall(linkedin_pattern, text, flags=re.IGNORECASE)
        if linkedin_matches:
            contact_info["linkedin"] = f"https://{linkedin_matches[0]}"

        return contact_info

    def _extract_skills_enhanced(
        self, text: str, industry: str
    ) -> Dict[str, List[str]]:
        """Enhanced skills extraction using manual datasets."""
        text_lower = text.lower()
        found_skills = {}

        # Get industry-specific skills
        industry_skills = self.dataset_manager.get_skills_by_industry(industry)

        # Also include general skills
        all_skills = self.dataset_manager.get_all_skills()

        # Check for skills presence
        for skill in set(industry_skills + all_skills):
            if skill.lower() in text_lower:
                # Find the category for this skill
                category = self._find_skill_category(skill, industry)
                if category not in found_skills:
                    found_skills[category] = []
                found_skills[category].append(skill.title())

        # Remove duplicates
        for category in found_skills:
            found_skills[category] = list(set(found_skills[category]))

        return found_skills

    def _find_skill_category(self, skill: str, industry: str) -> str:
        """Find the category for a specific skill."""
        skills_db = self.dataset_manager.skills_db

        # First check in the specific industry
        if industry in skills_db:
            for category, skills in skills_db[industry].items():
                if isinstance(skills, list) and skill.lower() in [
                    s.lower() for s in skills
                ]:
                    return category

        # Then check in all industries
        for ind, categories in skills_db.items():
            if isinstance(categories, dict):
                for category, skills in categories.items():
                    if isinstance(skills, list) and skill.lower() in [
                        s.lower() for s in skills
                    ]:
                        return category

        return "other"

    def _extract_experience_enhanced(self, text: str, doc) -> List[Dict]:
        """Enhanced experience extraction using dataset manager."""
        experience = []
        lines = text.split("\n")

        # Get job titles from dataset manager
        all_job_titles = self.dataset_manager.get_all_job_titles()

        # Create dynamic patterns based on dataset
        job_title_patterns = []

        # Add patterns for each job title in the dataset
        for title in all_job_titles:
            escaped_title = re.escape(title)
            job_title_patterns.extend([
                rf"^({escaped_title})",
                rf"^({escaped_title})\s*,\s*(.+)",
                rf"^({escaped_title})\s+at\s+(.+)",
                rf"^((?:Senior|Junior|Lead|Associate|Principal)\s+{escaped_title})",
            ])

        # Add general patterns for common title structures
        job_title_patterns.extend([
            r"^([A-Z][A-Za-z\s&]+(?:Designer|Manager|Analyst|Consultant|Trainer|Guard|Developer|Engineer|Director|Specialist|Coordinator|Assistant|Associate|Lead|Senior|Junior|Head|VP|CEO|CTO|CFO|Teacher|Instructor|Tutor|Educator))",
            r"^([A-Z][A-Za-z\s&]+ at [A-Z][A-Za-z\s&,]+)",
            r"^([A-Z][A-Za-z\s&]+), ([A-Z][A-Za-z\s&,]+)",
            r"^([A-Z][A-Za-z\s&]*(?:Mathematics|Computer|Science|English|Physics|Chemistry|Biology)\s+Teacher)",
            r"^([A-Z][A-Za-z\s&]*(?:Deputy|Senior|Assistant)?\s*(?:Prefect|Principal|Head))",
        ])

        # Enhanced date patterns for experience
        date_patterns = [
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*[—–-]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present|Current)",
            r"(\d{4})\s*[—–-]+\s*(\d{4}|Present|Current)",
            r"(\d{1,2}/\d{4})\s*[—–-]+\s*(\d{1,2}/\d{4}|Present|Current)",
        ]

        # Extract organizations with better accuracy
        org_entities = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        current_job = {}
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line or len(line) < 3:
                i += 1
                continue

            # Look for job title patterns
            job_match = None
            for pattern in job_title_patterns:
                job_match = re.search(pattern, line)
                if job_match:
                    break

            if job_match:
                # Save previous job if exists
                if current_job and ("title" in current_job or "company" in current_job):
                    experience.append(current_job)

                # Parse job title and company
                if " at " in line:
                    parts = line.split(" at ", 1)
                    current_job = {
                        "title": parts[0].strip(),
                        "company": parts[1].strip()
                    }
                elif ", " in line and len(line.split(", ")) == 2:
                    parts = line.split(", ", 1)
                    current_job = {
                        "title": parts[0].strip(),
                        "company": parts[1].strip()
                    }
                else:
                    current_job = {"title": line}

            # Look for date ranges in the next few lines
            elif any(re.search(pattern, line) for pattern in date_patterns):
                if current_job:
                    current_job["duration"] = line
                    current_job["years_calculated"] = self._calculate_years_from_duration(line)

            # Look for company names (if not already set)
            elif ("company" not in current_job and
                  any(org.lower() in line.lower() for org in org_entities) and
                  not line.startswith(("•", "-", "*"))):
                if current_job:
                    current_job["company"] = line

            # Collect responsibilities/achievements
            elif line.startswith(("•", "-", "*", "◦")) and current_job:
                if "responsibilities" not in current_job:
                    current_job["responsibilities"] = []
                responsibility = line.lstrip("•-*◦ ").strip()
                if len(responsibility) > 10:  # Filter out very short lines
                    current_job["responsibilities"].append(responsibility)

            # Look for location information
            elif ("location" not in current_job and
                  re.search(r"[A-Z][a-z]+,\s*[A-Z]{2,}|[A-Z][a-z]+,\s*[A-Z][a-z]+", line) and
                  not line.startswith(("•", "-", "*"))):
                if current_job:
                    current_job["location"] = line

            i += 1

        # Add the last job
        if current_job and ("title" in current_job or "company" in current_job):
            experience.append(current_job)

        # Clean up and validate experience entries
        validated_experience = []
        for exp in experience:
            if "title" in exp and len(exp["title"]) > 2:
                # Calculate experience years if duration exists
                if "duration" in exp and "years_calculated" not in exp:
                    exp["years_calculated"] = self._calculate_years_from_duration(exp["duration"])
                validated_experience.append(exp)

        return validated_experience[:8]  # Return top 8 experiences

    def _calculate_years_from_duration(self, duration_text: str) -> float:
        """Calculate years of experience from duration text."""
        try:
            duration_lower = duration_text.lower()

            # Enhanced date range patterns
            patterns = [
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[—–-]+\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})",
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[—–-]+\s*(present|current)",
                r"(\d{4})\s*[—–-]+\s*(\d{4})",
                r"(\d{4})\s*[—–-]+\s*(present|current)",
                r"(\d{1,2})/(\d{4})\s*[—–-]+\s*(\d{1,2})/(\d{4})",
                r"(\d{1,2})/(\d{4})\s*[—–-]+\s*(present|current)",
            ]

            current_year = 2025

            for pattern in patterns:
                match = re.search(pattern, duration_lower)
                if match:
                    groups = match.groups()

                    if "present" in duration_lower or "current" in duration_lower:
                        # Handle "X - Present" format
                        if len(groups) >= 2:
                            if groups[1].isdigit():
                                start_year = int(groups[1])
                            else:
                                start_year = int(groups[0]) if groups[0].isdigit() else current_year
                            return round((current_year - start_year) + 0.5, 1)
                    else:
                        # Handle "X - Y" format
                        if len(groups) >= 4:
                            start_year = int(groups[1]) if groups[1].isdigit() else current_year
                            end_year = int(groups[3]) if groups[3].isdigit() else current_year
                        elif len(groups) >= 2:
                            start_year = int(groups[0]) if groups[0].isdigit() else current_year
                            end_year = int(groups[1]) if groups[1].isdigit() else current_year
                        else:
                            continue

                        if end_year >= start_year:
                            return round(end_year - start_year + 0.5, 1)

            # Fallback: look for explicit year mentions
            year_match = re.search(r"(\d+)\s*years?", duration_lower)
            if year_match:
                return float(year_match.group(1))

            return 1.0  # Default 1 year if can't parse

        except Exception:
            return 1.0

    def _contains_date_pattern(self, text: str) -> bool:
        """Check if text contains date patterns."""
        date_patterns = [
            r"\b\d{4}\b",  # Year
            r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b",  # Month abbreviations
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",  # Full months
            r"\d{1,2}/\d{4}",  # MM/YYYY
            r"\d{1,2}-\d{4}",  # MM-YYYY
        ]

        for pattern in date_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _extract_education_enhanced(self, text: str, doc) -> List[Dict]:
        """Enhanced education extraction using dataset manager."""
        education = []
        lines = text.split("\n")

        # Get education keywords from dataset manager
        degree_types = self.dataset_manager.education_keywords.get("degree_types", [])
        institution_types = self.dataset_manager.education_keywords.get("institutions", [])
        field_types = self.dataset_manager.education_keywords.get("fields", [])
        honors_types = self.dataset_manager.education_keywords.get("honors", [])

        # Create dynamic degree patterns based on dataset
        degree_patterns = []
        for degree in degree_types:
            escaped_degree = re.escape(degree)
            degree_patterns.extend([
                rf"({escaped_degree})",
                rf"({escaped_degree}\s+(?:of|in)\s+[\w\s]+)",
                rf"({escaped_degree}\s+degree)",
            ])

        # Create institution patterns from dataset
        institution_patterns = []
        for inst_type in institution_types:
            escaped_inst = re.escape(inst_type)
            institution_patterns.extend([
                rf"(?:{escaped_inst})\s+(?:of\s+)?[\w\s,]+",
                rf"[\w\s]+\s+(?:{escaped_inst})",
            ])

        # Date range patterns for education
        education_date_patterns = [
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*[—–-]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present|Current)",
            r"(\d{4})\s*[—–-]+\s*(\d{4}|Present|Current)",
            r"(\d{1,2}/\d{4})\s*[—–-]+\s*(\d{1,2}/\d{4}|Present|Current)",
            r"(?:Graduated|Completed|Finished).*?(\d{4})",
            r"Class\s+of\s+(\d{4})",
        ]

        current_education = {}

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Skip if it's clearly an employment section
            if any(keyword in line_lower for keyword in ["employment", "experience", "work history", "career"]):
                continue

            # Look for degree patterns
            degree_found = False
            for pattern in degree_patterns:
                degree_match = re.search(pattern, line, re.IGNORECASE)
                if degree_match:
                    # Save previous education if exists
                    if current_education and "degree" in current_education:
                        education.append(current_education)

                    current_education = {
                        "degree": degree_match.group(1).strip(),
                        "raw_text": line
                    }

                    # Look for institution in the same line
                    remaining_text = line[degree_match.end():].strip()
                    if remaining_text:
                        # Remove leading comma or "at"
                        remaining_text = re.sub(r"^[,\s]*(?:at\s+|from\s+)?", "", remaining_text)
                        if remaining_text:
                            current_education["institution"] = remaining_text

                    degree_found = True
                    break

            # Look for institution if we have a degree but no institution
            if not degree_found and current_education and "institution" not in current_education:
                for pattern in institution_patterns:
                    inst_match = re.search(pattern, line, re.IGNORECASE)
                    if inst_match:
                        current_education["institution"] = inst_match.group().strip()
                        break

            # Look for dates
            if current_education:
                for pattern in education_date_patterns:
                    date_match = re.search(pattern, line, re.IGNORECASE)
                    if date_match:
                        current_education["duration"] = line
                        groups = date_match.groups()

                        # Extract graduation year
                        if len(groups) >= 2:
                            end_date = groups[1] if groups[1] not in ["Present", "Current"] else "2025"
                            if end_date.isdigit():
                                current_education["graduation_year"] = int(end_date)
                        elif len(groups) == 1 and groups[0].isdigit():
                            current_education["graduation_year"] = int(groups[0])
                        break

            # Look for GPA
            if current_education:
                gpa_match = re.search(r"gpa:?\s*(\d+\.?\d*)", line_lower)
                if gpa_match:
                    current_education["gpa"] = float(gpa_match.group(1))

            # Look for honors/achievements
            if current_education:
                honors_keywords = ["magna cum laude", "summa cum laude", "cum laude", "honors", "dean's list", "distinction"]
                for honor in honors_keywords:
                    if honor in line_lower:
                        if "honors" not in current_education:
                            current_education["honors"] = []
                        current_education["honors"].append(honor.title())

            # Look for relevant coursework or specialization
            if current_education and any(keyword in line_lower for keyword in ["major", "specialization", "concentration", "focus"]):
                spec_match = re.search(r"(?:major|specialization|concentration|focus)(?:\s*:)?\s*(.+)", line, re.IGNORECASE)
                if spec_match:
                    current_education["specialization"] = spec_match.group(1).strip()

        # Add the last education entry
        if current_education and "degree" in current_education:
            education.append(current_education)

        # Clean and validate education entries
        validated_education = []
        for edu in education:
            if "degree" in edu and len(edu["degree"]) > 2:
                # Determine education level
                degree_lower = edu["degree"].lower()
                if any(keyword in degree_lower for keyword in ["phd", "ph.d", "doctorate"]):
                    edu["level"] = "Doctorate"
                elif any(keyword in degree_lower for keyword in ["master", "mba", "m.s", "m.a"]):
                    edu["level"] = "Master's"
                elif any(keyword in degree_lower for keyword in ["bachelor", "b.s", "b.a"]):
                    edu["level"] = "Bachelor's"
                elif any(keyword in degree_lower for keyword in ["associate"]):
                    edu["level"] = "Associate"
                elif any(keyword in degree_lower for keyword in ["certificate", "certification"]):
                    edu["level"] = "Certificate"
                else:
                    edu["level"] = "Other"

                validated_education.append(edu)

        # Sort by education level (highest first)
        level_order = {"Doctorate": 5, "Master's": 4, "Bachelor's": 3, "Associate": 2, "Certificate": 1, "Other": 0}
        validated_education.sort(key=lambda x: level_order.get(x["level"], 0), reverse=True)

        return validated_education[:5]  # Return top 5 education entries

    def _extract_certifications_enhanced(self, text: str) -> List[Dict]:
        """Enhanced certification extraction using dataset manager."""
        certifications = []
        lines = text.split("\n")

        # Get certifications from dataset manager
        all_certifications = []
        cert_organizations = []

        for industry, certs in self.dataset_manager.certifications_db.items():
            all_certifications.extend(certs)

        # Extract organization names from certifications
        for cert in all_certifications:
            words = cert.split()
            for word in words:
                if len(word) > 2 and word.istitle():
                    cert_organizations.append(word)

        # Add common certification organizations
        cert_organizations.extend([
            "Adobe", "Microsoft", "Google", "Amazon", "AWS", "Cisco", "Oracle", "IBM",
            "Salesforce", "PMI", "ITIL", "CompTIA", "ACE", "NASM", "ACSM", "NCCA",
            "Red Cross", "American Heart Association", "CPR", "First Aid", "OSHA",
            "PMP", "Scrum", "Agile", "Six Sigma", "PRINCE2", "CISA", "CISSP"
        ])

        # Remove duplicates
        cert_organizations = list(set(cert_organizations))

        # Create dynamic certification patterns based on dataset
        cert_patterns = []

        # Add patterns for each certification in the dataset
        for cert in all_certifications:
            escaped_cert = re.escape(cert)
            cert_patterns.extend([
                rf"({escaped_cert})",
                rf"({escaped_cert})\s+(?:certificate|certification|license)",
                rf"(?:certificate|certification|license)\s+(?:in\s+)?({escaped_cert})",
            ])

        # Add general patterns
        cert_patterns.extend([
            r"([\w\s]+)\s*(?:Certified|Certificate|Certification|Licensed|License|Credential)",
            r"(?:Certified|Licensed)\s+([\w\s]+?)(?:\s*,|\s*$|\s*\n)",
            r"([\w\s]+)\s+(?:Certification|Certificate|License)(?:\s+Program)?",
            r"(?:Certificate|Certification|License)\s+(?:in\s+)?([\w\s]+)",
        ])

        # Date patterns for certifications
        cert_date_patterns = [
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s*[—–-]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present|Current)",
            r"(\d{4})\s*[—–-]+\s*(\d{4}|Present|Current)",
            r"(?:Obtained|Earned|Received|Completed).*?(\d{4})",
            r"(?:Valid|Expires?).*?(\d{4})",
            r"\b(\d{4})\b(?:\s*[—–-]\s*(\d{4}|Present|Current))?",
        ]

        current_cert = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Skip if it's clearly an education section (different from certifications)
            if any(keyword in line_lower for keyword in ["bachelor", "master", "degree", "university", "college", "major"]):
                continue

            # Look for certification patterns
            cert_found = False
            for pattern in cert_patterns:
                cert_match = re.search(pattern, line, re.IGNORECASE)
                if cert_match:
                    # Save previous certification if exists
                    if current_cert and "name" in current_cert:
                        certifications.append(current_cert)

                    cert_name = cert_match.group(1).strip() if cert_match.group(1) else line
                    current_cert = {
                        "name": cert_name,
                        "raw_text": line
                    }

                    # Look for organization in the same line
                    for org in cert_organizations:
                        if org.lower() in line_lower:
                            current_cert["issuing_organization"] = org
                            break

                    cert_found = True
                    break

            # Look for known certification organizations
            if not cert_found:
                for org in cert_organizations:
                    if org.lower() in line_lower and any(keyword in line_lower for keyword in ["certified", "certificate", "certification"]):
                        if current_cert and "name" in current_cert:
                            certifications.append(current_cert)

                        current_cert = {
                            "name": line,
                            "issuing_organization": org,
                            "raw_text": line
                        }
                        cert_found = True
                        break

            # Look for dates
            if current_cert:
                for pattern in cert_date_patterns:
                    date_match = re.search(pattern, line, re.IGNORECASE)
                    if date_match:
                        current_cert["duration"] = line
                        groups = date_match.groups()

                        # Extract year obtained and expiry
                        if len(groups) >= 2:
                            start_date = groups[0] if groups[0].isdigit() else None
                            end_date = groups[1] if groups[1] not in ["Present", "Current"] else None

                            if start_date:
                                current_cert["year_obtained"] = int(start_date)
                            if end_date and end_date.isdigit():
                                current_cert["expiry_year"] = int(end_date)
                                current_cert["has_expiry"] = True

                        elif len(groups) == 1 and groups[0].isdigit():
                            current_cert["year_obtained"] = int(groups[0])
                        break

            # Look for expiry information
            if current_cert and any(keyword in line_lower for keyword in ["expires", "expiry", "valid until", "renewal"]):
                current_cert["has_expiry"] = True
                expiry_match = re.search(r"(\d{4})", line)
                if expiry_match:
                    current_cert["expiry_year"] = int(expiry_match.group(1))

            # Look for specific certification levels
            if current_cert:
                level_keywords = ["beginner", "basic", "intermediate", "advanced", "expert", "professional", "associate", "professional", "expert"]
                for level in level_keywords:
                    if level in line_lower:
                        current_cert["level"] = level.title()
                        break

        # Add the last certification
        if current_cert and "name" in current_cert:
            certifications.append(current_cert)

        # Clean and validate certifications
        validated_certifications = []
        for cert in certifications:
            if "name" in cert and len(cert["name"]) > 3:
                # Determine certification type
                cert_name_lower = cert["name"].lower()
                if any(keyword in cert_name_lower for keyword in ["safety", "first aid", "cpr", "medical"]):
                    cert["type"] = "Safety/Medical"
                elif any(keyword in cert_name_lower for keyword in ["fitness", "trainer", "exercise", "nutrition"]):
                    cert["type"] = "Fitness/Health"
                elif any(keyword in cert_name_lower for keyword in ["security", "guard", "protection"]):
                    cert["type"] = "Security"
                elif any(keyword in cert_name_lower for keyword in ["tech", "software", "computer", "it", "programming"]):
                    cert["type"] = "Technology"
                elif any(keyword in cert_name_lower for keyword in ["project", "management", "pmp", "scrum", "agile"]):
                    cert["type"] = "Project Management"
                else:
                    cert["type"] = "Professional"

                # Check if currently valid
                if "expiry_year" in cert:
                    cert["is_current"] = cert["expiry_year"] >= 2025
                else:
                    cert["is_current"] = True  # Assume current if no expiry

                validated_certifications.append(cert)

        # Sort by relevance (most recent first, then by type)
        validated_certifications.sort(
            key=lambda x: (x.get("year_obtained", 0), x["type"] == "Technology"),
            reverse=True
        )

        return validated_certifications[:8]  # Return top 8 certifications

    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles mentioned in the resume."""
        text_lower = text.lower()
        all_job_titles = self.dataset_manager.get_all_job_titles()

        found_titles = []
        for title in all_job_titles:
            if title.lower() in text_lower:
                found_titles.append(title.title())

        return list(set(found_titles))[:10]  # Return top 10 unique titles

    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and accomplishments."""
        achievements = []
        achievement_keywords = [
            "achieved",
            "accomplished",
            "awarded",
            "recognized",
            "improved",
            "increased",
            "decreased",
            "reduced",
            "led",
            "managed",
            "developed",
            "created",
            "implemented",
            "successful",
            "exceeded",
            "delivered",
            "launched",
            "built",
            "designed",
            "taught",
            "trained",
            "mentored",
            "coached",
            "guided",
            "prepared",
            "helped",
            "assisted",
            "organized",
            "coordinated",
            "facilitated",
            "supervised",
            "established",
            "founded",
            "initiated",
        ]

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Look for bullet points with achievement keywords
            if line.startswith(("•", "-", "*")) and any(
                keyword in line_lower for keyword in achievement_keywords
            ):
                achievements.append(line.lstrip("•-* "))

            # Look for quantified achievements (numbers/percentages)
            elif any(
                keyword in line_lower for keyword in achievement_keywords
            ) and re.search(r"\d+%|\$\d+|\d+x|by \d+", line):
                achievements.append(line)

        return achievements[:8]  # Return top 8 achievements

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from text."""
        text_lower = text.lower()
        soft_skills_keywords = self.dataset_manager.skills_db.get("soft_skills", {})

        found_soft_skills = []
        for category, skills in soft_skills_keywords.items():
            if isinstance(skills, list):
                for skill in skills:
                    if skill.lower() in text_lower:
                        found_soft_skills.append(skill.title())

        return list(set(found_soft_skills))

    def _extract_languages(self, text: str) -> List[str]:
        """Extract language skills."""
        language_keywords = [
            "english",
            "spanish",
            "french",
            "german",
            "chinese",
            "mandarin",
            "japanese",
            "italian",
            "portuguese",
            "russian",
            "arabic",
            "hindi",
            "korean",
            "dutch",
            "swedish",
            "norwegian",
            "finnish",
            "polish",
            "czech",
            "hungarian",
        ]

        languages = []
        text_lower = text.lower()

        for lang in language_keywords:
            if lang in text_lower:
                # Check for proficiency level
                proficiency = "conversational"  # default
                lang_index = text_lower.find(lang)
                surrounding_text = text_lower[max(0, lang_index - 50) : lang_index + 50]

                if any(
                    level in surrounding_text
                    for level in ["native", "fluent", "advanced"]
                ):
                    proficiency = "advanced"
                elif any(
                    level in surrounding_text
                    for level in ["intermediate", "conversational"]
                ):
                    proficiency = "intermediate"
                elif any(level in surrounding_text for level in ["basic", "beginner"]):
                    proficiency = "basic"

                languages.append(f"{lang.title()} ({proficiency})")

        return list(set(languages))

    def _generate_professional_summary(self, text: str) -> str:
        """Generate a professional summary using enhanced text analysis."""
        sentences = re.split(r"[.!?]+", text)
        summary_sentences = []

        # Look for summary/objective section first
        text_lower = text.lower()
        summary_keywords = ["summary", "objective", "profile", "about", "overview"]

        for keyword in summary_keywords:
            keyword_index = text_lower.find(keyword)
            if keyword_index != -1:
                # Extract text after the keyword
                remaining_text = text[keyword_index : keyword_index + 500]
                summary_sentences = re.split(r"[.!?]+", remaining_text)[:3]
                break

        if not summary_sentences:
            # Fallback: get meaningful sentences from the beginning
            for sentence in sentences[:15]:
                sentence = sentence.strip()
                if (
                    len(sentence) > 30
                    and len(sentence) < 200
                    and not sentence.lower().startswith(("email", "phone", "address"))
                ):
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= 3:
                        break

        if summary_sentences:
            return ". ".join(s.strip() for s in summary_sentences if s.strip()) + "."
        return "Professional summary not available."

    def _determine_experience_level(self, text: str) -> str:
        """Enhanced experience level determination."""
        text_lower = text.lower()

        # Senior level indicators
        senior_indicators = [
            "senior",
            "lead",
            "principal",
            "director",
            "manager",
            "head of",
            "chief",
            "10+ years",
            "15+ years",
            "20+ years",
            "over 10 years",
            "decade",
            "expert",
            "architect",
            "executive",
        ]

        # Mid-level indicators
        mid_indicators = [
            "5+ years",
            "experienced",
            "proficient",
            "advanced",
            "specialist",
            "6 years",
            "7 years",
            "8 years",
            "9 years",
            "several years",
        ]

        # Junior level indicators
        junior_indicators = [
            "junior",
            "entry",
            "associate",
            "assistant",
            "coordinator",
            "1-2 years",
            "2-3 years",
            "recent graduate",
            "new graduate",
        ]

        senior_count = sum(
            1 for indicator in senior_indicators if indicator in text_lower
        )
        mid_count = sum(1 for indicator in mid_indicators if indicator in text_lower)
        junior_count = sum(
            1 for indicator in junior_indicators if indicator in text_lower
        )

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

    def _calculate_experience_years(self, text: str) -> int:
        """Enhanced experience years calculation."""
        year_patterns = [
            r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|work|employment)",
            r"(\d+)\+?\s*years?\s*in\s+(?:the\s+)?(?:field|industry|role)",
            r"over\s*(\d+)\s*years?",
            r"more\s*than\s*(\d+)\s*years?",
            r"(\d+)\s*years?\s*of\s*professional",
            r"(\d+)\+\s*years?",
        ]

        years = []
        text_lower = text.lower()

        for pattern in year_patterns:
            matches = re.findall(pattern, text_lower)
            years.extend([int(match) for match in matches if match.isdigit()])

        # Also try to calculate from employment dates
        date_years = self._extract_employment_years(text)
        if date_years:
            years.append(date_years)

        return max(years) if years else 0

    def _extract_employment_years(self, text: str) -> int:
        """Extract years from employment date ranges."""
        # Look for date ranges like "2018-2023", "Jan 2019 - Present"
        date_range_patterns = [
            r"(\d{4})\s*[-–]\s*(\d{4})",
            r"(\d{4})\s*[-–]\s*(?:present|current|now)",
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}",
        ]

        years = []
        current_year = 2024  # Update this as needed

        for pattern in date_range_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    try:
                        if (
                            match[1].lower() in ["present", "current", "now"]
                            or not match[1].isdigit()
                        ):
                            start_year = (
                                int(match[0]) if match[0].isdigit() else current_year
                            )
                            years.append(current_year - start_year)
                        else:
                            start_year = int(match[0]) if match[0].isdigit() else 0
                            end_year = (
                                int(match[1]) if match[1].isdigit() else current_year
                            )
                            if start_year and end_year:
                                years.append(end_year - start_year)
                    except (ValueError, IndexError):
                        continue

        return sum(years) if years else 0

    # === VOICE ANALYSIS === (Enhanced but keeping core functionality)

    def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
        """Transcribe audio file to text."""
        try:
            result = self.whisper_model.transcribe(file_path)
            transcript = result["text"]
            confidence = self._estimate_transcript_confidence(transcript)
            return transcript, confidence
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")

    def _estimate_transcript_confidence(self, transcript: str) -> float:
        """Estimate transcript confidence based on text quality."""
        if not transcript:
            return 0.0

        word_count = len(transcript.split())
        avg_word_length = sum(len(word) for word in transcript.split()) / max(
            word_count, 1
        )

        # Check for coherence indicators
        coherence_score = 0
        if word_count > 10:
            coherence_score += 0.2
        if avg_word_length > 3:
            coherence_score += 0.2
        if re.search(r"[.!?]", transcript):
            coherence_score += 0.2

        base_confidence = min(
            0.9, (word_count * 0.01) + (avg_word_length * 0.1) + coherence_score
        )
        return max(0.3, base_confidence)

    def analyze_voice(self, file_path: str, transcript: str) -> Dict:
        """Enhanced voice analysis with industry-specific insights."""
        try:
            # Detect industry from transcript
            industry = self.dataset_manager.detect_industry(transcript)

            speech_features = self._extract_speech_features(file_path)
            communication_analysis = self._analyze_communication_enhanced(
                transcript, industry
            )
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
        except Exception as e:
            raise Exception(f"Voice analysis failed: {str(e)}")

    def _safe_pitch_mean(self, y) -> float:
        """Safely calculate pitch mean handling NaN values."""
        try:
            pitch_values = librosa.yin(y, fmin=50, fmax=300, threshold=0.1)
            valid_pitch = pitch_values[~np.isnan(pitch_values)]
            if len(valid_pitch) > 0:
                return float(np.mean(valid_pitch))
            else:
                return 150.0
        except:
            return 150.0

    def _extract_speech_features(self, file_path: str) -> Dict:
        """Extract technical speech features from audio."""
        try:
            y, sr = librosa.load(file_path, sr=None)

            features = {
                "duration": float(librosa.get_duration(y=y, sr=sr)),
                "speaking_rate": len(y) / librosa.get_duration(y=y, sr=sr),
                "pitch_mean": self._safe_pitch_mean(y),
                "energy_mean": float(np.mean(librosa.feature.rms(y=y)[0])),
                "spectral_centroid": float(
                    np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0])
                ),
                "zero_crossing_rate": float(
                    np.mean(librosa.feature.zero_crossing_rate(y)[0])
                ),
            }

            return features
        except Exception as e:
            return {"error": f"Failed to extract speech features: {str(e)}"}

    def _analyze_communication_enhanced(self, transcript: str, industry: str) -> Dict:
        """Enhanced communication analysis with industry-specific keywords."""
        if not transcript:
            return {}

        blob = TextBlob(transcript)

        analysis = {
            "word_count": len(transcript.split()),
            "sentence_count": len(blob.sentences),
            "avg_sentence_length": len(transcript.split())
            / max(len(blob.sentences), 1),
            "sentiment_polarity": blob.sentiment.polarity,
            "sentiment_subjectivity": blob.sentiment.subjectivity,
        }

        # Industry-specific professional language
        industry_skills = self.dataset_manager.get_skills_by_industry(industry)
        industry_terms_count = sum(
            1 for skill in industry_skills if skill.lower() in transcript.lower()
        )
        analysis["industry_terminology_usage"] = industry_terms_count / max(
            len(transcript.split()), 1
        )

        # General professional language
        professional_words = [
            "experience",
            "achieved",
            "managed",
            "developed",
            "led",
            "improved",
            "created",
            "implemented",
            "successful",
            "responsibility",
            "team",
            "project",
            "solution",
            "strategy",
            "collaborate",
            "deliver",
        ]

        professional_count = sum(
            1 for word in professional_words if word in transcript.lower()
        )
        analysis["professional_language_ratio"] = professional_count / max(
            len(transcript.split()), 1
        )

        return analysis

    def _analyze_language_quality(self, transcript: str) -> Dict:
        """Enhanced language quality analysis."""
        if not transcript:
            return {}

        words = transcript.split()
        unique_words = set(word.lower().strip('.,!?;:"()[]') for word in words)

        # Check for filler words
        filler_words = [
            "um",
            "uh",
            "like",
            "you know",
            "actually",
            "basically",
            "literally",
        ]
        filler_count = sum(1 for word in words if word.lower() in filler_words)

        # Check for technical vocabulary
        complex_words = [word for word in words if len(word) > 6]

        return {
            "vocabulary_diversity": len(unique_words) / max(len(words), 1),
            "avg_word_length": sum(len(word) for word in words) / max(len(words), 1),
            "complex_words_ratio": len(complex_words) / max(len(words), 1),
            "filler_words_ratio": filler_count / max(len(words), 1),
            "sentence_variety": len(set(len(s.split()) for s in transcript.split(".")))
            / max(len(transcript.split(".")), 1),
        }

    def _calculate_communication_scores(
        self, speech_features: Dict, comm_analysis: Dict, lang_analysis: Dict
    ) -> Dict:
        """Enhanced communication scores calculation."""
        scores = {}

        # Clarity score
        if "energy_mean" in speech_features and "pitch_mean" in speech_features:
            energy_score = min(100, speech_features["energy_mean"] * 2000)  # Normalize
            pitch_score = min(
                100, abs(speech_features.get("pitch_mean", 100) - 150) * -2 + 100
            )  # Optimal around 150Hz
            clarity_score = (energy_score + pitch_score) / 2
            scores["clarity_score"] = int(max(30, min(100, clarity_score)))
        else:
            scores["clarity_score"] = 70

        # Confidence score
        if comm_analysis:
            sentiment_score = (
                comm_analysis.get("sentiment_polarity", 0) + 1
            ) * 50  # Convert -1,1 to 0,100
            professional_score = (
                comm_analysis.get("professional_language_ratio", 0) * 100
            )
            industry_score = comm_analysis.get("industry_terminology_usage", 0) * 100

            confidence_score = (
                sentiment_score * 0.4 + professional_score * 0.4 + industry_score * 0.2
            )
            scores["confidence_score"] = int(max(30, min(100, confidence_score)))
        else:
            scores["confidence_score"] = 70

        # Fluency score
        if comm_analysis and lang_analysis:
            sentence_length_score = max(
                0, 100 - abs(comm_analysis.get("avg_sentence_length", 15) - 15) * 3
            )
            filler_penalty = lang_analysis.get("filler_words_ratio", 0) * 100
            fluency_score = sentence_length_score - filler_penalty
            scores["fluency_score"] = int(max(30, min(100, fluency_score)))
        else:
            scores["fluency_score"] = 70

        # Vocabulary score
        if lang_analysis:
            diversity_score = lang_analysis.get("vocabulary_diversity", 0.5) * 100
            complexity_score = lang_analysis.get("complex_words_ratio", 0.2) * 100
            variety_score = lang_analysis.get("sentence_variety", 0.5) * 100

            vocab_score = (
                diversity_score * 0.4 + complexity_score * 0.4 + variety_score * 0.2
            )
            scores["vocabulary_score"] = int(max(30, min(100, vocab_score)))
        else:
            scores["vocabulary_score"] = 70

        # Overall score
        scores["overall_communication_score"] = int(
            (
                scores["clarity_score"] * 0.3
                + scores["confidence_score"] * 0.3
                + scores["fluency_score"] * 0.2
                + scores["vocabulary_score"] * 0.2
            )
        )

        # Industry-specific score
        if comm_analysis:
            scores["industry_knowledge_score"] = int(
                min(100, comm_analysis.get("industry_terminology_usage", 0) * 300)
            )
        else:
            scores["industry_knowledge_score"] = 50

        return scores

    def _generate_communication_insights(
        self, scores: Dict, comm_analysis: Dict, industry: str
    ) -> Dict:
        """Enhanced communication insights with industry context."""
        strengths = []
        improvements = []

        # Analyze strengths
        if scores.get("clarity_score", 0) >= 80:
            strengths.append("Excellent speech clarity and articulation")
        if scores.get("confidence_score", 0) >= 80:
            strengths.append("Confident and professional communication style")
        if scores.get("vocabulary_score", 0) >= 80:
            strengths.append("Strong vocabulary and language skills")
        if scores.get("industry_knowledge_score", 0) >= 70:
            strengths.append(f"Good knowledge of {industry} terminology")

        # Analyze improvements
        if scores.get("clarity_score", 0) < 60:
            improvements.append("Work on speech clarity and projection")
        if scores.get("confidence_score", 0) < 60:
            improvements.append("Build confidence in communication")
        if scores.get("fluency_score", 0) < 60:
            improvements.append("Reduce filler words and improve speech flow")
        if scores.get("vocabulary_score", 0) < 60:
            improvements.append("Expand professional vocabulary")
        if scores.get("industry_knowledge_score", 0) < 50:
            improvements.append(f"Learn more {industry}-specific terminology")

        # Speaking pace analysis
        speaking_pace = "normal"
        if comm_analysis.get("avg_sentence_length", 15) > 25:
            speaking_pace = "slow"
        elif comm_analysis.get("avg_sentence_length", 15) < 8:
            speaking_pace = "fast"

        # Emotional tone
        sentiment = comm_analysis.get("sentiment_polarity", 0)
        if sentiment > 0.3:
            emotional_tone = "positive"
        elif sentiment < -0.3:
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"

        # Industry-specific recommendations
        industry_recommendations = self._get_industry_communication_tips(
            industry, scores
        )

        return {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "speaking_pace": speaking_pace,
            "emotional_tone": emotional_tone,
            "industry_specific_tips": industry_recommendations,
        }

    def _get_industry_communication_tips(
        self, industry: str, scores: Dict
    ) -> List[str]:
        """Get industry-specific communication tips."""
        tips = []

        industry_tips = {
            "technology": [
                "Use precise technical terminology",
                "Explain complex concepts clearly",
                "Demonstrate problem-solving approach",
            ],
            "finance": [
                "Show attention to detail in numbers",
                "Use data to support arguments",
                "Demonstrate risk awareness",
            ],
            "healthcare": [
                "Show empathy and compassion",
                "Use clear, patient-friendly language",
                "Demonstrate attention to compliance",
            ],
            "sales": [
                "Show enthusiasm and energy",
                "Use persuasive language",
                "Demonstrate relationship-building skills",
            ],
            "marketing": [
                "Show creativity in expression",
                "Use storytelling techniques",
                "Demonstrate brand awareness",
            ],
        }

        if industry in industry_tips:
            tips.extend(industry_tips[industry])

        # Add score-based tips
        if scores.get("industry_knowledge_score", 0) < 70:
            tips.append(f"Study more {industry}-specific terminology and concepts")

        return tips[:3]  # Return top 3 tips

    # === ENHANCED JOB MATCHING ===

    def match_resume_to_job(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Enhanced job matching with industry context."""
        try:
            # Get industry context
            resume_industry = resume_data.get("detected_industry", "general")
            job_industry = job_requirements.get("industry", resume_industry)

            # Extract matching data
            resume_skills = self._flatten_skills(resume_data.get("skills", {}))
            resume_experience = resume_data.get("experience", [])
            resume_education = resume_data.get("education", [])
            resume_certifications = resume_data.get("certifications", [])

            # Job requirements
            job_required_skills = job_requirements.get("required_skills", [])
            job_preferred_skills = job_requirements.get("preferred_skills", [])
            job_experience_req = job_requirements.get("required_experience", {})
            job_education_req = job_requirements.get("required_education", {})
            job_certifications_req = job_requirements.get("required_certifications", [])

            # Calculate detailed scores
            skills_score = self._calculate_skills_match_enhanced(
                resume_skills, job_required_skills, job_preferred_skills, job_industry
            )
            experience_score = self._calculate_experience_match_enhanced(
                resume_experience,
                job_experience_req,
                resume_data.get("total_experience_years", 0),
            )
            education_score = self._calculate_education_match(
                resume_education, job_education_req
            )
            certifications_score = self._calculate_certifications_match(
                resume_certifications, job_certifications_req
            )
            industry_fit_score = self._calculate_industry_fit(
                resume_industry, job_industry
            )

            # Weighted overall score
            weights = job_requirements.get(
                "matching_weights",
                {
                    "skills": 0.35,
                    "experience": 0.25,
                    "education": 0.15,
                    "certifications": 0.15,
                    "industry_fit": 0.10,
                },
            )

            overall_score = int(
                skills_score * weights.get("skills", 0.35)
                + experience_score * weights.get("experience", 0.25)
                + education_score * weights.get("education", 0.15)
                + certifications_score * weights.get("certifications", 0.15)
                + industry_fit_score * weights.get("industry_fit", 0.10)
            )

            # Generate detailed analysis
            match_details = {
                "skills_score": skills_score,
                "experience_score": experience_score,
                "education_score": education_score,
                "certifications_score": certifications_score,
                "industry_fit_score": industry_fit_score,
                "matching_skills": self._get_matching_skills(
                    resume_skills, job_required_skills + job_preferred_skills
                ),
                "missing_skills": self._get_missing_skills(
                    resume_skills, job_required_skills
                ),
                "experience_gap": self._calculate_experience_gap(
                    resume_data, job_experience_req
                ),
                "strengths": self._identify_strengths_enhanced(
                    resume_data, job_requirements
                ),
                "concerns": self._identify_concerns_enhanced(
                    resume_data, job_requirements
                ),
                "recommendations": self._generate_improvement_recommendations(
                    resume_data, job_requirements
                ),
            }

            return {
                "overall_score": overall_score,
                "match_details": match_details,
                "industry_context": {
                    "resume_industry": resume_industry,
                    "job_industry": job_industry,
                    "industry_match": resume_industry == job_industry,
                },
            }
        except Exception as e:
            raise Exception(f"Job matching failed: {str(e)}")

    def _flatten_skills(self, skills_dict: Dict) -> List[str]:
        """Enhanced skills flattening."""
        all_skills = []
        if isinstance(skills_dict, dict):
            for category, skills in skills_dict.items():
                if isinstance(skills, list):
                    all_skills.extend([skill.lower() for skill in skills])
                elif isinstance(skills, str):
                    all_skills.append(skills.lower())
        elif isinstance(skills_dict, list):
            all_skills = [skill.lower() for skill in skills_dict]

        return list(set(all_skills))

    def _calculate_skills_match_enhanced(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        industry: str,
    ) -> int:
        """Enhanced skills matching with industry context."""
        if not required_skills and not preferred_skills:
            return 80

        required_skills_lower = [skill.lower() for skill in required_skills]
        preferred_skills_lower = [skill.lower() for skill in preferred_skills]

        # Calculate matches
        required_matches = sum(
            1 for skill in required_skills_lower if skill in resume_skills
        )
        preferred_matches = sum(
            1 for skill in preferred_skills_lower if skill in resume_skills
        )

        # Calculate scores
        required_score = (
            (required_matches / max(len(required_skills_lower), 1)) * 100
            if required_skills_lower
            else 100
        )
        preferred_score = (
            (preferred_matches / max(len(preferred_skills_lower), 1)) * 100
            if preferred_skills_lower
            else 0
        )

        # Industry bonus for relevant skills
        industry_skills = self.dataset_manager.get_skills_by_industry(industry)
        industry_matches = sum(
            1
            for skill in resume_skills
            if skill in [s.lower() for s in industry_skills]
        )
        industry_bonus = min(10, industry_matches * 2)  # Up to 10 bonus points

        if required_skills_lower:
            base_score = required_score * 0.8 + preferred_score * 0.2
        else:
            base_score = preferred_score

        return int(min(100, base_score + industry_bonus))

    def _calculate_experience_match_enhanced(
        self, resume_experience: List[Dict], job_experience_req: Dict, total_years: int
    ) -> int:
        """Enhanced experience matching."""
        if not job_experience_req:
            return 80

        required_years = job_experience_req.get("min_years", 0)
        required_roles = job_experience_req.get("preferred_roles", [])

        # Years-based score
        if total_years >= required_years:
            years_score = min(100, 80 + (total_years - required_years) * 3)
        else:
            years_score = max(30, int((total_years / max(required_years, 1)) * 80))

        # Role relevance score
        role_score = 50  # Default
        if required_roles:
            resume_titles = [exp.get("title", "").lower() for exp in resume_experience]
            role_matches = sum(
                1
                for role in required_roles
                if any(role.lower() in title for title in resume_titles)
            )
            role_score = min(100, (role_matches / len(required_roles)) * 100)

        return int((years_score * 0.7) + (role_score * 0.3))

    def _calculate_certifications_match(
        self, resume_certs: List[Dict], required_certs: List[str]
    ) -> int:
        """Calculate certifications matching score."""
        if not required_certs:
            return 80  # Default if no certifications required

        resume_cert_names = [cert.get("name", "").lower() for cert in resume_certs]
        required_certs_lower = [cert.lower() for cert in required_certs]

        matches = sum(
            1
            for req_cert in required_certs_lower
            if any(req_cert in cert_name for cert_name in resume_cert_names)
        )

        score = (
            (matches / len(required_certs_lower)) * 100 if required_certs_lower else 80
        )
        return int(max(30, score))

    def _calculate_industry_fit(self, resume_industry: str, job_industry: str) -> int:
        """Calculate how well the resume fits the job industry."""
        if resume_industry == job_industry:
            return 100

        # Related industries (you can expand this mapping)
        related_industries = {
            "technology": ["finance", "healthcare"],  # Tech skills transfer well
            "finance": ["technology", "consulting"],
            "marketing": ["sales", "media"],
            "sales": ["marketing", "retail"],
            "healthcare": ["technology", "education"],
            "education": ["healthcare", "consulting"],
        }

        if job_industry in related_industries.get(resume_industry, []):
            return 70

        return 40  # Default for unrelated industries

    def _calculate_experience_gap(
        self, resume_data: Dict, job_experience_req: Dict
    ) -> Dict:
        """Calculate experience gap analysis."""
        required_years = job_experience_req.get("min_years", 0)
        actual_years = resume_data.get("total_experience_years", 0)

        return {
            "required_years": required_years,
            "actual_years": actual_years,
            "gap_years": max(0, required_years - actual_years),
            "exceeds_requirement": actual_years > required_years,
            "gap_percentage": max(
                0, (required_years - actual_years) / max(required_years, 1) * 100
            ),
        }

    def _identify_strengths_enhanced(
        self, resume_data: Dict, job_requirements: Dict
    ) -> List[str]:
        """Enhanced strength identification."""
        strengths = []

        # Skill-based strengths
        resume_skills = self._flatten_skills(resume_data.get("skills", {}))
        job_skills = job_requirements.get("required_skills", []) + job_requirements.get(
            "preferred_skills", []
        )
        matching_skills = self._get_matching_skills(resume_skills, job_skills)

        if len(matching_skills) >= 5:
            strengths.append(
                f"Excellent technical skills match ({len(matching_skills)} relevant skills)"
            )
        elif len(matching_skills) >= 3:
            strengths.append(
                f"Good technical skills alignment ({len(matching_skills)} matching skills)"
            )

        # Experience strengths
        total_years = resume_data.get("total_experience_years", 0)
        required_years = job_requirements.get("required_experience", {}).get(
            "min_years", 0
        )

        if total_years >= required_years * 1.5:
            strengths.append("Extensive experience exceeding requirements")
        elif total_years >= required_years:
            strengths.append("Meets experience requirements")

        # Industry experience
        resume_industry = resume_data.get("detected_industry", "")
        job_industry = job_requirements.get("industry", "")
        if resume_industry == job_industry:
            strengths.append(f"Direct {resume_industry} industry experience")

        # Education strengths
        education = resume_data.get("education", [])
        if education and any(
            "master" in ed.get("degree", "").lower()
            or "mba" in ed.get("degree", "").lower()
            for ed in education
        ):
            strengths.append("Advanced degree qualification")

        # Certification strengths
        certifications = resume_data.get("certifications", [])
        required_certs = job_requirements.get("required_certifications", [])
        if certifications and required_certs:
            cert_matches = sum(
                1
                for cert in certifications
                if any(
                    req.lower() in cert.get("name", "").lower()
                    for req in required_certs
                )
            )
            if cert_matches > 0:
                strengths.append(
                    f"Relevant professional certifications ({cert_matches} matches)"
                )

        # Soft skills
        soft_skills = resume_data.get("soft_skills", [])
        if len(soft_skills) >= 3:
            strengths.append("Strong soft skills profile")

        return strengths[:5]  # Return top 5 strengths

    def _identify_concerns_enhanced(
        self, resume_data: Dict, job_requirements: Dict
    ) -> List[str]:
        """Enhanced concern identification."""
        concerns = []

        # Missing skills
        resume_skills = self._flatten_skills(resume_data.get("skills", {}))
        missing_skills = self._get_missing_skills(
            resume_skills, job_requirements.get("required_skills", [])
        )

        if len(missing_skills) >= 3:
            concerns.append(
                f"Missing multiple required skills ({len(missing_skills)} skills)"
            )
        elif len(missing_skills) > 0:
            concerns.append(
                f"Missing some required skills: {', '.join(missing_skills[:3])}"
            )

        # Experience gap
        experience_gap = self._calculate_experience_gap(
            resume_data, job_requirements.get("required_experience", {})
        )
        if experience_gap["gap_years"] > 2:
            concerns.append(
                f"Experience gap: {experience_gap['gap_years']} years below requirement"
            )
        elif experience_gap["gap_years"] > 0:
            concerns.append("Slightly below required experience level")

        # Industry mismatch
        resume_industry = resume_data.get("detected_industry", "")
        job_industry = job_requirements.get("industry", "")
        if resume_industry != job_industry and job_industry:
            concerns.append(
                f"Industry transition from {resume_industry} to {job_industry}"
            )

        # Education gap
        education = resume_data.get("education", [])
        required_education = job_requirements.get("required_education", {})
        if required_education.get("min_degree") and not education:
            concerns.append("No formal education listed")

        # Missing certifications
        required_certs = job_requirements.get("required_certifications", [])
        resume_certs = resume_data.get("certifications", [])
        if required_certs and not resume_certs:
            concerns.append("Missing required professional certifications")

        return concerns[:4]  # Return top 4 concerns

    def _generate_improvement_recommendations(
        self, resume_data: Dict, job_requirements: Dict
    ) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Skill recommendations
        missing_skills = self._get_missing_skills(
            self._flatten_skills(resume_data.get("skills", {})),
            job_requirements.get("required_skills", []),
        )

        if missing_skills:
            priority_skills = missing_skills[:3]  # Top 3 missing skills
            recommendations.append(f"Develop skills in: {', '.join(priority_skills)}")

        # Experience recommendations
        experience_gap = self._calculate_experience_gap(
            resume_data, job_requirements.get("required_experience", {})
        )
        if experience_gap["gap_years"] > 0:
            recommendations.append(
                f"Gain {experience_gap['gap_years']} more years of relevant experience or highlight transferable skills"
            )

        # Certification recommendations
        required_certs = job_requirements.get("required_certifications", [])
        resume_certs = [
            cert.get("name", "") for cert in resume_data.get("certifications", [])
        ]
        missing_certs = [
            cert
            for cert in required_certs
            if not any(
                cert.lower() in resume_cert.lower() for resume_cert in resume_certs
            )
        ]

        if missing_certs:
            recommendations.append(
                f"Obtain certifications: {', '.join(missing_certs[:2])}"
            )

        # Industry-specific recommendations
        job_industry = job_requirements.get("industry", "")
        if job_industry:
            industry_skills = self.dataset_manager.get_skills_by_industry(job_industry)
            resume_skills = self._flatten_skills(resume_data.get("skills", {}))
            missing_industry_skills = [
                skill
                for skill in industry_skills[:5]
                if skill.lower() not in resume_skills
            ]

            if missing_industry_skills:
                recommendations.append(
                    f"Learn {job_industry}-specific skills: {', '.join(missing_industry_skills[:2])}"
                )

        # General recommendations
        if not resume_data.get("achievements"):
            recommendations.append(
                "Add quantifiable achievements to demonstrate impact"
            )

        return recommendations[:5]  # Return top 5 recommendations

    def _get_matching_skills(
        self, resume_skills: List[str], job_skills: List[str]
    ) -> List[str]:
        """Get skills that match between resume and job."""
        job_skills_lower = [skill.lower() for skill in job_skills]
        return [skill for skill in resume_skills if skill in job_skills_lower]

    def _get_missing_skills(
        self, resume_skills: List[str], required_skills: List[str]
    ) -> List[str]:
        """Get required skills that are missing from resume."""
        required_skills_lower = [skill.lower() for skill in required_skills]
        return [
            skill for skill in required_skills if skill.lower() not in resume_skills
        ]

    def _extract_years_from_experience(self, experience: Dict) -> int:
        """Extract years from experience entry."""
        duration = experience.get("duration", "")
        if not duration:
            return 1

        # Enhanced year extraction patterns
        year_patterns = [
            r"(\d+)\s*years?",
            r"(\d{4})\s*[-–]\s*(\d{4})",
            r"(\d{4})\s*[-–]\s*(?:present|current)",
            r"(\d+)\s*months?",  # Convert months to years
        ]

        for pattern in year_patterns:
            matches = re.findall(pattern, duration.lower())
            if matches:
                if len(matches[0]) == 2 and isinstance(matches[0], tuple):
                    # Date range format
                    start_year, end_year = matches[0]
                    if end_year.isdigit():
                        return int(end_year) - int(start_year)
                    else:
                        return 2024 - int(start_year)  # Assuming current year is 2024
                elif "months" in duration.lower():
                    return max(1, int(matches[0]) // 12)  # Convert months to years
                else:
                    return int(matches[0])

        return 1  # Default


# Global AI service instance
ai_service = AIService()
