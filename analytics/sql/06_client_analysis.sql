/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 06_client_analysis.sql

        Purpose:
        --------
        Analyze end-client demand, recruitment activity,
        hiring performance, conversion rates and salaries.

===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. TOTAL END CLIENTS
===========================================================
*/

SELECT
    COUNT(*) AS total_end_clients
FROM companies
WHERE company_type IN ('End Client', 'Direct Client');


/*
===========================================================
2. END CLIENT JOB DEMAND
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(j.job_id) AS total_jobs,

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

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    total_jobs DESC;


/*
===========================================================
3. CLIENT RECRUITMENT FUNNEL
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(DISTINCT j.job_id)
        AS jobs,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    placements DESC,
    offers DESC,
    applications DESC;


/*
===========================================================
4. CLIENT CONVERSION RATES
===========================================================
*/

WITH client_metrics AS
(
    SELECT

        c.company_id,

        c.company_name AS end_client,

        COUNT(DISTINCT j.job_id)
            AS jobs,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM companies c

    LEFT JOIN jobs j
        ON c.company_id = j.end_client_id

    LEFT JOIN applications a
        ON j.job_id = a.job_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    WHERE
        c.company_type IN ('End Client', 'Direct Client')

    GROUP BY

        c.company_id,
        c.company_name
)

SELECT

    end_client,

    jobs,

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

FROM client_metrics

ORDER BY
    placements DESC;


/*
===========================================================
5. CLIENT OFFER ACCEPTANCE
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(DISTINCT o.offer_id)
        AS total_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Accepted'
        ) AS accepted_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Declined'
        ) AS declined_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Negotiating'
        ) AS negotiating_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Extended'
        ) AS extended_offers,

    COUNT(DISTINCT o.offer_id)
        FILTER (
            WHERE o.offer_status = 'Rescinded'
        ) AS rescinded_offers,

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
    ) AS acceptance_rate

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    acceptance_rate DESC;


/*
===========================================================
6. CLIENT OFFERED SALARY ANALYSIS
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(o.offer_id)
        AS total_offers,

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

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    average_offered_salary DESC;


/*
===========================================================
7. CLIENT PLACEMENT STATUS
===========================================================
*/

SELECT

    c.company_name AS end_client,

    p.placement_status,

    COUNT(p.placement_id)
        AS placement_count

FROM companies c

INNER JOIN jobs j
    ON c.company_id = j.end_client_id

INNER JOIN applications a
    ON j.job_id = a.job_id

INNER JOIN offers o
    ON a.application_id = o.application_id

INNER JOIN placements p
    ON o.offer_id = p.offer_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY

    c.company_name,
    p.placement_status

ORDER BY

    c.company_name,
    placement_count DESC;


/*
===========================================================
8. CLIENT SUCCESS RATE
===========================================================
*/

SELECT

    c.company_name AS end_client,

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

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    guarantee_completion_rate DESC;


/*
===========================================================
9. CLIENT APPLICATION VOLUME
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT a.candidate_id)
        AS unique_candidates,

    ROUND(
        COUNT(DISTINCT a.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT j.job_id),
            0
        ),
        2
    ) AS applications_per_job

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    applications DESC;


/*
===========================================================
10. CLIENT INTERVIEW PERFORMANCE
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.interview_id)
        AS interviews,

    COUNT(DISTINCT i.interview_id)
        FILTER (
            WHERE i.outcome = 'Passed'
        ) AS passed_interviews,

    COUNT(DISTINCT i.interview_id)
        FILTER (
            WHERE i.outcome = 'Failed'
        ) AS failed_interviews,

    ROUND(
        COUNT(DISTINCT i.interview_id)
        FILTER (
            WHERE i.outcome = 'Passed'
        )::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT i.interview_id),
            0
        )
        * 100,
        2
    ) AS interview_pass_rate

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    interview_pass_rate DESC;


/*
===========================================================
11. CLIENT JOB PERFORMANCE
===========================================================
*/

SELECT

    c.company_name AS end_client,

    j.job_title,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM companies c

INNER JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY

    c.company_name,
    j.job_title

ORDER BY
    placements DESC,
    applications DESC

LIMIT 30;


/*
===========================================================
12. CLIENT JOB DEMAND BY DEPARTMENT
===========================================================
*/

SELECT

    c.company_name AS end_client,

    d.department_name,

    COUNT(j.job_id)
        AS job_count

FROM companies c

INNER JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN departments d
    ON j.department_id = d.department_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY

    c.company_name,
    d.department_name

ORDER BY

    c.company_name,
    job_count DESC;


/*
===========================================================
13. CLIENT JOB DEMAND BY WORK MODE
===========================================================
*/

SELECT

    c.company_name AS end_client,

    j.work_mode,

    COUNT(j.job_id)
        AS job_count

FROM companies c

INNER JOIN jobs j
    ON c.company_id = j.end_client_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY

    c.company_name,
    j.work_mode

ORDER BY

    c.company_name,
    job_count DESC;


/*
===========================================================
14. TOP CLIENTS BY PLACEMENTS
===========================================================
*/

SELECT

    c.company_name AS end_client,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT a.application_id)
        AS applications

FROM companies c

LEFT JOIN jobs j
    ON c.company_id = j.end_client_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

WHERE
    c.company_type IN ('End Client', 'Direct Client')

GROUP BY
    c.company_name

ORDER BY
    placements DESC

LIMIT 10;


/*
===========================================================
15. CLIENT PERFORMANCE RANKING
===========================================================
*/

WITH client_metrics AS
(
    SELECT

        c.company_id,

        c.company_name AS end_client,

        COUNT(DISTINCT j.job_id)
            AS jobs,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM companies c

    LEFT JOIN jobs j
        ON c.company_id = j.end_client_id

    LEFT JOIN applications a
        ON j.job_id = a.job_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    WHERE
        c.company_type IN ('End Client', 'Direct Client')

    GROUP BY

        c.company_id,
        c.company_name
)

SELECT

    RANK() OVER (
        ORDER BY
            placements DESC
    ) AS client_rank,

    end_client,

    jobs,

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

FROM client_metrics

ORDER BY
    client_rank;


/*
===========================================================
16. FINAL CLIENT ANALYTICS SUMMARY
===========================================================
*/

WITH client_metrics AS
(
    SELECT

        c.company_id,

        c.company_name,

        COUNT(DISTINCT j.job_id)
            AS jobs,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements,

        ROUND(
            AVG(o.offered_salary),
            2
        ) AS average_offered_salary

    FROM companies c

    LEFT JOIN jobs j
        ON c.company_id = j.end_client_id

    LEFT JOIN applications a
        ON j.job_id = a.job_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    WHERE
        c.company_type IN ('End Client', 'Direct Client')

    GROUP BY

        c.company_id,
        c.company_name
)

SELECT

    company_name AS end_client,

    jobs,

    applications,

    interviews,

    offers,

    placements,

    average_offered_salary,

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

FROM client_metrics

ORDER BY
    placements DESC;


/*
===========================================================
END OF CLIENT ANALYSIS
===========================================================
*/