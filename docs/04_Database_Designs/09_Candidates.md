# Database Design
# Table: Candidates

**Module:** Database Design
**Table Name:** candidates
**Primary Key:** candidate_id

---

# 1. Purpose

The **candidates** table stores all individuals who apply for jobs or are sourced by recruiters.

It acts as the central profile for each candidate, capturing personal details, professional experience, work authorization, preferred work location, employment preferences, and current recruitment status.

This table serves as the foundation for resume parsing, AI job matching, recruiter workflows, analytics, and machine learning.

---

# 2. Business Description

A candidate represents a person who is seeking employment.

Candidates may enter the recruitment system through various channels such as LinkedIn, Dice, Monster, referrals, internal databases, or company career portals.

A candidate can:

- Apply for multiple jobs
- Attend multiple interviews
- Receive multiple offers
- Be hired multiple times over their career

However, a candidate has only one master profile in the system.

---

# 3. Table Purpose

The candidates table is responsible for:

- Maintaining candidate profiles
- Supporting recruiter searches
- Resume management
- AI resume parsing
- Job matching
- Candidate ranking
- Analytics and reporting

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| candidate_id | Unique candidate identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| source_id | sources.source_id |
| work_authorization_id | work_authorizations.work_authorization_id |
| preferred_location_id | locations.location_id |

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| candidate_id | BIGSERIAL | Yes | Primary Key |
| first_name | VARCHAR(100) | Yes | First name |
| last_name | VARCHAR(100) | Yes | Last name |
| email | VARCHAR(150) | Yes | Email address |
| phone | VARCHAR(30) | Yes | Mobile number |
| linkedin_url | VARCHAR(255) | No | LinkedIn profile |
| total_experience | DECIMAL(4,1) | Yes | Years of experience |
| current_job_title | VARCHAR(150) | No | Current designation |
| current_company | VARCHAR(200) | No | Current employer |
| current_salary | DECIMAL(12,2) | No | Current annual salary |
| expected_salary | DECIMAL(12,2) | No | Expected annual salary |
| notice_period_days | INTEGER | No | Notice period |
| source_id | INTEGER | Yes | Candidate source |
| work_authorization_id | INTEGER | Yes | Work authorization |
| preferred_location_id | INTEGER | No | Preferred work location |
| resume_path | VARCHAR(500) | No | Resume file path |
| resume_uploaded_at | TIMESTAMP | No | Resume upload date |
| ai_resume_score | DECIMAL(5,2) | No | AI-generated resume quality score |
| candidate_status | VARCHAR(50) | Yes | Current recruitment status |
| is_active | BOOLEAN | Yes | Active candidate |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 7. Relationships

One Candidate

↓

Many Applications

```
candidates
      │
      └────────► applications
```

---

One Candidate

↓

Many Interviews

```
candidates
      │
      └────────► interviews
```

---

One Candidate

↓

Many Offers

```
candidates
      │
      └────────► offers
```

---

One Candidate

↓

Many Placements

```
candidates
      │
      └────────► placements
```

---

One Candidate

↓

Many Skills

(via candidate_skills)

```
candidates
      │
      └────────► candidate_skills ◄──────── skills
```

Relationship Type

Many-to-Many

---

# 8. Business Rules

- Every candidate must have a unique email.
- Every candidate must have one work authorization.
- Every candidate must have one source.
- A candidate can apply for multiple jobs.
- Resume upload is optional but recommended.
- Duplicate candidate profiles should not be created.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| first_name | Cannot be empty |
| last_name | Cannot be empty |
| email | Must be unique |
| phone | Valid phone number |
| total_experience | Cannot be negative |
| current_salary | Cannot be negative |
| expected_salary | Cannot be negative |

---

# 10. Indexing Strategy

Indexes should be created on:

- email
- phone
- source_id
- work_authorization_id
- preferred_location_id
- candidate_status
- total_experience
- is_active

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 1,000 |
| Demo | 50,000 |
| Production | Millions |

---

# 12. Used By

This table is referenced by:

- Applications
- Interviews
- Offers
- Placements
- Candidate Skills
- Resume Parser
- Job Matcher
- AI Assistant
- Dashboards

---

# 13. Analytics Supported

The candidates table enables:

- Candidate Pipeline
- Experience Distribution
- Source Analysis
- Work Authorization Analysis
- Salary Analysis
- Notice Period Analysis
- Candidate Availability
- AI Resume Score Distribution

---

# 14. AI Features

This table powers:

- Resume Parsing
- Resume Embeddings
- Skill Extraction
- Candidate Ranking
- Resume Match Score
- Skill Gap Analysis
- AI Chat Assistant

---

# 15. Future Enhancements

Potential future additions:

- GitHub Profile
- Portfolio URL
- Certifications
- Languages Known
- Education History
- Employment History
- Resume Versioning
- Candidate Notes
- AI Candidate Summary

---

# 16. Summary

The **candidates** table is the core entity of the TalentIQ platform. It centralizes candidate information and serves as the foundation for recruitment operations, SQL analytics, Power BI dashboards, machine learning models, and AI-powered recruitment features.