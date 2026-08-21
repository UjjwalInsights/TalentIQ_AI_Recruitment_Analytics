/*
===============================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM
File: 12_dashboard_views.sql

Purpose:
Create Tableau-ready PostgreSQL views for the
Recruitment Analytics Executive Dashboard.

Database:
PostgreSQL

Schema:
recruitment

Source Tables:
    applications
    candidates
    jobs
    offers
    placements

Dashboard Layer:
    PostgreSQL Views → Tableau

Synthetic Dataset Reporting Snapshot:
    2026-12-31

IMPORTANT:
    Because the project uses synthetic recruitment data extending
    through December 2026, all "current age" calculations use
    DATE '2026-12-31' instead of CURRENT_DATE.

===============================================================
*/


-- =============================================================
-- 0. SET SCHEMA
-- =============================================================

SET search_path TO recruitment;


-- =============================================================
-- 1. EXECUTIVE KPI VIEW
-- =============================================================
-- Purpose:
-- One-row executive summary containing the major recruitment KPIs.
-- This view will power KPI cards in Tableau.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_executive_kpis AS

SELECT

    /* ---------------------------------------------------------
       CORE VOLUME
       --------------------------------------------------------- */

    (SELECT COUNT(*)
     FROM jobs) AS total_jobs,

    (SELECT COUNT(*)
     FROM jobs
     WHERE LOWER(job_status) = 'open') AS open_jobs,

    (SELECT COUNT(*)
     FROM candidates) AS total_candidates,

    (SELECT COUNT(*)
     FROM applications) AS total_applications,

    (SELECT COUNT(*)
     FROM offers) AS total_offers,

    (SELECT COUNT(*)
     FROM placements) AS total_placements,


    /* ---------------------------------------------------------
       APPLICATION STATUS
       --------------------------------------------------------- */

    (SELECT COUNT(*)
     FROM applications
     WHERE LOWER(status) = 'active') AS active_applications,

    (SELECT COUNT(*)
     FROM applications
     WHERE LOWER(status) = 'rejected') AS rejected_applications,

    (SELECT COUNT(*)
     FROM applications
     WHERE LOWER(status) = 'withdrawn') AS withdrawn_applications,

    (SELECT COUNT(*)
     FROM applications
     WHERE LOWER(status) = 'hired') AS hired_applications,


    /* ---------------------------------------------------------
       CONVERSION METRICS
       --------------------------------------------------------- */

    ROUND(
        100.0 *
        (SELECT COUNT(*)
         FROM offers)
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM applications),
            0
        ),
        2
    ) AS application_to_offer_rate,


    ROUND(
        100.0 *
        (SELECT COUNT(*)
         FROM placements)
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM applications),
            0
        ),
        2
    ) AS application_to_placement_rate,


    ROUND(
        100.0 *
        (SELECT COUNT(*)
         FROM placements)
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM offers),
            0
        ),
        2
    ) AS offer_to_placement_rate,


    /* ---------------------------------------------------------
       TIME METRICS
       --------------------------------------------------------- */

    ROUND(
        AVG(
            CASE
                WHEN p.placement_date IS NOT NULL
                 AND a.applied_date IS NOT NULL
                THEN
                    p.placement_date - a.applied_date
            END
        ),
        2
    ) AS avg_days_to_placement


FROM applications a

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id;



-- =============================================================
-- 2. RECRUITMENT FUNNEL VIEW
-- =============================================================
-- Purpose:
-- Provides stage-level recruitment funnel metrics.
-- Tableau can use this for a funnel chart.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_recruitment_funnel AS

SELECT
    current_stage,
    COUNT(*) AS application_count,

    ROUND(
        100.0 * COUNT(*)
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM applications),
            0
        ),
        2
    ) AS percentage_of_total

FROM applications

GROUP BY current_stage

ORDER BY application_count DESC;



-- =============================================================
-- 3. APPLICATION STATUS VIEW
-- =============================================================
-- Purpose:
-- Shows active, rejected, withdrawn and hired applications.
-- Useful for status distribution charts.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_application_status AS

SELECT
    status,
    COUNT(*) AS application_count,

    ROUND(
        100.0 * COUNT(*)
        /
        NULLIF(
            SUM(COUNT(*)) OVER (),
            0
        ),
        2
    ) AS percentage_of_total

