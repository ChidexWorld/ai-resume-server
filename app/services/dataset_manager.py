"""
Dataset Manager for AI Resume Server.
Manages manual datasets for skills, job titles, and industry-specific information.
"""

import os
import json
from typing import Dict, List, Optional


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
                    "golang",
                    "rust",
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
                    "typescript",
                    "full stack development",
                    "frontend development",
                    "backend development",
                    "api development",
                    "api integration",
                    "expressjs",
                    "responsive design",
                    "user interface design",
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
                    "mathematics teaching",
                    "computer science teaching",
                    "educational technology",
                    "student mentoring",
                    "academic coaching",
                    "exam preparation",
                    "private tutoring",
                    "group instruction",
                    "individual attention",
                    "student motivation",
                    "educational psychology",
                ],
                "technology": [
                    "learning management systems",
                    "blackboard",
                    "canvas",
                    "moodle",
                    "zoom",
                    "computer literacy",
                    "microsoft office",
                    "google classroom",
                    "educational software",
                    "interactive whiteboards",
                    "online teaching",
                    "remote learning",
                    "digital literacy",
                    "programming concepts",
                    "basic coding",
                ],
                "administration": [
                    "educational leadership",
                    "student services",
                    "academic advising",
                    "school administration",
                    "student records",
                    "academic planning",
                    "disciplinary management",
                    "parent communication",
                    "staff coordination",
                    "resource management",
                ],
                "subject_expertise": [
                    "mathematics",
                    "computer science",
                    "programming",
                    "algebra",
                    "geometry",
                    "calculus",
                    "statistics",
                    "data analysis",
                    "problem solving",
                    "logical thinking",
                    "analytical skills",
                ],
            },
            "fashion": {
                "design": [
                    "fashion design",
                    "pattern making",
                    "sketching",
                    "color theory",
                    "fabric selection",
                    "garment construction",
                    "trend forecasting",
                    "textile knowledge",
                ],
                "software": [
                    "adobe illustrator",
                    "adobe photoshop",
                    "cad",
                    "fashion cad",
                    "pattern design software",
                ],
                "production": [
                    "product development",
                    "manufacturing",
                    "quality control",
                    "vendor management",
                    "merchandising",
                    "collection development",
                ],
                "business": [
                    "brand development",
                    "market research",
                    "fashion marketing",
                    "retail buying",
                    "fashion merchandising",
                ],
            },
            "nutrition": {
                "clinical": [
                    "nutrition assessment",
                    "dietary counseling",
                    "meal planning",
                    "clinical nutrition",
                    "medical nutrition therapy",
                    "nutrition education",
                    "food service management",
                ],
                "specialized": [
                    "sports nutrition",
                    "pediatric nutrition",
                    "geriatric nutrition",
                    "eating disorders",
                    "diabetes management",
                    "weight management",
                ],
                "food_safety": [
                    "food preparation",
                    "food sanitation",
                    "haccp",
                    "food safety regulations",
                    "kitchen management",
                ],
                "programs": [
                    "wic program",
                    "nutrition programs",
                    "community nutrition",
                    "public health nutrition",
                ],
            },
            "fitness": {
                "training": [
                    "personal training",
                    "group fitness",
                    "strength training",
                    "cardiovascular training",
                    "functional training",
                    "sports conditioning",
                    "rehabilitation",
                ],
                "specializations": [
                    "weight loss",
                    "muscle building",
                    "sports performance",
                    "injury prevention",
                    "corrective exercise",
                    "flexibility training",
                ],
                "certifications": [
                    "ace certified",
                    "nasm certified",
                    "acsm certified",
                    "cpr certified",
                    "first aid certified",
                ],
                "business": [
                    "client retention",
                    "program design",
                    "fitness assessment",
                    "goal setting",
                    "motivation techniques",
                ],
            },
            "design": {
                "ux_ui": [
                    "user experience design",
                    "user interface design",
                    "wireframing",
                    "prototyping",
                    "user research",
                    "usability testing",
                    "information architecture",
                    "interaction design",
                ],
                "tools": [
                    "sketch",
                    "figma",
                    "adobe xd",
                    "invision",
                    "balsamiq",
                    "zeplin",
                    "principle",
                ],
                "web_design": [
                    "html5",
                    "css3",
                    "javascript",
                    "responsive design",
                    "mobile design",
                    "web accessibility",
                ],
                "research": [
                    "user interviews",
                    "surveys",
                    "a/b testing",
                    "analytics",
                    "persona development",
                    "journey mapping",
                ],
            },
            "security": {
                "physical_security": [
                    "surveillance",
                    "access control",
                    "patrol procedures",
                    "incident response",
                    "emergency procedures",
                    "security protocols",
                    "report writing",
                ],
                "equipment": [
                    "cctv systems",
                    "alarm systems",
                    "security equipment",
                    "communication devices",
                    "restraining devices",
                ],
                "skills": [
                    "observation skills",
                    "investigation skills",
                    "conflict resolution",
                    "crowd control",
                    "first aid",
                    "self defense",
                ],
                "compliance": [
                    "security regulations",
                    "safety compliance",
                    "criminal justice knowledge",
                    "legal procedures",
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
                "mathematics teacher",
                "computer teacher",
                "science teacher",
                "english teacher",
                "head teacher",
                "deputy principal",
                "senior prefect",
                "deputy senior prefect",
                "prefect",
                "regulatory prefect",
                "form teacher",
                "subject coordinator",
                "school administrator",
                "vice principal",
                "assistant teacher",
                "club president",
                "student representative",
            ],
            "fashion": [
                "fashion designer",
                "senior fashion designer",
                "associate fashion designer",
                "lead fashion designer",
                "creative director",
                "design director",
                "fashion stylist",
                "pattern maker",
                "textile designer",
                "fashion illustrator",
                "fashion merchandiser",
                "fashion buyer",
                "fashion coordinator",
            ],
            "nutrition": [
                "nutritionist",
                "dietitian",
                "nutrition consultant",
                "registered dietitian",
                "clinical nutritionist",
                "sports nutritionist",
                "community nutritionist",
                "nutrition educator",
                "food service director",
                "nutrition specialist",
                "wellness coordinator",
            ],
            "fitness": [
                "personal trainer",
                "fitness instructor",
                "group fitness instructor",
                "strength and conditioning coach",
                "fitness coordinator",
                "wellness coach",
                "exercise physiologist",
                "fitness manager",
                "gym manager",
                "fitness director",
                "athletic trainer",
                "sports trainer",
            ],
            "design": [
                "ux designer",
                "ui designer",
                "user experience designer",
                "user interface designer",
                "product designer",
                "interaction designer",
                "visual designer",
                "graphic designer",
                "web designer",
                "design lead",
                "senior designer",
                "junior designer",
                "design director",
                "design manager",
            ],
            "security": [
                "security guard",
                "security officer",
                "security specialist",
                "security coordinator",
                "security supervisor",
                "security manager",
                "loss prevention officer",
                "surveillance operator",
                "security analyst",
                "corporate security",
                "physical security specialist",
                "security consultant",
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
            "fitness": [
                "ace certified personal trainer",
                "ace certified group fitness instructor",
                "nasm certified personal trainer",
                "acsm certified",
                "cpr certification",
                "first aid certification",
                "cpr and first aid",
                "american heart association",
                "red cross certified",
            ],
            "nutrition": [
                "registered dietitian",
                "certified nutrition specialist",
                "certified nutrition consultant",
                "clinical nutrition certification",
                "sports nutrition certification",
                "certified diabetes educator",
                "food safety certification",
            ],
            "security": [
                "certified protection guard",
                "security guard license",
                "cpop certification",
                "security officer certification",
                "safety approach training",
                "security clearance",
                "armed security license",
                "loss prevention certification",
            ],
            "fashion": [
                "fashion design certification",
                "textile certification",
                "pattern making certification",
                "fashion merchandising certificate",
                "sustainable fashion certification",
            ],
            "design": [
                "adobe certified expert",
                "ux certification",
                "ui certification",
                "google ux design certificate",
                "interaction design certification",
                "human computer interaction certificate",
            ],
        }
        self._save_dataset("certifications.json", self.certifications_db)

    def _create_default_education_keywords(self):
        """Create default education keywords."""
        self.education_keywords = {
            "degree_types": [
                "bachelor",
                "bachelor's",
                "bachelors",
                "master",
                "master's",
                "masters",
                "phd",
                "ph.d",
                "doctorate",
                "doctoral",
                "associate",
                "associates",
                "diploma",
                "certificate",
                "certification",
                "mba",
                "m.b.a",
                "md",
                "m.d",
                "jd",
                "j.d",
                "bs",
                "b.s",
                "ba",
                "b.a",
                "ms",
                "m.s",
                "ma",
                "m.a",
                "bfa",
                "b.f.a",
                "mfa",
                "m.f.a",
                "waec",
                "ssce",
                "neco",
                "jamb",
                "utme",
                "senior school certificate",
                "west african examination council",
                "secondary school certificate",
                "o'level",
                "a'level",
                "ordinary level",
                "advanced level",
                "school leaving certificate",
            ],
            "institutions": [
                "university",
                "college",
                "institute",
                "school",
                "academy",
                "polytechnic",
                "community college",
                "state university",
                "technical college",
                "vocational school",
                "trade school",
                "online university",
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
                "fashion design",
                "textile design",
                "graphic design",
                "interaction design",
                "human computer interaction",
                "user experience",
                "nutrition",
                "dietetics",
                "food science",
                "exercise science",
                "kinesiology",
                "sports medicine",
                "criminal justice",
                "security management",
                "fine arts",
                "liberal arts",
                "communications",
                "journalism",
                "media studies",
                "mathematics education",
                "computer education",
                "educational technology",
                "curriculum and instruction",
                "educational leadership",
                "applied mathematics",
                "statistics",
                "data science",
            ],
            "honors": [
                "summa cum laude",
                "magna cum laude",
                "cum laude",
                "with honors",
                "dean's list",
                "honor roll",
                "phi beta kappa",
                "beta gamma sigma",
                "golden key",
                "national honor society",
                "first class",
                "second class upper",
                "second class lower",
                "third class",
                "distinction",
                "merit",
                "pass",
                "valedictorian",
                "salutatorian",
                "academic excellence",
                "outstanding student",
                "president of club",
                "deputy senior prefect",
                "senior prefect",
                "prefect",
                "class representative",
                "student leader",
            ],
            "gpa_indicators": [
                "gpa",
                "grade point average",
                "cumulative gpa",
                "major gpa",
                "overall gpa",
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

    def add_skills_to_dataset(self, industry: str, category: str, skills: List[str]):
        """Add new skills to the dataset."""
        if industry not in self.skills_db:
            self.skills_db[industry] = {}

        if category not in self.skills_db[industry]:
            self.skills_db[industry][category] = []

        # Add new skills (avoid duplicates)
        existing_skills = [
            s.lower() for s in self.skills_db[industry][category]
        ]
        for skill in skills:
            if skill.lower() not in existing_skills:
                self.skills_db[industry][category].append(skill)

        # Save updated dataset
        self._save_dataset("skills.json", self.skills_db)

    def add_job_titles_to_dataset(self, industry: str, titles: List[str]):
        """Add new job titles to the dataset."""
        if industry not in self.job_titles_db:
            self.job_titles_db[industry] = []

        # Add new titles (avoid duplicates)
        existing_titles = [
            t.lower() for t in self.job_titles_db[industry]
        ]
        for title in titles:
            if title.lower() not in existing_titles:
                self.job_titles_db[industry].append(title)

        # Save updated dataset
        self._save_dataset("job_titles.json", self.job_titles_db)

    def add_certifications_to_dataset(self, industry: str, certifications: List[str]):
        """Add new certifications to the dataset."""
        if industry not in self.certifications_db:
            self.certifications_db[industry] = []

        # Add new certifications (avoid duplicates)
        existing_certs = [
            c.lower() for c in self.certifications_db[industry]
        ]
        for cert in certifications:
            if cert.lower() not in existing_certs:
                self.certifications_db[industry].append(cert)

        # Save updated dataset
        self._save_dataset("certifications.json", self.certifications_db)

    def get_dataset_stats(self) -> Dict:
        """Get statistics about the current datasets."""
        stats = {
            "skills": {
                "total_industries": len(self.skills_db),
                "total_skills": len(self.get_all_skills()),
                "industries": list(self.skills_db.keys()),
            },
            "job_titles": {
                "total_industries": len(self.job_titles_db),
                "total_titles": len(self.get_all_job_titles()),
                "industries": list(self.job_titles_db.keys()),
            },
            "certifications": {
                "total_industries": len(self.certifications_db),
                "total_certifications": sum(
                    len(certs)
                    for certs in self.certifications_db.values()
                ),
                "industries": list(self.certifications_db.keys()),
            },
        }
        return stats

    def export_datasets(self, export_path: str = "datasets_export/"):
        """Export all datasets to specified directory."""
        os.makedirs(export_path, exist_ok=True)

        datasets = {
            "skills.json": self.skills_db,
            "job_titles.json": self.job_titles_db,
            "industries.json": self.industries_db,
            "certifications.json": self.certifications_db,
            "education_keywords.json": self.education_keywords,
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
                        setattr(self, attr_name, data)
                        datasets_loaded += 1
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")

        return f"Successfully imported {datasets_loaded} datasets"


# Global dataset manager instance
dataset_manager = DatasetManager()