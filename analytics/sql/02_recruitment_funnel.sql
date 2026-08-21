/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 02_recruitment_funnel.sql

        Purpose:
        --------
        Analyze the complete recruitment funnel.

        Funnel:

        Applications
              ↓
        Submitted to Client
              ↓
        Interviews
              ↓
        Offers
              ↓
        Accepted Offers
              ↓
        Placements

        Business Questions:
        --------------------
        1. How many applications enter each stage?
        2. What percentage converts to the next stage?
        3. Where is the biggest drop-off?
        4. What is the overall hiring conversion?

===========================================================
*/


SET search_path TO recruitment;


/*
===========================================================
1. TOTAL APPLICATIONS
===========================================================
*/

SELECT
    COUNT(*) AS total_applications
FROM applications;


/*
===========================================================
2. APPLICATIONS SUBMITTED TO CLIENT
===========================================================

An application is considered submitted when
submitted_to_client_date is not NULL.

===========================================================
*/

SELECT
    COUNT(*) AS submitted_to_client
FROM applications
WHERE submitted_to_client_date IS NOT NULL;


/*
===========================================================
3. APPLICATIONS WITH INTERVIEWS
===========================================================
*/

SELECT
    COUNT(DISTINCT application_id) AS applications_with_interview
FROM interviews;


/*
===========================================================
4. APPLICATIONS WITH OFFERS
===========================================================
*/

SELECT
    COUNT(DISTINCT application_id) AS applications_with_offer
FROM offers;


/*
===========================================================
5. ACCEPTED OFFERS
===========================================================
*/

SELECT
    COUNT(*) AS accepted_offers
FROM offers
WHERE offer_status = 'Accepted';


/*
===========================================================
6. TOTAL PLACEMENTS
===========================================================
*/

SELECT
    COUNT(*) AS total_placements
FROM placements;


/*
===========================================================
7. APPLICATION → SUBMITTED TO CLIENT
===========================================================
*/

SELECT
    ROUND(
        COUNT(*) FILTER (
            WHERE submitted_to_client_date IS NOT NULL
        )::NUMERIC
        / NULLIF(COUNT(*), 0)
        * 100,
        2
    ) AS application_to_client_rate
FROM applications;


/*
===========================================================
8. SUBMITTED TO CLIENT → INTERVIEW
===========================================================
*/

SELECT
    ROUND(
        COUNT(DISTINCT i.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(*) FILTER (
                WHERE a.submitted_to_client_date IS NOT NULL
            ),
            0
        )
        * 100,
        2
    ) AS client_to_interview_rate
FROM applications a
LEFT JOIN interviews i
    ON a.application_id = i.application_id
WHERE a.submitted_to_client_date IS NOT NULL;


/*
===========================================================
9. INTERVIEW → OFFER
===========================================================
*/

SELECT
    ROUND(
        COUNT(DISTINCT o.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT i.application_id),
            0
        )
        * 100,
        2
    ) AS interview_to_offer_rate
FROM interviews i
LEFT JOIN offers o
    ON i.application_id = o.application_id;


/*
===========================================================
10. OFFER → ACCEPTED OFFER
===========================================================
*/

SELECT
    ROUND(
        COUNT(*) FILTER (
            WHERE offer_status = 'Accepted'
        )::NUMERIC
        /
        NULLIF(COUNT(*), 0)
        * 100,
        2
    ) AS offer_acceptance_rate
FROM offers;


/*
===========================================================
11. ACCEPTED OFFER → PLACEMENT
===========================================================
*/

SELECT
    ROUND(
        COUNT(DISTINCT p.offer_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT o.offer_id)
            FILTER (
                WHERE o.offer_status = 'Accepted'
            ),
            0
        )
        * 100,
        2
    ) AS accepted_offer_to_placement_rate
FROM offers o
LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


/*
===========================================================
12. OVERALL APPLICATION → PLACEMENT RATE
===========================================================
*/

SELECT
    ROUND(
        COUNT(DISTINCT p.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        )
        * 100,
        2
    ) AS overall_application_to_placement_rate
FROM applications a
LEFT JOIN offers o
    ON a.application_id = o.application_id
LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


/*
===========================================================
13. FUNNEL SUMMARY TABLE
===========================================================

This creates one result set containing the complete
recruitment funnel.

===========================================================
*/

SELECT
    'Applications' AS funnel_stage,
    COUNT(*) AS candidate_count,
    100.00 AS percentage_of_applications
FROM applications

UNION ALL

SELECT
    'Submitted to Client',
    COUNT(*),
    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM applications),
            0
        )
        * 100,
        2
    )
