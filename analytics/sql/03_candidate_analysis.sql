/*
===========================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 03_candidate_analysis.sql

        Purpose:
        --------
        Analyze candidate profiles and identify patterns
        related to experience, education, location,
        work authorization, source, status, skills,
        applications, interviews, offers and placements.

        Business Questions:
        --------------------
        1. What is the candidate experience distribution?
        2. Which education levels are most common?
        3. Which locations provide the most candidates?
        4. Which work authorizations are most common?
        5. Which sources generate the most candidates?
        6. Which candidate statuses dominate?
        7. Which candidate groups receive interviews?
        8. Which candidate groups receive offers?
        9. Which candidate groups get placed?
        10. What are the strongest candidate sources?

===========================================================
*/


/*
===========================================================
SCHEMA CONFIGURATION
===========================================================
*/

SET search_path TO recruitment;


/*
===========================================================
1. TOTAL CANDIDATES
===========================================================
*/

SELECT
    COUNT(*) AS total_candidates
FROM candidates;


/*
===========================================================
2. CANDIDATE STATUS DISTRIBUTION
===========================================================
*/

SELECT
    status,
    COUNT(*) AS candidate_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM candidates),
            0
        )
        * 100,
        2
    ) AS percentage

FROM candidates

GROUP BY status

ORDER BY candidate_count DESC;


/*
===========================================================
3. EXPERIENCE DISTRIBUTION
===========================================================
*/

SELECT
    CASE
        WHEN experience_years < 2
            THEN '0-1 Years'

        WHEN experience_years BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN experience_years BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN experience_years BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END AS experience_group,

    COUNT(*) AS candidate_count,

    ROUND(
        AVG(experience_years),
        2
    ) AS average_experience

FROM candidates

GROUP BY
    CASE
        WHEN experience_years < 2
            THEN '0-1 Years'

        WHEN experience_years BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN experience_years BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN experience_years BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END

ORDER BY
    MIN(experience_years);


/*
===========================================================
4. EDUCATION DISTRIBUTION
===========================================================
*/

SELECT
    education,
    COUNT(*) AS candidate_count,

    ROUND(
        COUNT(*)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM candidates),
            0
        )
        * 100,
        2
    ) AS percentage

FROM candidates

GROUP BY education

ORDER BY candidate_count DESC;


/*
===========================================================
5. CANDIDATES BY LOCATION
===========================================================
*/

SELECT
    l.city,
    l.state,
    l.country,

    COUNT(c.candidate_id) AS candidate_count

FROM candidates c

LEFT JOIN locations l
    ON c.location_id = l.location_id

GROUP BY
    l.city,
    l.state,
    l.country

ORDER BY candidate_count DESC;


/*
===========================================================
6. CANDIDATES BY WORK AUTHORIZATION
===========================================================
*/

SELECT
    wa.authorization_name,

    COUNT(c.candidate_id) AS candidate_count,

    ROUND(
        COUNT(c.candidate_id)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM candidates),
            0
        )
        * 100,
        2
    ) AS percentage

FROM candidates c

LEFT JOIN work_authorizations wa
    ON c.work_authorization_id =
       wa.work_authorization_id

GROUP BY
    wa.authorization_name

ORDER BY candidate_count DESC;


/*
===========================================================
7. CANDIDATES BY SOURCE
===========================================================
*/

SELECT
    s.source_name,
    s.source_category,

    COUNT(c.candidate_id) AS candidate_count,

    ROUND(
        COUNT(c.candidate_id)::NUMERIC
        /
        NULLIF(
            (SELECT COUNT(*) FROM candidates),
            0
        )
        * 100,
        2
    ) AS percentage

FROM candidates c

LEFT JOIN sources s
    ON c.source_id = s.source_id

GROUP BY
    s.source_name,
    s.source_category

ORDER BY candidate_count DESC;


