# Database Design
# Table: Offers

**Module:** Database Design  
**Table Name:** offers  
**Primary Key:** offer_id

---

# 1. Purpose

The **offers** table stores every employment offer extended to a candidate after successfully completing the interview process.

It captures offer details, compensation, negotiation history, acceptance status, joining dates, and final hiring outcomes.

This table supports offer management, hiring analytics, recruiter performance evaluation, and executive reporting.

---

# 2. Business Description

An offer represents the formal employment proposal made to a candidate.

A candidate may:

- Accept the offer
- Reject the offer
- Negotiate the offer
- Let the offer expire
- Withdraw before joining

Every offer belongs to one application.

---

# 3. Table Purpose

This table is responsible for:

- Offer generation
- Compensation tracking
- Offer negotiations
- Offer acceptance tracking
- Joining confirmation
- Executive reporting

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| offer_id | Unique offer identifier |

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
| offer_id | BIGSERIAL | Yes | Primary Key |
| application_id | BIGINT | Yes | Related application |
| candidate_id | BIGINT | Yes | Candidate |
| job_id | BIGINT | Yes | Job |
| recruiter_id | BIGINT | Yes | Recruiter |
| offer_date | DATE | Yes | Date offer was released |
| offer_status | VARCHAR(50) | Yes | Pending, Accepted, Rejected, Expired, Withdrawn |
| offered_salary | DECIMAL(12,2) | Yes | Annual offered salary |
| offered_hourly_rate | DECIMAL(10,2) | No | Hourly rate for contract roles |
| joining_bonus | DECIMAL(10,2) | No | Joining bonus |
| joining_date | DATE | No | Planned joining date |
| acceptance_date | DATE | No | Date candidate accepted |
| rejection_reason | TEXT | No | Reason for rejection |
| negotiation_notes | TEXT | No | Salary negotiation comments |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 7. Relationships

One Application

↓

One Offer

```
applications
      │
      └────────► offers
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

One Job

↓

Many Offers

```
jobs
   │
   └────────► offers
```

---

One Recruiter

↓

Many Offers

```
recruiters
      │
      └────────► offers
```

---

# 8. Offer Workflow

```
Interview Passed

↓

Offer Generated

↓

Candidate Reviews Offer

↓

Negotiation (Optional)

↓

Accepted / Rejected / Expired

↓

Placement
```

---

# 9. Business Rules

- Every offer belongs to one application.
- An application can have only one active offer.
- Accepted offers require an acceptance date.
- Rejected offers require a rejection reason.
- Offered salary cannot be negative.
- Joining date must be after the offer date.

---

# 10. Validation Rules

| Field | Validation |
|---------|------------|
| application_id | Must exist |
| offer_date | Cannot be empty |
| offered_salary | Greater than zero |
| offer_status | Valid status |
| joining_date | Must be after offer_date |

---

# 11. Indexing Strategy

Indexes should be created on:

- application_id
- candidate_id
- recruiter_id
- offer_status
- offer_date
- joining_date

---

# 12. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 500 |
| Demo | 20,000 |
| Production | Millions |

---

# 13. Used By

This table is referenced by:

- Placements
- Dashboards
- Recruiter Reports
- Executive Reports
- AI Hiring Assistant

---

# 14. Analytics Supported

The offers table enables:

- Offer Acceptance Rate
- Offer Rejection Rate
- Average Offered Salary
- Salary Negotiation Trends
- Recruiter Offer Success Rate
- Time from Interview to Offer
- Offer Expiry Analysis

---

# 15. AI Features

The offers table supports:

- Offer Acceptance Prediction
- Salary Recommendation
- Compensation Benchmarking
- Joining Probability Prediction
- AI Hiring Insights

---

# 16. Future Enhancements

Potential future additions:

- Digital Offer Letter
- E-Signature Integration
- Multiple Offer Revisions
- Approval Workflow
- Compensation Breakdown
- Benefits Package

---

# 17. Summary

The **offers** table manages the final stage before hiring by storing compensation details, offer status, negotiations, and acceptance outcomes. It is essential for measuring hiring success, recruiter effectiveness, and offer conversion while supporting AI-driven salary recommendations and acceptance predictions.