FROM applications
WHERE submitted_to_client_date IS NOT NULL

UNION ALL

SELECT
    'Interview',
    COUNT(DISTINCT application_id),
    ROUND(
        COUNT(DISTINCT application_id)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM applications),
            0
        )
        * 100,
        2
    )
FROM interviews

UNION ALL

SELECT
    'Offer',
    COUNT(DISTINCT application_id),
    ROUND(
        COUNT(DISTINCT application_id)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM applications),
            0
        )
        * 100,
        2
    )
FROM offers

UNION ALL

SELECT
    'Accepted Offer',
    COUNT(*),
    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM applications),
            0
        )
        * 100,
        2
    )
FROM offers
WHERE offer_status = 'Accepted'

UNION ALL

SELECT
    'Placement',
    COUNT(*),
    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM applications),
            0
        )
        * 100,
        2
    )
FROM placements

ORDER BY
    CASE funnel_stage
        WHEN 'Applications' THEN 1
        WHEN 'Submitted to Client' THEN 2
        WHEN 'Interview' THEN 3
        WHEN 'Offer' THEN 4
        WHEN 'Accepted Offer' THEN 5
        WHEN 'Placement' THEN 6
    END;


/*
===========================================================
14. FUNNEL DROP-OFF ANALYSIS
===========================================================
*/

WITH funnel AS
(
    SELECT
        1 AS stage_order,
        'Applications' AS stage,
        COUNT(*) AS total
    FROM applications

    UNION ALL

    SELECT
        2,
        'Submitted to Client',
        COUNT(*)
    FROM applications
    WHERE submitted_to_client_date IS NOT NULL

    UNION ALL

    SELECT
        3,
        'Interview',
        COUNT(DISTINCT application_id)
    FROM interviews

    UNION ALL

    SELECT
        4,
        'Offer',
        COUNT(DISTINCT application_id)
    FROM offers

    UNION ALL

    SELECT
        5,
        'Accepted Offer',
        COUNT(*)
    FROM offers
    WHERE offer_status = 'Accepted'

    UNION ALL

    SELECT
        6,
        'Placement',
        COUNT(*)
    FROM placements
),

funnel_with_previous AS
(
    SELECT
        stage_order,
        stage,
        total,
        LAG(total) OVER (
            ORDER BY stage_order
        ) AS previous_stage_total
    FROM funnel
)

SELECT
    stage_order,
    stage,
    total,
    previous_stage_total,

    CASE
        WHEN previous_stage_total IS NULL
        THEN NULL

        ELSE previous_stage_total - total
    END AS drop_off_count,

    CASE
        WHEN previous_stage_total IS NULL
             OR previous_stage_total = 0
        THEN NULL

        ELSE ROUND(
            (
                previous_stage_total - total
            )::NUMERIC
            /
            previous_stage_total
            * 100,
            2
        )
    END AS drop_off_percentage

FROM funnel_with_previous

ORDER BY stage_order;


/*
===========================================================
15. BIGGEST FUNNEL DROP-OFF
===========================================================
*/

WITH funnel AS
(
    SELECT
        1 AS stage_order,
        'Applications' AS stage,
        COUNT(*) AS total
    FROM applications

    UNION ALL

    SELECT
        2,
        'Submitted to Client',
        COUNT(*)
    FROM applications
    WHERE submitted_to_client_date IS NOT NULL

    UNION ALL

    SELECT
        3,
        'Interview',
        COUNT(DISTINCT application_id)
    FROM interviews

    UNION ALL

    SELECT
        4,
        'Offer',
        COUNT(DISTINCT application_id)
    FROM offers

    UNION ALL

    SELECT
        5,
        'Accepted Offer',
        COUNT(*)
    FROM offers
    WHERE offer_status = 'Accepted'

    UNION ALL

    SELECT
        6,
        'Placement',
        COUNT(*)
    FROM placements
),

dropoff AS
(
    SELECT
        stage,
        total,
        LAG(total) OVER (
            ORDER BY stage_order
        ) AS previous_total
    FROM funnel
)

SELECT
    stage,
    previous_total,
    total,
    previous_total - total AS drop_off_count,

    ROUND(
        (
            previous_total - total
        )::NUMERIC
        /
        NULLIF(previous_total, 0)
        * 100,
        2
    ) AS drop_off_percentage

FROM dropoff

WHERE previous_total IS NOT NULL

ORDER BY drop_off_percentage DESC

LIMIT 1;


/*
===========================================================
END OF RECRUITMENT FUNNEL ANALYSIS
===========================================================
*/