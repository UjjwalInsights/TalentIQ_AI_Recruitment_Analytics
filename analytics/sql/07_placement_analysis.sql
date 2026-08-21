

/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 07_placement_analysis.sql

        Purpose:
        --------
        Analyze placement outcomes, joining performance,
        placement status, guarantee-period completion,
        salary and placement trends.

===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. TOTAL PLACEMENTS
===========================================================
*/

SELECT
    COUNT(*) AS total_placements
FROM placements;


/*
===========================================================
2. PLACEMENT STATUS DISTRIBUTION
===========================================================
*/

SELECT

    placement_status,

    COUNT(*) AS placement_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM placements),
            0
        )
        * 100,
        2
    ) AS percentage

FROM placements

GROUP BY
    placement_status

ORDER BY
    placement_count DESC;


/*
===========================================================
3. PLACEMENTS BY DEPARTMENT
===========================================================
*/

SELECT

    p.department,

    COUNT(*) AS placements,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM placements),
            0
        )
        * 100,
        2
    ) AS percentage

FROM placements p

GROUP BY
    p.department

ORDER BY
    placements DESC;


/*
===========================================================
4. PLACEMENTS BY DESIGNATION
===========================================================
*/

SELECT

    designation,

    COUNT(*) AS placements

FROM placements

GROUP BY
    designation

ORDER BY
    placements DESC;


/*
===========================================================
5. PLACEMENTS BY JOB
===========================================================
*/

SELECT

    j.job_code,

    j.job_title,

    COUNT(p.placement_id)
        AS placements

FROM placements p

LEFT JOIN jobs j
    ON p.job_id = j.job_id

GROUP BY

    j.job_code,
    j.job_title

ORDER BY
    placements DESC

LIMIT 20;


/*
===========================================================
6. PLACEMENTS BY JOINING YEAR
===========================================================
*/

SELECT

    EXTRACT(
        YEAR FROM joining_date
    )::INTEGER AS joining_year,

    COUNT(*) AS placements

FROM placements

WHERE joining_date IS NOT NULL

GROUP BY
    joining_year

ORDER BY
    joining_year;


/*
===========================================================
7. PLACEMENTS BY JOINING MONTH
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        joining_date
    )::DATE AS joining_month,

    COUNT(*) AS placements

FROM placements

WHERE joining_date IS NOT NULL

GROUP BY
    joining_month

ORDER BY
    joining_month;


/*
===========================================================
8. PLACEMENTS BY PLACEMENT MONTH
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS placement_month,

    COUNT(*) AS placements

FROM placements

WHERE placement_date IS NOT NULL

GROUP BY
    placement_month

ORDER BY
    placement_month;


/*
===========================================================
9. OFFER → PLACEMENT CONVERSION
===========================================================
*/

SELECT

    COUNT(DISTINCT o.offer_id)
        AS total_offers,

    COUNT(DISTINCT p.placement_id)
        AS total_placements,

    ROUND(
        COUNT(DISTINCT p.placement_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT o.offer_id),
            0
        )
        * 100,
        2
    ) AS offer_to_placement_rate

FROM offers o

LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


/*
===========================================================
10. PLACEMENT SUCCESS RATE
===========================================================
*/

SELECT

    COUNT(*) AS total_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        ) AS successful_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Fell Through'
        ) AS failed_placements,

    ROUND(
        COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        )::NUMERIC
        /
        NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS placement_success_rate

FROM placements;


/*
===========================================================
11. ACTIVE PLACEMENTS
===========================================================
*/

SELECT

    COUNT(*) AS active_placements,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM placements),
            0
        )
        * 100,
        2
    ) AS percentage_of_total_placements

FROM placements

WHERE
    placement_status = 'Active';


/*
===========================================================
12. COMPLETED GUARANTEE PERIOD
===========================================================
*/

SELECT

    COUNT(*) AS completed_guarantee_period,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM placements),
            0
        )
        * 100,
        2
    ) AS percentage_of_total_placements

FROM placements

WHERE
    placement_status =
    'Completed Guarantee Period';


/*
===========================================================
13. FELL THROUGH ANALYSIS
===========================================================
*/

SELECT

    COUNT(*) AS fell_through_placements,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM placements),
            0
        )
        * 100,
        2
    ) AS fell_through_rate

FROM placements

WHERE
    placement_status = 'Fell Through';


/*
===========================================================
14. PLACEMENT PERFORMANCE BY DEPARTMENT
===========================================================
*/

SELECT

    p.department,

    COUNT(*) AS total_placements,

    COUNT(*)
        FILTER (
            WHERE p.placement_status =
                  'Completed Guarantee Period'
        ) AS completed_guarantee,

    COUNT(*)
        FILTER (
            WHERE p.placement_status =
                  'Active'
        ) AS active,

    COUNT(*)
        FILTER (
            WHERE p.placement_status =
                  'Fell Through'
        ) AS fell_through,

    ROUND(
        COUNT(*)
        FILTER (
            WHERE p.placement_status =
                  'Completed Guarantee Period'
        )::NUMERIC
        /
        NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS success_rate

FROM placements p

GROUP BY
    p.department

ORDER BY
    success_rate DESC;


/*
===========================================================
15. PLACEMENT PERFORMANCE BY DESIGNATION
===========================================================
*/

SELECT

    designation,

    COUNT(*) AS total_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        ) AS completed_guarantee,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Fell Through'
        ) AS fell_through,

    ROUND(
        COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        )::NUMERIC
        /
        NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS success_rate

FROM placements

GROUP BY
    designation

HAVING
    COUNT(*) >= 3

ORDER BY
    success_rate DESC;


/*
===========================================================
16. AVERAGE TIME FROM PLACEMENT TO JOINING
===========================================================
*/

