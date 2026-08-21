/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 04_job_analysis.sql

        Purpose:
        --------
        Analyze job demand, job characteristics,
        client demand, salary/bill rates and recruitment
        outcomes by job.

===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. TOTAL JOBS
===========================================================
*/

SELECT
    COUNT(*) AS total_jobs
FROM jobs;


/*
===========================================================
2. JOB STATUS DISTRIBUTION
===========================================================
*/

SELECT
    job_status,
    COUNT(*) AS job_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM jobs),
            0
        )
        * 100,
        2
    ) AS percentage

FROM jobs

GROUP BY job_status

ORDER BY job_count DESC;


/*
===========================================================
3. JOBS BY DEPARTMENT
===========================================================
*/

SELECT
    d.department_name,

    COUNT(j.job_id) AS job_count,

    ROUND(
        COUNT(j.job_id)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM jobs),
            0
        )
        * 100,
        2
    ) AS percentage

FROM departments d

LEFT JOIN jobs j
    ON d.department_id = j.department_id

GROUP BY
    d.department_name

ORDER BY job_count DESC;


/*
===========================================================
4. JOBS BY EMPLOYMENT TYPE
===========================================================
*/

SELECT
    employment_type,
    COUNT(*) AS job_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM jobs),
            0
        )
        * 100,
        2
    ) AS percentage

FROM jobs

GROUP BY employment_type

ORDER BY job_count DESC;


/*
===========================================================
5. JOBS BY WORK MODE
===========================================================
*/

SELECT
    work_mode,
    COUNT(*) AS job_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM jobs),
            0
        )
        * 100,
        2
    ) AS percentage

FROM jobs

GROUP BY work_mode

ORDER BY job_count DESC;


/*
===========================================================
6. JOBS BY LOCATION
===========================================================
*/

SELECT
    l.city,
    l.state,
    l.country,

    COUNT(j.job_id) AS job_count

FROM jobs j

LEFT JOIN locations l
    ON j.location_id = l.location_id

GROUP BY
    l.city,
    l.state,
    l.country

ORDER BY job_count DESC;


/*
===========================================================
7. JOBS BY END CLIENT
===========================================================
*/

SELECT
    c.company_name AS end_client,

    COUNT(j.job_id) AS job_count

FROM jobs j

LEFT JOIN companies c
    ON j.end_client_id = c.company_id

GROUP BY
    c.company_name

ORDER BY job_count DESC;


/*
===========================================================
8. JOBS BY VENDOR
===========================================================
*/

SELECT
    c.company_name AS vendor,

    COUNT(j.job_id) AS job_count

FROM jobs j

LEFT JOIN companies c
    ON j.vendor_id = c.company_id

GROUP BY
    c.company_name

ORDER BY job_count DESC;


/*
===========================================================
9. EXPERIENCE REQUIREMENT DISTRIBUTION
===========================================================
*/

SELECT

    CASE
        WHEN experience_required < 2
            THEN '0-1 Years'

        WHEN experience_required BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN experience_required BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN experience_required BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END AS experience_required_group,

    COUNT(*) AS job_count

FROM jobs

GROUP BY
    CASE
        WHEN experience_required < 2
            THEN '0-1 Years'

        WHEN experience_required BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN experience_required BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN experience_required BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END

ORDER BY
    MIN(experience_required);


/*
===========================================================
10. SALARY ANALYSIS
===========================================================
*/

SELECT

    ROUND(AVG(min_salary), 2)
        AS avg_min_salary,

    ROUND(AVG(max_salary), 2)
        AS avg_max_salary,

    ROUND(MIN(min_salary), 2)
        AS lowest_min_salary,

    ROUND(MAX(max_salary), 2)
        AS highest_max_salary,

    ROUND(AVG(max_salary - min_salary), 2)
        AS average_salary_range

FROM jobs

WHERE
    min_salary IS NOT NULL
    AND max_salary IS NOT NULL;


/*
===========================================================
11. BILL RATE ANALYSIS
===========================================================
*/

SELECT

    bill_rate_type,

    COUNT(*) AS job_count,

    ROUND(
        AVG(bill_rate),
        2
    ) AS average_bill_rate,

    ROUND(
        MIN(bill_rate),
        2
    ) AS minimum_bill_rate,

    ROUND(
        MAX(bill_rate),
        2
    ) AS maximum_bill_rate

FROM jobs

WHERE bill_rate IS NOT NULL

GROUP BY bill_rate_type

ORDER BY average_bill_rate DESC;


