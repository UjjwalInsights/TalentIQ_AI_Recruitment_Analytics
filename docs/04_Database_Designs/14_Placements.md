# Database Design
# Table: Placements

**Module:** Database Design
**Table Name:** placements
**Primary Key:** placement_id

---

# 1. Purpose

The **placements** table stores successful hiring records where a candidate has accepted an offer and officially joined the client organization.

A placement represents the successful completion of the recruitment lifecycle.

This table enables revenue reporting, recruiter performance tracking, placement margin analysis, hiring success metrics, and executive dashboards.

---

# 2. Business Description

A placement is created after:

Job Created

↓

Candidate Applied

↓

Interview Completed

↓

Offer Accepted

↓

Candidate Joined

Once a placement exists, the recruitment process for that application is considered complete.

---

# 3. Table Purpose

The placements table is responsible for:

- Recording successful hires
- Tracking joining information
- Calculating placement margins
- Measuring recruiter performance
- Supporting executive dashboards
- Revenue analytics
- AI hiring outcome analysis

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| placement_id | Unique placement identifier |

---

# 5. Foreign Keys

| Column | References |
|----------|------------|
| application_id | applications.application_id |
| candidate_id | candidates.candidate_id |
| job_id | jobs.job_id |
| offer_id | offers.offer_id |
| recruiter_id | recruiters.recruiter_id |

---

# 6. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| placement_id | BIGSERIAL | Yes | Primary Key |
| application_id | BIGINT | Yes | Related application |
| candidate_id | BIGINT | Yes | Candidate |
| job_id | BIGINT | Yes | Job |
| offer_id | BIGINT | Yes | Accepted offer |
| recruiter_id | BIGINT | Yes | Assigned recruiter |
| joining_date | DATE | Yes | Candidate joining date |
| employment_status | VARCHAR(50) | Yes | Active, Completed, Terminated |
| bill_rate | DECIMAL(10,2) | No | Client billing rate |
| pay_rate | DECIMAL(10,2) | No | Candidate pay rate |
| placement_margin | DECIMAL(10,2) | No | Bill Rate - Pay Rate |
| placement_type | VARCHAR(50) | Yes | Contract, Full-Time, C2H |
| contract_duration_months | INTEGER | No | Contract duration |
| probation_end_date | DATE | No | End of probation |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 7. Relationships

One Offer

↓

One Placement

```
offers
   │
   └────────► placements
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

One Recruiter

↓

Many Placements

```
recruiters
      │
      └────────► placements
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

# 8. Placement Workflow

```
Offer Accepted

↓

Joining Confirmed

↓

Placement Created

↓

Revenue Generated

↓

Contract Completed
```

---

# 9. Business Rules

- A placement must reference an accepted offer.
- Joining date cannot be before the offer acceptance date.
- Bill rate must be greater than or equal to pay rate.
- Placement margin is calculated automatically.
- One application can result in only one placement.

---

# 10. Validation Rules

| Field | Validation |
|---------|------------|
| application_id | Must exist |
| offer_id | Must exist |
| joining_date | Cannot be empty |
| bill_rate | Greater than or equal to pay_rate |
| placement_margin | Calculated automatically |

---

# 11. Indexing Strategy

Indexes should be created on:

- application_id
- candidate_id
- recruiter_id
- joining_date
- placement_type
- employment_status

---

# 12. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 500 |
| Demo | 10,000 |
| Production | Millions |

---

# 13. Used By

This table is referenced by:

- Executive Dashboard
- Revenue Dashboard
- Recruiter Dashboard
- Margin Reports
- AI Hiring Analytics
- Client Reports

---

# 14. Analytics Supported

The placements table enables:

- Total Placements
- Placement Success Rate
- Time to Fill
- Time to Hire
- Placement Margin
- Revenue by Recruiter
- Revenue by Client
- Revenue by Department
- Placement Trend
- Monthly Hiring Trend
- Contract vs Full-Time Placements

---

# 15. AI Features

The placements table supports:

- Hiring Success Prediction
- Revenue Forecasting
- Recruiter Performance Prediction
- Client Demand Forecasting
- Placement Probability Analysis

---

# 16. Future Enhancements

Potential future additions:

- Early Attrition Tracking
- Candidate Performance Reviews
- Contract Extension History
- Client Satisfaction Rating
- Recruiter Commission Calculation
- Invoice Tracking
- Payroll Integration

---

# 17. Summary

The **placements** table represents the successful completion of the recruitment lifecycle. It captures candidate joining information, financial metrics, recruiter ownership, and placement outcomes while serving as the foundation for revenue reporting, executive dashboards, AI analytics, and business performance measurement.