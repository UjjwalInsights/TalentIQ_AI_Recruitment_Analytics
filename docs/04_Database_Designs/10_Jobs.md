# Database Design
# Table: Jobs

**Module:** Database Design  
**Table Name:** jobs  
**Primary Key:** job_id

---

# 1. Purpose

The **jobs** table stores all job requisitions received by the recruitment agency from end clients or implementation partners.

Each job contains business information, technical requirements, hiring details, compensation, and recruitment status. It serves as the foundation for candidate applications, interviews, offers, placements, analytics, and AI-powered job matching.

---

# 2. Business Description

A job represents an open position that needs to be filled.

A job may be received:

- Directly from an End Client
- Through an Implementation Partner

Examples:

- Python Data Analyst
- Java Full Stack Developer
- DevOps Engineer
- Data Engineer
- Business Analyst

A single job can receive multiple applications but is usually filled by one or more successful candidates.

---

# 3. Table Purpose

This table is responsible for:

- Managing job requisitions
- Tracking hiring progress
- Supporting recruiter assignments
- AI job matching
- Dashboard reporting
- Hiring analytics

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| job_id | Unique job identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| client_company_id | companies.company_id |
| implementation_partner_id | companies.company_id |
| recruiter_id | recruiters.recruiter_id |
| department_id | departments.department_id |
| location_id | locations.location_id |

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| job_id | BIGSERIAL | Yes | Primary Key |
| job_code | VARCHAR(50) | Yes | Internal job reference |
| job_title | VARCHAR(200) | Yes | Position title |
| client_company_id | BIGINT | Yes | End Client |
| implementation_partner_id | BIGINT | No | Vendor / Implementation Partner |
| recruiter_id | BIGINT | Yes | Assigned recruiter |
| department_id | INTEGER | Yes | Department |
| location_id | BIGINT | Yes | Job location |
| job_description | TEXT | Yes | Full job description |
| required_experience | DECIMAL(4,1) | Yes | Minimum experience |
| openings | INTEGER | Yes | Number of openings |
| employment_type | VARCHAR(50) | Yes | Contract / Full-time / C2C / W2 |
| work_mode | VARCHAR(50) | Yes | Remote / Hybrid / Onsite |
| bill_rate | DECIMAL(10,2) | No | Client bill rate |
| pay_rate | DECIMAL(10,2) | No | Candidate pay rate |
| priority | VARCHAR(30) | Yes | High / Medium / Low |
| job_status | VARCHAR(50) | Yes | Open / Closed / On Hold |
| opened_date | DATE | Yes | Job opening date |
| target_fill_date | DATE | No | Target completion date |
| closed_date | DATE | No | Job closing date |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 7. Relationships

One Job

↓

Many Applications

```
jobs
   │
   └────────► applications
```

---

One Job

↓

Many Interviews

```
jobs
   │
   └────────► interviews
```

---

One Job

↓

Many Offers

```
jobs
   │
   └────────► offers
```

---

One Job

↓

Many Placements

```
jobs
   │
   └────────► placements
```

---

One Job

↓

Many Skills

(via job_skills)

```
jobs
   │
   └────────► job_skills ◄──────── skills
```

---

# 8. Business Rules

- Every job must have one assigned recruiter.
- Every job must belong to one department.
- Every job must have one client company.
- Job codes must be unique.
- Closed jobs cannot accept new applications.
- Bill rate must be greater than or equal to pay rate.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| job_title | Cannot be empty |
| job_code | Must be unique |
| openings | Must be greater than zero |
| required_experience | Cannot be negative |
| bill_rate | Cannot be negative |
| pay_rate | Cannot be negative |

---

# 10. Indexing Strategy

Indexes should be created on:

- job_code
- job_title
- recruiter_id
- client_company_id
- department_id
- location_id
- job_status
- priority
- opened_date

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 500 |
| Demo | 10,000 |
| Production | Millions |

---

# 12. Used By

This table is referenced by:

- Applications
- Interviews
- Offers
- Placements
- Job Skills
- AI Job Matcher
- Dashboards
- Executive Reports

---

# 13. Analytics Supported

The jobs table enables:

- Open Positions
- Hiring Velocity
- Time to Fill
- Jobs by Client
- Jobs by Recruiter
- Jobs by Department
- Margin Analysis
- Open vs Closed Jobs

---

# 14. AI Features

This table powers:

- Resume Matching
- Candidate Ranking
- Skill Gap Analysis
- Job Recommendation
- AI Hiring Assistant

---

# 15. Future Enhancements

Potential future additions:

- Hiring Manager
- Budget
- Job Templates
- Approval Workflow
- Interview Panel
- Required Certifications
- Salary Range
- Benefits

---

# 16. Summary

The **jobs** table is the central entity for managing recruitment demand within TalentIQ. It connects companies, recruiters, candidates, applications, and placements while enabling analytics, dashboard reporting, and AI-powered job matching.