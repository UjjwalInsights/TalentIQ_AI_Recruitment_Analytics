
/*==============================================================================
    TALENTIQ AI RECRUITMENT ANALYTICS
    SCRIPT: 13_dashboard_validation.sql

    PURPOSE
    -------
    Final validation of the Recruitment Analytics database and dashboard views
    before connecting the data to Tableau.

    VALIDATION AREAS
    ----------------
    1. Database Object Validation
    2. Row Count Validation
    3. Primary Key / Duplicate Validation
    4. NULL / Data Quality Validation
    5. Foreign Key Integrity Validation
    6. Applications & Recruitment Funnel Validation
    7. Offers & Placements Validation
    8. KPI Reconciliation
    9. Dashboard View Validation
    10. Dashboard Data Readiness Checks

    IMPORTANT
    ---------
    This script is READ-ONLY.

    It does NOT:
    - DROP tables
    - DELETE records
    - UPDATE records
    - ALTER tables
    - Recreate views

    It only validates the existing database.

==============================================================================*/

SET search_path TO recruitment;


/*==============================================================================
    SECTION 1
    DATABASE OBJECT VALIDATION
==============================================================================

    PURPOSE
    -------
    Confirm that all expected base tables and dashboard views exist.

==============================================================================*/


/*------------------------------------------------------------------------------
1.1 BASE TABLES
------------------------------------------------------------------------------*/

SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'recruitment'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;


/*------------------------------------------------------------------------------
1.2 DASHBOARD VIEWS
------------------------------------------------------------------------------*/

SELECT
    table_schema,
    table_name AS dashboard_view
FROM information_schema.views
WHERE table_schema = 'recruitment'
  AND table_name LIKE 'vw_dashboard_%'
ORDER BY table_name;


/*------------------------------------------------------------------------------
1.3 EXPECTED TABLE COUNT
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS base_table_count
FROM information_schema.tables
WHERE table_schema = 'recruitment'
  AND table_type = 'BASE TABLE';


/*------------------------------------------------------------------------------
1.4 EXPECTED DASHBOARD VIEW COUNT
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS dashboard_view_count
FROM information_schema.views
WHERE table_schema = 'recruitment'
  AND table_name LIKE 'vw_dashboard_%';


/*==============================================================================
    SECTION 2
    ROW COUNT VALIDATION

    PURPOSE
    -------
    Confirm that the main tables contain data and identify unexpected
    zero-row tables.

==============================================================================*/


SELECT
    'companies' AS table_name,
    COUNT(*) AS row_count
FROM companies

UNION ALL

SELECT
    'departments',
    COUNT(*)
FROM departments

UNION ALL

SELECT
    'locations',
    COUNT(*)
FROM locations

UNION ALL

SELECT
    'sources',
    COUNT(*)
FROM sources

UNION ALL

SELECT
    'skills',
    COUNT(*)
FROM skills

UNION ALL

SELECT
    'work_authorizations',
    COUNT(*)
FROM work_authorizations

UNION ALL

SELECT
    'recruiters',
    COUNT(*)
FROM recruiters

UNION ALL

SELECT
    'candidates',
    COUNT(*)
FROM candidates

UNION ALL

SELECT
    'candidate_skills',
    COUNT(*)
FROM candidate_skills

UNION ALL

SELECT
    'jobs',
    COUNT(*)
FROM jobs

UNION ALL

SELECT
    'job_skills',
    COUNT(*)
FROM job_skills

UNION ALL

SELECT
    'applications',
    COUNT(*)
FROM applications

UNION ALL

SELECT
    'interviews',
    COUNT(*)
FROM interviews

UNION ALL

SELECT
    'offers',
    COUNT(*)
FROM offers

UNION ALL

SELECT
    'placements',
    COUNT(*)
FROM placements

ORDER BY table_name;


/*==============================================================================
    SECTION 3
    PRIMARY KEY / DUPLICATE VALIDATION

    PURPOSE
    -------
    Confirm that primary identifiers are unique.

==============================================================================*/


/*------------------------------------------------------------------------------
3.1 COMPANIES
------------------------------------------------------------------------------*/

SELECT
    company_id,
    COUNT(*) AS duplicate_count
FROM companies
GROUP BY company_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.2 DEPARTMENTS
------------------------------------------------------------------------------*/