/*
===========================================================
8. SOURCE QUALITY ANALYSIS
===========================================================

Measures:

Candidates
Applications
Interviews
Offers
Placements

This helps determine whether a source generates
quality candidates rather than simply high volume.

===========================================================
*/

SELECT

    s.source_name,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviewed_candidates,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM sources s

LEFT JOIN candidates c
    ON s.source_id = c.source_id

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    s.source_name

ORDER BY
    placements DESC,
    offers DESC,
    candidates DESC;


/*
===========================================================
9. SOURCE CONVERSION ANALYSIS
===========================================================
*/

WITH source_metrics AS
(
    SELECT

        s.source_name,

        COUNT(DISTINCT c.candidate_id)
            AS candidates,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM sources s

    LEFT JOIN candidates c
        ON s.source_id = c.source_id

    LEFT JOIN applications a
        ON c.candidate_id = a.candidate_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        s.source_name
)

SELECT

    source_name,

    candidates,

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
        NULLIF(candidates, 0)
        * 100,
        2
    ) AS candidate_to_placement_rate

FROM source_metrics

ORDER BY
    placements DESC;


/*
===========================================================
10. EXPERIENCE VS RECRUITMENT OUTCOME
===========================================================
*/

SELECT

    CASE
        WHEN c.experience_years < 2
            THEN '0-1 Years'

        WHEN c.experience_years BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN c.experience_years BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN c.experience_years BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END AS experience_group,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM candidates c

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    CASE
        WHEN c.experience_years < 2
            THEN '0-1 Years'

        WHEN c.experience_years BETWEEN 2 AND 4
            THEN '2-4 Years'

        WHEN c.experience_years BETWEEN 5 AND 7
            THEN '5-7 Years'

        WHEN c.experience_years BETWEEN 8 AND 10
            THEN '8-10 Years'

        ELSE '11+ Years'
    END

ORDER BY
    MIN(c.experience_years);


/*
===========================================================
11. EXPERIENCE GROUP CONVERSION RATES
===========================================================
*/

WITH experience_metrics AS
(
    SELECT

        CASE
            WHEN c.experience_years < 2
                THEN '0-1 Years'

            WHEN c.experience_years BETWEEN 2 AND 4
                THEN '2-4 Years'

            WHEN c.experience_years BETWEEN 5 AND 7
                THEN '5-7 Years'

            WHEN c.experience_years BETWEEN 8 AND 10
                THEN '8-10 Years'

            ELSE '11+ Years'
        END AS experience_group,

        COUNT(DISTINCT c.candidate_id)
            AS candidates,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT i.application_id)
            AS interviews,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM candidates c

    LEFT JOIN applications a
        ON c.candidate_id = a.candidate_id

    LEFT JOIN interviews i
        ON a.application_id = i.application_id

    LEFT JOIN offers o
        ON a.application_id = o.application_id

    LEFT JOIN placements p
        ON o.offer_id = p.offer_id

    GROUP BY
        CASE
            WHEN c.experience_years < 2
                THEN '0-1 Years'

            WHEN c.experience_years BETWEEN 2 AND 4
                THEN '2-4 Years'

            WHEN c.experience_years BETWEEN 5 AND 7
                THEN '5-7 Years'

            WHEN c.experience_years BETWEEN 8 AND 10
                THEN '8-10 Years'

            ELSE '11+ Years'
        END
)

SELECT

    experience_group,

    candidates,

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

FROM experience_metrics

ORDER BY
    CASE experience_group
        WHEN '0-1 Years' THEN 1
        WHEN '2-4 Years' THEN 2
        WHEN '5-7 Years' THEN 3
        WHEN '8-10 Years' THEN 4
        WHEN '11+ Years' THEN 5
    END;


/*
===========================================================
12. EDUCATION VS RECRUITMENT OUTCOME
===========================================================
*/

SELECT

    c.education,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM candidates c

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    c.education

ORDER BY
    placements DESC;


