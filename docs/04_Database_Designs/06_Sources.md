# Database Design
# Table: Sources

**Module:** Database Design  
**Table Name:** sources  
**Primary Key:** source_id

---

# 1. Purpose

The **sources** table stores all candidate sourcing channels used by recruiters.

Instead of storing source names repeatedly across candidate and application records, the system references a standardized source using a foreign key.

This enables accurate reporting, analytics, and source effectiveness measurement.

---

# 2. Business Description

A source represents where a candidate was discovered or applied from.

Examples include:

- LinkedIn
- Dice
- Monster
- CareerBuilder
- Indeed
- Referral
- Internal Database
- Company Website
- Job Fair

A single source can provide thousands of candidates.

---

# 3. Table Purpose

This table is responsible for:

- Standardizing sourcing channels
- Measuring source effectiveness
- Tracking recruiter sourcing performance
- Supporting dashboard filters
- Supporting ROI analysis

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| source_id | Unique source identifier |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| source_id | SMALLSERIAL | Yes | Primary Key |
| source_name | VARCHAR(100) | Yes | Source name |
| source_category | VARCHAR(50) | Yes | Type of source |
| website | VARCHAR(255) | No | Official website |
| description | TEXT | No | Additional notes |
| is_paid | BOOLEAN | Yes | Paid or free source |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 6. Default Records

| ID | Source | Category |
|----|--------|----------|
| 1 | LinkedIn | Professional Network |
| 2 | Dice | Job Board |
| 3 | Monster | Job Board |
| 4 | CareerBuilder | Job Board |
| 5 | Indeed | Job Board |
| 6 | Referral | Employee Referral |
| 7 | Internal Database | ATS |
| 8 | Company Website | Career Portal |
| 9 | Job Fair | Recruitment Event |

---

# 7. Relationships

One Source

↓

Many Candidates

```
sources
     │
     └────────► candidates
```

---

One Source

↓

Many Applications

```
sources
     │
     └────────► applications
```

Relationship Type

**One-to-Many (1:N)**

---

# 8. Business Rules

- Every source must have a unique name.
- A candidate must be associated with one primary source.
- Inactive sources cannot be used for new candidates.
- Paid and free sources should be distinguishable.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| source_name | Cannot be empty |
| source_name | Must be unique |
| source_category | Cannot be empty |
| is_paid | TRUE or FALSE |
| is_active | TRUE or FALSE |

---

# 10. Indexing Strategy

Indexes should be created on:

- source_name
- source_category
- is_paid
- is_active

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 10 |
| Demo | 15 |
| Production | 50+ |

---

# 12. Used By

This table is referenced by:

- Candidates
- Applications
- Recruiter Analytics
- Executive Dashboard
- Source Effectiveness Dashboard

---

# 13. Sample Records

| Source | Category | Paid |
|---------|----------|------|
| LinkedIn | Professional Network | Yes |
| Dice | Job Board | Yes |
| Monster | Job Board | Yes |
| CareerBuilder | Job Board | Yes |
| Indeed | Job Board | Yes |
| Referral | Employee Referral | No |
| Internal Database | ATS | No |
| Company Website | Career Portal | No |
| Job Fair | Recruitment Event | Yes |

---

# 14. Analytics Supported

This table enables the following KPIs:

- Candidates by Source
- Interviews by Source
- Offers by Source
- Hires by Source
- Source Conversion Rate
- Cost per Hire by Source
- Source ROI
- Recruiter Source Utilization

---

# 15. Future Enhancements

Potential future additions:

- Source Cost
- Monthly Subscription Cost
- Recruiter-specific Source Access
- API Integration with Job Boards
- Source Quality Score

---

# 16. Summary

The **sources** table standardizes candidate sourcing channels across the TalentIQ platform. It enables consistent data entry, supports recruiter performance analysis, and powers one of the most important recruitment metrics: **Source Effectiveness**.