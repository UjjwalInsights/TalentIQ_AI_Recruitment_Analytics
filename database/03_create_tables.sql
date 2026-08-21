/*
=====================================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 03_create_tables.sql

        Purpose:
        --------
        Creates the core relational database structure for
        TalentIQ's recruitment lifecycle.

        Recruitment Flow:

        COMPANY
           |
           ▼
        JOB
           |
           ▼
        CANDIDATE
           |
           ▼
        APPLICATION
           |
           ├────────► INTERVIEW
           |
           └────────► OFFER
                         |
                         ▼
                     PLACEMENT

        Master Tables:
        --------------
        1. companies
        2. recruiters
        3. departments
        4. locations
        5. sources
        6. skills
        7. work_authorizations

        Transaction Tables:
        -------------------
        8. candidates
        9. jobs
        10. applications
        11. interviews
        12. offers
        13. placements

        Mapping Tables:
        ---------------
        14. candidate_skills
        15. job_skills

=====================================================================
*/


/*
=====================================================================
SCHEMA CONFIGURATION
=====================================================================
*/

SET search_path TO recruitment;


/*
=====================================================================
TABLE 1 : COMPANIES
=====================================================================

Stores organizations involved in the recruitment ecosystem.

Examples:
- Apple
- JPMorgan Chase
- Wells Fargo
- Mphasis
- Capgemini
- HCL Technologies
- Recruitment Agencies
=====================================================================
*/

CREATE TABLE recruitment.companies
(
    company_id SERIAL PRIMARY KEY,

    company_name VARCHAR(200) NOT NULL UNIQUE,

    company_type VARCHAR(50) NOT NULL,

    industry VARCHAR(100),

    website VARCHAR(255),

    email VARCHAR(150),

    phone VARCHAR(30),

    city VARCHAR(100),

    state VARCHAR(100),

    country VARCHAR(100),

    employee_size INT,

    founded_year INT,

    notes TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================================
TABLE 2 : RECRUITERS
=====================================================================

Stores recruiters responsible for sourcing and managing candidates.
=====================================================================
*/

CREATE TABLE recruitment.recruiters
(
    recruiter_id SERIAL PRIMARY KEY,

    recruiter_name VARCHAR(150) NOT NULL,

    email VARCHAR(150) UNIQUE,

    phone VARCHAR(30),

    company_id INT,

    designation VARCHAR(100),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id)
        REFERENCES recruitment.companies(company_id)
);


/*
=====================================================================
TABLE 3 : DEPARTMENTS
=====================================================================

Stores departments within companies.

Examples:
- IT
- Analytics
- Engineering
- Finance
- Human Resources
=====================================================================
*/

CREATE TABLE recruitment.departments
(
    department_id SERIAL PRIMARY KEY,

    company_id INT NOT NULL,

    department_name VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id)
        REFERENCES recruitment.companies(company_id)
);


/*
=====================================================================
TABLE 4 : LOCATIONS
=====================================================================

Stores job locations.

Examples:
- New York
- Dallas
- Chicago
- Remote
- Bangalore
- Hyderabad
=====================================================================
*/