/*
===========================================================
13. LOCATION VS RECRUITMENT OUTCOME
===========================================================
*/

SELECT

    l.city,
    l.state,
    l.country,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM candidates c

LEFT JOIN locations l
    ON c.location_id = l.location_id

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    l.city,
    l.state,
    l.country

ORDER BY
    placements DESC;


/*
===========================================================
14. WORK AUTHORIZATION VS RECRUITMENT OUTCOME
===========================================================
*/

SELECT

    wa.authorization_name,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM work_authorizations wa

LEFT JOIN candidates c
    ON wa.work_authorization_id =
       c.work_authorization_id

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    wa.authorization_name

ORDER BY
    placements DESC;


/*
===========================================================
15. TOP CANDIDATES BY APPLICATION ACTIVITY
===========================================================
*/

SELECT

    c.candidate_id,

    c.candidate_name,

    c.experience_years,

    COUNT(a.application_id)
        AS total_applications,

    COUNT(DISTINCT i.application_id)
        AS interviews,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM candidates c

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY

    c.candidate_id,
    c.candidate_name,
    c.experience_years

ORDER BY
    total_applications DESC

LIMIT 20;


/*
===========================================================
16. CANDIDATE SKILL ANALYSIS
===========================================================
*/

SELECT

    s.skill_name,

    COUNT(DISTINCT cs.candidate_id)
        AS candidates_with_skill,

    ROUND(
        AVG(cs.years_experience),
        2
    ) AS average_skill_experience

FROM candidate_skills cs

INNER JOIN skills s
    ON cs.skill_id = s.skill_id

GROUP BY
    s.skill_name

ORDER BY
    candidates_with_skill DESC

LIMIT 20;


/*
===========================================================
17. SKILL VS PLACEMENT ANALYSIS
===========================================================
*/

SELECT

    s.skill_name,

    COUNT(DISTINCT cs.candidate_id)
        AS candidates_with_skill,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        COUNT(DISTINCT p.placement_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT cs.candidate_id),
            0
        )
        * 100,
        2
    ) AS placement_rate

FROM candidate_skills cs

INNER JOIN skills s
    ON cs.skill_id = s.skill_id

LEFT JOIN candidates c
    ON cs.candidate_id = c.candidate_id

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id

GROUP BY
    s.skill_name

HAVING
    COUNT(DISTINCT cs.candidate_id) >= 20

ORDER BY
    placement_rate DESC;


/*
===========================================================
18. FINAL CANDIDATE ANALYTICS SUMMARY
===========================================================
*/

SELECT

    COUNT(DISTINCT c.candidate_id)
        AS total_candidates,

    ROUND(
        AVG(c.experience_years),
        2
    ) AS average_experience,

    COUNT(DISTINCT a.application_id)
        AS total_applications,

    COUNT(DISTINCT i.application_id)
        AS interviewed_candidates,

    COUNT(DISTINCT o.offer_id)
        AS total_offers,

    COUNT(DISTINCT p.placement_id)
        AS total_placements,

    ROUND(
        COUNT(DISTINCT i.application_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT a.application_id),
            0
        )
        * 100,
        2
    ) AS interview_rate,

    ROUND(
        COUNT(DISTINCT o.offer_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT i.application_id),
            0
        )
        * 100,
        2
    ) AS offer_rate,

    ROUND(
        COUNT(DISTINCT p.placement_id)::NUMERIC
        /
        NULLIF(
            COUNT(DISTINCT o.offer_id),
            0
        )
        * 100,
        2
    ) AS placement_rate

FROM candidates c

LEFT JOIN applications a
    ON c.candidate_id = a.candidate_id

LEFT JOIN interviews i
    ON a.application_id = i.application_id

LEFT JOIN offers o
    ON a.application_id = o.application_id

LEFT JOIN placements p
    ON o.offer_id = p.offer_id;


/*
===========================================================
END OF CANDIDATE ANALYSIS
===========================================================
*/