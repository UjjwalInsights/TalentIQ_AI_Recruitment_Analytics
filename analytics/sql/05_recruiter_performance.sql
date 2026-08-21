

/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 05_recruiter_performance.sql

        Purpose:
        --------
        Analyze recruiter workload, productivity,
        conversion rates and placement performance.

===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. TOTAL RECRUITERS
===========================================================
*/

SELECT
    COUNT(*) AS total_recruiters
FROM recruiters;


/*
===========================================================
2. RECRUITER STATUS / ACTIVE RECRUITERS
===========================================================
*/

SELECT
    COUNT(*) AS active_recruiters
FROM recruiters
WHERE is_active = TRUE;

/*
===========================================================
3. RECRUITER WORKLOAD
===========================================================
*/

SELECT

    r.recruiter_id,
    r.recruiter_name,

    COUNT(DISTINCT j.job_id)
        AS assigned_jobs,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.interview_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM recruiters r

LEFT JOIN jobs j
    ON r.recruiter_id = j.assigned_recruiter_id

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    r.recruiter_id,
    r.recruiter_name

ORDER BY
    placements DESC;


/*
===========================================================
4. RECRUITER PERFORMANCE FUNNEL
===========================================================
*/

SELECT

    r.recruiter_id,
    r.recruiter_name,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviewed_applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM recruiters r

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    r.recruiter_id,
    r.recruiter_name

ORDER BY
    placements DESC;


/*
===========================================================
5. RECRUITER CONVERSION RATES
===========================================================
*/

WITH recruiter_metrics AS
(
    SELECT

        r.recruiter_id,
        r.recruiter_name,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM recruiters r

    LEFT JOIN applications a
        ON r.recruiter_id = a.recruiter_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        r.recruiter_id,
        r.recruiter_name
)

SELECT

    recruiter_id,
    recruiter_name,

    applications,
    interviews,
    offers,
    placements,

    ROUND(
        interviews::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS interview_rate,

    ROUND(
        offers::NUMERIC
        /
        NULLIF(interviews, 0)
        * 100,
        2
    ) AS offer_rate,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(offers, 0)
        * 100,
        2
    ) AS placement_rate,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS application_to_placement_rate

FROM recruiter_metrics

ORDER BY
    placements DESC;


/*
===========================================================
6. RECRUITER JOB ASSIGNMENT
===========================================================
*/

SELECT

    r.recruiter_name,

    COUNT(j.job_id) AS assigned_jobs,

    COUNT(j.job_id)
        FILTER (
            WHERE j.job_status = 'Open'
        ) AS open_jobs,

    COUNT(j.job_id)
        FILTER (
            WHERE j.job_status = 'Filled'
        ) AS filled_jobs,

    COUNT(j.job_id)
        FILTER (
            WHERE j.job_status = 'Closed'
        ) AS closed_jobs,

    COUNT(j.job_id)
        FILTER (
            WHERE j.job_status = 'On Hold'
        ) AS on_hold_jobs

FROM recruiters r

LEFT JOIN jobs j
    ON r.recruiter_id = j.assigned_recruiter_id

GROUP BY
    r.recruiter_name

ORDER BY
    assigned_jobs DESC;


/*
===========================================================
7. RECRUITER PLACEMENTS BY DEPARTMENT
===========================================================
*/

SELECT

    r.recruiter_name,

    d.department_name,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM recruiters r

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN jobs j
    ON a.job_id = j.job_id

LEFT JOIN departments d
    ON j.department_id = d.department_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    r.recruiter_name,
    d.department_name

ORDER BY
    placements DESC;


/*
===========================================================
8. RECRUITER PERFORMANCE BY JOB
===========================================================
*/

SELECT

    r.recruiter_name,

    j.job_title,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM recruiters r

INNER JOIN applications a
    ON r.recruiter_id = a.recruiter_id

INNER JOIN jobs j
    ON a.job_id = j.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    r.recruiter_name,
    j.job_title

ORDER BY
    placements DESC,
    applications DESC

LIMIT 30;


/*
===========================================================
9. RECRUITER OFFER ACCEPTANCE
===========================================================
*/

SELECT

    r.recruiter_name,

    COUNT(DISTINCT o.offer_id)
        AS total_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Accepted'
        ) AS accepted_offers,

    ROUND(
        COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Accepted'
        )::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT o.offer_id),
            0
        )
        * 100,
        2
    ) AS offer_acceptance_rate

FROM recruiters r

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

GROUP BY
    r.recruiter_name

ORDER BY
    offer_acceptance_rate DESC;


/*
===========================================================
10. RECRUITER PLACEMENT STATUS
===========================================================
*/

SELECT

    r.recruiter_name,

    p.placement_status,

    COUNT(*) AS placement_count

FROM recruiters r

INNER JOIN applications a
    ON r.recruiter_id = a.recruiter_id

INNER JOIN offers o
    ON a.application_id = o.application_id

INNER JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    r.recruiter_name,
    p.placement_status

ORDER BY

    r.recruiter_name,
    placement_count DESC;


/*
===========================================================
11. RECRUITER AVERAGE OFFERED SALARY
===========================================================
*/