FROM applications

GROUP BY status

ORDER BY application_count DESC;



-- =============================================================
-- 4. JOB PERFORMANCE VIEW
-- =============================================================
-- Purpose:
-- Measures application and hiring performance for every job.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_job_performance AS

SELECT

    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status,

    j.opened_date,
    j.closed_date,

    j.department_id,
    j.end_client_id,
    j.vendor_id,
    j.location_id,
    j.assigned_recruiter_id,

    j.experience_required,
    j.employment_type,
    j.work_mode,

    j.bill_rate,
    j.bill_rate_type,

    j.min_salary,
    j.max_salary,


    /* ---------------------------------------------------------
       APPLICATION METRICS
       --------------------------------------------------------- */

    COUNT(DISTINCT a.application_id)
        AS total_applications,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'screening'
            THEN a.application_id
        END
    ) AS screening_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'submitted to client'
            THEN a.application_id
        END
    ) AS submitted_to_client_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'interview'
            THEN a.application_id
        END
    ) AS interview_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'offer'
            THEN a.application_id
        END
    ) AS offer_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'hired'
            THEN a.application_id
        END
    ) AS hired_count,


    /* ---------------------------------------------------------
       PLACEMENT
       --------------------------------------------------------- */

    COUNT(
        DISTINCT p.placement_id
    ) AS placement_count,


    /* ---------------------------------------------------------
       APPLICATION → PLACEMENT
       --------------------------------------------------------- */

    ROUND(
        100.0 *
        COUNT(DISTINCT p.placement_id)
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        ),
        2
    ) AS application_to_placement_rate,


    /* ---------------------------------------------------------
       JOB AGE

       Closed jobs:
           closed_date - opened_date

       Open / On Hold jobs:
           snapshot_date - opened_date

       Synthetic snapshot date:
           2026-12-31
       --------------------------------------------------------- */

    CASE

        WHEN j.opened_date IS NULL
        THEN NULL

        WHEN j.closed_date IS NOT NULL
        THEN j.closed_date - j.opened_date

        ELSE DATE '2026-12-31' - j.opened_date

    END AS job_age_days,


    /* ---------------------------------------------------------
       JOB AGING BUCKET
       --------------------------------------------------------- */

    CASE

        WHEN j.opened_date IS NULL
        THEN NULL

        WHEN
            CASE
                WHEN j.closed_date IS NOT NULL
                THEN j.closed_date - j.opened_date
                ELSE DATE '2026-12-31' - j.opened_date
            END >= 90
        THEN '90+ DAYS'

        WHEN
            CASE
                WHEN j.closed_date IS NOT NULL
                THEN j.closed_date - j.opened_date
                ELSE DATE '2026-12-31' - j.opened_date
            END >= 60
        THEN '60-89 DAYS'

        WHEN
            CASE
                WHEN j.closed_date IS NOT NULL
                THEN j.closed_date - j.opened_date
                ELSE DATE '2026-12-31' - j.opened_date
            END >= 30
        THEN '30-59 DAYS'

        ELSE '0-29 DAYS'

    END AS aging_bucket


FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status,
    j.opened_date,
    j.closed_date,
    j.department_id,
    j.end_client_id,
    j.vendor_id,
    j.location_id,
    j.assigned_recruiter_id,
    j.experience_required,
    j.employment_type,
    j.work_mode,
    j.bill_rate,
    j.bill_rate_type,
    j.min_salary,
    j.max_salary;



-- =============================================================
-- 5. JOB AGING VIEW
-- =============================================================
-- Purpose:
-- Provides job-aging metrics.
--
-- NOTE:
-- All job statuses are intentionally retained so the existing
-- dashboard row structure remains unchanged.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_job_aging AS

SELECT

    job_id,
    job_code,
    job_title,
    job_status,
    opened_date,
    closed_date,

    job_age_days,
    aging_bucket,

    total_applications,
    offer_count,
    hired_count,
    placement_count,

    application_to_placement_rate

FROM vw_dashboard_job_performance

ORDER BY job_age_days DESC;



