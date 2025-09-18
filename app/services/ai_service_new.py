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


class DatasetManager:
    """Manages manual datasets for skills, job titles, and industry-specific information."""

    def __init__(self, dataset_path: str = "datasets/"):
        self.dataset_path = dataset_path
        self.skills_db = {}
        self.job_titles_db = {}
        self.industries_db = {}
        self.certifications_db = {}
        self.education_keywords = {}
        self._load_datasets()

    def _load_datasets(self):
        """Load all manual datasets."""
        try:
            self._load_skills_dataset()
            self._load_job_titles_dataset()
            self._load_industries_dataset()
            self._load_certifications_dataset()
            self._load_education_keywords()
        except Exception as e:
            print(f"Warning: Could not load some datasets: {e}")
            self._load_fallback_data()

    def _load_skills_dataset(self):
        """Load skills dataset from JSON file."""
        skills_file = os.path.join(self.dataset_path, "skills.json")
        try:
            with open(skills_file, "r", encoding="utf-8") as f:
                self.skills_db = json.load(f)
        except FileNotFoundError:
            self._create_default_skills_dataset()

    def _load_job_titles_dataset(self):
        """Load job titles dataset."""
        titles_file = os.path.join(self.dataset_path, "job_titles.json")
        try:
            with open(titles_file, "r", encoding="utf-8") as f:
                self.job_titles_db = json.load(f)
        except FileNotFoundError:
            self._create_default_job_titles_dataset()

    def _load_industries_dataset(self):
        """Load industries dataset."""
        industries_file = os.path.join(self.dataset_path, "industries.json")
        try:
            with open(industries_file, "r", encoding="utf-8") as f:
                self.industries_db = json.load(f)
        except FileNotFoundError:
            self._create_default_industries_dataset()

    def _load_certifications_dataset(self):
        """Load certifications dataset."""
        cert_file = os.path.join(self.dataset_path, "certifications.json")
        try:
            with open(cert_file, "r", encoding="utf-8") as f:
                self.certifications_db = json.load(f)
        except FileNotFoundError:
            self._create_default_certifications_dataset()

    def _load_education_keywords(self):
        """Load education keywords dataset."""
        edu_file = os.path.join(self.dataset_path, "education_keywords.json")
        try:
            with open(edu_file, "r", encoding="utf-8") as f:
                self.education_keywords = json.load(f)
        except FileNotFoundError:
            self._create_default_education_keywords()

    def _create_default_skills_dataset(self):
        """Create default skills dataset covering multiple industries."""
        self.skills_db = {
            "technology": {
                "programming": [
                    "python",
                    "javascript",
                    "java",
                    "c++",
                    "c#",
                    "php",
                    "ruby",
                    "go",
                    "rust",
                    "r",
                    "sql",
                ],
                "web_development": [
                    "html",
                    "css",
                    "react",
                    "angular",
                    "vue",
                    "node.js",
                    "bootstrap",
                ],
                "databases": [
                    "mysql",
                    "postgresql",
                    "mongodb",
                    "redis",
                    "oracle",
                    "sqlite",
                ],
                "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins"],
                "tools": ["git", "jira", "confluence", "slack"],
            },
            "marketing": {
                "digital_marketing": [
                    "seo",
                    "sem",
                    "google ads",
                    "facebook ads",
                    "content marketing",
                    "email marketing",
                ],
                "analytics": [
                    "google analytics",
                    "adobe analytics",
                    "tableau",
                    "power bi",
                    "excel",
                ],
                "social_media": [
                    "social media management",
                    "hootsuite",
                    "buffer",
                    "sprout social",
                ],
                "content": [
                    "copywriting",
                    "content creation",
                    "blogging",
                    "video editing",
                    "graphic design",
                ],
            },
            "finance": {
                "accounting": [
                    "quickbooks",
                    "sap",
                    "oracle financials",
                    "gaap",
                    "ifrs",
                    "financial modeling",
                ],
                "analysis": [
                    "financial analysis",
                    "risk management",
                    "investment analysis",
                    "budgeting",
                    "forecasting",
                ],
                "tools": [
                    "excel",
                    "bloomberg terminal",
                    "matlab",
                    "r",
                    "python",
                    "sql",
                ],
            },
            "healthcare": {
                "clinical": [
                    "patient care",
                    "medical records",
                    "hipaa",
                    "clinical research",
                    "medical coding",
                ],
                "administrative": [
                    "healthcare administration",
                    "insurance",
                    "billing",
                    "scheduling",
                ],
                "technical": [
                    "epic",
                    "cerner",
                    "allscripts",
                    "meditech",
                    "emr systems",
                ],
            },
            "sales": {
                "techniques": [
                    "cold calling",
                    "lead generation",
                    "negotiation",
                    "closing",
                    "prospecting",
                ],
                "crm": ["salesforce", "hubspot", "pipedrive", "zoho", "dynamics 365"],
                "analysis": [
                    "sales analytics",
                    "forecasting",
                    "pipeline management",
                    "territory management",
                ],
            },
            "human_resources": {
                "recruitment": [
                    "talent acquisition",
                    "interviewing",
                    "onboarding",
                    "ats systems",
                ],
                "compliance": [
                    "employment law",
                    "hr policies",
                    "benefits administration",
                    "payroll",
                ],
                "systems": ["workday", "bamboohr", "adp", "successfactors"],
            },
            "operations": {
                "management": [
                    "project management",
                    "process improvement",
                    "lean",
                    "six sigma",
                    "agile",
                ],
                "supply_chain": [
                    "inventory management",
                    "logistics",
                    "procurement",
                    "vendor management",
                ],
                "quality": [
                    "quality assurance",
                    "iso standards",
                    "continuous improvement",
                ],
            },
            "education": {
                "teaching": [
                    "curriculum development",
                    "lesson planning",
                    "classroom management",
                    "student assessment",
                ],
                "technology": [
                    "learning management systems",
                    "blackboard",
                    "canvas",
                    "moodle",
                    "zoom",
                ],
                "administration": [
                    "educational leadership",
                    "student services",
                    "academic advising",
                ],
            },
            "soft_skills": {
                "leadership": [
                    "team leadership",
                    "mentoring",
                    "coaching",
                    "strategic thinking",
                    "decision making",
                ],
                "communication": [
                    "public speaking",
                    "presentation",
                    "writing",
                    "interpersonal",
                    "negotiation",
                ],
                "problem_solving": [
                    "analytical thinking",
                    "creative problem solving",
                    "troubleshooting",
                    "innovation",
                ],
                "personal": [
                    "time management",
                    "adaptability",
                    "attention to detail",
                    "multitasking",
                    "organization",
                ],
            },
        }
        self._save_dataset("skills.json", self.skills_db)

    def _create_default_job_titles_dataset(self):
        """Create default job titles dataset."""
        self.job_titles_db = {
            "technology": [
                "software engineer",
                "developer",
                "programmer",
                "web developer",
                "data scientist",
                "systems analyst",
                "database administrator",
                "network engineer",
                "cybersecurity analyst",
                "devops engineer",
                "product manager",
                "technical lead",
                "architect",
                "qa engineer",
            ],
            "marketing": [
                "marketing manager",
                "digital marketer",
                "content marketer",
                "seo specialist",
                "ppc specialist",
                "brand manager",
                "social media manager",
                "marketing coordinator",
                "growth hacker",
                "marketing analyst",
                "email marketing specialist",
                "influencer marketer",
            ],
            "finance": [
                "financial analyst",
                "accountant",
                "controller",
                "cfo",
                "investment banker",
                "financial advisor",
                "credit analyst",
                "budget analyst",
                "tax specialist",
                "audit manager",
                "treasury analyst",
                "risk analyst",
                "compliance officer",
            ],
            "healthcare": [
                "registered nurse",
                "physician",
                "medical assistant",
                "healthcare administrator",
                "physical therapist",
                "pharmacist",
                "medical technician",
                "radiologist",
                "healthcare manager",
                "clinical coordinator",
                "medical coder",
            ],
            "sales": [
                "sales representative",
                "account manager",
                "business development",
                "sales manager",
                "inside sales",
                "outside sales",
                "sales coordinator",
                "key account manager",
                "sales engineer",
                "channel partner manager",
                "regional sales manager",
            ],
            "human_resources": [
                "hr manager",
                "recruiter",
                "hr coordinator",
                "talent acquisition",
                "hr business partner",
                "compensation analyst",
                "benefits administrator",
                "hr generalist",
                "training manager",
                "employee relations",
                "hr director",
                "people operations",
            ],
            "operations": [
                "operations manager",
                "project manager",
                "program manager",
                "business analyst",
                "process improvement",
                "supply chain manager",
                "logistics coordinator",
                "operations analyst",
                "facility manager",
                "quality manager",
            ],
            "education": [
                "teacher",
                "professor",
                "instructor",
                "academic advisor",
                "principal",
                "dean",
                "curriculum coordinator",
                "educational consultant",
                "tutor",
                "training specialist",
                "instructional designer",
                "education administrator",
            ],
        }
        self._save_dataset("job_titles.json", self.job_titles_db)

    def _create_default_industries_dataset(self):
        """Create default industries dataset."""
        self.industries_db = {
            "technology": [
                "software",
                "it services",
                "telecommunications",
                "internet",
                "computer hardware",
            ],
            "finance": ["banking", "investment", "insurance", "real estate", "fintech"],
            "healthcare": [
                "hospitals",
                "pharmaceuticals",
                "medical devices",
                "biotechnology",
                "healthcare services",
            ],
            "retail": [
                "e-commerce",
                "fashion",
                "consumer goods",
                "automotive",
                "food & beverage",
            ],
            "manufacturing": [
                "aerospace",
                "automotive",
                "chemicals",
                "electronics",
                "industrial equipment",
            ],
            "energy": [
                "oil & gas",
                "renewable energy",
                "utilities",
                "mining",
                "environmental services",
            ],
            "media": [
                "advertising",
                "entertainment",
                "publishing",
                "broadcasting",
                "digital media",
            ],
            "consulting": [
                "management consulting",
                "strategy",
                "operations",
                "hr consulting",
                "it consulting",
            ],
            "education": [
                "universities",
                "k-12 schools",
                "online education",
                "training",
                "educational technology",
            ],
            "government": [
                "federal government",
                "state government",
                "local government",
                "military",
                "non-profit",
            ],
        }
        self._save_dataset("industries.json", self.industries_db)

    def _create_default_certifications_dataset(self):
        """Create default certifications dataset."""
        self.certifications_db = {
            "technology": [
                "aws certified",
                "microsoft certified",
                "google cloud certified",
                "cisco certified",
                "comptia security+",
                "pmp",
                "cissp",
                "cisa",
                "itil",
                "scrum master",
            ],
            "finance": [
                "cpa",
                "cfa",
                "frm",
                "caia",
                "fpa",
                "cfp",
                "cia",
                "cma",
                "acca",
            ],
            "healthcare": [
                "bls",
                "acls",
                "cpr",
                "medical license",
                "nursing license",
                "pharmacy license",
            ],
            "marketing": [
                "google ads certified",
                "hubspot certified",
                "facebook blueprint",
                "hootsuite certified",
                "google analytics certified",
                "marketo certified",
            ],
            "project_management": [
                "pmp",
                "prince2",
                "agile certified",
                "scrum master",
                "lean six sigma",
                "capm",
            ],
            "hr": ["shrm-cp", "shrm-scp", "phr", "sphr", "hrci", "cipd"],
        }
        self._save_dataset("certifications.json", self.certifications_db)

    def _create_default_education_keywords(self):
        """Create default education keywords."""
        self.education_keywords = {
            "degree_types": [
                "bachelor",
                "master",
                "phd",
                "doctorate",
                "associate",
                "diploma",
                "certificate",
                "mba",
                "md",
                "jd",
                "bs",
                "ba",
                "ms",
                "ma",
            ],
            "institutions": [
                "university",
                "college",
                "institute",
                "school",
                "academy",
                "polytechnic",
            ],
            "fields": [
                "computer science",
                "business administration",
                "engineering",
                "marketing",
                "finance",
                "psychology",
                "biology",
                "chemistry",
                "physics",
                "mathematics",
                "economics",
                "accounting",
                "nursing",
                "medicine",
                "law",
                "education",
            ],
        }
        self._save_dataset("education_keywords.json", self.education_keywords)

    def _save_dataset(self, filename: str, data: Dict):
        """Save dataset to file."""
        os.makedirs(self.dataset_path, exist_ok=True)
        filepath = os.path.join(self.dataset_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_fallback_data(self):
        """Load minimal fallback data if datasets can't be loaded."""
        self.skills_db = {
            "general": {"basic": ["communication", "teamwork", "problem solving"]}
        }
        self.job_titles_db = {
            "general": ["manager", "specialist", "coordinator", "analyst"]
        }
        self.industries_db = {"general": ["business", "services", "manufacturing"]}
        self.certifications_db = {"general": ["certified", "licensed"]}
        self.education_keywords = {"degree_types": ["bachelor", "master", "degree"]}

    def get_all_skills(self) -> List[str]:
        """Get all skills from all categories."""
        all_skills = []
        for industry in self.skills_db.values():
            if isinstance(industry, dict):
                for category in industry.values():
                    if isinstance(category, list):
                        all_skills.extend(category)
        return list(set(all_skills))

    def get_skills_by_industry(self, industry: str) -> List[str]:
        """Get skills for specific industry."""
        industry_skills = []
        if industry in self.skills_db:
            for category in self.skills_db[industry].values():
                if isinstance(category, list):
                    industry_skills.extend(category)
        return industry_skills

    def get_all_job_titles(self) -> List[str]:
        """Get all job titles."""
        all_titles = []
        for titles in self.job_titles_db.values():
            if isinstance(titles, list):
                all_titles.extend(titles)
        return list(set(all_titles))

    def detect_industry(self, text: str) -> str:
        """Detect industry based on text content."""
        text_lower = text.lower()
        industry_scores = {}

        for industry, keywords in self.industries_db.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                industry_scores[industry] = score

        # Also check skills and job titles for industry detection
        for industry in self.skills_db.keys():
            skills = self.get_skills_by_industry(industry)
            skill_matches = sum(1 for skill in skills if skill.lower() in text_lower)
            industry_scores[industry] = (
                industry_scores.get(industry, 0) + skill_matches * 0.5
            )

        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return "general"


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

        # --- Extract phone (enhanced patterns) ---
        phone_patterns = [
            r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            r"(?:\+?[0-9]{1,3}[-.\s]?)?(?:\(?[0-9]{2,4}\)?[-.\s]?)?[0-9]{3,4}[-.\s]?[0-9]{3,4}",
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
        """Enhanced experience extraction."""
        experience = []
        lines = text.split("\n")

        # Get all job titles from dataset
        all_job_titles = self.dataset_manager.get_all_job_titles()

        # Extract organizations
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        # Extract dates
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

            # Check for company names
            elif any(org.lower() in line.lower() for org in orgs):
                if current_job:
                    current_job["company"] = line

            # Check for dates
            elif any(date in line for date in dates) or self._contains_date_pattern(
                line
            ):
                if current_job:
                    current_job["duration"] = line

            # Check for bullet points (responsibilities/achievements)
            elif line.startswith(("•", "-", "*")) and current_job:
                if "responsibilities" not in current_job:
                    current_job["responsibilities"] = []
                current_job["responsibilities"].append(line.lstrip("•-* "))

        if current_job and "title" in current_job:
            experience.append(current_job)

        return experience[:5]

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
        """Enhanced education extraction using dataset keywords."""
        education = []
        degree_keywords = self.dataset_manager.education_keywords.get(
            "degree_types", []
        )
        field_keywords = self.dataset_manager.education_keywords.get("fields", [])

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Check if line contains degree keywords
            has_degree = any(degree.lower() in line_lower for degree in degree_keywords)
            has_field = any(field.lower() in line_lower for field in field_keywords)

            if has_degree or has_field:
                edu_entry = {"degree": line}

                # Try to extract GPA
                gpa_match = re.search(r"gpa:?\s*(\d+\.?\d*)", line_lower)
                if gpa_match:
                    edu_entry["gpa"] = gpa_match.group(1)

                # Try to extract year
                year_match = re.search(r"\b(19|20)\d{2}\b", line)
                if year_match:
                    edu_entry["year"] = year_match.group()

                education.append(edu_entry)

        return education[:3]

    def _extract_certifications_enhanced(self, text: str) -> List[Dict]:
        """Enhanced certification extraction using manual dataset."""
        certifications = []
        cert_keywords = []

        # Get all certifications from dataset
        for category, certs in self.dataset_manager.certifications_db.items():
            cert_keywords.extend(certs)

        # Add general certification keywords
        cert_keywords.extend(
            ["certified", "certification", "certificate", "license", "licensed"]
        )

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            # Check if line contains certification keywords
            if any(keyword.lower() in line_lower for keyword in cert_keywords):
                cert_entry = {"name": line}

                # Try to extract year
                year_match = re.search(r"\b(19|20)\d{2}\b", line)
                if year_match:
                    cert_entry["year"] = year_match.group()

                # Try to extract expiry
                if "expires" in line_lower or "expiry" in line_lower:
                    cert_entry["has_expiry"] = True

                certifications.append(cert_entry)

        return certifications[:5]

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

    # === DATASET MANAGEMENT METHODS ===

    def add_skills_to_dataset(self, industry: str, category: str, skills: List[str]):
        """Add new skills to the dataset."""
        if industry not in self.dataset_manager.skills_db:
            self.dataset_manager.skills_db[industry] = {}

        if category not in self.dataset_manager.skills_db[industry]:
            self.dataset_manager.skills_db[industry][category] = []

        # Add new skills (avoid duplicates)
        existing_skills = [
            s.lower() for s in self.dataset_manager.skills_db[industry][category]
        ]
        for skill in skills:
            if skill.lower() not in existing_skills:
                self.dataset_manager.skills_db[industry][category].append(skill)

        # Save updated dataset
        self.dataset_manager._save_dataset(
            "skills.json", self.dataset_manager.skills_db
        )

    def add_job_titles_to_dataset(self, industry: str, titles: List[str]):
        """Add new job titles to the dataset."""
        if industry not in self.dataset_manager.job_titles_db:
            self.dataset_manager.job_titles_db[industry] = []

        # Add new titles (avoid duplicates)
        existing_titles = [
            t.lower() for t in self.dataset_manager.job_titles_db[industry]
        ]
        for title in titles:
            if title.lower() not in existing_titles:
                self.dataset_manager.job_titles_db[industry].append(title)

        # Save updated dataset
        self.dataset_manager._save_dataset(
            "job_titles.json", self.dataset_manager.job_titles_db
        )

    def add_certifications_to_dataset(self, industry: str, certifications: List[str]):
        """Add new certifications to the dataset."""
        if industry not in self.dataset_manager.certifications_db:
            self.dataset_manager.certifications_db[industry] = []

        # Add new certifications (avoid duplicates)
        existing_certs = [
            c.lower() for c in self.dataset_manager.certifications_db[industry]
        ]
        for cert in certifications:
            if cert.lower() not in existing_certs:
                self.dataset_manager.certifications_db[industry].append(cert)

        # Save updated dataset
        self.dataset_manager._save_dataset(
            "certifications.json", self.dataset_manager.certifications_db
        )

    def get_dataset_stats(self) -> Dict:
        """Get statistics about the current datasets."""
        stats = {
            "skills": {
                "total_industries": len(self.dataset_manager.skills_db),
                "total_skills": len(self.dataset_manager.get_all_skills()),
                "industries": list(self.dataset_manager.skills_db.keys()),
            },
            "job_titles": {
                "total_industries": len(self.dataset_manager.job_titles_db),
                "total_titles": len(self.dataset_manager.get_all_job_titles()),
                "industries": list(self.dataset_manager.job_titles_db.keys()),
            },
            "certifications": {
                "total_industries": len(self.dataset_manager.certifications_db),
                "total_certifications": sum(
                    len(certs)
                    for certs in self.dataset_manager.certifications_db.values()
                ),
                "industries": list(self.dataset_manager.certifications_db.keys()),
            },
        }
        return stats

    def export_datasets(self, export_path: str = "datasets_export/"):
        """Export all datasets to specified directory."""
        os.makedirs(export_path, exist_ok=True)

        datasets = {
            "skills.json": self.dataset_manager.skills_db,
            "job_titles.json": self.dataset_manager.job_titles_db,
            "industries.json": self.dataset_manager.industries_db,
            "certifications.json": self.dataset_manager.certifications_db,
            "education_keywords.json": self.dataset_manager.education_keywords,
        }

        for filename, data in datasets.items():
            filepath = os.path.join(export_path, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return f"Datasets exported to {export_path}"

    def import_datasets(self, import_path: str = "datasets_import/"):
        """Import datasets from specified directory."""
        if not os.path.exists(import_path):
            raise FileNotFoundError(f"Import directory {import_path} does not exist")

        datasets_loaded = 0

        dataset_files = {
            "skills.json": "skills_db",
            "job_titles.json": "job_titles_db",
            "industries.json": "industries_db",
            "certifications.json": "certifications_db",
            "education_keywords.json": "education_keywords",
        }

        for filename, attr_name in dataset_files.items():
            filepath = os.path.join(import_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        setattr(self.dataset_manager, attr_name, data)
                        datasets_loaded += 1
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")

        return f"Successfully imported {datasets_loaded} datasets"


# Global AI service instance
ai_service = AIService()


# === USAGE EXAMPLES ===


def example_usage():
    """Example usage of the enhanced AI service."""

    # Initialize service (will create default datasets if none exist)
    service = AIService("./my_datasets/")

    # Add custom skills for a new industry
    service.add_skills_to_dataset(
        industry="retail",
        category="customer_service",
        skills=[
            "customer support",
            "pos systems",
            "inventory management",
            "visual merchandising",
        ],
    )

    # Add job titles for retail
    service.add_job_titles_to_dataset(
        industry="retail",
        titles=[
            "store manager",
            "sales associate",
            "merchandiser",
            "cashier",
            "inventory specialist",
        ],
    )

    # Analyze a resume with industry targeting
    resume_text = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    
    Professional Summary
    Experienced retail manager with 8 years of experience in customer service and team leadership.
    
    Experience
    Store Manager - Best Buy (2019-2023)
    - Managed team of 15 sales associates
    - Increased store revenue by 25%
    - Implemented new inventory management system
    
    Skills
    - Customer service
    - Team leadership
    - POS systems
    - Inventory management
    - Visual merchandising
    
    Education
    Bachelor of Business Administration
    University of Commerce, 2015
    """

    # Analyze resume
    resume_analysis = service.analyze_resume(resume_text, target_industry="retail")
    print("Resume Analysis:", json.dumps(resume_analysis, indent=2))

    # Match against job requirements
    job_requirements = {
        "industry": "retail",
        "required_skills": ["customer service", "team leadership", "pos systems"],
        "preferred_skills": ["inventory management", "visual merchandising", "sales"],
        "required_experience": {
            "min_years": 5,
            "preferred_roles": ["store manager", "assistant manager"],
        },
        "required_education": {"min_degree": "bachelor"},
        "matching_weights": {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "certifications": 0.1,
        },
    }

    match_results = service.match_resume_to_job(resume_analysis, job_requirements)
    print("Job Match Results:", json.dumps(match_results, indent=2))

    # Get dataset statistics
    stats = service.get_dataset_stats()
    print("Dataset Stats:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    example_usage()
