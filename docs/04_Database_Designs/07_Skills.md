# Database Design
# Table: Skills

**Module:** Database Design  
**Table Name:** skills  
**Primary Key:** skill_id

---

# 1. Purpose

The **skills** table stores all technical, functional, and soft skills recognized by the TalentIQ platform.

Instead of storing skill names repeatedly in resumes and job descriptions, each skill is stored once and referenced throughout the system.

This enables powerful analytics, AI-powered resume parsing, job matching, and candidate ranking.

---

# 2. Business Description

A skill represents a competency required by a job or possessed by a candidate.

Examples include:

Technical Skills

- Python
- SQL
- Java
- AWS
- Azure
- React
- Tableau
- Power BI
- Snowflake

Soft Skills

- Communication
- Leadership
- Teamwork
- Problem Solving

Certifications

- AWS Certified Developer
- Azure Administrator
- PMP
- Scrum Master

---

# 3. Table Purpose

This table is responsible for:

- Maintaining the master list of skills
- Supporting AI Resume Parser
- Supporting Job Matching
- Supporting Candidate Ranking
- Supporting Skill Gap Analysis
- Powering dashboards showing skill demand

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| skill_id | Unique skill identifier |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| skill_id | BIGSERIAL | Yes | Primary Key |
| skill_name | VARCHAR(150) | Yes | Name of the skill |
| skill_category | VARCHAR(100) | Yes | Technical, Soft Skill, Certification, Language, Tool |
| description | TEXT | No | Skill description |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 6. Sample Categories

Technical

- Python
- Java
- SQL
- C#
- JavaScript

Cloud

- AWS
- Azure
- GCP

Data

- Tableau
- Power BI
- Snowflake
- Hadoop
- Spark

AI / ML

- TensorFlow
- PyTorch
- LangChain
- OpenAI API
- Machine Learning

Soft Skills

- Communication
- Leadership
- Teamwork
- Time Management

Certifications

- PMP
- AWS Certified Solutions Architect
- Azure Administrator

---

# 7. Relationships

One Skill

↓

Many Candidates

(via candidate_skills)

```
skills
      │
      └────────► candidate_skills
```

---

One Skill

↓

Many Jobs

(via job_skills)

```
skills
      │
      └────────► job_skills
```

Relationship Type

Many-to-Many

---

# 8. Business Rules

- Every skill name must be unique.
- A skill belongs to one category.
- Skills cannot be duplicated.
- Inactive skills cannot be assigned to new jobs.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| skill_name | Cannot be empty |
| skill_name | Must be unique |
| skill_category | Cannot be empty |
| is_active | TRUE or FALSE |

---

# 10. Indexing Strategy

Indexes should be created on:

- skill_name
- skill_category
- is_active

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 200 |
| Demo | 500 |
| Production | 5,000+ |

---

# 12. Used By

This table is referenced by:

- Candidate Skills
- Job Skills
- Resume Parser
- Job Matcher
- AI Recruitment Assistant
- Skill Analytics
- Executive Dashboard

---

# 13. Analytics Supported

The skills table enables:

- Most In-Demand Skills
- Most Common Candidate Skills
- Skill Gap Analysis
- Skill Distribution
- Candidate Skill Matrix
- Job Skill Matrix
- AI Match Score
- Skill Trends

---

# 14. Future Enhancements

Potential future additions:

- Skill aliases (e.g., JS → JavaScript)
- Skill hierarchy
- Skill proficiency levels
- Skill popularity score
- AI-generated related skills

---

# 15. Summary

The **skills** table is one of the foundational master tables in TalentIQ. It standardizes all skills across candidates and jobs, enabling powerful SQL analytics, machine learning models, and AI-driven features such as resume parsing, job matching, and candidate ranking.