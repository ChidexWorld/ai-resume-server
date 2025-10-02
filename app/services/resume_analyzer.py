"""
Resume analysis component for file and text processing.
Enhanced with PyResParser and dataset_manager for better accuracy.
"""

import re
import os
from typing import Dict, Optional

# CRITICAL: Set up NLTK paths BEFORE any pyresparser import
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    import setup_nltk  # This sets up NLTK data paths
except ImportError:
    pass

from .name_extractor import name_extractor
from .dataset_manager import dataset_manager

# Try to import PyResParser
try:
    from pyresparser import ResumeParser
    PYRESPARSER_AVAILABLE = True
except ImportError:
    PYRESPARSER_AVAILABLE = False
    ResumeParser = None


class ResumeAnalyzer:
    """Handles resume analysis from files and text."""

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
        try:
            import PyPDF2
            text = ""
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            raise Exception("PyPDF2 not installed. Please install it to process PDF files.")
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except ImportError:
            raise Exception("python-docx not installed. Please install it to process DOCX files.")
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")

    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Text file extraction failed: {str(e)}")

    def analyze_resume_from_file(self, file_path: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume from file using PyResParser if available, fallback to text analysis."""
        # First try PyResParser for better accuracy
        if PYRESPARSER_AVAILABLE and ResumeParser:
            try:
                return self._analyze_with_pyresparser(file_path, target_industry)
            except Exception as e:
                print(f"PyResParser failed: {e}, falling back to text analysis")

        # Fallback to text analysis
        mime_type = self._detect_mime_type(file_path)
        extracted_text = self.extract_text_from_file(file_path, mime_type)
        return self.analyze_resume(extracted_text, target_industry)

    def analyze_resume(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume text and extract key information."""
        # Clean and format text properly
        formatted_text = self._format_extracted_text(text)

        contact_info = self._extract_contact_info(formatted_text)
        skills_data = self._extract_enhanced_skills(formatted_text)
        # Use global experience extraction for better results
        global_exp = self.extract_global_experience(formatted_text)
        experience_data = [job['formatted'] for job in global_exp['job_positions']] + \
                         [ach['text'] for ach in global_exp['achievements'][:3]]
        education_data = self._extract_enhanced_education(formatted_text)
        certifications_data = self._extract_enhanced_certifications(formatted_text)

        detected_industry = target_industry or dataset_manager.detect_industry(formatted_text)

        return {
            "contact_info": contact_info,
            "detected_industry": detected_industry,
            "skills": skills_data,
            "experience": experience_data,
            "education": education_data,
            "certifications": certifications_data,
            "languages": skills_data.get('languages', []),
            "professional_summary": self._extract_summary(formatted_text),
            "experience_level": self._determine_experience_level(experience_data),
            "total_experience_years": self._calculate_total_experience(experience_data),
            "job_titles": self._extract_enhanced_job_titles(formatted_text, detected_industry),
            "achievements": self._extract_achievements(formatted_text),
            "soft_skills": skills_data.get('soft_skills', []),
        }

    def analyze_resume_from_text(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Synchronous version for route compatibility."""
        return self.analyze_resume(text, target_industry)

    async def analyze_resume_from_text_async(self, text: str, target_industry: Optional[str] = None) -> Dict:
        """Async version if needed."""
        return self.analyze_resume(text, target_industry)

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information with accurate name extraction."""
        contact_info = {}

        # Extract name using dedicated name extractor
        contact_info["name"] = name_extractor.extract_name(text)

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]

        # Extract phone
        phone_patterns = [
            r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            r"(\d{10})",
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                if isinstance(phones[0], tuple):
                    contact_info["phone"] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
                else:
                    contact_info["phone"] = phones[0]
                break

        return contact_info

    def _extract_basic_skills(self, text: str) -> Dict:
        """Extract basic skills from text categorized by type."""
        # Categorized skill patterns
        skill_categories = {
            'technical_skills': [
                'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css',
                'git', 'docker', 'kubernetes', 'aws', 'azure', 'machine learning',
                'data analysis', 'tensorflow', 'pytorch', 'pandas', 'numpy'
            ],
            'soft_skills': [
                'communication', 'leadership', 'problem solving', 'teamwork',
                'project management', 'time management', 'analytical thinking',
                'creativity', 'adaptability', 'critical thinking'
            ],
            'languages': [
                'english', 'spanish', 'french', 'german', 'chinese', 'japanese',
                'portuguese', 'italian', 'russian', 'arabic'
            ]
        }

        found_skills = {
            'technical_skills': [],
            'soft_skills': [],
            'languages': []
        }

        text_lower = text.lower()

        for category, skills in skill_categories.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills[category].append(skill.title())

        return found_skills

    def _extract_basic_experience(self, text: str) -> list:
        """Extract basic experience information."""
        experience = []

        # Look for job positions and dates
        position_patterns = [
            r'(\w+(?:\s+\w+)*)\s*[-–]\s*(\d{4})\s*(?:[-–]\s*(\d{4}|present|current))?',
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)\s*:?\s*(.+?)(?:\n|$)',
        ]

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['experience', 'employment', 'work history', 'career']):
                continue

            # Look for job titles with companies
            if len(line) > 10 and any(indicator in line.lower() for indicator in ['engineer', 'developer', 'manager', 'analyst', 'consultant', 'specialist']):
                experience.append(line)

        # Look for years of experience mentions
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)',
        ]

        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years = max([int(x) for x in matches])
                experience.append(f"{years} years of experience")
                break

        return experience[:5]  # Limit to top 5 experiences

    def _extract_education(self, text: str) -> list:
        """Extract education information."""
        education = []

        # Common degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate|diploma)(?:\s+of\s+|\s+in\s+|\s+degree\s+in\s+)([a-zA-Z\s]+)',
            r'(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?)(?:\s+in\s+)?([a-zA-Z\s]+)',
        ]

        # Universities and institutions
        institution_patterns = [
            r'university\s+of\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+university',
            r'([a-zA-Z\s]+)\s+college',
            r'([a-zA-Z\s]+)\s+institute',
        ]

        text_lower = text.lower()

        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    degree_type = match[0].strip()
                    field = match[1].strip() if len(match) > 1 else ""
                    education.append(f"{degree_type.title()} in {field.title()}")

        for pattern in institution_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if len(match.strip()) > 2:
                    education.append(f"Studied at {match.strip().title()}")

        return list(set(education))[:3]  # Remove duplicates and limit to 3

    def _extract_certifications(self, text: str) -> list:
        """Extract certifications and licenses."""
        certifications = []

        cert_keywords = [
            'certified', 'certification', 'certificate', 'license', 'licensed',
            'pmp', 'cissp', 'cisa', 'ccna', 'mcse', 'aws', 'azure', 'google cloud',
            'scrum master', 'agile', 'itil', 'prince2'
        ]

        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in cert_keywords):
                if len(line.strip()) > 5 and len(line.strip()) < 100:
                    certifications.append(line.strip())

        return certifications[:5]  # Limit to 5 certifications

    def _detect_industry(self, text: str) -> str:
        """Detect industry based on resume content."""
        text_lower = text.lower()

        industry_keywords = {
            'technology': ['software', 'programming', 'developer', 'engineer', 'tech', 'it', 'computer'],
            'finance': ['finance', 'banking', 'investment', 'accounting', 'financial'],
            'healthcare': ['medical', 'healthcare', 'nurse', 'doctor', 'hospital', 'clinical'],
            'marketing': ['marketing', 'advertising', 'digital marketing', 'social media', 'brand'],
            'sales': ['sales', 'business development', 'account management', 'customer relations'],
            'education': ['teacher', 'professor', 'education', 'academic', 'research'],
            'consulting': ['consultant', 'consulting', 'advisory', 'strategy'],
        }

        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                industry_scores[industry] = score

        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return "general"

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary."""
        lines = text.split('\n')

        summary_indicators = ['summary', 'profile', 'objective', 'about']

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(indicator in line_lower for indicator in summary_indicators):
                # Get next few lines as summary
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 20:
                        summary_lines.append(lines[j].strip())

                if summary_lines:
                    return ' '.join(summary_lines)

        # Fallback: use first substantial paragraph
        for line in lines[:10]:
            if len(line.strip()) > 50:
                return line.strip()

        return "Professional summary extraction available in full version"

    def _determine_experience_level(self, experience_data: list) -> str:
        """Determine experience level based on experience data and job titles."""
        total_exp = self._calculate_total_experience(experience_data)

        # Check for senior/leadership indicators in job titles
        experience_text = " ".join(str(exp) for exp in experience_data).lower()

        senior_keywords = ['senior', 'lead', 'principal', 'architect', 'director', 'manager', 'head', 'chief']
        executive_keywords = ['ceo', 'cto', 'cfo', 'vp', 'vice president', 'president', 'founder', 'co-founder']
        entry_keywords = ['intern', 'trainee', 'graduate', 'junior', 'assistant', 'entry']

        # Override based on job titles if explicit
        if any(keyword in experience_text for keyword in executive_keywords):
            return "executive"
        elif any(keyword in experience_text for keyword in senior_keywords):
            return "senior"
        elif any(keyword in experience_text for keyword in entry_keywords) and total_exp < 3:
            return "entry"

        # Fallback to experience-based calculation
        if total_exp == 0:
            return "entry"
        elif total_exp < 2:
            return "entry"
        elif total_exp < 5:
            return "mid"
        elif total_exp < 10:
            return "senior"
        else:
            return "executive"

    def _calculate_total_experience(self, experience_data: list) -> int:
        """Calculate total years of experience with enhanced parsing and fallback methods."""
        from datetime import datetime
        current_year = datetime.now().year
        total_years = 0

        # If experience_data is empty or None, try to infer from context
        if not experience_data:
            return 0

        for exp in experience_data:
            exp_text = str(exp) if exp else ""
            exp_lower = exp_text.lower()

            # Method 1: Look for explicit years mentions with multiple patterns
            years_patterns = [
                r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp|tenure)',
                r'(\d+)\s*(?:years?|yrs?)\s*(?:working|in|at|with)',
                r'(?:over|more than|about)\s*(\d+)\+?\s*(?:years?|yrs?)',
                r'(\d{1,2})\s*(?:years?|yrs?)\s*(?:experience|exp)',
                r'(\d+)\+\s*(?:years?|yrs?)',
            ]

            for pattern in years_patterns:
                years_match = re.search(pattern, exp_lower)
                if years_match:
                    years = int(years_match.group(1))
                    if 1 <= years <= 50:  # Reasonable range
                        total_years = max(total_years, years)

            # Method 2: Calculate from date ranges with multiple formats
            date_patterns = [
                r'(\d{4})\s*[—–-]\s*(\d{4}|present|current)',  # 2020 — 2023
                r'(\w+\s+\d{4})\s*[—–-]\s*(\w+\s+\d{4}|present|current)',  # January 2021 — July 2022
                r'(\d{1,2}\/\d{4})\s*[—–-]\s*(\d{1,2}\/\d{4}|present|current)',  # 01/2021 — 05/2023
                r'(\d{4})\s*to\s*(\d{4}|present|current)',  # 2020 to 2023
                r'from\s+(\d{4})\s*to\s*(\d{4}|present|current)',  # from 2020 to 2023
                r'(\d{4})\s*-\s*(\d{4}|present|current)',  # 2020-2023
            ]

            for pattern in date_patterns:
                date_match = re.search(pattern, exp_text, re.IGNORECASE)
                if date_match:
                    start_str, end_str = date_match.groups()
                    try:
                        # Extract start year
                        start_year_match = re.search(r'\d{4}', start_str)
                        if not start_year_match:
                            continue
                        start_year = int(start_year_match.group())

                        # Extract end year
                        if any(word in end_str.lower() for word in ['present', 'current', 'now']):
                            end_year = current_year
                        else:
                            end_year_match = re.search(r'\d{4}', end_str)
                            if not end_year_match:
                                continue
                            end_year = int(end_year_match.group())

                        # Calculate years difference
                        if start_year > 1970 and start_year <= current_year:  # Reasonable year range
                            job_years = max(0, end_year - start_year)
                            if 0 <= job_years <= 15:  # Reasonable job duration
                                total_years += job_years
                    except (ValueError, AttributeError):
                        continue

            # Method 3: Look for tenure indicators
            tenure_indicators = [
                r'since\s+(\d{4})',
                r'(\d+)\s*(?:months?|mos?)\s*(?:experience|exp)',
                r'started\s+in\s+(\d{4})',
                r'joined\s+in\s+(\d{4})',
            ]

            for pattern in tenure_indicators:
                match = re.search(pattern, exp_lower)
                if match:
                    value = int(match.group(1))
                    if 'months?' in pattern or 'mos?' in pattern:
                        years = max(1, value // 12)  # Convert months to years, minimum 1
                    elif 'since' in pattern or 'started' in pattern or 'joined' in pattern:
                        years = current_year - value
                    else:
                        years = value

                    if 1 <= years <= 50:
                        total_years = max(total_years, years)

        # If still no experience calculated, use fallback heuristics
        if total_years == 0:
            # Look for graduation years and infer experience
            graduation_pattern = r'(?:graduated|degree|bachelor|master|phd).*?(\d{4})'
            for exp in experience_data:
                grad_match = re.search(graduation_pattern, str(exp).lower())
                if grad_match:
                    grad_year = int(grad_match.group(1))
                    if 1990 <= grad_year <= current_year - 1:  # Reasonable graduation year
                        inferred_experience = current_year - grad_year - 1  # Subtract 1 for graduation year
                        if inferred_experience > 0:
                            total_years = max(total_years, min(inferred_experience, 30))

        return min(total_years, 50)  # Cap at reasonable maximum

    def _extract_job_titles(self, text: str) -> list:
        """Extract job titles from resume."""
        job_titles = []

        title_keywords = [
            'engineer', 'developer', 'manager', 'analyst', 'consultant',
            'specialist', 'coordinator', 'supervisor', 'director', 'lead',
            'senior', 'junior', 'associate', 'principal', 'architect'
        ]

        lines = text.split('\n')
        for line in lines:
            line_clean = line.strip()
            if any(keyword in line_clean.lower() for keyword in title_keywords):
                if 10 < len(line_clean) < 60:  # Reasonable title length
                    job_titles.append(line_clean)

        return job_titles[:5]

    def _extract_achievements(self, text: str) -> list:
        """Extract achievements and accomplishments."""
        achievements = []

        achievement_indicators = [
            'achieved', 'accomplished', 'increased', 'decreased', 'improved',
            'led', 'managed', 'developed', 'created', 'implemented',
            'award', 'recognition', 'promoted', 'exceeded'
        ]

        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(indicator in line_lower for indicator in achievement_indicators):
                if 20 < len(line.strip()) < 150:  # Reasonable achievement length
                    achievements.append(line.strip())

        return achievements[:5]

    def _analyze_with_pyresparser(self, file_path: str, target_industry: Optional[str] = None) -> Dict:
        """Analyze resume using PyResParser for better accuracy."""
        try:
            # Use PyResParser to extract data
            data = ResumeParser(file_path).get_extracted_data()

            # Extract text for additional processing
            mime_type = self._detect_mime_type(file_path)
            extracted_text = self.extract_text_from_file(file_path, mime_type)
            formatted_text = self._format_extracted_text(extracted_text)

            # Enhance PyResParser results with our dataset manager
            enhanced_skills = self._enhance_pyresparser_skills(data.get('skills', []), formatted_text)
            enhanced_experience = self._enhance_pyresparser_experience(data.get('experience', []), formatted_text)
            enhanced_education = self._enhance_pyresparser_education(data.get('education', []), formatted_text)

            detected_industry = target_industry or dataset_manager.detect_industry(formatted_text)

            return {
                "contact_info": {
                    "name": data.get('name', ''),
                    "email": data.get('email', ''),
                    "phone": data.get('mobile_number', ''),
                },
                "detected_industry": detected_industry,
                "skills": enhanced_skills,
                "experience": enhanced_experience,
                "education": enhanced_education,
                "certifications": self._extract_enhanced_certifications(formatted_text),
                "languages": enhanced_skills.get('languages', []),
                "professional_summary": self._extract_summary(formatted_text),
                "experience_level": self._determine_experience_level(enhanced_experience),
                "total_experience_years": data.get('total_experience', self._calculate_total_experience(enhanced_experience)),
                "job_titles": self._extract_enhanced_job_titles(formatted_text, detected_industry),
                "achievements": self._extract_achievements(formatted_text),
                "soft_skills": enhanced_skills.get('soft_skills', []),
            }

        except Exception as e:
            raise Exception(f"PyResParser analysis failed: {str(e)}")

    def _format_extracted_text(self, text: str) -> str:
        """Format extracted text properly for analysis."""
        if not text:
            return ""

        # Clean up text formatting
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            # Remove excessive whitespace
            line = re.sub(r'\s+', ' ', line.strip())

            # Skip empty lines
            if not line:
                continue

            # Add line to formatted text
            formatted_lines.append(line)

        # Join lines with proper spacing
        formatted_text = '\n'.join(formatted_lines)

        # Additional cleanup
        formatted_text = re.sub(r'\n\s*\n', '\n\n', formatted_text)  # Multiple newlines to double
        formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)   # Limit to max 2 newlines

        return formatted_text

    def _detect_mime_type(self, file_path: str) -> str:
        """Detect MIME type from file extension."""
        _, ext = os.path.splitext(file_path.lower())

        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain'
        }

        return mime_types.get(ext, 'application/octet-stream')

    def _enhance_pyresparser_skills(self, pyres_skills: list, text: str) -> Dict:
        """Enhance PyResParser skills with dataset manager."""
        # Get industry-specific skills from dataset manager
        detected_industry = dataset_manager.detect_industry(text)
        industry_skills = dataset_manager.get_skills_by_industry(detected_industry)
        all_skills = dataset_manager.get_all_skills()

        # Combine PyResParser skills with our enhanced extraction
        enhanced_skills = self._extract_enhanced_skills(text)

        # Add PyResParser skills to appropriate categories
        text_lower = text.lower()

        for skill in pyres_skills:
            skill_lower = skill.lower()

            # Categorize skill based on dataset manager
            if skill_lower in [s.lower() for s in industry_skills]:
                enhanced_skills['technical_skills'].append(skill)
            elif any(lang in skill_lower for lang in ['english', 'spanish', 'french', 'german', 'chinese']):
                enhanced_skills['languages'].append(skill)
            else:
                enhanced_skills['technical_skills'].append(skill)

        # Remove duplicates and return
        for category in enhanced_skills:
            enhanced_skills[category] = list(set(enhanced_skills[category]))

        return enhanced_skills

    def _enhance_pyresparser_experience(self, pyres_experience: list, text: str) -> list:
        """Enhance PyResParser experience with detailed formatting."""
        enhanced_experience = []

        # Process PyResParser experience data first (it's more accurate)
        for exp in pyres_experience:
            if isinstance(exp, dict):
                # PyResParser returns structured experience data
                company = exp.get('company', '')
                position = exp.get('position', '') or exp.get('title', '')
                duration = exp.get('duration', '') or exp.get('period', '')
                description = exp.get('description', '') or exp.get('details', '')

                # Format experience entry
                exp_parts = []
                if position:
                    exp_parts.append(position)
                if company:
                    exp_parts.append(f"at {company}")
                if duration:
                    exp_parts.append(f"({duration})")

                if exp_parts:
                    formatted_exp = " ".join(exp_parts)
                    enhanced_experience.append(formatted_exp)

                # Add description as separate entry if it's substantial
                if description and len(description) > 20:
                    enhanced_experience.append(f"• {description}")

            elif isinstance(exp, str) and len(exp) > 10:
                # String format from PyResParser
                enhanced_experience.append(exp)

        # Add our custom extraction as backup
        our_experience = self._extract_enhanced_experience(text)
        for exp in our_experience:
            if exp not in enhanced_experience:
                enhanced_experience.append(exp)

        return enhanced_experience[:12]  # Allow more experiences

    def _enhance_pyresparser_education(self, pyres_education: list, text: str) -> list:
        """Enhance PyResParser education with our extraction."""
        enhanced_education = self._extract_enhanced_education(text)

        # Add PyResParser education data
        for edu in pyres_education:
            if isinstance(edu, str) and edu not in enhanced_education:
                enhanced_education.append(edu)

        return enhanced_education[:5]  # Limit to 5 education entries

    def _extract_enhanced_skills(self, text: str) -> Dict:
        """Extract skills using dataset manager for better accuracy."""
        text_lower = text.lower()

        # Get all skills from dataset manager
        all_skills = dataset_manager.get_all_skills()

        found_skills = {
            'technical_skills': [],
            'soft_skills': [],
            'languages': []
        }

        # Check against comprehensive skill database
        for skill in all_skills:
            if skill.lower() in text_lower:
                # Categorize based on dataset manager structure
                for industry, categories in dataset_manager.skills_db.items():
                    if isinstance(categories, dict):
                        for category, skills in categories.items():
                            if isinstance(skills, list) and skill in skills:
                                if 'language' in category.lower():
                                    found_skills['languages'].append(skill.title())
                                elif category in ['soft_skills', 'communication', 'leadership', 'personal']:
                                    found_skills['soft_skills'].append(skill.title())
                                else:
                                    found_skills['technical_skills'].append(skill.title())
                                break

        # Enhanced language detection from text sections
        languages_found = self._extract_languages_from_text(text)
        found_skills['languages'].extend(languages_found)

        # Remove duplicates
        for category in found_skills:
            found_skills[category] = list(set(found_skills[category]))

        return found_skills

    def _extract_languages_from_text(self, text: str) -> list:
        """Extract languages from text sections and language lists."""
        languages = []
        lines = text.split('\n')

        # Common languages to look for
        language_list = [
            'english', 'spanish', 'french', 'german', 'italian', 'portuguese',
            'chinese', 'mandarin', 'japanese', 'korean', 'arabic', 'russian',
            'hindi', 'dutch', 'swedish', 'norwegian', 'danish', 'polish'
        ]

        text_lower = text.lower()

        # Method 1: Look for explicit language mentions
        for lang in language_list:
            if lang in text_lower:
                languages.append(lang.title())

        # Method 2: Look for "Languages" section
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if line_lower == 'languages' or line_lower == 'language':
                # Check next few lines for language names
                for j in range(i+1, min(i+5, len(lines))):
                    next_line = lines[j].strip()
                    if len(next_line) > 1 and len(next_line) < 20:
                        next_line_lower = next_line.lower()
                        if next_line_lower in language_list:
                            languages.append(next_line.title())
                        # Also check for common language patterns
                        elif any(lang in next_line_lower for lang in language_list):
                            for lang in language_list:
                                if lang in next_line_lower:
                                    languages.append(lang.title())
                break

        return list(set(languages))  # Remove duplicates

    def _extract_enhanced_experience(self, text: str) -> list:
        """Extract experience using enhanced patterns with better structure."""
        experience = []
        lines = text.split('\n')

        # Enhanced patterns for job experience with company and dates
        experience_patterns = [
            # Pattern: "Position at Company, Location"
            r'([A-Z][a-zA-Z\s]+(?:Associate|Assistant|Manager|Engineer|Developer|Analyst|Coordinator|Specialist|Director|Lead))\s+at\s+([A-Z][a-zA-Z\s&,\.]+)(?:,\s*([A-Za-z\s]+))?',
            # Pattern: "Company, Location" on separate lines followed by dates
            r'^([A-Z][a-zA-Z\s&,\.]+)(?:,\s*([A-Za-z\s]+))?$',
            # Pattern with dates: "January 2021 — July 2022"
            r'([A-Z][a-z]+\s+\d{4})\s*[—–-]\s*([A-Z][a-z]+\s+\d{4}|present|current)',
        ]

        # Job title keywords from dataset manager
        all_job_titles = dataset_manager.get_all_job_titles()
        job_title_keywords = [title.lower() for title in all_job_titles[:100]]  # Top 100 for better coverage

        # Process text to find structured experience entries
        current_position = None
        current_company = None
        current_dates = None

        for i, line in enumerate(lines):
            line_clean = line.strip()
            if len(line_clean) < 3:
                continue

            line_lower = line_clean.lower()

            # Skip section headers
            if any(header in line_lower for header in ['employment history', 'work experience', 'experience', 'career']):
                continue

            # Pattern 1: "Position at Company, Location"
            position_match = re.search(r'([A-Z][a-zA-Z\s]+(?:Associate|Assistant|Manager|Engineer|Developer|Analyst|Coordinator|Specialist|Director|Lead))\s+at\s+([A-Z][a-zA-Z\s&,\.]+)(?:,\s*([A-Za-z\s]+))?', line_clean)
            if position_match:
                position, company, location = position_match.groups()
                current_position = position.strip()
                current_company = company.strip()

                # Look for dates in next few lines
                for next_i in range(i+1, min(i+3, len(lines))):
                    next_line = lines[next_i].strip()
                    date_match = re.search(r'([A-Z][a-z]+\s+\d{4})\s*[—–-]\s*([A-Z][a-z]+\s+\d{4}|present|current)', next_line)
                    if date_match:
                        start_date, end_date = date_match.groups()
                        exp_entry = f"{current_position} at {current_company}"
                        if location:
                            exp_entry += f", {location}"
                        exp_entry += f" ({start_date} - {end_date})"
                        experience.append(exp_entry)
                        break
                else:
                    # No dates found, add without dates
                    exp_entry = f"{current_position} at {current_company}"
                    if location:
                        exp_entry += f", {location}"
                    experience.append(exp_entry)
                continue

            # Pattern 2: Standalone date ranges
            date_match = re.search(r'^([A-Z][a-z]+\s+\d{4})\s*[—–-]\s*([A-Z][a-z]+\s+\d{4}|present|current)$', line_clean)
            if date_match and current_position and current_company:
                start_date, end_date = date_match.groups()
                exp_entry = f"{current_position} at {current_company} ({start_date} - {end_date})"
                # Update the last experience entry if it exists
                if experience and current_position in experience[-1]:
                    experience[-1] = exp_entry
                else:
                    experience.append(exp_entry)
                continue

            # Pattern 3: Look for job positions using job title keywords
            if any(keyword in line_lower for keyword in job_title_keywords[:50]):
                if 10 < len(line_clean) < 100 and not line_clean.startswith('•'):
                    # This might be a job title, store it as current position
                    if ' at ' in line_clean:
                        experience.append(line_clean)
                    else:
                        current_position = line_clean

            # Pattern 4: Look for company names (lines that might be company names)
            elif (len(line_clean) > 5 and len(line_clean) < 80 and
                  not line_clean.startswith('•') and
                  not line_clean.startswith('-') and
                  any(char.isupper() for char in line_clean[:3])):
                # This might be a company name
                current_company = line_clean

        # Look for years of experience mentions in profile/summary
        experience_years_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\'\s*(?:tenure)',  # "five years' tenure"
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:with|over|about)\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:in|of)',
        ]

        for pattern in experience_years_patterns:
            years_matches = re.findall(pattern, text.lower())
            if years_matches:
                years = max([int(x) for x in years_matches])
                experience.append(f"{years} years of professional experience")
                break

        return experience[:10]  # Limit to 10 experiences

    def _extract_enhanced_education(self, text: str) -> list:
        """Extract education using dataset manager keywords."""
        education = []

        # Get education keywords from dataset manager
        edu_keywords = dataset_manager.education_keywords
        degree_types = edu_keywords.get('degree_types', [])
        institutions = edu_keywords.get('institutions', [])
        fields = edu_keywords.get('fields', [])

        lines = text.split('\n')
        text_lower = text.lower()

        # Enhanced education extraction
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Check for degree types
            if any(degree in line_lower for degree in degree_types):
                if len(line_clean) > 10 and len(line_clean) < 150:
                    education.append(line_clean)

            # Check for institution names
            elif any(inst in line_lower for inst in institutions):
                if len(line_clean) > 5 and len(line_clean) < 100:
                    education.append(line_clean)

        # Pattern-based extraction for structured education info
        edu_patterns = [
            r'(bachelor|master|phd|doctorate|diploma|certificate)(?:\s+of\s+|\s+in\s+|\s+degree\s+in\s+)([a-zA-Z\s]+)',
            r'(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?)(?:\s+in\s+)?([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+(university|college|institute|school)',
        ]

        for pattern in edu_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    edu_entry = ' '.join(match).title()
                    if edu_entry not in education and len(edu_entry) > 5:
                        education.append(edu_entry)

        return list(set(education))[:5]  # Remove duplicates and limit

    def _extract_enhanced_certifications(self, text: str) -> list:
        """Extract certifications using dataset manager."""
        certifications = []

        # Get all certifications from dataset manager
        all_certs = []
        for industry_certs in dataset_manager.certifications_db.values():
            if isinstance(industry_certs, list):
                all_certs.extend(industry_certs)

        text_lower = text.lower()
        lines = text.split('\n')

        # Check against comprehensive certification database
        for cert in all_certs:
            if cert.lower() in text_lower:
                certifications.append(cert.title())

        # Pattern-based extraction for structured certifications
        cert_patterns = [
            r'certified\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+certified',
            r'([a-zA-Z\s]+)\s+certification',
            r'([a-zA-Z\s]+)\s+certificate',
            r'([a-zA-Z\s]+)\s+license',
        ]

        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['certified', 'certification', 'certificate', 'license']):
                if 5 < len(line.strip()) < 100:
                    certifications.append(line.strip())

        return list(set(certifications))[:8]  # Remove duplicates and limit

    def _extract_enhanced_job_titles(self, text: str, industry: str) -> list:
        """Extract job titles using dataset manager."""
        job_titles = []

        # Get industry-specific job titles
        industry_titles = dataset_manager.job_titles_db.get(industry, [])
        all_titles = dataset_manager.get_all_job_titles()

        text_lower = text.lower()
        lines = text.split('\n')

        # Check against job title database
        for title in industry_titles + all_titles[:100]:  # Prioritize industry titles + top 100 general
            if title.lower() in text_lower:
                job_titles.append(title.title())

        # Pattern-based extraction
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Check if line matches job title pattern
            if any(keyword in line_lower for keyword in ['manager', 'engineer', 'developer', 'analyst', 'specialist']):
                if 5 < len(line_clean) < 60:
                    job_titles.append(line_clean)

        return list(set(job_titles))[:6]  # Remove duplicates and limit

    def extract_global_experience(self, text: str) -> Dict:
        """
        Global comprehensive experience extraction from resume.
        Returns structured experience data with years calculation.
        """
        lines = text.split('\n')

        # Initialize experience data structure
        experience_data = {
            'job_positions': [],
            'academic_experience': [],
            'courses_certifications': [],
            'achievements': [],
            'total_years': 0,
            'experience_summary': '',
            'skills_gained': []
        }

        # 1. Extract all job positions with companies and dates
        job_positions = self._extract_all_job_positions(lines)
        experience_data['job_positions'] = job_positions

        # 2. Extract academic/educational experience
        academic_exp = self._extract_all_academic_experience(lines)
        experience_data['academic_experience'] = academic_exp

        # 3. Extract courses, certifications, and training
        courses = self._extract_all_courses_training(lines)
        experience_data['courses_certifications'] = courses

        # 4. Extract achievements with metrics
        achievements = self._extract_performance_achievements(lines)
        experience_data['achievements'] = achievements

        # 5. Calculate total years of experience globally
        total_years = self._calculate_global_experience_years(text, job_positions)
        experience_data['total_years'] = total_years

        # 6. Extract overall experience summary
        summary = self._extract_experience_summary(text)
        experience_data['experience_summary'] = summary

        # 7. Extract skills gained from experience descriptions
        skills = self._extract_skills_from_experience(text)
        experience_data['skills_gained'] = skills

        return experience_data

    def _extract_all_job_positions(self, lines: list) -> list:
        """Extract all job positions with comprehensive parsing."""
        positions = []

        for i, line in enumerate(lines):
            line_clean = line.strip()
            if len(line_clean) < 5:
                continue

            # Pattern: "Position at Company, Location"
            job_match = re.search(
                r'([A-Z][a-zA-Z\s]+(?:Guard|Associate|Assistant|Manager|Engineer|Developer|Analyst|Coordinator|Specialist|Director|Lead|Officer|Intern))\s+at\s+([A-Z][a-zA-Z\s&,\.]+)(?:,\s*([A-Za-z\s]+))?',
                line_clean
            )

            if job_match:
                position, company, location = job_match.groups()
                current_position = position.strip()
                current_company = company.strip()
                current_location = location.strip() if location else None
                current_dates = None

                # Look for dates in next 3 lines
                for next_i in range(i+1, min(i+4, len(lines))):
                    next_line = lines[next_i].strip()
                    date_match = re.search(
                        r'([A-Z][a-z]+\s+\d{4})\s*[—–-]\s*([A-Z][a-z]+\s+\d{4}|present|current)',
                        next_line
                    )
                    if date_match:
                        start_date, end_date = date_match.groups()
                        current_dates = f"{start_date} - {end_date}"
                        break

                # Create position entry
                position_entry = {
                    'title': current_position,
                    'company': current_company,
                    'location': current_location,
                    'dates': current_dates,
                    'formatted': self._format_position_entry(current_position, current_company, current_location, current_dates)
                }
                positions.append(position_entry)

        return positions

    def _extract_all_academic_experience(self, lines: list) -> list:
        """Extract all academic and educational experience."""
        academic = []

        for i, line in enumerate(lines):
            line_clean = line.strip()

            # Look for degree programs
            degree_patterns = [
                r'(Bachelor|Master|Associates?\s+Degree|Graduate\s+Certificate|Certificate)\s+(?:of\s+|in\s+)?([^,]+)(?:,\s*([^,]+))?(?:,\s*([^,]+))?',
                r'([A-Z][a-zA-Z\s]+(?:Program|Course|Training|Certificate))[^,]*,\s*([^,]+)',
            ]

            for pattern in degree_patterns:
                match = re.search(pattern, line_clean, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        program = groups[0].strip()
                        field_or_institution = groups[1].strip()

                        # Look for dates
                        dates = None
                        for next_i in range(i+1, min(i+3, len(lines))):
                            next_line = lines[next_i].strip()
                            date_match = re.search(
                                r'([A-Z][a-z]+\s+\d{4})\s*[—–-]\s*([A-Z][a-z]+\s+\d{4})',
                                next_line
                            )
                            if date_match:
                                dates = f"{date_match.group(1)} - {date_match.group(2)}"
                                break

                        academic_entry = {
                            'type': program,
                            'field': field_or_institution,
                            'institution': groups[2] if len(groups) > 2 and groups[2] else '',
                            'dates': dates,
                            'formatted': f"{program} in {field_or_institution}" + (f" ({dates})" if dates else "")
                        }
                        academic.append(academic_entry)
                    break

        return academic

    def _extract_all_courses_training(self, lines: list) -> list:
        """Extract courses, training, and certification programs."""
        courses = []

        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Look for training, courses, and certification programs
            if any(keyword in line_lower for keyword in ['training', 'course', 'program', 'approach', 'certification']):
                if len(line_clean) > 15 and len(line_clean) < 200:
                    # Extract course/training information
                    course_patterns = [
                        r'([^,]+(?:Training|Course|Program|Approach|Certification))[^,]*(?:,\s*([^,]+))?',
                        r'([A-Z][A-Za-z\s\.]+(?:Level\s+[IVX]+|Certificate))[^,]*(?:,\s*([^,]+))?'
                    ]

                    for pattern in course_patterns:
                        match = re.search(pattern, line_clean)
                        if match:
                            course_name = match.group(1).strip()
                            institution = match.group(2).strip() if match.group(2) else ''

                            course_entry = {
                                'name': course_name,
                                'institution': institution,
                                'formatted': f"{course_name}" + (f" at {institution}" if institution else "")
                            }
                            courses.append(course_entry)
                            break

        return courses

    def _extract_performance_achievements(self, lines: list) -> list:
        """Extract achievements with performance metrics and quantifiable results."""
        achievements = []

        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Look for achievement bullets with metrics
            if (line_clean.startswith('•') or line_clean.startswith('-')) and len(line_clean) > 20:
                # Check for performance indicators
                performance_keywords = [
                    'decreased', 'increased', 'improved', 'reduced', 'saved', 'cut',
                    'maintained', 'achieved', 'exceeded', 'enhanced', 'optimized',
                    'implemented', 'introduced', 'awarded', 'certified', 'qualified'
                ]

                if any(keyword in line_lower for keyword in performance_keywords):
                    achievement_text = line_clean[1:].strip()  # Remove bullet

                    # Extract percentage or numeric metrics
                    metrics = re.findall(r'(\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s*(?:years?|months?|days?))', achievement_text)

                    achievement_entry = {
                        'text': achievement_text,
                        'metrics': metrics,
                        'category': self._categorize_achievement(achievement_text)
                    }
                    achievements.append(achievement_entry)

        return achievements[:8]  # Top 8 achievements

    def _categorize_achievement(self, achievement_text: str) -> str:
        """Categorize achievement by type."""
        text_lower = achievement_text.lower()

        if any(word in text_lower for word in ['theft', 'security', 'loss', 'prevention']):
            return 'security'
        elif any(word in text_lower for word in ['efficiency', 'speed', 'accuracy', 'performance']):
            return 'performance'
        elif any(word in text_lower for word in ['cost', 'saved', 'budget', 'revenue']):
            return 'financial'
        elif any(word in text_lower for word in ['training', 'certification', 'qualified']):
            return 'professional_development'
        else:
            return 'general'

    def _calculate_global_experience_years(self, text: str, job_positions: list) -> int:
        """Calculate total years from all sources - job dates, profile mentions, and experience descriptions."""
        total_years = 0

        # Method 1: Calculate from job position dates
        job_years = 0
        for position in job_positions:
            if position['dates']:
                dates_str = position['dates']
                try:
                    # Extract years from date range
                    years_match = re.findall(r'\d{4}', dates_str)
                    if len(years_match) >= 2:
                        start_year = int(years_match[0])
                        end_year = int(years_match[1]) if 'present' not in dates_str.lower() and 'current' not in dates_str.lower() else 2024
                        position_years = max(0, end_year - start_year)
                        if position_years <= 15:  # Reasonable job duration
                            job_years += position_years
                except:
                    pass

        # Method 2: Extract from profile/summary text
        profile_years = 0
        experience_patterns = [
            r'(\w+)\s+years?\'\s*(?:experience|tenure)',  # "five years' tenure"
            r'(?:with|over|about)\s+(\w+)\s+years?',       # "with five years"
            r'(\d+)\s+years?\s*(?:of\s*)?(?:experience|exp)',  # "5 years experience"
        ]

        # Convert word numbers to digits
        word_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'fifteen': 15, 'twenty': 20
        }

        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if match in word_to_num:
                    profile_years = max(profile_years, word_to_num[match])
                elif match.isdigit():
                    profile_years = max(profile_years, int(match))

        # Use the higher value between calculated job years and profile years
        total_years = max(job_years, profile_years)

        return min(total_years, 50)  # Cap at reasonable maximum

    def _extract_experience_summary(self, text: str) -> str:
        """Extract comprehensive experience summary from profile."""
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Find profile/summary section
            if any(header in line_lower for header in ['profile', 'summary', 'objective', 'about']):
                # Get content from next few lines
                summary_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    content_line = lines[j].strip()
                    if len(content_line) > 20 and not content_line.lower().startswith(('employment', 'education', 'skills')):
                        summary_lines.append(content_line)

                if summary_lines:
                    return ' '.join(summary_lines)

        return ''

    def _extract_skills_from_experience(self, text: str) -> list:
        """Extract skills mentioned in experience descriptions."""
        # Get all skills from dataset manager
        all_skills = dataset_manager.get_all_skills()
        found_skills = []

        text_lower = text.lower()

        # Check for skills in experience context
        for skill in all_skills[:200]:  # Check top 200 skills
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills[:20]  # Top 20 skills found

    def _format_position_entry(self, position: str, company: str, location: str, dates: str) -> str:
        """Format a position entry consistently."""
        entry = f"{position} at {company}"
        if location:
            entry += f", {location}"
        if dates:
            entry += f" ({dates})"
        return entry


# Global instance
resume_analyzer = ResumeAnalyzer()