-- =============================================================
-- 6. RECRUITER PERFORMANCE VIEW
-- =============================================================
-- Purpose:
-- Measures recruiter-level productivity and conversion.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_recruiter_performance AS

SELECT

    a.recruiter_id,

    COUNT(DISTINCT a.application_id)
        AS total_applications,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'screening'
            THEN a.application_id
        END
    ) AS screening_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'submitted to client'
            THEN a.application_id
        END
    ) AS submitted_to_client_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'interview'
            THEN a.application_id
        END
    ) AS interview_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'offer'
            THEN a.application_id
        END
    ) AS offer_count,

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'hired'
            THEN a.application_id
        END
    ) AS hired_count,

    COUNT(
        DISTINCT p.placement_id
    ) AS placement_count,


    /* ---------------------------------------------------------
       CONVERSION
       --------------------------------------------------------- */

    ROUND(
        100.0 *
        COUNT(
            DISTINCT CASE
                WHEN LOWER(a.status) = 'hired'
                THEN a.application_id
            END
        )
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        ),
        2
    ) AS hire_rate,


    ROUND(
        100.0 *
        COUNT(DISTINCT p.placement_id)
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        ),
        2
    ) AS placement_rate,


    /* ---------------------------------------------------------
       AVERAGE APPLICATION AGE

       Synthetic snapshot date:
           2026-12-31
       --------------------------------------------------------- */

    ROUND(
        AVG(
            DATE '2026-12-31' - a.applied_date
        ),
        2
    ) AS avg_application_age_days


FROM applications a

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    a.recruiter_id

ORDER BY
    placement_count DESC,
    hire_rate DESC;



-- =============================================================
-- 7. TIME TREND VIEW
-- =============================================================
-- Purpose:
-- Monthly recruitment performance.
-- Tableau can use this for line and area charts.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_time_trends AS

SELECT

    DATE_TRUNC(
        'month',
        a.applied_date
    )::date AS month,


    /* ---------------------------------------------------------
       APPLICATIONS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT a.application_id
    ) AS applications,


    /* ---------------------------------------------------------
       SCREENING
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'screening'
            THEN a.application_id
        END
    ) AS screening,


    /* ---------------------------------------------------------
       CLIENT SUBMISSIONS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'submitted to client'
            THEN a.application_id
        END
    ) AS submitted_to_client,


    /* ---------------------------------------------------------
       INTERVIEWS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'interview'
            THEN a.application_id
        END
    ) AS interviews,


    /* ---------------------------------------------------------
       OFFERS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT o.offer_id
    ) AS offers,


    /* ---------------------------------------------------------
       HIRES
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'hired'
            THEN a.application_id
        END
    ) AS hires,


    /* ---------------------------------------------------------
       PLACEMENTS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT p.placement_id
    ) AS placements


FROM applications a

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

WHERE a.applied_date IS NOT NULL

GROUP BY
    DATE_TRUNC(
        'month',
        a.applied_date
    )::date

ORDER BY
    month;



-- =============================================================
-- 8. SALARY ANALYSIS VIEW
-- =============================================================
-- Purpose:
-- Compare offered salary with job salary range.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_salary_analysis AS

SELECT

    o.offer_id,
    o.application_id,
    o.offer_date,
    o.offered_salary,
    o.offer_status,
    o.joining_date,

    a.candidate_id,
    a.job_id,


    /* ---------------------------------------------------------
       JOB INFORMATION
       --------------------------------------------------------- */

    j.job_title,
    j.min_salary,
    j.max_salary,


    /* ---------------------------------------------------------
       SALARY POSITION
       --------------------------------------------------------- */

    CASE

        WHEN o.offered_salary < j.min_salary
        THEN 'BELOW RANGE'

        WHEN o.offered_salary > j.max_salary
        THEN 'ABOVE RANGE'

        ELSE 'WITHIN RANGE'

    END AS salary_position,


    /* ---------------------------------------------------------
       DIFFERENCE FROM MIDPOINT
       --------------------------------------------------------- */

    ROUND(
        o.offered_salary
        -
        (
            (j.min_salary + j.max_salary) / 2
        ),
        2
    ) AS difference_from_salary_midpoint,


    /* ---------------------------------------------------------
       OFFER STATUS
       --------------------------------------------------------- */

    o.offer_status AS final_offer_status