CREATE TABLE recruitment.locations
(
    location_id SERIAL PRIMARY KEY,

    city VARCHAR(100),

    state VARCHAR(100),

    country VARCHAR(100) NOT NULL,

    work_mode VARCHAR(30),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================================
TABLE 5 : SOURCES
=====================================================================

Recruitment sources used by recruiters.

Examples:
- LinkedIn
- Dice
- Monster
- Indeed
- CareerBuilder
- Referral
- Internal ATS
=====================================================================
*/

CREATE TABLE recruitment.sources
(
    source_id SERIAL PRIMARY KEY,

    source_name VARCHAR(100) NOT NULL UNIQUE,

    source_category VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================================
TABLE 6 : SKILLS
=====================================================================

Master list of technical and professional skills.

Examples:
- Python
- SQL
- Java
- AWS
- React
- Tableau
=====================================================================
*/

CREATE TABLE recruitment.skills
(
    skill_id SERIAL PRIMARY KEY,

    skill_name VARCHAR(100) NOT NULL UNIQUE,

    skill_category VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================================
TABLE 7 : WORK_AUTHORIZATIONS
=====================================================================

Stores work authorization categories commonly used in US IT
recruitment.

Examples:
- US Citizen
- Green Card
- H1B
- EAD
- TN
- OPT
- CPT
=====================================================================
*/

CREATE TABLE recruitment.work_authorizations
(
    work_authorization_id SERIAL PRIMARY KEY,

    authorization_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================================
TABLE 8 : CANDIDATES
=====================================================================

Stores candidate information.

Business Usage:
- Candidate analysis
- Source effectiveness
- Experience analysis
- Work authorization analysis
- Recruitment funnel
=====================================================================
*/

CREATE TABLE recruitment.candidates
(
    candidate_id SERIAL PRIMARY KEY,

    candidate_name VARCHAR(150) NOT NULL,

    email VARCHAR(150) UNIQUE,

    phone VARCHAR(30),

    experience_years INT,

    education VARCHAR(150),

    location_id INT,

    work_authorization_id INT,

    source_id INT,

    resume_path VARCHAR(500),

    applied_date DATE,

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (location_id)
        REFERENCES recruitment.locations(location_id),

    FOREIGN KEY (work_authorization_id)
        REFERENCES recruitment.work_authorizations(work_authorization_id),

    FOREIGN KEY (source_id)
        REFERENCES recruitment.sources(source_id)
);


/*
=====================================================================
TABLE 9 : JOBS
=====================================================================

Stores job requisitions received from clients / vendors.

This table represents the real-world recruiting requirement you
used to receive as a US IT Recruiter.

Important fields:
- Job ID
- Client
- Vendor
- Location
- Work Mode
- Bill Rate
- Required Experience
- Job Responsibilities
=====================================================================
*/

CREATE TABLE recruitment.jobs
(
    job_id SERIAL PRIMARY KEY,

    job_code VARCHAR(100) UNIQUE,

    job_title VARCHAR(150) NOT NULL,

    department_id INT,

    end_client_id INT NOT NULL,

    vendor_id INT,

    location_id INT,

    assigned_recruiter_id INT,

    experience_required INT,

    employment_type VARCHAR(50),

    work_mode VARCHAR(30),

    bill_rate NUMERIC(12,2),

    bill_rate_type VARCHAR(30),

    min_salary NUMERIC(12,2),

    max_salary NUMERIC(12,2),

    job_description TEXT,

    responsibilities TEXT,

    job_status VARCHAR(50),

    opened_date DATE,

    closed_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (department_id)
        REFERENCES recruitment.departments(department_id),

    FOREIGN KEY (end_client_id)
        REFERENCES recruitment.companies(company_id),

    FOREIGN KEY (vendor_id)
        REFERENCES recruitment.companies(company_id),

    FOREIGN KEY (location_id)
        REFERENCES recruitment.locations(location_id),

    FOREIGN KEY (assigned_recruiter_id)
        REFERENCES recruitment.recruiters(recruiter_id)
);


/*
=====================================================================
TABLE 10 : APPLICATIONS
=====================================================================

Bridge between candidates and jobs.

One candidate can apply to multiple jobs.
One job can have multiple candidates.
=====================================================================
*/

CREATE TABLE recruitment.applications
(
    application_id SERIAL PRIMARY KEY,

    candidate_id INT NOT NULL,

    job_id INT NOT NULL,

    recruiter_id INT,

    applied_date DATE,

    current_stage VARCHAR(50),

    status VARCHAR(50),

    submitted_to_client_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id)
        REFERENCES recruitment.candidates(candidate_id),

    FOREIGN KEY (job_id)
        REFERENCES recruitment.jobs(job_id),

    FOREIGN KEY (recruiter_id)
        REFERENCES recruitment.recruiters(recruiter_id),

    UNIQUE (candidate_id, job_id)
);


/*
=====================================================================
TABLE 11 : INTERVIEWS
=====================================================================

Stores interviews conducted for applications.
=====================================================================
*/

CREATE TABLE recruitment.interviews
(
    interview_id SERIAL PRIMARY KEY,

    application_id INT NOT NULL,

    interview_date TIMESTAMP,

    interviewer VARCHAR(150),

    interview_type VARCHAR(50),

    interview_round VARCHAR(50),

    outcome VARCHAR(50),

    feedback TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES recruitment.applications(application_id)
);


/*
=====================================================================
TABLE 12 : OFFERS
=====================================================================

Stores offers made to candidates.
=====================================================================
*/

CREATE TABLE recruitment.offers
(
    offer_id SERIAL PRIMARY KEY,

    application_id INT NOT NULL,

    offer_date DATE,

    offered_salary NUMERIC(12,2),

    offer_status VARCHAR(50),

    joining_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES recruitment.applications(application_id)
);


/*
=====================================================================
TABLE 13 : PLACEMENTS
=====================================================================

Represents successful recruitment outcomes.

This replaces the previous "employees" table.

A placement means the candidate successfully accepted an offer
and joined the organization.
=====================================================================
*/

CREATE TABLE recruitment.placements
(
    placement_id SERIAL PRIMARY KEY,

    offer_id INT NOT NULL,

    candidate_id INT NOT NULL,

    job_id INT NOT NULL,

    placement_date DATE,

    joining_date DATE,

    placement_status VARCHAR(50),

    department VARCHAR(100),

    designation VARCHAR(150),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (offer_id)
        REFERENCES recruitment.offers(offer_id),

    FOREIGN KEY (candidate_id)
        REFERENCES recruitment.candidates(candidate_id),

    FOREIGN KEY (job_id)
        REFERENCES recruitment.jobs(job_id)
);


/*
=====================================================================
TABLE 14 : CANDIDATE_SKILLS
=====================================================================

Mapping table between candidates and skills.

One candidate can have many skills.
One skill can belong to many candidates.
=====================================================================
*/

CREATE TABLE recruitment.candidate_skills
(
    candidate_id INT NOT NULL,

    skill_id INT NOT NULL,

    proficiency_level VARCHAR(50),

    years_experience NUMERIC(5,2),

    PRIMARY KEY (candidate_id, skill_id),

    FOREIGN KEY (candidate_id)
        REFERENCES recruitment.candidates(candidate_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES recruitment.skills(skill_id)
        ON DELETE CASCADE
);


/*
=====================================================================
TABLE 15 : JOB_SKILLS
=====================================================================

Mapping table between jobs and required skills.

Used to distinguish:

Must-have skills
Nice-to-have skills
=====================================================================
*/

CREATE TABLE recruitment.job_skills
(
    job_id INT NOT NULL,

    skill_id INT NOT NULL,

    priority VARCHAR(30),

    PRIMARY KEY (job_id, skill_id),

    FOREIGN KEY (job_id)
        REFERENCES recruitment.jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES recruitment.skills(skill_id)
        ON DELETE CASCADE
);


/*
=====================================================================
TABLE CREATION COMPLETED
=====================================================================

MASTER TABLES
--------------
✔ companies
✔ recruiters
✔ departments
✔ locations
✔ sources
✔ skills
✔ work_authorizations

TRANSACTION TABLES
------------------
✔ candidates
✔ jobs
✔ applications
✔ interviews
✔ offers
✔ placements

MAPPING TABLES
--------------
✔ candidate_skills
✔ job_skills

TOTAL TABLES: 15

=====================================================================
*/