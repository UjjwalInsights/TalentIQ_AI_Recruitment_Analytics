# Database Design
# Table: Locations

**Module:** Database Design  
**Table Name:** locations  
**Primary Key:** location_id

---

# 1. Purpose

The **locations** table stores standardized geographic locations used throughout the TalentIQ platform.

Rather than storing city, state, and country repeatedly in multiple tables, the system stores them once and references them using a foreign key.

This improves consistency, reduces data duplication, and supports location-based reporting.

---

# 2. Business Description

A location represents a physical place where:

- A company operates
- A job is located
- A candidate prefers to work
- A placement occurs

Examples:

- New York, NY, USA
- Dallas, TX, USA
- Chicago, IL, USA
- Hyderabad, India
- Bengaluru, India

---

# 3. Table Purpose

This table is responsible for:

- Standardizing locations
- Supporting remote, hybrid, and onsite jobs
- Enabling location-based analytics
- Powering dashboard filters

---

# 4. Primary Key

| Column | Description |
|----------|-------------|
| location_id | Unique location identifier |

---

# 5. Columns

| Column | Data Type | Required | Description |
|----------|-----------|----------|-------------|
| location_id | BIGSERIAL | Yes | Primary Key |
| city | VARCHAR(100) | Yes | City |
| state | VARCHAR(100) | Yes | State / Province |
| country | VARCHAR(100) | Yes | Country |
| postal_code | VARCHAR(20) | No | ZIP / Postal Code |
| timezone | VARCHAR(100) | No | Time zone |
| is_active | BOOLEAN | Yes | Active status |
| created_at | TIMESTAMP | Yes | Record creation |
| updated_at | TIMESTAMP | Yes | Last update |

---

# 6. Relationships

One Location

↓

Many Companies

One Location

↓

Many Jobs

One Location

↓

Many Candidates

One Location

↓

Many Placements

---

# 7. Business Rules

- A location should be stored only once.
- City, state, and country together should be unique.
- Inactive locations cannot be assigned to new records.

---

# 8. Validation Rules

- City cannot be empty.
- State cannot be empty.
- Country cannot be empty.

---

# 9. Indexing Strategy

Indexes:

- city
- state
- country
- is_active

---

# 10. Estimated Records

| Environment | Estimated Records |
|-------------|------------------:|
| Development | 50 |
| Demo | 500 |
| Production | Unlimited |

---

# 11. Used By

- Companies
- Jobs
- Candidates
- Placements
- Dashboards
- Analytics

---

# 12. Sample Records

| City | State | Country |
|------|-------|----------|
| New York | New York | USA |
| Dallas | Texas | USA |
| Chicago | Illinois | USA |
| Hyderabad | Telangana | India |
| Bengaluru | Karnataka | India |

---

# 13. Summary

The **locations** table provides a standardized repository of geographic information used throughout TalentIQ, ensuring consistent data entry, easier reporting, and scalable database design.