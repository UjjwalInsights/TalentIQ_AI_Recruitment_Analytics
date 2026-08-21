# Database Design
# Table: Recruiters

**Module:** Database Design  
**Table Name:** recruiters  
**Primary Key:** recruiter_id

---

# 1. Purpose

The **recruiters** table stores information about all recruiters working within a recruitment agency.

Recruiters are responsible for managing job requisitions, sourcing candidates, scheduling interviews, negotiating offers, and placing candidates.

Each recruiter belongs to one recruitment agency (company).

---

# 2. Business Description

A recruiter is an employee of a recruitment agency.

Examples:

- Technical Recruiter
- Senior Recruiter
- Lead Recruiter
- Recruitment Manager

Each recruiter may work on multiple job requisitions.

Each recruiter may submit multiple candidates.

Each recruiter may create multiple placements.

---

# 3. Table Purpose

This table is responsible for:

- Managing recruiter information
- Assigning recruiters to jobs
- Tracking recruiter performance
- Measuring hiring productivity
- Supporting recruiter dashboards
- Supporting recruiter-based analytics

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| recruiter_id | Unique recruiter identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| company_id | companies.company_id |

Each recruiter belongs to one recruitment agency.

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| recruiter_id | BIGSERIAL | Yes | Primary Key |
| company_id | BIGINT | Yes | Recruitment Agency |
| first_name | VARCHAR(100) | Yes | Recruiter first name |
| last_name | VARCHAR(100) | Yes | Recruiter last name |
| email | VARCHAR(150) | Yes | Official email |
| phone | VARCHAR(30) | No | Contact number |
| employee_id | VARCHAR(50) | No | Internal employee ID |
| designation | VARCHAR(100) | Yes | Recruiter role |
| experience_years | DECIMAL(4,1) | No | Total recruitment experience |
| specialization | VARCHAR(150) | No | Technology or domain specialization |
| hire_date | DATE | Yes | Joining date |
| manager_id | BIGINT | No | Reporting manager (self-reference) |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation timestamp |
| updated_at | TIMESTAMP | Yes | Last update timestamp |
| created_by | VARCHAR(100) | No | Created by |
| updated_by | VARCHAR(100) | No | Updated by |

---

# 7. Relationships

One Company

↓

Many Recruiters

```
companies
      │
      └────────► recruiters
```

---

One Recruiter

↓

Many Jobs

```
recruiters
      │
      └────────► jobs
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

One Recruiter

↓

Many Placements

```
recruiters
      │
      └────────► placements
```

---

One Manager

↓

Many Recruiters

```
recruiters
      │
      └────────► recruiters
```

(Self-referencing relationship)

---

# 8. Business Rules

- Every recruiter must belong to one recruitment agency.
- Every recruiter must have a unique email.
- Only active recruiters can be assigned to new jobs.
- A recruiter may report to another recruiter acting as a manager.
- Recruiters can work on multiple jobs simultaneously.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| first_name | Cannot be empty |
| last_name | Cannot be empty |
| email | Must be unique and valid |
| experience_years | Cannot be negative |
| hire_date | Cannot be in the future |
| company_id | Must exist in companies table |

---

# 10. Indexing Strategy

Indexes should be created on:

- company_id
- email
- designation
- specialization
- is_active

These indexes improve recruiter search, dashboard filtering, and reporting performance.

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 20 |
| Demo | 50 |
| Production | Unlimited |

---

# 12. Used By

This table is referenced by:

- Jobs
- Applications
- Placements
- Recruiter Performance Dashboard
- Executive Dashboard
- AI Analytics

---

# 13. Sample Records

| Recruiter | Company | Designation | Specialization |
|------------|---------|-------------|----------------|
| John Smith | Precision Technologies | Senior Recruiter | Data Engineering |
| Sarah Johnson | Precision Technologies | Technical Recruiter | Java |
| David Lee | Precision Technologies | Lead Recruiter | Cloud & DevOps |
| Emily Brown | Precision Technologies | Recruitment Manager | Full Stack Hiring |

---

# 14. Recruiter Performance Metrics

The system should calculate:

- Jobs Assigned
- Candidates Sourced
- Candidates Submitted
- Interviews Scheduled
- Offers Released
- Placements
- Time to Fill
- Offer Acceptance Rate
- Placement Revenue
- Placement Margin

These KPIs will power recruiter scorecards and executive dashboards.

---

# 15. Future Enhancements

Future versions may include:

- Recruiter certifications
- Performance targets
- Incentive tracking
- Leave management
- Recruiter workload balancing
- AI recruiter recommendations

---

# 16. Summary

The **recruiters** table represents the recruitment team responsible for sourcing, managing, and placing candidates. It is one of the central operational tables in TalentIQ and serves as the basis for recruiter performance analytics, hiring productivity metrics, and recruitment workflow management.