SELECT

    ROUND(
        AVG(
            p.joining_date - p.placement_date
        ),
        2
    ) AS average_days_to_join,

    MIN(
        p.joining_date - p.placement_date
    ) AS minimum_days_to_join,

    MAX(
        p.joining_date - p.placement_date
    ) AS maximum_days_to_join

FROM placements p

WHERE

    p.placement_date IS NOT NULL
    AND p.joining_date IS NOT NULL;


/*
===========================================================
17. JOINING TIME DISTRIBUTION
===========================================================
*/

SELECT

    CASE

        WHEN p.joining_date - p.placement_date <= 7
            THEN '0-7 Days'

        WHEN p.joining_date - p.placement_date <= 14
            THEN '8-14 Days'

        WHEN p.joining_date - p.placement_date <= 30
            THEN '15-30 Days'

        WHEN p.joining_date - p.placement_date <= 60
            THEN '31-60 Days'

        ELSE '61+ Days'

    END AS joining_time_group,

    COUNT(*) AS placements

FROM placements p

WHERE

    p.placement_date IS NOT NULL
    AND p.joining_date IS NOT NULL

GROUP BY

    CASE

        WHEN p.joining_date - p.placement_date <= 7
            THEN '0-7 Days'

        WHEN p.joining_date - p.placement_date <= 14
            THEN '8-14 Days'

        WHEN p.joining_date - p.placement_date <= 30
            THEN '15-30 Days'

        WHEN p.joining_date - p.placement_date <= 60
            THEN '31-60 Days'

        ELSE '61+ Days'

    END

ORDER BY
    MIN(
        p.joining_date - p.placement_date
    );


/*
===========================================================
18. PLACEMENTS BY LOCATION
===========================================================
*/

SELECT

    l.city,

    l.state,

    l.country,

    COUNT(p.placement_id)
        AS placements

FROM placements p

LEFT JOIN jobs j
    ON p.job_id = j.job_id

LEFT JOIN locations l
    ON j.location_id = l.location_id

GROUP BY

    l.city,
    l.state,
    l.country

ORDER BY
    placements DESC

LIMIT 20;


/*
===========================================================
19. PLACEMENT SALARY ANALYSIS
===========================================================
*/

SELECT

    COUNT(p.placement_id)
        AS placements,

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_placement_salary,

    ROUND(
        MIN(o.offered_salary),
        2
    ) AS minimum_placement_salary,

    ROUND(
        MAX(o.offered_salary),
        2
    ) AS maximum_placement_salary

FROM placements p

LEFT JOIN offers o
    ON p.offer_id = o.offer_id;


/*
===========================================================
20. SALARY BY DEPARTMENT
===========================================================
*/

SELECT

    p.department,

    COUNT(p.placement_id)
        AS placements,

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_salary,

    ROUND(
        MIN(o.offered_salary),
        2
    ) AS minimum_salary,

    ROUND(
        MAX(o.offered_salary),
        2
    ) AS maximum_salary

FROM placements p

LEFT JOIN offers o
    ON p.offer_id = o.offer_id

GROUP BY
    p.department

ORDER BY
    average_salary DESC;


/*
===========================================================
21. PLACEMENT PERFORMANCE BY RECRUITER
===========================================================
*/

SELECT

    r.recruiter_name,

    COUNT(p.placement_id)
        AS placements,

    COUNT(p.placement_id)
        FILTER (
            WHERE p.placement_status =
                  'Completed Guarantee Period'
        ) AS successful_placements,

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
    ) AS success_rate

FROM placements p

LEFT JOIN offers o
    ON p.offer_id = o.offer_id

LEFT JOIN applications a
    ON o.application_id = a.application_id

LEFT JOIN recruiters r
    ON a.recruiter_id = r.recruiter_id

GROUP BY
    r.recruiter_name

ORDER BY
    placements DESC;


/*
===========================================================
22. TOP PLACEMENT JOB TITLES
===========================================================
*/

SELECT

    j.job_title,

    COUNT(p.placement_id)
        AS placements,

    ROUND(
        AVG(o.offered_salary),
        2
    ) AS average_salary

FROM placements p

LEFT JOIN jobs j
    ON p.job_id = j.job_id

LEFT JOIN offers o
    ON p.offer_id = o.offer_id

GROUP BY
    j.job_title

ORDER BY
    placements DESC

LIMIT 20;


/*
===========================================================
23. PLACEMENT MONTHLY TREND WITH STATUS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS placement_month,

    COUNT(*) AS total_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status = 'Active'
        ) AS active,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        ) AS completed_guarantee,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Fell Through'
        ) AS fell_through

FROM placements

GROUP BY
    placement_month

ORDER BY
    placement_month;


/*
===========================================================
24. FINAL PLACEMENT ANALYTICS SUMMARY
===========================================================
*/

SELECT

    COUNT(*) AS total_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status = 'Active'
        ) AS active_placements,

    COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        ) AS completed_guarantee_period,

    COUNT(*)
        FILTER (
            WHERE placement_status = 'Fell Through'
        ) AS fell_through,

    ROUND(
        COUNT(*)
        FILTER (
            WHERE placement_status =
                  'Completed Guarantee Period'
        )::NUMERIC
        /
        NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS placement_success_rate,

    ROUND(
AVG(
    p.joining_date - p.placement_date
),
        2
    ) AS average_days_to_join,

    ROUND(
        AVG(
            o.offered_salary
        ),
        2
    ) AS average_offered_salary

FROM placements p

LEFT JOIN offers o
    ON p.offer_id = o.offer_id;


/*
===========================================================
END OF PLACEMENT ANALYSIS
===========================================================
*/
