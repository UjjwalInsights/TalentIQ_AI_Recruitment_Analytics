/*
===========================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

File:
01_executive_kpis.sql

Purpose:
--------
Calculate the primary recruitment KPIs for management.

These KPIs will later feed the Tableau Executive Dashboard.

===========================================================
*/


SET search_path TO recruitment;


-- =========================================================
-- 1. TOTAL JOBS
-- =========================================================

SELECT
    COUNT(*) AS total_jobs
FROM jobs;


-- =========================================================
-- 2. OPEN JOBS
-- =========================================================

SELECT
    COUNT(*) AS open_jobs
FROM jobs
WHERE job_status = 'Open';


-- =========================================================
-- 3. TOTAL CANDIDATES
-- =========================================================

SELECT
    COUNT(*) AS total_candidates
FROM candidates;


-- =========================================================
-- 4. TOTAL APPLICATIONS
-- =========================================================

SELECT
    COUNT(*) AS total_applications
FROM applications;


-- =========================================================
-- 5. TOTAL INTERVIEWS
-- =========================================================

SELECT
    COUNT(*) AS total_interviews
FROM interviews;


-- =========================================================
-- 6. TOTAL OFFERS
-- =========================================================

SELECT
    COUNT(*) AS total_offers
FROM offers;


-- =========================================================
-- 7. ACCEPTED OFFERS
-- =========================================================

SELECT
    COUNT(*) AS accepted_offers
FROM offers
WHERE offer_status = 'Accepted';


-- =========================================================
-- 8. TOTAL PLACEMENTS
-- =========================================================

SELECT
    COUNT(*) AS total_placements
FROM placements;


-- =========================================================
-- 9. ACTIVE PLACEMENTS
-- =========================================================

SELECT
    COUNT(*) AS active_placements
FROM placements
WHERE placement_status = 'Active';


-- =========================================================
-- 10. APPLICATION → INTERVIEW RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(DISTINCT i.application_id)::NUMERIC
        / NULLIF(COUNT(DISTINCT a.application_id), 0)
        * 100,
        2
    ) AS application_to_interview_rate
FROM applications a
LEFT JOIN interviews i
    ON a.application_id = i.application_id;


-- =========================================================
-- 11. INTERVIEW → OFFER RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(DISTINCT o.application_id)::NUMERIC
        / NULLIF(COUNT(DISTINCT i.application_id), 0)
        * 100,
        2
    ) AS interview_to_offer_rate
FROM interviews i
LEFT JOIN offers o
    ON i.application_id = o.application_id;


-- =========================================================
-- 12. OFFER ACCEPTANCE RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(*) FILTER (
            WHERE offer_status = 'Accepted'
        )::NUMERIC
        / NULLIF(COUNT(*), 0)
        * 100,
        2
    ) AS offer_acceptance_rate
FROM offers;


-- =========================================================
-- 13. OFFER → PLACEMENT RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(DISTINCT p.offer_id)::NUMERIC
        / NULLIF(
            COUNT(DISTINCT o.offer_id)
            FILTER (
                WHERE o.offer_status = 'Accepted'
            ),
            0
        )
        * 100,
        2
    ) AS offer_to_placement_rate
FROM offers o
LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


-- =========================================================
-- 14. OVERALL HIRING RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(DISTINCT p.candidate_id)::NUMERIC
        / NULLIF(COUNT(DISTINCT c.candidate_id), 0)
        * 100,
        2
    ) AS overall_hiring_rate
FROM candidates c
LEFT JOIN placements p
    ON c.candidate_id = p.candidate_id;


-- =========================================================
-- 15. AVERAGE OFFERED SALARY
-- =========================================================

SELECT
    ROUND(
        AVG(offered_salary),
        2
    ) AS average_offered_salary
FROM offers;


-- =========================================================
-- 16. MINIMUM OFFERED SALARY
-- =========================================================

SELECT
    MIN(offered_salary) AS minimum_offered_salary
FROM offers;


-- =========================================================
-- 17. MAXIMUM OFFERED SALARY
-- =========================================================

SELECT
    MAX(offered_salary) AS maximum_offered_salary
FROM offers;


-- =========================================================
-- 18. AVERAGE EXPERIENCE OF CANDIDATES
-- =========================================================

SELECT
    ROUND(
        AVG(experience_years),
        2
    ) AS average_candidate_experience
FROM candidates;


-- =========================================================
-- 19. PLACEMENT SUCCESS RATE
-- =========================================================

SELECT
    ROUND(
        COUNT(*) FILTER (
            WHERE placement_status
            IN ('Active', 'Completed Guarantee Period')
        )::NUMERIC
        / NULLIF(COUNT(*), 0)
        * 100,
        2
    ) AS placement_success_rate
FROM placements;


-- =========================================================
-- 20. EXECUTIVE KPI SUMMARY
-- =========================================================
--
-- One query containing the major KPIs.
-- This will be especially useful for Tableau.
--
-- =========================================================

SELECT

    -- Recruitment volume
    (SELECT COUNT(*)
     FROM jobs) AS total_jobs,

    (SELECT COUNT(*)
     FROM jobs
     WHERE job_status = 'Open') AS open_jobs,

    (SELECT COUNT(*)
     FROM candidates) AS total_candidates,

    (SELECT COUNT(*)
     FROM applications) AS total_applications,

    -- Recruitment activity
    (SELECT COUNT(*)
     FROM interviews) AS total_interviews,

    (SELECT COUNT(*)
     FROM offers) AS total_offers,

    (SELECT COUNT(*)
     FROM offers
     WHERE offer_status = 'Accepted') AS accepted_offers,

    (SELECT COUNT(*)
     FROM placements) AS total_placements,

    -- Conversion metrics
    ROUND(
        (
            SELECT COUNT(DISTINCT i.application_id)::NUMERIC
            FROM interviews i
        )
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM applications),
            0
        )
        * 100,
        2
    ) AS application_to_interview_rate,

    ROUND(
        (
            SELECT COUNT(DISTINCT o.application_id)::NUMERIC
            FROM offers o
        )
        /
        NULLIF(
            (SELECT COUNT(DISTINCT i.application_id)
             FROM interviews i),
            0
        )
        * 100,
        2
    ) AS interview_to_offer_rate,

    ROUND(
        (
            SELECT COUNT(*)
            FROM offers
            WHERE offer_status = 'Accepted'
        )::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM offers),
            0
        )
        * 100,
        2
    ) AS offer_acceptance_rate,

    ROUND(
        (
            SELECT COUNT(*)
            FROM placements
        )::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*)
             FROM offers
             WHERE offer_status = 'Accepted'),
            0
        )
        * 100,
        2
    ) AS offer_to_placement_rate,

    -- Compensation
    ROUND(
        (
            SELECT AVG(offered_salary)
            FROM offers
        ),
        2
    ) AS average_offered_salary,

    -- Candidate profile
    ROUND(
        (
            SELECT AVG(experience_years)
            FROM candidates
        ),
        2
    ) AS average_candidate_experience;