SELECT
    department_id,
    COUNT(*) AS duplicate_count
FROM departments
GROUP BY department_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.3 LOCATIONS
------------------------------------------------------------------------------*/

SELECT
    location_id,
    COUNT(*) AS duplicate_count
FROM locations
GROUP BY location_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.4 SOURCES
------------------------------------------------------------------------------*/

SELECT
    source_id,
    COUNT(*) AS duplicate_count
FROM sources
GROUP BY source_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.5 SKILLS
------------------------------------------------------------------------------*/

SELECT
    skill_id,
    COUNT(*) AS duplicate_count
FROM skills
GROUP BY skill_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.6 WORK AUTHORIZATIONS
------------------------------------------------------------------------------*/

SELECT
    work_authorization_id,
    COUNT(*) AS duplicate_count
FROM work_authorizations
GROUP BY work_authorization_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.7 RECRUITERS
------------------------------------------------------------------------------*/

SELECT
    recruiter_id,
    COUNT(*) AS duplicate_count
FROM recruiters
GROUP BY recruiter_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.8 CANDIDATES
------------------------------------------------------------------------------*/

SELECT
    candidate_id,
    COUNT(*) AS duplicate_count
FROM candidates
GROUP BY candidate_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.9 JOBS
------------------------------------------------------------------------------*/

SELECT
    job_id,
    COUNT(*) AS duplicate_count
FROM jobs
GROUP BY job_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.10 APPLICATIONS
------------------------------------------------------------------------------*/

SELECT
    application_id,
    COUNT(*) AS duplicate_count
FROM applications
GROUP BY application_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.11 INTERVIEWS
------------------------------------------------------------------------------*/

SELECT
    interview_id,
    COUNT(*) AS duplicate_count
FROM interviews
GROUP BY interview_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.12 OFFERS
------------------------------------------------------------------------------*/

SELECT
    offer_id,
    COUNT(*) AS duplicate_count
FROM offers
GROUP BY offer_id
HAVING COUNT(*) > 1;


/*------------------------------------------------------------------------------
3.13 PLACEMENTS
------------------------------------------------------------------------------*/

SELECT
    placement_id,
    COUNT(*) AS duplicate_count
FROM placements
GROUP BY placement_id
HAVING COUNT(*) > 1;


/*==============================================================================
    SECTION 4
    NULL / DATA QUALITY VALIDATION
==============================================================================*/


