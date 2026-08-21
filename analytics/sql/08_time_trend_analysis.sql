/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 08_time_trend_analysis.sql

        Purpose:
        --------
        Analyze recruitment activity and hiring trends
        over time.

===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. MONTHLY JOB OPENINGS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        opened_date
    )::DATE AS month,

    COUNT(*) AS jobs_opened

FROM jobs

WHERE opened_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
2. MONTHLY JOB CLOSURES
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        closed_date
    )::DATE AS month,

    COUNT(*) AS jobs_closed

FROM jobs

WHERE closed_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
3. MONTHLY CANDIDATE REGISTRATIONS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        applied_date
    )::DATE AS month,

    COUNT(*) AS candidates

FROM candidates

WHERE applied_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
4. MONTHLY APPLICATIONS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        applied_date
    )::DATE AS month,

    COUNT(*) AS applications

FROM applications

WHERE applied_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
5. MONTHLY INTERVIEWS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        interview_date
    )::DATE AS month,

    COUNT(*) AS interviews

FROM interviews

WHERE interview_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
6. MONTHLY OFFERS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        offer_date
    )::DATE AS month,

    COUNT(*) AS offers

FROM offers

WHERE offer_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
7. MONTHLY PLACEMENTS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS month,

    COUNT(*) AS placements

FROM placements

WHERE placement_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
8. MONTHLY RECRUITMENT FUNNEL
===========================================================
*/

WITH monthly_data AS
(
    SELECT

        DATE_TRUNC(
            'month',
            a.applied_date
        )::DATE AS month,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM applications a

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        month
)

SELECT

    month,

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

FROM monthly_data

ORDER BY
    month;


/*
===========================================================
9. MONTHLY OFFER ACCEPTANCE
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        offer_date
    )::DATE AS month,

    COUNT(*) AS total_offers,

    COUNT(*)
        FILTER (
            WHERE offer_status = 'Accepted'
        ) AS accepted_offers,

    COUNT(*)
        FILTER (
            WHERE offer_status = 'Declined'
        ) AS declined_offers,

    ROUND(
        COUNT(*)
        FILTER (
            WHERE offer_status = 'Accepted'
        )::NUMERIC
        /
        NULLIF(
            COUNT(*),
            0
        )
        * 100,
        2
    ) AS acceptance_rate

FROM offers

WHERE offer_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
10. MONTHLY PLACEMENT STATUS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS month,

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
            WHERE placement_status = 'Fell Through'
        ) AS fell_through

FROM placements

WHERE placement_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
11. QUARTERLY RECRUITMENT PERFORMANCE
===========================================================
*/

SELECT

    DATE_TRUNC(
        'quarter',
        applied_date
    )::DATE AS quarter,

    COUNT(*) AS applications

FROM applications

WHERE applied_date IS NOT NULL

GROUP BY
    quarter

ORDER BY
    quarter;


/*
===========================================================
12. QUARTERLY HIRING PERFORMANCE
===========================================================
*/

WITH quarterly_data AS
(
    SELECT

        DATE_TRUNC(
            'quarter',
            a.applied_date
        )::DATE AS quarter,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM applications a

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        quarter
)

SELECT

    quarter,

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

FROM quarterly_data

ORDER BY
    quarter;


/*
===========================================================
13. YEARLY RECRUITMENT PERFORMANCE
===========================================================
*/

WITH yearly_data AS
(
    SELECT

        EXTRACT(
            YEAR FROM a.applied_date
        )::INTEGER AS year,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM applications a

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        year
)

SELECT

    year,

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

FROM yearly_data

ORDER BY
    year;


/*
===========================================================
14. MONTHLY RECRUITER ACTIVITY
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        a.applied_date
    )::DATE AS month,

    r.recruiter_name,

    COUNT(*) AS applications

FROM applications a

LEFT JOIN recruiters r
    ON a.recruiter_id = r.recruiter_id

GROUP BY

    month,
    r.recruiter_name

ORDER BY

    month,
    applications DESC;


/*
===========================================================
15. MONTHLY JOB STATUS SNAPSHOT
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        opened_date
    )::DATE AS month,

    job_status,

    COUNT(*) AS jobs

FROM jobs

WHERE opened_date IS NOT NULL

GROUP BY

    month,
    job_status

ORDER BY

    month,
    jobs DESC;


/*
===========================================================
16. MONTHLY AVERAGE OFFERED SALARY
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        offer_date
    )::DATE AS month,

    COUNT(*) AS offers,

    ROUND(
        AVG(offered_salary),
        2
    ) AS average_salary,

    ROUND(
        MIN(offered_salary),
        2
    ) AS minimum_salary,

    ROUND(
        MAX(offered_salary),
        2
    ) AS maximum_salary

FROM offers

WHERE offer_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
17. MONTHLY AVERAGE TIME TO JOIN
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS month,

    COUNT(*) AS placements,

    ROUND(
        AVG(
            p.joining_date - p.placement_date
        ),
        2
    ) AS average_days_to_join

FROM placements p

WHERE

    p.placement_date IS NOT NULL
    AND p.joining_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
18. MONTHLY PLACEMENT SUCCESS RATE
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS month,

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
    ) AS guarantee_completion_rate

FROM placements

WHERE placement_date IS NOT NULL

GROUP BY
    month

ORDER BY
    month;


/*
===========================================================
19. MONTHLY APPLICATION GROWTH
===========================================================
*/

