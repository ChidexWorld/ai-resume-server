# Dataset Manager - Complete Documentation

## Overview

The Dataset Manager is a lightweight, standalone service responsible for managing manual datasets for skills, job titles, industries, certifications, and education keywords. It operates independently of heavy AI dependencies and provides the foundation for industry-specific analysis.

## Architecture

### Core Components

```
DatasetManager
├── Dataset Loading & Creation
├── Industry Detection
├── Skills Management
├── Job Titles Management
├── Certifications Management
├── Education Keywords Management
└── Export/Import Functionality
```

### Key Features

- **Zero Dependencies**: Uses only Python standard library
- **Automatic Fallback**: Creates default datasets if files are missing
- **Industry-Specific**: Organizes data by industry categories
- **Extensible**: Easy to add new industries, skills, and categories
- **Persistent**: Saves changes automatically to JSON files
- **Import/Export**: Full dataset backup and migration support

## File Structure

```
datasets/
├── skills.json              # Skills organized by industry and category
├── job_titles.json          # Job titles grouped by industry
├── industries.json          # Industry keywords for detection
├── certifications.json      # Professional certifications by field
└── education_keywords.json  # Education-related terms and degrees
```

## Dataset Schemas

### Skills Dataset (`skills.json`)

```json
{
  "industry_name": {
    "category_name": [
      "skill1",
      "skill2",
      "skill3"
    ]
  }
}
```

**Example:**
```json
{
  "technology": {
    "programming": ["python", "javascript", "java"],
    "databases": ["mysql", "postgresql", "mongodb"],
    "cloud": ["aws", "azure", "gcp"]
  },
  "marketing": {
    "digital_marketing": ["seo", "sem", "google ads"],
    "analytics": ["google analytics", "tableau", "power bi"]
  }
}
```

### Job Titles Dataset (`job_titles.json`)

```json
{
  "industry_name": [
    "job_title1",
    "job_title2",
    "job_title3"
  ]
}
```

**Example:**
```json
{
  "technology": [
    "software engineer",
    "data scientist",
    "product manager"
  ],
  "finance": [
    "financial analyst",
    "accountant",
    "investment banker"
  ]
}
```

### Industries Dataset (`industries.json`)

```json
{
  "industry_name": [
    "keyword1",
    "keyword2",
    "keyword3"
  ]
}
```

**Example:**
```json
{
  "technology": [
    "software",
    "it services",
    "telecommunications"
  ],
  "healthcare": [
    "hospitals",
    "pharmaceuticals",
    "medical devices"
  ]
}
```

### Certifications Dataset (`certifications.json`)

```json
{
  "field_name": [
    "certification1",
    "certification2"
  ]
}
```

**Example:**
```json
{
  "technology": [
    "aws certified",
    "microsoft certified",
    "google cloud certified"
  ],
  "finance": [
    "cpa",
    "cfa",
    "frm"
  ]
}
```

### Education Keywords (`education_keywords.json`)

```json
{
  "degree_types": ["bachelor", "master", "phd"],
  "institutions": ["university", "college", "institute"],
  "fields": ["computer science", "business administration"]
}
```

## API Reference

### Initialization

```python
from app.services.dataset_manager import DatasetManager, dataset_manager

# Use global instance
dm = dataset_manager

# Or create new instance with custom path
dm = DatasetManager(dataset_path="custom/path/")
```

### Core Methods

#### `get_dataset_stats() -> Dict`
Returns comprehensive statistics about all datasets.

```python
stats = dm.get_dataset_stats()
# Returns:
{
  "skills": {
    "total_industries": 9,
    "total_skills": 148,
    "industries": ["technology", "marketing", ...]
  },
  "job_titles": {
    "total_industries": 8,
    "total_titles": 95,
    "industries": ["technology", "finance", ...]
  },
  "certifications": {
    "total_industries": 6,
    "total_certifications": 43,
    "industries": ["technology", "finance", ...]
  }
}
```

#### `get_all_skills() -> List[str]`
Returns a flat list of all skills across all industries.

```python
all_skills = dm.get_all_skills()
# Returns: ["python", "javascript", "seo", "financial modeling", ...]
```

#### `get_skills_by_industry(industry: str) -> List[str]`
Returns all skills for a specific industry.

