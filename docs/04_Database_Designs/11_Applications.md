# Database Design
# Table: Applications

**Module:** Database Design
**Table Name:** applications
**Primary Key:** application_id

---

# 1. Purpose

The **applications** table records every instance of a candidate applying for a specific job.

It serves as the central transaction table in the recruitment lifecycle, connecting candidates, jobs, recruiters, interviews, offers, and placements.

Every recruitment process begins with an application.

---

# 2. Business Description

An application represents a candidate's submission for a job.

Examples:

John Smith
↓

Applied for

Python Data Analyst

Status

Applied

↓

Screening

↓

Interview

↓

Offer

↓

Hired

A candidate may apply to multiple jobs.

A job may receive applications from multiple candidates.

---

# 3. Table Purpose

This table is responsible for:

- Tracking candidate applications
- Managing recruitment pipeline stages
- Recording recruiter activity
- Supporting interview scheduling
- Tracking hiring progress
- Supporting dashboards
- Providing ML training data

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| application_id | Unique application identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| candidate_id | candidates.candidate_id |
| job_id | jobs.job_id |
| recruiter_id | recruiters.recruiter_id |
| source_id | sources.source_id |

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| application_id | BIGSERIAL | Yes | Primary Key |
| candidate_id | BIGINT | Yes | Candidate |
| job_id | BIGINT | Yes | Applied Job |
| recruiter_id | BIGINT | Yes | Assigned Recruiter |
| source_id | INTEGER | Yes | Candidate Source |
| application_date | DATE | Yes | Date of application |
| current_stage | VARCHAR(50) | Yes | Current recruitment stage |
| application_status | VARCHAR(50) | Yes | Active, Rejected, Withdrawn, Hired |
| stage_updated_at | TIMESTAMP | Yes | Last stage update |
| ai_match_score | DECIMAL(5,2) | No | AI matching score |
| recruiter_notes | TEXT | No | Recruiter comments |
| expected_joining_date | DATE | No | Expected joining |
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

One Job

↓

Many Applications

```
jobs
    │
    └────────► applications
```

---

One Recruiter

↓

Many Applications

```
recruiters
      │
      └────────► applications
```

---

One Application

↓

Many Interviews

```
applications
        │
        └────────► interviews
```

---

One Application

↓

One Offer

```
applications
        │
        └────────► offers
```

---

One Application

↓

One Placement

```
applications
        │
        └────────► placements
```

---

# 8. Recruitment Pipeline

Each application progresses through the following stages:

```
Applied

↓

Resume Screening

↓

Recruiter Call

↓

Client Submission

↓

Interview

↓

Offer

↓

Offer Accepted

↓

Placement

↓

Joined
```

Applications may also end as:

- Rejected
- Withdrawn
- On Hold

---

# 9. Business Rules

- A candidate may apply to multiple jobs.
- A job may have multiple applicants.
- A recruiter manages each application.
- Every application belongs to exactly one candidate and one job.
- Duplicate active applications for the same candidate and job are not allowed.
- Once marked as Joined, the application cannot return to a previous stage.

---

# 10. Validation Rules

| Field | Validation |
|---------|------------|
| candidate_id | Must exist |
| job_id | Must exist |
| recruiter_id | Must exist |
| application_date | Cannot be in the future |
| ai_match_score | Must be between 0 and 100 |

---

# 11. Indexing Strategy

Indexes should be created on:

- candidate_id
- job_id
- recruiter_id
- application_date
- current_stage
- application_status
- ai_match_score

---

# 12. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 2,000 |
| Demo | 100,000 |
| Production | Millions |

---

# 13. Used By

This table is referenced by:

- Interviews
- Offers
- Placements
- Dashboards
- ML Models
- AI Assistant
- Executive Reports

---

# 14. Analytics Supported

This table enables:

- Recruitment Funnel
- Stage Conversion Rate
- Time in Each Stage
- Recruiter Productivity
- Candidate Pipeline
- Job Pipeline
- AI Match Score Analysis
- Source Effectiveness

---

# 15. AI Features

The applications table powers:

- Candidate Ranking
- Resume Match Score
- Hiring Prediction
- Skill Gap Analysis
- AI Recruitment Assistant

---

# 16. Future Enhancements

Potential future additions:

- Application History
- Stage Change Audit Log
- Automated Notifications
- SLA Tracking
- Candidate Feedback
- Recruiter Activity Log

---

# 17. Summary

The **applications** table is the core transaction table of TalentIQ. It connects candidates, jobs, recruiters, interviews, offers, and placements while tracking every stage of the recruitment lifecycle. Nearly all recruitment analytics, dashboards, machine learning models, and AI features depend on this table.