FROM offers o

LEFT JOIN applications a
    ON o.application_id = a.application_id

LEFT JOIN jobs j
    ON a.job_id = j.job_id;



-- =============================================================
-- 9. PLACEMENT ANALYSIS VIEW
-- =============================================================
-- Purpose:
-- Provides placement-level metrics for Tableau.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_placement_analysis AS

SELECT

    p.placement_id,

    p.offer_id,
    p.candidate_id,
    p.job_id,

    p.placement_date,
    p.joining_date,

    p.placement_status,

    p.department,
    p.designation,


    /* ---------------------------------------------------------
       JOB INFORMATION
       --------------------------------------------------------- */

    j.job_code,
    j.job_title,
    j.job_status,
    j.department_id,
    j.end_client_id,
    j.vendor_id,
    j.location_id,
    j.assigned_recruiter_id,


    /* ---------------------------------------------------------
       OFFER INFORMATION
       --------------------------------------------------------- */

    o.offer_date,
    o.offered_salary,
    o.offer_status,


    /* ---------------------------------------------------------
       TIME TO PLACEMENT
       --------------------------------------------------------- */

    CASE

        WHEN a.applied_date IS NOT NULL
         AND p.placement_date IS NOT NULL

        THEN p.placement_date - a.applied_date

    END AS days_to_placement,


    /* ---------------------------------------------------------
       TIME TO JOINING
       --------------------------------------------------------- */

    CASE

        WHEN p.placement_date IS NOT NULL
         AND p.joining_date IS NOT NULL

        THEN p.joining_date - p.placement_date

    END AS days_from_placement_to_joining,


    /* ---------------------------------------------------------
       PLACEMENT OUTCOME
       --------------------------------------------------------- */

    CASE

        WHEN LOWER(p.placement_status)
             IN ('active', 'completed guarantee period')

        THEN 'SUCCESSFUL'

        WHEN LOWER(p.placement_status)
             IN ('fell through', 'cancelled', 'failed')

        THEN 'UNSUCCESSFUL'

        ELSE 'OTHER'

    END AS placement_outcome


FROM placements p

LEFT JOIN offers o
    ON p.offer_id = o.offer_id

LEFT JOIN applications a
    ON o.application_id = a.application_id

LEFT JOIN jobs j
    ON p.job_id = j.job_id;



-- =============================================================
-- 10. CANDIDATE ANALYSIS VIEW
-- =============================================================
-- Purpose:
-- Candidate-level recruitment performance.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_candidate_analysis AS

SELECT

    c.candidate_id,
    c.candidate_name,
    c.email,

    c.experience_years,
    c.education,

    c.location_id,
    c.work_authorization_id,
    c.source_id,

    c.applied_date,
    c.status AS candidate_status,


    /* ---------------------------------------------------------
       APPLICATION METRICS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT a.application_id
    ) AS total_applications,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'rejected'
            THEN a.application_id
        END
    ) AS rejected_applications,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'withdrawn'
            THEN a.application_id
        END
    ) AS withdrawn_applications,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'hired'
            THEN a.application_id
        END
    ) AS hired_applications,


    /* ---------------------------------------------------------
       OFFERS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT o.offer_id
    ) AS total_offers,


    /* ---------------------------------------------------------
       PLACEMENTS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT p.placement_id
    ) AS total_placements,


    /* ---------------------------------------------------------
       AVERAGE OFFER
       --------------------------------------------------------- */

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_offered_salary,


    /* ---------------------------------------------------------
       CANDIDATE AGE IN PIPELINE

       Synthetic snapshot date:
           2026-12-31
       --------------------------------------------------------- */

    CASE

        WHEN c.applied_date IS NOT NULL
        THEN DATE '2026-12-31' - c.applied_date

    END AS candidate_age_days


FROM candidates c

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    c.candidate_id,
    c.candidate_name,
    c.email,
    c.experience_years,
    c.education,
    c.location_id,
    c.work_authorization_id,
    c.source_id,
    c.applied_date,
    c.status;



-- =============================================================
-- 11. CLIENT ANALYSIS VIEW
-- =============================================================
-- Purpose:
-- Client-level recruitment performance.
--
-- Note:
-- This uses end_client_id because the confirmed jobs schema
-- contains end_client_id.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_client_analysis AS