/*
===========================================================
12. JOBS BY DESIGNATION / JOB TITLE
===========================================================
*/

SELECT

    job_title,

    COUNT(*) AS job_count

FROM jobs

GROUP BY job_title

ORDER BY job_count DESC

LIMIT 20;


/*
===========================================================
13. JOB DEMAND VS APPLICATIONS
===========================================================
*/

SELECT

    j.job_id,

    j.job_code,

    j.job_title,

    j.job_status,

    COUNT(a.application_id)
        AS applications

FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

GROUP BY

    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status

ORDER BY applications DESC

LIMIT 20;


/*
===========================================================
14. JOB PERFORMANCE FUNNEL
===========================================================
*/

SELECT

    j.job_id,

    j.job_code,

    j.job_title,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviewed_applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    j.job_id,
    j.job_code,
    j.job_title

ORDER BY
    placements DESC,
    offers DESC,
    applications DESC

LIMIT 20;


/*
===========================================================
15. JOB CONVERSION RATES
===========================================================
*/

WITH job_metrics AS
(
    SELECT

        j.job_id,

        j.job_code,

        j.job_title,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM jobs j

    LEFT JOIN applications a
        ON j.job_id = a.job_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY

        j.job_id,
        j.job_code,
        j.job_title
)

SELECT

    job_id,

    job_code,

    job_title,

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

FROM job_metrics

ORDER BY
    placements DESC,
    application_to_placement_rate DESC

LIMIT 20;


/*
===========================================================
16. DEPARTMENT RECRUITMENT PERFORMANCE
===========================================================
*/

SELECT

    d.department_name,

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

FROM departments d

LEFT JOIN jobs j
    ON d.department_id = j.department_id

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    d.department_name

ORDER BY
    placements DESC;


/*
===========================================================
17. DEPARTMENT CONVERSION RATES
===========================================================
*/

WITH department_metrics AS
(
    SELECT

        d.department_name,

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

    FROM departments d

    LEFT JOIN jobs j
        ON d.department_id = j.department_id

    LEFT JOIN applications a
        ON j.job_id = a.job_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        d.department_name
)

SELECT

    department_name,

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

FROM department_metrics

ORDER BY
    placements DESC;


/*
===========================================================
18. JOB SKILL DEMAND
===========================================================
*/

SELECT

    s.skill_name,

    COUNT(DISTINCT js.job_id)
        AS jobs_requiring_skill,

    COUNT(DISTINCT j.job_id)
        AS total_jobs

FROM job_skills js

INNER JOIN skills s
    ON js.skill_id = s.skill_id

LEFT JOIN jobs j
    ON js.job_id = j.job_id

GROUP BY
    s.skill_name

ORDER BY
    jobs_requiring_skill DESC

LIMIT 20;


/*
===========================================================
19. MUST-HAVE SKILL DEMAND
===========================================================
*/

SELECT

    s.skill_name,

    COUNT(DISTINCT js.job_id)
        AS must_have_jobs

FROM job_skills js

INNER JOIN skills s
    ON js.skill_id = s.skill_id

WHERE
    js.priority = 'Must-have'

GROUP BY
    s.skill_name

ORDER BY
    must_have_jobs DESC

LIMIT 20;


/*
===========================================================
20. JOBS WITH HIGHEST COMPETITION
===========================================================
*/

SELECT

    j.job_id,

    j.job_code,

    j.job_title,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        COUNT(DISTINCT a.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT p.placement_id),
            0
        ),
        2
    ) AS applications_per_placement

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
    j.job_title

HAVING
    COUNT(DISTINCT a.application_id) > 0

ORDER BY
    applications_per_placement DESC

LIMIT 20;


/*
===========================================================
21. FINAL JOB ANALYTICS SUMMARY
===========================================================
*/

SELECT

    COUNT(DISTINCT j.job_id)
        AS total_jobs,

    COUNT(DISTINCT j.job_id)
        FILTER (
            WHERE j.job_status = 'Open'
        )
        AS open_jobs,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviewed_applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        AVG(j.experience_required),
        2
    ) AS average_experience_required,

    ROUND(
        AVG(j.min_salary),
        2
    ) AS average_min_salary,

    ROUND(
        AVG(j.max_salary),
        2
    ) AS average_max_salary,

    ROUND(
        AVG(j.bill_rate),
        2
    ) AS average_bill_rate

FROM jobs j

LEFT JOIN applications a
    ON j.job_id = a.job_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


/*
===========================================================
END OF JOB ANALYSIS
===========================================================
*/