/*------------------------------------------------------------------------------
4.1 CANDIDATES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_candidates,

    COUNT(*) FILTER (
        WHERE candidate_name IS NULL
           OR TRIM(candidate_name) = ''
    ) AS missing_candidate_name,

    COUNT(*) FILTER (
        WHERE email IS NULL
           OR TRIM(email) = ''
    ) AS missing_email,

    COUNT(*) FILTER (
        WHERE experience_years IS NULL
    ) AS missing_experience,

    COUNT(*) FILTER (
        WHERE location_id IS NULL
    ) AS missing_location,

    COUNT(*) FILTER (
        WHERE work_authorization_id IS NULL
    ) AS missing_work_authorization,

    COUNT(*) FILTER (
        WHERE source_id IS NULL
    ) AS missing_source

FROM candidates;


/*------------------------------------------------------------------------------
4.2 JOBS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_jobs,

    COUNT(*) FILTER (
        WHERE job_title IS NULL
           OR TRIM(job_title) = ''
    ) AS missing_job_title,

    COUNT(*) FILTER (
        WHERE department_id IS NULL
    ) AS missing_department,

    COUNT(*) FILTER (
        WHERE location_id IS NULL
    ) AS missing_location,

    COUNT(*) FILTER (
        WHERE assigned_recruiter_id IS NULL
    ) AS missing_recruiter,

    COUNT(*) FILTER (
        WHERE opened_date IS NULL
    ) AS missing_opened_date,

    COUNT(*) FILTER (
        WHERE job_status IS NULL
           OR TRIM(job_status) = ''
    ) AS missing_job_status

FROM jobs;


/*------------------------------------------------------------------------------
4.3 APPLICATIONS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_applications,

    COUNT(*) FILTER (
        WHERE candidate_id IS NULL
    ) AS missing_candidate_id,

    COUNT(*) FILTER (
        WHERE job_id IS NULL
    ) AS missing_job_id,

    COUNT(*) FILTER (
        WHERE recruiter_id IS NULL
    ) AS missing_recruiter_id,

    COUNT(*) FILTER (
        WHERE applied_date IS NULL
    ) AS missing_applied_date,

    COUNT(*) FILTER (
        WHERE current_stage IS NULL
           OR TRIM(current_stage) = ''
    ) AS missing_current_stage,

    COUNT(*) FILTER (
        WHERE status IS NULL
           OR TRIM(status) = ''
    ) AS missing_status

FROM applications;


/*------------------------------------------------------------------------------
4.4 OFFERS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_offers,

    COUNT(*) FILTER (
        WHERE application_id IS NULL
    ) AS missing_application_id,

    COUNT(*) FILTER (
        WHERE offer_date IS NULL
    ) AS missing_offer_date,

    COUNT(*) FILTER (
        WHERE offered_salary IS NULL
    ) AS missing_salary,

    COUNT(*) FILTER (
        WHERE offer_status IS NULL
           OR TRIM(offer_status) = ''
    ) AS missing_offer_status

FROM offers;


/*------------------------------------------------------------------------------
4.5 PLACEMENTS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_placements,

    COUNT(*) FILTER (
        WHERE candidate_id IS NULL
    ) AS missing_candidate_id,

    COUNT(*) FILTER (
        WHERE job_id IS NULL
    ) AS missing_job_id,

    COUNT(*) FILTER (
        WHERE placement_date IS NULL
    ) AS missing_placement_date,

    COUNT(*) FILTER (
        WHERE placement_status IS NULL
           OR TRIM(placement_status) = ''
    ) AS missing_placement_status

FROM placements;


/*==============================================================================
    SECTION 5
    FOREIGN KEY / RELATIONSHIP VALIDATION

    PURPOSE
    -------
    Identify orphan records where child tables reference IDs that do not
    exist in their parent tables.
==============================================================================*/


/*------------------------------------------------------------------------------
5.1 APPLICATIONS → CANDIDATES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_applications_candidates
FROM applications a
LEFT JOIN candidates c
    ON a.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL;


/*------------------------------------------------------------------------------
5.2 APPLICATIONS → JOBS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_applications_jobs
FROM applications a
LEFT JOIN jobs j
    ON a.job_id = j.job_id
WHERE j.job_id IS NULL;


/*------------------------------------------------------------------------------
5.3 APPLICATIONS → RECRUITERS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_applications_recruiters
FROM applications a
LEFT JOIN recruiters r
    ON a.recruiter_id = r.recruiter_id
WHERE r.recruiter_id IS NULL;


/*------------------------------------------------------------------------------
5.4 INTERVIEWS → APPLICATIONS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_interviews
FROM interviews i
LEFT JOIN applications a
    ON i.application_id = a.application_id
WHERE a.application_id IS NULL;


/*------------------------------------------------------------------------------
5.5 OFFERS → APPLICATIONS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_offers
FROM offers o
LEFT JOIN applications a
    ON o.application_id = a.application_id
WHERE a.application_id IS NULL;


/*------------------------------------------------------------------------------
5.6 PLACEMENTS → OFFERS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_placements_offers
FROM placements p
LEFT JOIN offers o
    ON p.offer_id = o.offer_id
WHERE o.offer_id IS NULL;


/*------------------------------------------------------------------------------
5.7 PLACEMENTS → CANDIDATES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_placements_candidates
FROM placements p
LEFT JOIN candidates c
    ON p.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL;


/*------------------------------------------------------------------------------
5.8 PLACEMENTS → JOBS
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS orphan_placements_jobs
FROM placements p
LEFT JOIN jobs j
    ON p.job_id = j.job_id
WHERE j.job_id IS NULL;


/*==============================================================================
    SECTION 6
    APPLICATION / RECRUITMENT FUNNEL VALIDATION

    IMPORTANT
    ---------
    Your schema uses:

        applications.current_stage
        applications.status

    Do NOT use "application_status".
==============================================================================*/


/*------------------------------------------------------------------------------
6.1 CURRENT STAGE DISTRIBUTION
------------------------------------------------------------------------------*/

SELECT
    current_stage,
    COUNT(*) AS application_count,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage_of_total

FROM applications

GROUP BY current_stage

