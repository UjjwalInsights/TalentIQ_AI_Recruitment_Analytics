# Database Design
# Table: Company Types

**Module:** Database Design  
**Table Name:** company_types  
**Primary Key:** company_type_id

---

# 1. Purpose

The **company_types** table is a reference (lookup) table that stores the different types of companies involved in the recruitment process.

Instead of storing text values such as "End Client" or "Implementation Partner" repeatedly in the companies table, TalentIQ stores them once in this table and references them using a foreign key.

This improves data consistency, reduces duplication, and follows database normalization principles.

---

# 2. Business Description

Every company in the system belongs to one company type.

Examples include:

- Recruitment Agency
- End Client
- Implementation Partner
- Direct Client

A single company type can be assigned to many companies.

---

# 3. Table Purpose

This table is responsible for:

- Standardizing company classifications
- Preventing inconsistent company type names
- Supporting database normalization
- Simplifying reporting and analytics
- Providing dropdown values in the application

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| company_type_id | Unique identifier for each company type |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| company_type_id | SMALLSERIAL | Yes | Primary Key |
| company_type_name | VARCHAR(100) | Yes | Name of the company type |
| description | TEXT | No | Description of the company type |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation timestamp |
| updated_at | TIMESTAMP | Yes | Last update timestamp |

---

# 6. Default Records

The following values should exist when the database is created.

| ID | Company Type | Description |
|----|--------------|-------------|
| 1 | Recruitment Agency | Organization responsible for sourcing and placing candidates |
| 2 | End Client | Company where the candidate will ultimately work |
| 3 | Implementation Partner | Company acting between the recruitment agency and end client |
| 4 | Direct Client | Company hiring directly without an implementation partner |

---

# 7. Relationships

One Company Type

↓

Many Companies

```
company_types
        │
        └────────► companies
```

Relationship Type

**One-to-Many (1:N)**

---

# 8. Business Rules

- Every company must belong to one company type.
- Company type names must be unique.
- System-defined company types should not be deleted.
- Inactive company types cannot be assigned to new companies.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| company_type_name | Cannot be empty |
| company_type_name | Must be unique |
| is_active | Must be TRUE or FALSE |

---

# 10. Indexing Strategy

Indexes should be created on:

- company_type_name
- is_active

These indexes improve search performance and reporting.

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 4 |
| Demo | 4 |
| Production | 4–10 |

Although this table contains only a few records, it is essential because it is referenced throughout the system.

---

# 12. Used By

This table is referenced by:

- Companies
- Recruiter Management
- Job Management
- Executive Dashboard
- Analytics Reports

---

# 13. Sample Records

| company_type_id | company_type_name |
|----------------:|-------------------|
| 1 | Recruitment Agency |
| 2 | End Client |
| 3 | Implementation Partner |
| 4 | Direct Client |

---

# 14. Future Enhancements

Future versions may include additional company types such as:

- Managed Service Provider (MSP)
- Vendor Management System (VMS)
- Consulting Partner
- Strategic Partner

These can be added without changing the database structure.

---

# 15. Summary

The **company_types** table is a reference table that standardizes company classifications across the TalentIQ platform. It ensures consistent data entry, supports normalization, improves reporting accuracy, and provides reusable values for application dropdowns and analytics.