# Database Design
# Table: Work Authorizations

**Module:** Database Design  
**Table Name:** work_authorizations  
**Primary Key:** work_authorization_id

---

# 1. Purpose

The **work_authorizations** table stores the employment authorization types that determine a candidate's legal eligibility to work in a specific country.

In TalentIQ, this table primarily models US work authorization categories commonly used in the IT staffing industry.

Instead of storing authorization values repeatedly, the system references this master table using a foreign key.

---

# 2. Business Description

Every candidate has one primary work authorization status.

Examples include:

- US Citizen
- Green Card
- H1B
- H4 EAD
- OPT
- CPT
- TN Visa
- L2 EAD

Recruiters use this information to determine whether a candidate is eligible for a particular job.

---

# 3. Table Purpose

This table is responsible for:

- Standardizing work authorization values
- Supporting recruiter searches
- Supporting compliance reporting
- Filtering candidates
- Supporting AI candidate matching

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| work_authorization_id | Unique authorization identifier |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| work_authorization_id | SMALLSERIAL | Yes | Primary Key |
| authorization_name | VARCHAR(100) | Yes | Work authorization type |
| sponsorship_required | BOOLEAN | Yes | Indicates whether employer sponsorship is required |
| description | TEXT | No | Additional details |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 6. Default Records

| ID | Authorization | Sponsorship Required |
|----|---------------|----------------------|
| 1 | US Citizen | No |
| 2 | Green Card | No |
| 3 | H1B | Yes |
| 4 | H4 EAD | No |
| 5 | OPT | Yes |
| 6 | CPT | Yes |
| 7 | TN Visa | Sometimes |
| 8 | L2 EAD | No |
| 9 | E3 Visa | Yes |

---

# 7. Relationships

One Work Authorization

↓

Many Candidates

```
work_authorizations
          │
          └────────► candidates
```

Relationship Type

One-to-Many (1:N)

---

# 8. Business Rules

- Every candidate must have one work authorization.
- Authorization names must be unique.
- Inactive authorizations cannot be assigned to new candidates.
- Sponsorship requirements must be clearly defined.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| authorization_name | Cannot be empty |
| authorization_name | Must be unique |
| sponsorship_required | TRUE or FALSE |

---

# 10. Indexing Strategy

Indexes should be created on:

- authorization_name
- sponsorship_required
- is_active

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 9 |
| Demo | 9 |
| Production | 20+ |

---

# 12. Used By

This table is referenced by:

- Candidates
- AI Job Matcher
- Recruiter Search
- Candidate Filters
- Dashboards

---

# 13. Sample Records

| Authorization | Sponsorship Required |
|---------------|----------------------|
| US Citizen | No |
| Green Card | No |
| H1B | Yes |
| OPT | Yes |
| CPT | Yes |
| H4 EAD | No |
| TN Visa | Sometimes |

---

# 14. Analytics Supported

This table enables:

- Candidate Distribution by Work Authorization
- Sponsorship Requirement Analysis
- Recruiter Pipeline by Visa Status
- Job Eligibility Reports
- Placement Analysis by Work Authorization

---

# 15. Future Enhancements

Potential future additions:

- Expiration Date Tracking
- Country-Specific Work Authorizations
- Visa Renewal Status
- Document Verification Status
- Immigration Compliance Checks

---

# 16. Summary

The **work_authorizations** table standardizes employment eligibility information across the TalentIQ platform. It is essential for modeling real-world US IT staffing workflows and enables accurate recruiter searches, analytics, and AI-assisted candidate matching.