WITH monthly_applications AS
(
    SELECT

        DATE_TRUNC(
            'month',
            applied_date
        )::DATE AS month,

        COUNT(*) AS applications

    FROM applications

    WHERE applied_date IS NOT NULL

    GROUP BY
        month
)

SELECT

    month,

    applications,

    LAG(applications)
        OVER (
            ORDER BY month
        ) AS previous_month_applications,

    ROUND(
        (
            applications
            -
            LAG(applications)
            OVER (
                ORDER BY month
            )
        )::NUMERIC
        /
        NULLIF(
            LAG(applications)
            OVER (
                ORDER BY month
            ),
            0
        )
        * 100,
        2
    ) AS month_over_month_growth

FROM monthly_applications

ORDER BY
    month;


/*
===========================================================
20. MONTHLY PLACEMENT GROWTH
===========================================================
*/

WITH monthly_placements AS
(
    SELECT

        DATE_TRUNC(
            'month',
            placement_date
        )::DATE AS month,

        COUNT(*) AS placements

    FROM placements

    WHERE placement_date IS NOT NULL

    GROUP BY
        month
)

SELECT

    month,

    placements,

    LAG(placements)
        OVER (
            ORDER BY month
        ) AS previous_month_placements,

    ROUND(
        (
            placements
            -
            LAG(placements)
            OVER (
                ORDER BY month
            )
        )::NUMERIC
        /
        NULLIF(
            LAG(placements)
            OVER (
                ORDER BY month
            ),
            0
        )
        * 100,
        2
    ) AS month_over_month_growth

FROM monthly_placements

ORDER BY
    month;


/*
===========================================================
21. BEST PERFORMING MONTHS
===========================================================
*/

SELECT

    DATE_TRUNC(
        'month',
        placement_date
    )::DATE AS month,

    COUNT(*) AS placements

FROM placements

WHERE placement_date IS NOT NULL

GROUP BY
    month

ORDER BY
    placements DESC

LIMIT 10;


/*
===========================================================
22. MONTHLY RECRUITMENT SUMMARY
===========================================================
*/

WITH applications_monthly AS
(
    SELECT

        DATE_TRUNC(
            'month',
            applied_date
        )::DATE AS month,

        COUNT(*) AS applications

    FROM applications

    GROUP BY
        month
),

interviews_monthly AS
(
    SELECT

        DATE_TRUNC(
            'month',
            interview_date
        )::DATE AS month,

        COUNT(*) AS interviews

    FROM interviews

    GROUP BY
        month
),

offers_monthly AS
(
    SELECT

        DATE_TRUNC(
            'month',
            offer_date
        )::DATE AS month,

        COUNT(*) AS offers

    FROM offers

    GROUP BY
        month
),

placements_monthly AS
(
    SELECT

        DATE_TRUNC(
            'month',
            placement_date
        )::DATE AS month,

        COUNT(*) AS placements

    FROM placements

    GROUP BY
        month
)

SELECT

    COALESCE(
        a.month,
        i.month,
        o.month,
        p.month
    ) AS month,

    COALESCE(
        a.applications,
        0
    ) AS applications,

    COALESCE(
        i.interviews,
        0
    ) AS interviews,

    COALESCE(
        o.offers,
        0
    ) AS offers,

    COALESCE(
        p.placements,
        0
    ) AS placements

FROM applications_monthly a

FULL OUTER JOIN interviews_monthly i
    ON a.month = i.month

FULL OUTER JOIN offers_monthly o
    ON COALESCE(a.month, i.month) = o.month

FULL OUTER JOIN placements_monthly p
    ON COALESCE(a.month, i.month, o.month) = p.month

ORDER BY
    month;


/*
===========================================================
END OF TIME TREND ANALYSIS
===========================================================
*/