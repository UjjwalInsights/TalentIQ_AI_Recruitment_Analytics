/*
=====================================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 04_constraints.sql

        Purpose:
        --------
        Adds business rules, validation rules, unique constraints,
        and foreign-key relationships to the TalentIQ database.

        Run AFTER:
        03_create_tables.sql

=====================================================================
*/

SET search_path TO recruitment;


/*
=====================================================================
1. COMPANIES
=====================================================================
*/

ALTER TABLE recruitment.companies

ADD CONSTRAINT chk_company_type
CHECK
(
    company_type IN
    (
        'End Client',
        'Implementation Partner',
        'Recruitment Agency',
        'Direct Client'
    )
),

ADD CONSTRAINT chk_employee_size
CHECK
(
    employee_size IS NULL
    OR employee_size > 0
),

ADD CONSTRAINT chk_founded_year
CHECK
(
    founded_year IS NULL
    OR founded_year <= EXTRACT(YEAR FROM CURRENT_DATE)
);


/*
=====================================================================
2. RECRUITERS
=====================================================================
*/

ALTER TABLE recruitment.recruiters

ADD CONSTRAINT fk_recruiter_company
FOREIGN KEY (company_id)
REFERENCES recruitment.companies(company_id);


/*
=====================================================================
3. DEPARTMENTS
=====================================================================
*/

ALTER TABLE recruitment.departments

ADD CONSTRAINT uq_department_company
UNIQUE
(
    company_id,
    department_name
);


/*
=====================================================================
4. LOCATIONS
=====================================================================
*/

ALTER TABLE recruitment.locations

ADD CONSTRAINT chk_work_mode
CHECK
(
    work_mode IS NULL
    OR work_mode IN
    (
        'Onsite',
        'Hybrid',
        'Remote'
    )
);


/*
=====================================================================
5. SOURCES
=====================================================================
*/

ALTER TABLE recruitment.sources

ADD CONSTRAINT chk_source_category
CHECK
(
    source_category IS NULL
    OR source_category IN
    (
        'Inbound',
        'Outbound',
        'Referral'
    )
);


/*
=====================================================================
6. SKILLS
=====================================================================
*/

ALTER TABLE recruitment.skills

ADD CONSTRAINT chk_skill_category
CHECK
(
    skill_category IS NULL
    OR skill_category IN
    (
        'Technical',
        'Tool',
        'Soft Skill',
        'Certification'
    )
);


/*
=====================================================================
7. WORK AUTHORIZATIONS
=====================================================================
*/


/*
No additional constraints required currently.

The UNIQUE constraint on authorization_name
was already created in 03_create_tables.sql.
*/


/*
=====================================================================
8. CANDIDATES
=====================================================================
*/

ALTER TABLE recruitment.candidates

ADD CONSTRAINT chk_candidate_experience
CHECK
(
    experience_years IS NULL
    OR experience_years >= 0
),

ADD CONSTRAINT chk_candidate_status
CHECK
(
    status IS NULL
    OR status IN
    (
        'Active',
        'Screening',
        'Interview',
        'Offer',
        'Hired',
        'Rejected',
        'Withdrawn'
    )
);


/*
=====================================================================
9. JOBS
=====================================================================
*/

ALTER TABLE recruitment.jobs

ADD CONSTRAINT chk_job_experience
CHECK
(
    experience_required IS NULL
    OR experience_required >= 0
),

ADD CONSTRAINT chk_employment_type
CHECK
(
    employment_type IS NULL
    OR employment_type IN
    (
        'Full-time',
        'Contract',
        'Contract-to-Hire',
        'Part-time'
    )
),

ADD CONSTRAINT chk_job_work_mode
CHECK
(
    work_mode IS NULL
    OR work_mode IN
    (
        'Onsite',
        'Hybrid',
        'Remote'
    )
),

ADD CONSTRAINT chk_bill_rate_type
CHECK
(
    bill_rate_type IS NULL
    OR bill_rate_type IN
    (
        'Hourly',
        'Annual'
    )
),

ADD CONSTRAINT chk_bill_rate
CHECK
(
    bill_rate IS NULL
    OR bill_rate >= 0
),