```python
tech_skills = dm.get_skills_by_industry("technology")
# Returns: ["python", "javascript", "aws", "docker", ...]
```

#### `get_all_job_titles() -> List[str]`
Returns a flat list of all job titles.

```python
all_titles = dm.get_all_job_titles()
# Returns: ["software engineer", "data scientist", "marketing manager", ...]
```

#### `detect_industry(text: str) -> str`
Analyzes text content to detect the most likely industry.

```python
industry = dm.detect_industry("Python developer with AWS experience")
# Returns: "technology"

industry = dm.detect_industry("Financial analyst with CFA certification")
# Returns: "finance"
```

### Data Management Methods

#### `add_skills_to_dataset(industry: str, category: str, skills: List[str])`
Adds new skills to a specific industry and category.

```python
dm.add_skills_to_dataset(
    industry="retail",
    category="customer_service",
    skills=["customer support", "pos systems", "inventory management"]
)
```

#### `add_job_titles_to_dataset(industry: str, titles: List[str])`
Adds new job titles to an industry.

```python
dm.add_job_titles_to_dataset(
    industry="retail",
    titles=["store manager", "sales associate", "cashier"]
)
```

#### `add_certifications_to_dataset(industry: str, certifications: List[str])`
Adds new certifications to an industry.

```python
dm.add_certifications_to_dataset(
    industry="retail",
    certifications=["retail management certification", "pos system certified"]
)
```

### Import/Export Methods

#### `export_datasets(export_path: str = "datasets_export/") -> str`
Exports all datasets to a specified directory.

```python
result = dm.export_datasets("backup/datasets/")
# Returns: "Datasets exported to backup/datasets/"
```

#### `import_datasets(import_path: str = "datasets_import/") -> str`
Imports datasets from a specified directory.

```python
result = dm.import_datasets("backup/datasets/")
# Returns: "Successfully imported 5 datasets"
```

## Default Dataset Content

### Technology Industry
- **Programming**: python, javascript, java, c++, c#, php, ruby, go, rust, r, sql
- **Web Development**: html, css, react, angular, vue, node.js, bootstrap
- **Databases**: mysql, postgresql, mongodb, redis, oracle, sqlite
- **Cloud**: aws, azure, gcp, docker, kubernetes, jenkins
- **Tools**: git, jira, confluence, slack

### Marketing Industry
- **Digital Marketing**: seo, sem, google ads, facebook ads, content marketing, email marketing
- **Analytics**: google analytics, adobe analytics, tableau, power bi, excel
- **Social Media**: social media management, hootsuite, buffer, sprout social
- **Content**: copywriting, content creation, blogging, video editing, graphic design

### Finance Industry
- **Accounting**: quickbooks, sap, oracle financials, gaap, ifrs, financial modeling
- **Analysis**: financial analysis, risk management, investment analysis, budgeting, forecasting
- **Tools**: excel, bloomberg terminal, matlab, r, python, sql

### Healthcare Industry
- **Clinical**: patient care, medical records, hipaa, clinical research, medical coding
- **Administrative**: healthcare administration, insurance, billing, scheduling
- **Technical**: epic, cerner, allscripts, meditech, emr systems

### Sales Industry
- **Techniques**: cold calling, lead generation, negotiation, closing, prospecting
- **CRM**: salesforce, hubspot, pipedrive, zoho, dynamics 365
- **Analysis**: sales analytics, forecasting, pipeline management, territory management

### Human Resources Industry
- **Recruitment**: talent acquisition, interviewing, onboarding, ats systems
- **Compliance**: employment law, hr policies, benefits administration, payroll
- **Systems**: workday, bamboohr, adp, successfactors

### Operations Industry
- **Management**: project management, process improvement, lean, six sigma, agile
- **Supply Chain**: inventory management, logistics, procurement, vendor management
- **Quality**: quality assurance, iso standards, continuous improvement

### Education Industry
- **Teaching**: curriculum development, lesson planning, classroom management, student assessment
- **Technology**: learning management systems, blackboard, canvas, moodle, zoom
- **Administration**: educational leadership, student services, academic advising

