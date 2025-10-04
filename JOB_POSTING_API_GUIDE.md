# Job Posting API Guide

## What Changed

### ✅ Fixed Issues

1. **Dict fields now properly validated** - No more sending strings like `"{}"` or `"null"`
2. **Automatic defaults** - Empty dicts/lists are provided automatically
3. **Salary validation** - `salary_max` must be ≥ `salary_min`
4. **Clear error messages** - You'll know exactly what's wrong

---

## Field Types & Validation

### Required Fields (String)
- `title`: Min 3 characters
- `description`: Min 50 characters
- `location`: Any string

### Required Fields (Enum)
- `job_type`: `"full_time"` | `"part_time"` | `"contract"` | `"internship"` | `"freelance"`
- `experience_level`: `"entry"` | `"junior"` | `"mid"` | `"senior"` | `"lead"` | `"executive"`

### Required Fields (List)
- `required_skills`: Array of strings (min 1 item)

### Optional Fields (Dict) - Default: `{}`
These fields **must be JSON objects**, not strings:
- `required_experience`
- `required_education`
- `communication_requirements`
- `matching_weights`

### Optional Fields (List) - Default: `[]`
- `preferred_skills`: Array of strings

### Optional Fields (Number)
- `salary_min`: Integer (no decimals)
- `salary_max`: Integer ≥ `salary_min`
- `minimum_match_score`: 0-100 (default: 70)
- `max_applications`: Positive integer

### Optional Fields (Boolean) - Defaults shown
- `remote_allowed`: `false`
- `is_urgent`: `false`
- `auto_match_enabled`: `true`

---

## Common Mistakes & Fixes

### ❌ **WRONG** - Sending strings instead of objects
```json
{
  "required_education": "{}",
  "required_experience": "null",
  "communication_requirements": "{\"clarity\": 70}"
}
```

### ✅ **CORRECT** - Send actual JSON objects
```json
{
  "required_education": {},
  "required_experience": {},
  "communication_requirements": {"clarity": 70}
}
```

---

### ❌ **WRONG** - salary_max < salary_min
```json
{
  "salary_min": 100000,
  "salary_max": 80000
}
```
**Error**: `salary_max (80000) must be greater than or equal to salary_min (100000)`

### ✅ **CORRECT**
```json
{
  "salary_min": 80000,
  "salary_max": 100000
}
```

---

### ❌ **WRONG** - Empty required_skills
```json
{
  "required_skills": []
}
```
**Error**: `At least one required skill must be provided`

### ✅ **CORRECT**
```json
{
  "required_skills": ["Python", "FastAPI"]
}
```

---

## Minimal Valid Payload

The absolute minimum to create a job posting:

```json
{
  "title": "Software Engineer",
  "description": "We are looking for a talented software engineer to join our team and work on exciting projects.",
  "location": "San Francisco, CA",
  "job_type": "FULL_TIME",
  "experience_level": "SENIOR",
  "required_skills": ["Python", "FastAPI"]
}
```

All other fields will use defaults:
- `remote_allowed`: `false`
- `currency`: `"USD"`
- `preferred_skills`: `[]`
- `required_experience`: `{}`
- `required_education`: `{}`
- `communication_requirements`: `{}`
- `matching_weights`: `{}`
- `minimum_match_score`: `70`
- `is_urgent`: `false`
- `auto_match_enabled`: `true`

---

## Recommended Field Structures

### `required_experience`
```json
{
  "minimum_years": 5,
  "preferred_areas": ["Web Development", "API Design"],
  "leadership_experience": false,
  "internship_acceptable": false
}
```

### `required_education`
```json
{
  "degree_required": true,
  "minimum_degree": "Bachelor",
  "preferred_fields": ["Computer Science", "Software Engineering"],
  "certifications": ["AWS Certified Developer", "PMP"]
}
```

### `communication_requirements`
```json
{
  "clarity_threshold": 70,
  "fluency_threshold": 75,
  "confidence_threshold": 65,
  "vocabulary_threshold": 70,
  "requires_voice_analysis": true
}
```

### `matching_weights`
```json
{
  "skills_weight": 0.4,
  "experience_weight": 0.3,
  "education_weight": 0.15,
  "communication_weight": 0.15
}
```
**Note**: Weights should sum to 1.0

---

## Testing Your Payload

### cURL Example
```bash
curl -X POST http://localhost:8000/api/employer/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "Exciting opportunity to work on cutting-edge AI and machine learning projects using Python and modern frameworks.",
    "location": "Remote",
    "remote_allowed": true,
    "job_type": "FULL_TIME",
    "experience_level": "SENIOR",
    "salary_min": 100000,
    "salary_max": 150000,
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["Docker", "AWS"],
    "minimum_match_score": 75,
    "is_urgent": true
  }'
```

---

## Error Responses

### 422 Unprocessable Entity
Validation failed. Check the error details:

```json
{
  "detail": [
    {
      "loc": ["body", "salary_max"],
      "msg": "salary_max (80000) must be greater than or equal to salary_min (100000)",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
Server-side issue. Check if:
- Database connection is working
- All migrations are applied
- Required services are running

---

## See Also

- Full examples: `example_job_posting_payloads.json`
- API documentation: `http://localhost:8000/docs` (when server running)
