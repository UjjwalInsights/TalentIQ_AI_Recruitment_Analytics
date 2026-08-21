# Database Design Overview

## Purpose

The TalentIQ database is designed to support the complete recruitment lifecycle for staffing agencies, HR departments, and recruitment companies.

The database follows Third Normal Form (3NF) to minimize redundancy and ensure data integrity.

---

## Database Goals

- Store recruitment data efficiently
- Support SQL analytics
- Power executive dashboards
- Support AI-powered resume matching
- Enable machine learning models
- Scale to large datasets

---

## Database Type

Relational Database

Database Engine:

- PostgreSQL

---

## Database Layers

### Master Tables

- Companies
- Recruiters
- Skills
- Sources
- Locations
- Departments

---

### Transaction Tables

- Jobs
- Candidates
- Applications
- Interviews
- Offers
- Placements

---

### Mapping Tables

- Candidate Skills
- Job Skills

---

### AI Tables

- Resume Documents
- Resume Matches
- Chat History

---

### Analytics Views

- Recruitment Funnel
- Recruiter Performance
- Source Effectiveness
- Hiring Velocity
- Margin Analysis

---

## Database Standards

Naming Convention

- snake_case

Primary Keys

- table_name_id

Foreign Keys

- parent_table_id

Audit Columns

Every major table contains

- created_at
- updated_at
- created_by
- updated_by
- is_active

---

## Estimated Database Size

Companies: 200

Recruiters: 50

Jobs: 10,000

Candidates: 50,000

Applications: 100,000+

Interviews: 40,000

Offers: 15,000

Placements: 10,000

---

## Next Step

Each table will be designed individually before implementation in PostgreSQL.