ORDER BY application_count DESC;


/*------------------------------------------------------------------------------
6.2 APPLICATION STATUS DISTRIBUTION
------------------------------------------------------------------------------*/

SELECT
    status,
    COUNT(*) AS application_count,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage_of_total

FROM applications

GROUP BY status

ORDER BY application_count DESC;


/*------------------------------------------------------------------------------
6.3 APPLICATIONS BY RECRUITER
------------------------------------------------------------------------------*/

SELECT
    a.recruiter_id,
    r.recruiter_name,

    COUNT(*) AS total_applications,

    COUNT(*) FILTER (
        WHERE a.current_stage = 'Screening'
    ) AS screening_count,

    COUNT(*) FILTER (
        WHERE a.current_stage = 'Interview'
    ) AS interview_count,

    COUNT(*) FILTER (
        WHERE a.current_stage = 'Offer'
    ) AS offer_count,

    COUNT(*) FILTER (
        WHERE a.current_stage = 'Hired'
    ) AS hired_count

FROM applications a

LEFT JOIN recruiters r
    ON a.recruiter_id = r.recruiter_id

GROUP BY
    a.recruiter_id,
    r.recruiter_name

ORDER BY total_applications DESC;


/*==============================================================================
    SECTION 7
    INTERVIEW VALIDATION
==============================================================================*/


/*------------------------------------------------------------------------------
7.1 INTERVIEW OUTCOMES
------------------------------------------------------------------------------*/

SELECT
    outcome,
    COUNT(*) AS interview_count,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage

FROM interviews

GROUP BY outcome

ORDER BY interview_count DESC;


/*------------------------------------------------------------------------------
7.2 INTERVIEW TYPES
------------------------------------------------------------------------------*/

SELECT
    interview_type,
    COUNT(*) AS interview_count
FROM interviews
GROUP BY interview_type
ORDER BY interview_count DESC;


/*------------------------------------------------------------------------------
7.3 INTERVIEW ROUNDS
------------------------------------------------------------------------------*/

SELECT
    interview_round,
    COUNT(*) AS interview_count
FROM interviews
GROUP BY interview_round
ORDER BY interview_count DESC;


/*==============================================================================
    SECTION 8
    OFFER VALIDATION
==============================================================================*/


/*------------------------------------------------------------------------------
8.1 OFFER STATUS
------------------------------------------------------------------------------*/

SELECT
    offer_status,
    COUNT(*) AS offer_count,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage

FROM offers

GROUP BY offer_status

ORDER BY offer_count DESC;


/*------------------------------------------------------------------------------
8.2 SALARY VALIDATION
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS total_offers,

    ROUND(MIN(offered_salary), 2) AS minimum_offer,

    ROUND(MAX(offered_salary), 2) AS maximum_offer,

    ROUND(AVG(offered_salary), 2) AS average_offer,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY offered_salary
        ),
        2
    ) AS median_offer

FROM offers;


/*------------------------------------------------------------------------------
8.3 INVALID NEGATIVE SALARIES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS negative_salary_records
FROM offers
WHERE offered_salary < 0;


/*==============================================================================
    SECTION 9
    PLACEMENT VALIDATION
==============================================================================*/


/*------------------------------------------------------------------------------
9.1 PLACEMENT STATUS
------------------------------------------------------------------------------*/

