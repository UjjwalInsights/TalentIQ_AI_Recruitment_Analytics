# Database Design
# Table: Interviews

**Module:** Database Design
**Table Name:** interviews
**Primary Key:** interview_id

---

# 1. Purpose

The **interviews** table stores every interview scheduled between a candidate and a company during the recruitment process.

Each interview represents one interview round and records scheduling details, interviewer information, feedback, ratings, and the interview outcome.

This table enables interview tracking, recruiter coordination, candidate evaluation, and executive reporting.

---

# 2. Business Description

A candidate may go through multiple interview rounds for a single application.

Typical interview flow:

Resume Screening

↓

Recruiter Screening

↓

Technical Round 1

↓

Technical Round 2

↓

Manager Round

↓

Client Round

↓

HR Round

↓

Offer

Each interview is stored as an independent record.

---

# 3. Table Purpose

This table is responsible for:

- Interview scheduling
- Interview tracking
- Recording interviewer feedback
- Candidate evaluation
- Interview analytics
- AI interview insights
- Dashboard reporting

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| interview_id | Unique interview identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| application_id | applications.application_id |
| candidate_id | candidates.candidate_id |
| job_id | jobs.job_id |
| recruiter_id | recruiters.recruiter_id |

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| interview_id | BIGSERIAL | Yes | Primary Key |
| application_id | BIGINT | Yes | Related application |
| candidate_id | BIGINT | Yes | Candidate |
| job_id | BIGINT | Yes | Job |
| recruiter_id | BIGINT | Yes | Recruiter |
| interview_round | INTEGER | Yes | Round number |
| interview_type | VARCHAR(50) | Yes | HR, Technical, Client, Manager |
| interview_mode | VARCHAR(50) | Yes | Online, Onsite, Phone |
| interviewer_name | VARCHAR(150) | Yes | Interviewer's name |
| scheduled_datetime | TIMESTAMP | Yes | Scheduled date & time |
| duration_minutes | INTEGER | Yes | Duration |
| interview_status | VARCHAR(50) | Yes | Scheduled, Completed, Cancelled |
| rating | DECIMAL(3,1) | No | Interview score (0–10) |
| recommendation | VARCHAR(30) | No | Hire, Reject, Hold |
| feedback | TEXT | No | Interview feedback |
| completed_at | TIMESTAMP | No | Completion time |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 7. Relationships

One Application

↓

Many Interviews

```
applications
      │
      └────────► interviews
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

One Job

↓

Many Interviews

```
jobs
   │
   └────────► interviews
```

---

One Recruiter

↓

Many Interviews

```
recruiters
      │
      └────────► interviews
```

---

# 8. Interview Workflow

```
Interview Scheduled

↓

Candidate Confirmed

↓

Interview Conducted

↓

Feedback Submitted

↓

Decision Recorded

↓

Next Round / Reject / Offer
```

---

# 9. Business Rules

- Every interview belongs to one application.
- A candidate may have multiple interview rounds.
- Interview rounds should be sequential.
- Completed interviews must have a recommendation.
- Rating must be between 0 and 10.

---

# 10. Validation Rules

| Field | Validation |
|---------|------------|
| application_id | Must exist |
| interview_round | Greater than 0 |
| duration_minutes | Greater than 0 |
| rating | Between 0 and 10 |
| scheduled_datetime | Cannot be empty |

---

# 11. Indexing Strategy

Indexes should be created on:

- application_id
- candidate_id
- recruiter_id
- interview_status
- interview_type
- scheduled_datetime

---

# 12. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 5,000 |
| Demo | 200,000 |
| Production | Millions |

---

# 13. Used By

This table is referenced by:

- Offers
- Dashboards
- Recruiter Performance Reports
- Interview Analytics
- AI Assistant

---

# 14. Analytics Supported

The interviews table enables:

- Interview Success Rate
- Interview Conversion Rate
- Average Interview Rating
- Recruiter Interview Load
- Candidate Interview History
- Average Time Between Rounds
- Interview Cancellation Rate

---

# 15. AI Features

The interviews table supports:

- Interview Outcome Prediction
- Candidate Success Prediction
- Interview Feedback Summarization
- AI Hiring Recommendations
- Recruiter Performance Insights

---

# 16. Future Enhancements

Potential future additions:

- Multiple Interviewers
- Interview Panel
- Calendar Integration
- Meeting Links
- AI Interview Transcript Analysis
- Automated Feedback Generation

---

# 17. Summary

The **interviews** table captures every interview event within the recruitment lifecycle. It enables interview scheduling, evaluation, recruiter coordination, analytics, and AI-driven hiring insights while maintaining a complete history of every candidate's interview journey.