### Soft Skills
- **Leadership**: team leadership, mentoring, coaching, strategic thinking, decision making
- **Communication**: public speaking, presentation, writing, interpersonal, negotiation
- **Problem Solving**: analytical thinking, creative problem solving, troubleshooting, innovation
- **Personal**: time management, adaptability, attention to detail, multitasking, organization

## Industry Detection Algorithm

The `detect_industry()` method uses a weighted scoring system:

1. **Direct Industry Keywords**: Matches against industry-specific keywords (weight: 1.0)
2. **Skills Matching**: Matches against industry skills (weight: 0.5)
3. **Job Titles**: Implicit matching through job title context

```python
def detect_industry(self, text: str) -> str:
    text_lower = text.lower()
    industry_scores = {}

    # Score based on industry keywords
    for industry, keywords in self.industries_db.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        if score > 0:
            industry_scores[industry] = score

    # Score based on skills (weighted)
    for industry in self.skills_db.keys():
        skills = self.get_skills_by_industry(industry)
        skill_matches = sum(1 for skill in skills if skill.lower() in text_lower)
        industry_scores[industry] = (
            industry_scores.get(industry, 0) + skill_matches * 0.5
        )

    return max(industry_scores, key=industry_scores.get) if industry_scores else "general"
```

## Usage Examples

### Basic Usage

```python
from app.services.dataset_manager import dataset_manager as dm

# Get overview
stats = dm.get_dataset_stats()
print(f"Total skills: {stats['skills']['total_skills']}")

# Find industry for resume text
resume_text = "Experienced software engineer with Python, AWS, and Docker expertise"
industry = dm.detect_industry(resume_text)
print(f"Detected industry: {industry}")  # Output: "technology"

# Get relevant skills for matching
tech_skills = dm.get_skills_by_industry("technology")
relevant_skills = [skill for skill in tech_skills if skill in resume_text.lower()]
```

### Adding Custom Industry

```python
# Add a new industry: "cybersecurity"
dm.add_skills_to_dataset(
    industry="cybersecurity",
    category="security_tools",
    skills=["wireshark", "metasploit", "nessus", "burp suite", "nmap"]
)

dm.add_skills_to_dataset(
    industry="cybersecurity",
    category="frameworks",
    skills=["nist", "iso 27001", "owasp", "cobit"]
)

dm.add_job_titles_to_dataset(
    industry="cybersecurity",
    titles=["security analyst", "penetration tester", "security architect", "ciso"]
)

dm.add_certifications_to_dataset(
    industry="cybersecurity",
    certifications=["cissp", "ceh", "oscp", "gcih", "cism"]
)
```

### Data Migration

```python
# Export current datasets
backup_path = dm.export_datasets("backup_2024/")
print(backup_path)  # "Datasets exported to backup_2024/"

# Import from different environment
result = dm.import_datasets("production_datasets/")
print(result)  # "Successfully imported 5 datasets"
```

### Integration with Resume Analysis

```python
def analyze_resume_skills(resume_text: str):
    # Detect industry
    detected_industry = dm.detect_industry(resume_text)

    # Get industry-specific skills
    industry_skills = dm.get_skills_by_industry(detected_industry)

    # Find matching skills
    resume_lower = resume_text.lower()
    found_skills = [skill for skill in industry_skills if skill in resume_lower]

    # Get all skills for comprehensive analysis
    all_skills = dm.get_all_skills()
    all_found_skills = [skill for skill in all_skills if skill in resume_lower]

    return {
        "detected_industry": detected_industry,
        "industry_skills_found": found_skills,
        "all_skills_found": all_found_skills,
        "skills_coverage": len(found_skills) / len(industry_skills) if industry_skills else 0
    }
```

## Error Handling

The Dataset Manager includes robust error handling:

### Missing Files
- Automatically creates default datasets if files are missing
- Graceful fallback to minimal dataset if creation fails

### Invalid Data
- Validates data structure before saving
- Skips invalid entries during import
- Maintains data integrity

### File System Errors
- Creates directories automatically
- Handles permission errors gracefully
- Provides clear error messages

```python
try:
    dm.add_skills_to_dataset("new_industry", "category", ["skill1", "skill2"])
except Exception as e:
    print(f"Failed to add skills: {e}")
    # System continues to work with existing data
```

## Performance Considerations