SELECT

    r.recruiter_name,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_offered_salary,

    ROUND(
        MIN(o.offered_salary),
        2
    ) AS minimum_offered_salary,

    ROUND(
        MAX(o.offered_salary),
        2
    ) AS maximum_offered_salary

FROM recruiters r

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

GROUP BY
    r.recruiter_name

ORDER BY
    average_offered_salary DESC;


/*
===========================================================
12. RECRUITER PLACEMENT SUCCESS
===========================================================
*/

SELECT

    r.recruiter_name,

    COUNT(p.placement_id)
        AS total_placements,

    COUNT(p.placement_id)
        FILTER (
            WHERE p.placement_status =
                  'Completed Guarantee Period'
        ) AS completed_guarantee_period,

    COUNT(p.placement_id)
        FILTER (
            WHERE p.placement_status =
                  'Active'
        ) AS active_placements,

    COUNT(p.placement_id)
        FILTER (
            WHERE p.placement_status =
                  'Fell Through'
        ) AS fell_through,

    ROUND(
        COUNT(p.placement_id)
        FILTER (
            WHERE p.placement_status =
                  'Completed Guarantee Period'
        )::NUMERIC
        /
        NULLIF(
            COUNT(p.placement_id),
            0
        )
        * 100,
        2
    ) AS guarantee_completion_rate

FROM recruiters r

LEFT JOIN applications a
    ON r.recruiter_id = a.recruiter_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    r.recruiter_name

ORDER BY
    guarantee_completion_rate DESC;


/*
===========================================================
13. TOP RECRUITERS BY PLACEMENTS
===========================================================
*/

WITH recruiter_performance AS
(
    SELECT

        r.recruiter_id,
        r.recruiter_name,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM recruiters r

    LEFT JOIN applications a
        ON r.recruiter_id = a.recruiter_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY

        r.recruiter_id,
        r.recruiter_name
)

SELECT

    recruiter_name,

    applications,

    interviews,

    offers,

    placements,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS placement_rate

FROM recruiter_performance

ORDER BY
    placements DESC,
    placement_rate DESC;


/*
===========================================================
14. RECRUITER RANKING
===========================================================
*/

WITH recruiter_metrics AS
(
    SELECT

        r.recruiter_id,
        r.recruiter_name,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM recruiters r

    LEFT JOIN applications a
        ON r.recruiter_id = a.recruiter_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY

        r.recruiter_id,
        r.recruiter_name
)

SELECT

    RANK() OVER (
        ORDER BY placements DESC
    ) AS recruiter_rank,

    recruiter_name,

    applications,

    interviews,

    offers,

    placements,

    ROUND(
        interviews::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS interview_rate,

    ROUND(
        offers::NUMERIC
        /
        NULLIF(interviews, 0)
        * 100,
        2
    ) AS offer_rate,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(offers, 0)
        * 100,
        2
    ) AS placement_rate

FROM recruiter_metrics

ORDER BY
    recruiter_rank;


/*
===========================================================
15. RECRUITER PRODUCTIVITY
===========================================================
*/

WITH recruiter_productivity AS
(
    SELECT

        r.recruiter_id,
        r.recruiter_name,

        COUNT(DISTINCT j.job_id)
            AS assigned_jobs,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM recruiters r

    LEFT JOIN jobs j
        ON r.recruiter_id = j.assigned_recruiter_id

    LEFT JOIN applications a
        ON r.recruiter_id = a.recruiter_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY

        r.recruiter_id,
        r.recruiter_name
)

SELECT

    recruiter_name,

    assigned_jobs,

    applications,

    placements,

    ROUND(
        applications::NUMERIC
        /
        NULLIF(assigned_jobs, 0),
        2
    ) AS applications_per_job,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(assigned_jobs, 0),
        2
    ) AS placements_per_job

FROM recruiter_productivity

ORDER BY
    placements_per_job DESC;


/*
===========================================================
16. FINAL RECRUITER PERFORMANCE SUMMARY
===========================================================
*/

WITH recruiter_metrics AS
(
    SELECT

        r.recruiter_id,

        r.recruiter_name,

        COUNT(DISTINCT j.job_id)
            AS assigned_jobs,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements,

        COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Accepted'
        ) AS accepted_offers

    FROM recruiters r

    LEFT JOIN jobs j
        ON r.recruiter_id = j.assigned_recruiter_id

    LEFT JOIN applications a
        ON r.recruiter_id = a.recruiter_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY

        r.recruiter_id,
        r.recruiter_name
)

SELECT

    recruiter_name,

    assigned_jobs,

    applications,

    interviews,

    offers,

    accepted_offers,

    placements,

    ROUND(
        interviews::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS interview_rate,

    ROUND(
        offers::NUMERIC
        /
        NULLIF(interviews, 0)
        * 100,
        2
    ) AS offer_rate,

    ROUND(
        accepted_offers::NUMERIC
        /
        NULLIF(offers, 0)
        * 100,
        2
    ) AS acceptance_rate,

    ROUND(
        placements::NUMERIC
        /
        NULLIF(applications, 0)
        * 100,
        2
    ) AS application_to_placement_rate

FROM recruiter_metrics

ORDER BY
    placements DESC;


/*
===========================================================
END OF RECRUITER PERFORMANCE ANALYSIS
===========================================================
*/
