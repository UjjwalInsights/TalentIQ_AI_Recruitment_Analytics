# Database Design
# Table: Companies

**Module:** Database Design  
**Table Name:** companies  
**Primary Key:** company_id

---

# 1. Purpose

The **companies** table stores every organization involved in the recruitment lifecycle.

Instead of maintaining separate tables for clients, vendors, implementation partners, and recruitment agencies, TalentIQ uses a unified company model.

The role of each organization is identified through the **company_type** field.

This approach keeps the database flexible, scalable, and easier to maintain.

---

# 2. Business Description

A company can represent:

- Recruitment Agency
- End Client
- Implementation Partner
- Direct Client

Examples

| Company | Type |
|----------|------|
| Apple | End Client |
| JPMorgan Chase | End Client |
| Wells Fargo | End Client |
| Capgemini | Implementation Partner |
| HCL Technologies | Implementation Partner |
| Mphasis | Implementation Partner |
| Precision Technologies | Recruitment Agency |

One company may have multiple jobs.

One company may receive multiple placements.

One company may work with multiple recruiters.

---

# 3. Table Purpose

This table is responsible for:

- Managing client information
- Managing implementation partners
- Managing recruitment agencies
- Tracking company performance
- Supporting analytics
- Supporting margin calculations
- Supporting recruiter assignments

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| company_id | Unique identifier for each company |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| company_id | BIGSERIAL | Yes | Primary Key |
| company_name | VARCHAR(200) | Yes | Official company name |
| company_type | VARCHAR(50) | Yes | Recruitment Agency, End Client, Implementation Partner, Direct Client |
| industry | VARCHAR(100) | Yes | Industry classification |
| website | VARCHAR(255) | No | Official website |
| email | VARCHAR(150) | No | General contact email |
| phone | VARCHAR(30) | No | Contact number |
| address_line_1 | VARCHAR(255) | No | Address |
| address_line_2 | VARCHAR(255) | No | Address |
| city | VARCHAR(100) | Yes | City |
| state | VARCHAR(100) | Yes | State |
| country | VARCHAR(100) | Yes | Country |
| postal_code | VARCHAR(20) | No | ZIP / Postal code |
| employee_size | INTEGER | No | Approximate workforce |
| founded_year | INTEGER | No | Year company was founded |
| linkedin_url | VARCHAR(255) | No | Company LinkedIn page |
| notes | TEXT | No | Internal notes |
| is_active | BOOLEAN | Yes | Active company flag |
| created_at | TIMESTAMP | Yes | Record creation timestamp |
| updated_at | TIMESTAMP | Yes | Last update timestamp |
| created_by | VARCHAR(100) | No | User who created the record |
| updated_by | VARCHAR(100) | No | User who last updated the record |

---

# 6. Candidate Values

## company_type

Allowed values

- Recruitment Agency
- End Client
- Implementation Partner
- Direct Client

---

## industry

Examples

- Information Technology
- Banking
- Finance
- Healthcare
- Retail
- Insurance
- Manufacturing
- Telecommunications

---

# 7. Relationships

The companies table participates in several one-to-many relationships.

### One Company → Many Jobs

```
companies
      │
      └────────► jobs
```

---

### One Company → Many Placements

```
companies
      │
      └────────► placements
```

---

### One Company → Many Recruiters (Agency)

```
companies
      │
      └────────► recruiters
```

---

### One Company → Many Hiring Managers (Future)

```
companies
      │
      └────────► hiring_managers
```

---

# 8. Business Rules

- Every company must have a unique name.
- Every company must belong to one company type.
- Inactive companies cannot receive new job requisitions.
- A recruitment agency can recruit for multiple clients.
- An implementation partner may work with multiple end clients.
- Company information should be retained even if no active jobs exist.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| company_name | Cannot be empty |
| company_type | Must be one of the allowed values |
| website | Valid URL if provided |
| email | Valid email format if provided |
| founded_year | Must not be greater than the current year |
| employee_size | Must be positive |
| country | Cannot be empty |

---

# 10. Indexing Strategy

Indexes should be created on:

- company_name
- company_type
- country
- city
- is_active

These indexes will improve search performance and dashboard filtering.

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 50 |
| Demo | 200 |
| Production | Unlimited |

---

# 12. Used By

This table is referenced by:

- Jobs
- Recruiters
- Placements
- Analytics
- Power BI Dashboards
- AI Reporting

---

# 13. Sample Records

| Company | Type | Industry |
|----------|------|----------|
| Apple | End Client | Information Technology |
| JPMorgan Chase | End Client | Banking |
| Wells Fargo | End Client | Banking |
| Capgemini | Implementation Partner | Information Technology |
| HCL Technologies | Implementation Partner | Information Technology |
| Mphasis | Implementation Partner | Information Technology |
| Precision Technologies | Recruitment Agency | Staffing & Recruiting |

---

# 14. Future Enhancements

Potential future additions include:

- Company contacts
- Multiple office locations
- SLA tracking
- Contract history
- Client satisfaction metrics
- Revenue by client
- Vendor scorecards
- Account managers
- Preferred vendor status

---

# 15. Summary

The **companies** table is the foundation of the TalentIQ platform. It centralizes all organizations participating in the recruitment ecosystem, enabling flexible relationships, scalable reporting, and accurate analytics without duplicating company information across multiple tables.