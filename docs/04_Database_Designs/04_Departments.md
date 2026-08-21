# Database Design
# Table: Departments

**Module:** Database Design  
**Table Name:** departments  
**Primary Key:** department_id

---

# 1. Purpose

The **departments** table stores the business departments or functional areas within an organization.

Departments help organize recruiters, jobs, and hiring analytics. They allow the system to report hiring performance by business unit and improve operational visibility.

---

# 2. Business Description

Every job belongs to one department.

Examples of departments include:

- Information Technology
- Data & Analytics
- Human Resources
- Finance
- Healthcare
- Sales
- Marketing
- Operations

A department may contain multiple jobs and may have multiple recruiters working within it.

---

# 3. Table Purpose

This table is responsible for:

- Organizing business units
- Classifying job requisitions
- Supporting department-wise reporting
- Supporting executive dashboards
- Improving hiring analytics

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| department_id | Unique department identifier |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| department_id | SMALLSERIAL | Yes | Primary Key |
| department_name | VARCHAR(100) | Yes | Department name |
| department_code | VARCHAR(20) | Yes | Short department code |
| description | TEXT | No | Department description |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation timestamp |
| updated_at | TIMESTAMP | Yes | Last update timestamp |

---

# 6. Default Records

| ID | Department |
|----|------------|
| 1 | Information Technology |
| 2 | Data & Analytics |
| 3 | Human Resources |
| 4 | Finance |
| 5 | Healthcare |
| 6 | Sales |
| 7 | Marketing |
| 8 | Operations |

---

# 7. Relationships

One Department

↓

Many Jobs

```
departments
        │
        └────────► jobs
```

---

One Department

↓

Many Recruiters

```
departments
        │
        └────────► recruiters
```

---

# 8. Business Rules

- Every department must have a unique name.
- Department codes must be unique.
- Jobs must belong to one department.
- Inactive departments cannot receive new jobs.

---

# 9. Validation Rules

| Field | Validation |
|---------|------------|
| department_name | Cannot be empty |
| department_code | Must be unique |
| is_active | TRUE or FALSE |

---

# 10. Indexing Strategy

Indexes should be created on:

- department_name
- department_code
- is_active

---

# 11. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 8 |
| Demo | 15 |
| Production | Unlimited |

---

# 12. Used By

This table is referenced by:

- Recruiters
- Jobs
- Analytics
- Power BI Dashboards
- Executive Reports

---

# 13. Sample Records

| Department | Code |
|------------|------|
| Information Technology | IT |
| Data & Analytics | DATA |
| Human Resources | HR |
| Finance | FIN |
| Healthcare | HC |
| Sales | SALES |
| Marketing | MKT |
| Operations | OPS |

---

# 14. Future Enhancements

Future versions may include:

- Parent Departments
- Department Managers
- Budget Allocation
- Hiring Targets
- Department Cost Centers

---

# 15. Summary

The **departments** table provides a standardized way to classify jobs and recruiters into business units. It supports department-level analytics, improves reporting accuracy, and keeps the database organized as the system grows.