SELECT

    j.end_client_id AS client_id,


    /* ---------------------------------------------------------
       JOB VOLUME
       --------------------------------------------------------- */

    COUNT(
        DISTINCT j.job_id
    ) AS total_jobs,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(j.job_status) = 'open'
            THEN j.job_id
        END
    ) AS open_jobs,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(j.job_status) = 'closed'
            THEN j.job_id
        END
    ) AS closed_jobs,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(j.job_status) = 'filled'
            THEN j.job_id
        END
    ) AS filled_jobs,


    /* ---------------------------------------------------------
       APPLICATION VOLUME
       --------------------------------------------------------- */

    COUNT(
        DISTINCT a.application_id
    ) AS total_applications,


    /* ---------------------------------------------------------
       OFFERS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT o.offer_id
    ) AS total_offers,


    /* ---------------------------------------------------------
       PLACEMENTS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT p.placement_id
    ) AS total_placements,


    /* ---------------------------------------------------------
       CONVERSION
       --------------------------------------------------------- */

    ROUND(
        100.0 *
        COUNT(DISTINCT p.placement_id)
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        ),
        2
    ) AS placement_rate,


    /* ---------------------------------------------------------
       AVERAGE OFFERED SALARY
       --------------------------------------------------------- */

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_offered_salary


FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    j.end_client_id

ORDER BY
    total_placements DESC;



-- =============================================================
-- 12. EXECUTIVE JOB SUMMARY VIEW
-- =============================================================
-- Purpose:
-- One clean dataset for the main Tableau job-performance table.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_executive_job_summary AS

SELECT

    job_id,
    job_code,
    job_title,
    job_status,

    opened_date,
    closed_date,

    job_age_days,
    aging_bucket,

    total_applications,
    screening_count,
    submitted_to_client_count,
    interview_count,
    offer_count,
    hired_count,
    placement_count,

    application_to_placement_rate,

    assigned_recruiter_id,
    end_client_id,

    employment_type,
    work_mode,

    min_salary,
    max_salary,

    bill_rate,
    bill_rate_type

FROM vw_dashboard_job_performance

ORDER BY
    total_applications DESC;



-- =============================================================
-- 13. DASHBOARD MASTER VIEW
-- =============================================================
-- Purpose:
-- Provides a single job-level dataset containing the most
-- important recruitment dimensions and KPIs.
--
-- This can be used as the primary Tableau data source.
-- =============================================================

CREATE OR REPLACE VIEW vw_dashboard_master AS

SELECT

    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status,

    j.department_id,
    j.end_client_id,
    j.vendor_id,
    j.location_id,
    j.assigned_recruiter_id,

    j.experience_required,
    j.employment_type,
    j.work_mode,

    j.bill_rate,
    j.bill_rate_type,

    j.min_salary,
    j.max_salary,

    j.opened_date,
    j.closed_date,


    /* ---------------------------------------------------------
       JOB AGE

       Synthetic snapshot date:
           2026-12-31
       --------------------------------------------------------- */

    CASE

        WHEN j.opened_date IS NULL
        THEN NULL

        WHEN j.closed_date IS NOT NULL
        THEN j.closed_date - j.opened_date

        ELSE DATE '2026-12-31' - j.opened_date

    END AS job_age_days,


    /* ---------------------------------------------------------
       APPLICATIONS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT a.application_id
    ) AS total_applications,


    /* ---------------------------------------------------------
       PIPELINE STAGES
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'screening'
            THEN a.application_id
        END
    ) AS screening_count,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'submitted to client'
            THEN a.application_id
        END
    ) AS submitted_to_client_count,


    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.current_stage) = 'interview'
            THEN a.application_id
        END
    ) AS interview_count,


    /* ---------------------------------------------------------
       OFFERS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT o.offer_id
    ) AS total_offers,


    /* ---------------------------------------------------------
       HIRES
       --------------------------------------------------------- */

    COUNT(
        DISTINCT CASE
            WHEN LOWER(a.status) = 'hired'
            THEN a.application_id
        END
    ) AS total_hires,


    /* ---------------------------------------------------------
       PLACEMENTS
       --------------------------------------------------------- */

    COUNT(
        DISTINCT p.placement_id
    ) AS total_placements,


    /* ---------------------------------------------------------
       CONVERSION
       --------------------------------------------------------- */

    ROUND(
        100.0 *
        COUNT(DISTINCT p.placement_id)
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        ),
        2
    ) AS placement_rate


FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status,

    j.department_id,
    j.end_client_id,
    j.vendor_id,
    j.location_id,
    j.assigned_recruiter_id,

    j.experience_required,
    j.employment_type,
    j.work_mode,

    j.bill_rate,
    j.bill_rate_type,

    j.min_salary,
    j.max_salary,

    j.opened_date,
    j.closed_date;



-- =============================================================
-- 14. VALIDATION QUERIES
-- =============================================================
-- Run these after creating the views.
-- =============================================================


-- Executive KPIs
SELECT *
FROM vw_dashboard_executive_kpis;


-- Recruitment Funnel
SELECT *
FROM vw_dashboard_recruitment_funnel;


-- Application Status
SELECT *
FROM vw_dashboard_application_status;


-- Job Performance
SELECT *
FROM vw_dashboard_job_performance
LIMIT 20;


-- Job Aging
SELECT *
FROM vw_dashboard_job_aging
LIMIT 20;


-- Recruiter Performance
SELECT *
FROM vw_dashboard_recruiter_performance;


-- Time Trends
SELECT *
FROM vw_dashboard_time_trends
ORDER BY month;


-- Salary Analysis
SELECT *
FROM vw_dashboard_salary_analysis
LIMIT 20;


-- Placement Analysis
SELECT *
FROM vw_dashboard_placement_analysis
LIMIT 20;


-- Candidate Analysis
SELECT *
FROM vw_dashboard_candidate_analysis
LIMIT 20;


-- Client Analysis
SELECT *
FROM vw_dashboard_client_analysis;


-- Executive Job Summary
SELECT *
FROM vw_dashboard_executive_job_summary
LIMIT 20;


-- Master Dashboard Dataset
SELECT *
FROM vw_dashboard_master
LIMIT 20;



-- =============================================================
-- 15. SNAPSHOT-DATE VALIDATION
-- =============================================================
-- Purpose:
-- Confirm that synthetic snapshot-date calculations do not
-- produce negative job or candidate ages.
-- =============================================================


-- -------------------------------------------------------------
-- 15.1 JOB AGE VALIDATION
-- -------------------------------------------------------------

SELECT
    MIN(job_age_days) AS minimum_job_age,
    MAX(job_age_days) AS maximum_job_age,

    COUNT(*) FILTER (
        WHERE job_age_days < 0
    ) AS negative_job_ages

FROM vw_dashboard_job_performance;


-- -------------------------------------------------------------
-- 15.2 JOB AGING VIEW VALIDATION
-- -------------------------------------------------------------

SELECT
    aging_bucket,
    COUNT(*) AS job_count

FROM vw_dashboard_job_aging

GROUP BY aging_bucket

ORDER BY job_count DESC;


-- -------------------------------------------------------------
-- 15.3 CANDIDATE AGE VALIDATION
-- -------------------------------------------------------------

SELECT

    MIN(candidate_age_days)
        AS minimum_candidate_age,

    MAX(candidate_age_days)
        AS maximum_candidate_age,

    COUNT(*) FILTER (
        WHERE candidate_age_days < 0
    ) AS negative_candidate_ages

FROM vw_dashboard_candidate_analysis;


-- -------------------------------------------------------------
-- 15.4 RECRUITER APPLICATION AGE VALIDATION
-- -------------------------------------------------------------

SELECT
    recruiter_id,
    avg_application_age_days

FROM vw_dashboard_recruiter_performance

ORDER BY recruiter_id;


-- -------------------------------------------------------------
-- 15.5 MASTER VIEW NEGATIVE JOB AGE CHECK
-- -------------------------------------------------------------

SELECT
    COUNT(*) AS negative_master_job_ages

FROM vw_dashboard_master

WHERE job_age_days < 0;



-- =============================================================
-- END OF DASHBOARD VIEWS
-- =============================================================