SELECT
    placement_status,
    COUNT(*) AS placement_count,

    ROUND(
        COUNT(*) * 100.0 /
        NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage

FROM placements

GROUP BY placement_status

ORDER BY placement_count DESC;


/*------------------------------------------------------------------------------
9.2 PLACEMENT TIMING
------------------------------------------------------------------------------*/

SELECT

    COUNT(*) AS total_placements,

    ROUND(
        AVG(
            (joining_date - placement_date)::numeric
        ),
        2
    ) AS avg_days_placement_to_joining,

    MIN(
        joining_date - placement_date
    ) AS minimum_days,

    MAX(
        joining_date - placement_date
    ) AS maximum_days

FROM placements

WHERE placement_date IS NOT NULL
  AND joining_date IS NOT NULL;


/*------------------------------------------------------------------------------
9.3 INVALID PLACEMENT DATES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS invalid_placement_dates

FROM placements

WHERE joining_date IS NOT NULL
  AND placement_date IS NOT NULL
  AND joining_date < placement_date;


/*==============================================================================
    SECTION 10
    EXECUTIVE KPI RECONCILIATION

    PURPOSE
    -------
    Independently calculate the major KPIs and compare them with the
    executive dashboard view.

==============================================================================*/


/*------------------------------------------------------------------------------
10.1 RAW KPI CALCULATION
------------------------------------------------------------------------------*/

WITH raw_kpis AS (

    SELECT

        (SELECT COUNT(*)
         FROM jobs)
        AS total_jobs,

        (SELECT COUNT(*)
         FROM jobs
         WHERE LOWER(job_status) = 'open')
        AS open_jobs,

        (SELECT COUNT(*)
         FROM candidates)
        AS total_candidates,

        (SELECT COUNT(*)
         FROM applications)
        AS total_applications,

        (SELECT COUNT(*)
         FROM offers)
        AS total_offers,

        (SELECT COUNT(*)
         FROM placements)
        AS total_placements,

        (SELECT COUNT(*)
         FROM applications
         WHERE LOWER(status) NOT IN
             ('rejected', 'withdrawn', 'hired'))
        AS active_applications,

        (SELECT COUNT(*)
         FROM applications
         WHERE LOWER(status) = 'rejected')
        AS rejected_applications,

        (SELECT COUNT(*)
         FROM applications
         WHERE LOWER(status) = 'withdrawn')
        AS withdrawn_applications,

        (SELECT COUNT(*)
         FROM applications
         WHERE LOWER(status) = 'hired')
        AS hired_applications
)

SELECT *
FROM raw_kpis;


/*------------------------------------------------------------------------------
10.2 DASHBOARD KPI VIEW
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_executive_kpis;


/*------------------------------------------------------------------------------
10.3 KPI RECONCILIATION

    This query compares the raw calculations with the dashboard view.
------------------------------------------------------------------------------*/

WITH raw_kpis AS (

    SELECT

        (SELECT COUNT(*)
         FROM jobs)
        AS total_jobs,

        (SELECT COUNT(*)
         FROM jobs
         WHERE LOWER(job_status) = 'open')
        AS open_jobs,

        (SELECT COUNT(*)
         FROM candidates)
        AS total_candidates,

        (SELECT COUNT(*)
         FROM applications)
        AS total_applications,

        (SELECT COUNT(*)
         FROM offers)
        AS total_offers,

        (SELECT COUNT(*)
         FROM placements)
        AS total_placements

),

dashboard_kpis AS (

    SELECT
        total_jobs,
        open_jobs,
        total_candidates,
        total_applications,
        total_offers,
        total_placements

    FROM vw_dashboard_executive_kpis
)

SELECT
    r.total_jobs,
    d.total_jobs AS dashboard_total_jobs,
    r.total_jobs = d.total_jobs AS total_jobs_match,

    r.open_jobs,
    d.open_jobs AS dashboard_open_jobs,
    r.open_jobs = d.open_jobs AS open_jobs_match,

    r.total_candidates,
    d.total_candidates AS dashboard_total_candidates,
    r.total_candidates = d.total_candidates AS total_candidates_match,

    r.total_applications,
    d.total_applications AS dashboard_total_applications,
    r.total_applications = d.total_applications AS total_applications_match,

    r.total_offers,
    d.total_offers AS dashboard_total_offers,
    r.total_offers = d.total_offers AS total_offers_match,

    r.total_placements,
    d.total_placements AS dashboard_total_placements,
    r.total_placements = d.total_placements AS total_placements_match

FROM raw_kpis r
CROSS JOIN dashboard_kpis d;


/*==============================================================================
    SECTION 11
    DASHBOARD VIEW VALIDATION

    PURPOSE
    -------
    Make sure every dashboard view returns usable data.
==============================================================================*/


/*------------------------------------------------------------------------------
11.1 EXECUTIVE KPIs
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_executive_kpis;


/*------------------------------------------------------------------------------
11.2 RECRUITMENT FUNNEL
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_recruitment_funnel
ORDER BY application_count DESC;


/*------------------------------------------------------------------------------
11.3 APPLICATION STATUS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_application_status
ORDER BY application_count DESC;


/*------------------------------------------------------------------------------
11.4 TIME TRENDS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_time_trends
ORDER BY month;


/*------------------------------------------------------------------------------
11.5 JOB PERFORMANCE
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_job_performance
ORDER BY total_applications DESC
LIMIT 20;


/*------------------------------------------------------------------------------
11.6 JOB AGING
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_job_aging
ORDER BY job_age_days DESC
LIMIT 20;


/*------------------------------------------------------------------------------
11.7 RECRUITER PERFORMANCE
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_recruiter_performance
ORDER BY placement_count DESC;


/*------------------------------------------------------------------------------
11.8 CANDIDATE ANALYSIS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_candidate_analysis
ORDER BY total_applications DESC
LIMIT 20;


/*------------------------------------------------------------------------------
11.9 CLIENT ANALYSIS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_client_analysis
ORDER BY total_placements DESC;


/*------------------------------------------------------------------------------
11.10 PLACEMENT ANALYSIS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_placement_analysis
ORDER BY placement_date DESC
LIMIT 20;


/*------------------------------------------------------------------------------
11.11 SALARY ANALYSIS
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_salary_analysis
ORDER BY offered_salary DESC
LIMIT 20;


/*------------------------------------------------------------------------------
11.12 MASTER DASHBOARD VIEW
------------------------------------------------------------------------------*/

SELECT *
FROM vw_dashboard_master
LIMIT 20;


/*==============================================================================
    SECTION 12
    DASHBOARD VIEW ROW COUNTS

    PURPOSE
    -------
    Identify empty dashboard views before Tableau connection.
==============================================================================*/


SELECT
    'vw_dashboard_executive_kpis' AS view_name,
    COUNT(*) AS row_count
FROM vw_dashboard_executive_kpis

UNION ALL

SELECT
    'vw_dashboard_recruitment_funnel',
    COUNT(*)
FROM vw_dashboard_recruitment_funnel

UNION ALL

SELECT
    'vw_dashboard_application_status',
    COUNT(*)
FROM vw_dashboard_application_status

UNION ALL

SELECT
    'vw_dashboard_time_trends',
    COUNT(*)
FROM vw_dashboard_time_trends

UNION ALL

SELECT
    'vw_dashboard_job_performance',
    COUNT(*)
FROM vw_dashboard_job_performance

UNION ALL

SELECT
    'vw_dashboard_job_aging',
    COUNT(*)
FROM vw_dashboard_job_aging

UNION ALL

SELECT
    'vw_dashboard_recruiter_performance',
    COUNT(*)
FROM vw_dashboard_recruiter_performance

UNION ALL

SELECT
    'vw_dashboard_candidate_analysis',
    COUNT(*)
FROM vw_dashboard_candidate_analysis

UNION ALL

SELECT
    'vw_dashboard_client_analysis',
    COUNT(*)
FROM vw_dashboard_client_analysis

UNION ALL

SELECT
    'vw_dashboard_placement_analysis',
    COUNT(*)
FROM vw_dashboard_placement_analysis

UNION ALL

SELECT
    'vw_dashboard_salary_analysis',
    COUNT(*)
FROM vw_dashboard_salary_analysis

UNION ALL

SELECT
    'vw_dashboard_master',
    COUNT(*)
FROM vw_dashboard_master

ORDER BY view_name;


/*==============================================================================
    SECTION 13
    DASHBOARD DATA QUALITY CHECKS
==============================================================================*/


/*------------------------------------------------------------------------------
13.1 FUNNEL PERCENTAGES
------------------------------------------------------------------------------*/

SELECT
    current_stage,
    application_count,
    percentage_of_total

FROM vw_dashboard_recruitment_funnel

ORDER BY application_count DESC;


/*------------------------------------------------------------------------------
13.2 CHECK FOR NEGATIVE / INVALID FUNNEL PERCENTAGES
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS invalid_percentage_records

FROM vw_dashboard_recruitment_funnel

WHERE percentage_of_total < 0
   OR percentage_of_total > 100;


/*------------------------------------------------------------------------------
13.3 JOB AGING VALIDATION
------------------------------------------------------------------------------*/

SELECT
    aging_bucket,
    COUNT(*) AS jobs

FROM vw_dashboard_job_aging

GROUP BY aging_bucket

ORDER BY jobs DESC;


/*------------------------------------------------------------------------------
13.4 RECRUITER PERFORMANCE VALIDATION
------------------------------------------------------------------------------*/

SELECT
    COUNT(*) AS recruiters,

    COUNT(*) FILTER (
        WHERE hire_rate < 0
           OR hire_rate > 100
    ) AS invalid_hire_rates,

    COUNT(*) FILTER (
        WHERE placement_rate < 0
           OR placement_rate > 100
    ) AS invalid_placement_rates

FROM vw_dashboard_recruiter_performance;


/*------------------------------------------------------------------------------
13.5 SALARY POSITION VALIDATION
------------------------------------------------------------------------------*/

SELECT
    salary_position,
    COUNT(*) AS offer_count

FROM vw_dashboard_salary_analysis

GROUP BY salary_position

ORDER BY offer_count DESC;


/*==============================================================================
    SECTION 14
    DATE RANGE VALIDATION
==============================================================================*/


/*------------------------------------------------------------------------------
14.1 APPLICATION DATE RANGE
------------------------------------------------------------------------------*/

SELECT
    MIN(applied_date) AS first_application_date,
    MAX(applied_date) AS latest_application_date
FROM applications;


/*------------------------------------------------------------------------------
14.2 JOB DATE RANGE
------------------------------------------------------------------------------*/

SELECT
    MIN(opened_date) AS first_job_opened,
    MAX(opened_date) AS latest_job_opened
FROM jobs;


/*------------------------------------------------------------------------------
14.3 OFFER DATE RANGE
------------------------------------------------------------------------------*/

SELECT
    MIN(offer_date) AS first_offer_date,
    MAX(offer_date) AS latest_offer_date
FROM offers;


/*------------------------------------------------------------------------------
14.4 PLACEMENT DATE RANGE
------------------------------------------------------------------------------*/

SELECT
    MIN(placement_date) AS first_placement_date,
    MAX(placement_date) AS latest_placement_date
FROM placements;


/*==============================================================================
    SECTION 15
    FINAL DATA QUALITY SUMMARY

    PURPOSE
    -------
    Produce a compact final health check.

==============================================================================*/


SELECT
    'Candidates' AS metric,
    COUNT(*) AS total_records
FROM candidates

UNION ALL

SELECT
    'Jobs',
    COUNT(*)
FROM jobs

UNION ALL

SELECT
    'Applications',
    COUNT(*)
FROM applications

UNION ALL

SELECT
    'Interviews',
    COUNT(*)
FROM interviews

UNION ALL

SELECT
    'Offers',
    COUNT(*)
FROM offers

UNION ALL

SELECT
    'Placements',
    COUNT(*)
FROM placements;


/*==============================================================================
    SECTION 16
    FINAL VALIDATION CHECKLIST
==============================================================================

    EXPECTED RESULTS
    ----------------

    1. Base tables exist
       → PASS

    2. Dashboard views exist
       → PASS

    3. Primary key duplicate queries return zero rows
       → PASS

    4. Orphan foreign-key queries return zero
       → PASS

    5. Critical NULL checks are zero or explainable
       → PASS / REVIEW

    6. Applications have valid current_stage and status values
       → REVIEW DISTRIBUTION

    7. Offers have valid salaries
       → PASS

    8. Placements have valid dates
       → PASS

    9. Executive KPI values match the dashboard view
       → ALL *_MATCH columns should be TRUE

    10. Dashboard views return data
        → PASS

    11. Funnel percentages remain between 0 and 100
        → PASS

    12. Recruiter hire/placement rates remain between 0 and 100
        → PASS

    13. Date ranges are reasonable
        → PASS

==============================================================================*/


/*==============================================================================
    END OF 13_dashboard_validation.sql

    NEXT PROJECT STAGE
    ------------------

    If the validation results are clean:

        DATABASE
           ↓
        ANALYTICS SQL
           ↓
        DASHBOARD VIEWS
           ↓
        VALIDATION  ← YOU ARE HERE
           ↓
        TABLEAU DATA CONNECTION
           ↓
        EXECUTIVE DASHBOARD
           ↓
        RECRUITMENT FUNNEL DASHBOARD
           ↓
        RECRUITER PERFORMANCE DASHBOARD
           ↓
        CANDIDATE / CLIENT ANALYTICS
           ↓
        AI RECRUITMENT ASSISTANT

==============================================================================*/