ADD CONSTRAINT chk_min_salary
CHECK
(
    min_salary IS NULL
    OR min_salary >= 0
),

ADD CONSTRAINT chk_max_salary
CHECK
(
    max_salary IS NULL
    OR max_salary >= 0
),

ADD CONSTRAINT chk_salary_range
CHECK
(
    min_salary IS NULL
    OR max_salary IS NULL
    OR max_salary >= min_salary
),

ADD CONSTRAINT chk_job_status
CHECK
(
    job_status IS NULL
    OR job_status IN
    (
        'Open',
        'On Hold',
        'Closed',
        'Filled',
        'Cancelled'
    )
);


/*
=====================================================================
10. APPLICATIONS
=====================================================================
*/

ALTER TABLE recruitment.applications

ADD CONSTRAINT chk_application_stage
CHECK
(
    current_stage IS NULL
    OR current_stage IN
    (
        'Applied',
        'Screening',
        'Submitted to Client',
        'Interview',
        'Offer',
        'Hired',
        'Rejected',
        'Withdrawn'
    )
),

ADD CONSTRAINT chk_application_status
CHECK
(
    status IS NULL
    OR status IN
    (
        'Active',
        'Rejected',
        'Withdrawn',
        'Hired'
    )
);


/*
=====================================================================
11. INTERVIEWS
=====================================================================
*/

ALTER TABLE recruitment.interviews

ADD CONSTRAINT chk_interview_type
CHECK
(
    interview_type IS NULL
    OR interview_type IN
    (
        'Phone Screen',
        'Technical',
        'Panel',
        'Client',
        'Final'
    )
),

ADD CONSTRAINT chk_interview_round
CHECK
(
    interview_round IS NULL
    OR interview_round IN
    (
        'Round 1',
        'Round 2',
        'Round 3',
        'Final'
    )
),

ADD CONSTRAINT chk_interview_outcome
CHECK
(
    outcome IS NULL
    OR outcome IN
    (
        'Passed',
        'Failed',
        'No Show',
        'Cancelled',
        'Pending'
    )
);


/*
=====================================================================
12. OFFERS
=====================================================================
*/

ALTER TABLE recruitment.offers

ADD CONSTRAINT chk_offered_salary
CHECK
(
    offered_salary IS NULL
    OR offered_salary >= 0
),

ADD CONSTRAINT chk_offer_status
CHECK
(
    offer_status IS NULL
    OR offer_status IN
    (
        'Extended',
        'Accepted',
        'Declined',
        'Rescinded',
        'Negotiating'
    )
);


/*
=====================================================================
13. PLACEMENTS
=====================================================================
*/

ALTER TABLE recruitment.placements

ADD CONSTRAINT chk_placement_status
CHECK
(
    placement_status IS NULL
    OR placement_status IN
    (
        'Active',
        'Fell Through',
        'Completed Guarantee Period'
    )
);


/*
=====================================================================
14. CANDIDATE SKILLS
=====================================================================
*/

ALTER TABLE recruitment.candidate_skills

ADD CONSTRAINT chk_proficiency_level
CHECK
(
    proficiency_level IS NULL
    OR proficiency_level IN
    (
        'Beginner',
        'Intermediate',
        'Advanced',
        'Expert'
    )
),

ADD CONSTRAINT chk_skill_years
CHECK
(
    years_experience IS NULL
    OR years_experience >= 0
);


/*
=====================================================================
15. JOB SKILLS
=====================================================================
*/

ALTER TABLE recruitment.job_skills

ADD CONSTRAINT chk_skill_priority
CHECK
(
    priority IN
    (
        'Must-have',
        'Nice-to-have'
    )
);


/*
=====================================================================
CONSTRAINTS COMPLETED
=====================================================================

Companies              ✔
Recruiters             ✔
Departments            ✔
Locations              ✔
Sources                ✔
Skills                 ✔
Candidates             ✔
Jobs                   ✔
Applications           ✔
Interviews             ✔
Offers                 ✔
Placements             ✔
Candidate Skills       ✔
Job Skills             ✔

=====================================================================
*/