### Memory Usage
- Datasets are loaded into memory for fast access
- Typical memory usage: ~1-5MB for default datasets
- Scales linearly with dataset size

### File I/O
- Datasets are saved only when modified
- JSON format provides human-readable storage
- Automatic backup during updates

### Initialization Time
- Initial load: ~10-50ms for default datasets
- Subsequent operations: <1ms per query
- No network dependencies

## Best Practices

### Dataset Organization
```python
# Good: Specific, searchable skills
dm.add_skills_to_dataset("technology", "programming", ["python", "java", "javascript"])

# Avoid: Vague or overly broad terms
dm.add_skills_to_dataset("technology", "general", ["programming", "computers"])
```

### Industry Naming
```python
# Good: Consistent, lowercase naming
"technology", "healthcare", "finance"

# Avoid: Mixed case or spaces
"Technology", "Health Care", "FINANCE"
```

### Regular Maintenance
```python
# Periodic cleanup and validation
stats = dm.get_dataset_stats()
print(f"Dataset health check: {stats}")

# Export backups regularly
dm.export_datasets(f"backup_{datetime.now().strftime('%Y%m%d')}/")
```

## Integration Points

### With AI Service
```python
# AI Service uses Dataset Manager for:
# - Industry detection
# - Skills extraction
# - Job title matching
# - Certification validation

from app.services import ai_service, dataset_manager

# The AI Service automatically uses the dataset manager
analysis = ai_service.analyze_resume(resume_text)
# Internally calls: dataset_manager.detect_industry(resume_text)
```

### With API Endpoints
```python
# FastAPI routes can access dataset manager directly
from app.services import dataset_manager

@app.get("/api/industries")
def get_industries():
    stats = dataset_manager.get_dataset_stats()
    return stats["skills"]["industries"]

@app.post("/api/detect-industry")
def detect_industry(text: str):
    industry = dataset_manager.detect_industry(text)
    return {"detected_industry": industry}
```

## Troubleshooting

### Common Issues

#### "Dataset files not found"
**Symptoms**: Warning messages during initialization
**Solution**: Automatic - default datasets are created
**Prevention**: Regular backups using `export_datasets()`

#### "Failed to save dataset"
**Symptoms**: Changes not persisting
**Causes**: File permissions, disk space, invalid path
**Solution**: Check file permissions and available disk space

#### "Industry not detected"
**Symptoms**: `detect_industry()` returns "general"
**Causes**: Text doesn't match known keywords/skills
**Solution**: Add relevant keywords to industry datasets

### Debug Commands

```python
# Check dataset integrity
stats = dm.get_dataset_stats()
print(f"Skills loaded: {stats['skills']['total_skills']}")
print(f"Industries: {stats['skills']['industries']}")

# Test industry detection
test_texts = [
    "Python developer with AWS experience",
    "Financial analyst with Excel skills",
    "Nurse with patient care experience"
]
for text in test_texts:
    industry = dm.detect_industry(text)
    print(f"'{text}' -> {industry}")

# Validate dataset files
import os
dataset_files = ["skills.json", "job_titles.json", "industries.json",
                "certifications.json", "education_keywords.json"]
for file in dataset_files:
    path = os.path.join(dm.dataset_path, file)
    exists = os.path.exists(path)
    print(f"{file}: {'✓' if exists else '✗'}")
```

## Future Enhancements

### Planned Features
- **Skill Synonyms**: Map alternative skill names
- **Skill Hierarchies**: Parent-child skill relationships
- **Industry Transitions**: Career path mappings
- **Skill Popularity**: Track trending skills by industry
- **Multilingual Support**: Non-English skill names

### Extension Points
```python
# Example: Adding skill synonyms
class EnhancedDatasetManager(DatasetManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skill_synonyms = self._load_skill_synonyms()

    def find_skill_matches(self, text: str) -> List[str]:
        # Enhanced matching with synonyms
        matches = []
        for skill in self.get_all_skills():
            if skill in text or any(synonym in text for synonym in self.skill_synonyms.get(skill, [])):
                matches.append(skill)
        return matches
```

This comprehensive Dataset Manager provides the foundation for intelligent resume analysis and job matching, operating efficiently with minimal dependencies while maintaining extensibility for future enhancements.