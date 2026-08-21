

SET search_path TO recruitment, public;

/* ================================================================
   TALENTIQ -  SKILL ANALYSIS
   ================================================================ */

/* Query 1 - Total Skills */
SELECT COUNT(*) AS total_skills
FROM skills;


/* Query 2 - Candidate Skill Distribution */
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count,
    ROUND(
        COUNT(DISTINCT cs.candidate_id)::numeric
        / NULLIF((SELECT COUNT(*) FROM candidates), 0) * 100, 2
    ) AS candidate_percentage
FROM skills s
LEFT JOIN candidate_skills cs ON cs.skill_id = s.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY candidate_count DESC, s.skill_name;


/* Query 3 - Top 20 Candidate Skills */
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY candidate_count DESC, s.skill_name
LIMIT 20;


/* Query 4 - Skill Category Distribution */
SELECT
    s.skill_category,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count,
    COUNT(DISTINCT js.job_id) AS job_count
FROM skills s
LEFT JOIN candidate_skills cs ON cs.skill_id = s.skill_id
LEFT JOIN job_skills js ON js.skill_id = s.skill_id
GROUP BY s.skill_category
ORDER BY candidate_count DESC;


/* Query 5 - Most Demanded Job Skills */
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT js.job_id) AS job_demand,
    ROUND(
        COUNT(DISTINCT js.job_id)::numeric
        / NULLIF((SELECT COUNT(*) FROM jobs), 0) * 100, 2
    ) AS demand_percentage
FROM skills s
JOIN job_skills js ON js.skill_id = s.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY job_demand DESC, s.skill_name
LIMIT 20;


/* Query 6 - Skill Demand, Accepted Offers and Placements */
WITH demand AS (
    SELECT skill_id, COUNT(DISTINCT job_id) AS job_demand
    FROM job_skills
    GROUP BY skill_id
),
accepted AS (
    SELECT
        js.skill_id,
        COUNT(DISTINCT o.offer_id) AS accepted_offers
    FROM job_skills js
    JOIN applications a ON a.job_id = js.job_id
    JOIN offers o ON o.application_id = a.application_id
    WHERE LOWER(TRIM(o.offer_status)) = 'accepted'
    GROUP BY js.skill_id
),
placed AS (
    SELECT
        js.skill_id,
        COUNT(DISTINCT p.placement_id) AS placements
    FROM job_skills js
    JOIN applications a ON a.job_id = js.job_id
    JOIN offers o ON o.application_id = a.application_id
    JOIN placements p ON p.offer_id = o.offer_id
    GROUP BY js.skill_id
)
SELECT
    s.skill_name,
    COALESCE(d.job_demand, 0) AS job_demand,
    COALESCE(ac.accepted_offers, 0) AS accepted_offers,
    COALESCE(pl.placements, 0) AS placements,
    ROUND(
        COALESCE(ac.accepted_offers, 0)::numeric
        / NULLIF(d.job_demand, 0) * 100, 2
    ) AS offer_rate,
    ROUND(
        COALESCE(pl.placements, 0)::numeric
        / NULLIF(ac.accepted_offers, 0) * 100, 2
    ) AS placement_rate
FROM skills s
JOIN demand d ON d.skill_id = s.skill_id
LEFT JOIN accepted ac ON ac.skill_id = s.skill_id
LEFT JOIN placed pl ON pl.skill_id = s.skill_id
ORDER BY d.job_demand DESC, s.skill_name;



/* =========================================================
   QUERY 7 — CANDIDATE SUPPLY VS JOB DEMAND
   =========================================================
   Positive gap  = candidate surplus
   Negative gap  = candidate shortage
   ========================================================= */

WITH supply AS (
    SELECT
        skill_id,
        COUNT(DISTINCT candidate_id) AS candidate_supply
    FROM candidate_skills
    GROUP BY skill_id
),
demand AS (
    SELECT
        skill_id,
        COUNT(DISTINCT job_id) AS job_demand
    FROM job_skills
    GROUP BY skill_id
)
SELECT
    s.skill_name,
    s.skill_category,

    COALESCE(sp.candidate_supply, 0) AS candidate_supply,
    COALESCE(d.job_demand, 0) AS job_demand,

    COALESCE(sp.candidate_supply, 0)
        - COALESCE(d.job_demand, 0) AS skill_gap,

    CASE
        WHEN COALESCE(sp.candidate_supply, 0)
             < COALESCE(d.job_demand, 0)
            THEN 'SHORTAGE'

        WHEN COALESCE(sp.candidate_supply, 0)
             = COALESCE(d.job_demand, 0)
            THEN 'BALANCED'

        ELSE 'SURPLUS'
    END AS market_status

FROM skills s

LEFT JOIN supply sp
    ON sp.skill_id = s.skill_id

LEFT JOIN demand d
    ON d.skill_id = s.skill_id

WHERE COALESCE(d.job_demand, 0) > 0

ORDER BY skill_gap ASC, s.skill_name;


/* =========================================================
   QUERY 8 — SKILL GAP ANALYSIS
   =========================================================
   Measures candidate supply against job demand
   for each skill.

   gap = candidate supply - job demand

   Positive = surplus
   Negative = shortage
   Zero     = balanced
   ========================================================= */

WITH candidate_supply AS (
    SELECT
        skill_id,
        COUNT(DISTINCT candidate_id) AS candidate_supply
    FROM candidate_skills
    GROUP BY skill_id
),

job_demand AS (
    SELECT
        skill_id,
        COUNT(DISTINCT job_id) AS job_demand
    FROM job_skills
    GROUP BY skill_id
),

skill_gap AS (
    SELECT
        s.skill_id,
        s.skill_name,
        s.skill_category,

        COALESCE(cs.candidate_supply, 0) AS candidate_supply,
        COALESCE(jd.job_demand, 0) AS job_demand

    FROM skills s

    LEFT JOIN candidate_supply cs
        ON cs.skill_id = s.skill_id

    LEFT JOIN job_demand jd
        ON jd.skill_id = s.skill_id
)

SELECT
    skill_name,
    skill_category,
    candidate_supply,
    job_demand,

    candidate_supply - job_demand AS skill_gap,

    CASE
        WHEN candidate_supply < job_demand
            THEN 'SHORTAGE'

        WHEN candidate_supply = job_demand
            THEN 'BALANCED'

        ELSE 'SURPLUS'
    END AS gap_status

FROM skill_gap

WHERE job_demand > 0

ORDER BY
    skill_gap ASC,
    skill_name;



/* Query 9 - Candidate Skill Proficiency */
SELECT
    s.skill_name,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count,
    ROUND(AVG(cs.years_experience)::numeric, 2) AS avg_years_experience,
    ROUND(MIN(cs.years_experience)::numeric, 2) AS min_years_experience,
    ROUND(MAX(cs.years_experience)::numeric, 2) AS max_years_experience
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
GROUP BY s.skill_id, s.skill_name
ORDER BY avg_years_experience DESC, candidate_count DESC;


/* Query 10 - Highest Average Experience */
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count,
    ROUND(AVG(cs.years_experience)::numeric, 2) AS avg_years_experience
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
HAVING COUNT(DISTINCT cs.candidate_id) >= 10
ORDER BY avg_years_experience DESC
LIMIT 20;


/* Query 11 - Proficiency Level Distribution */
SELECT
    s.skill_name,
    cs.proficiency_level,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count
FROM candidate_skills cs
JOIN skills s ON s.skill_id = cs.skill_id
GROUP BY s.skill_id, s.skill_name, cs.proficiency_level
ORDER BY s.skill_name, candidate_count DESC;


/* Query 12 - Skill Demand by Category */
SELECT
    s.skill_category,
    COUNT(DISTINCT s.skill_id) AS skills_demanded,
    COUNT(DISTINCT js.job_id) AS jobs_demanding_skill
FROM skills s
JOIN job_skills js ON js.skill_id = s.skill_id
GROUP BY s.skill_category
ORDER BY jobs_demanding_skill DESC;


/* Query 13 - Skills Associated with Accepted Offers */
WITH accepted AS (
    SELECT DISTINCT o.offer_id, a.candidate_id
    FROM offers o
    JOIN applications a ON a.application_id = o.application_id
    WHERE LOWER(TRIM(o.offer_status)) = 'accepted'
)
SELECT
    s.skill_name,
    COUNT(DISTINCT ac.candidate_id) AS candidates_with_skill,
    COUNT(DISTINCT ac.offer_id) AS accepted_offers,
    ROUND(
        COUNT(DISTINCT ac.offer_id)::numeric
        / NULLIF(COUNT(DISTINCT ac.candidate_id), 0) * 100, 2
    ) AS association_rate
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
JOIN accepted ac ON ac.candidate_id = cs.candidate_id
GROUP BY s.skill_id, s.skill_name
ORDER BY association_rate DESC, accepted_offers DESC;


/* Query 14 - Skills Associated with Placements */
WITH placed AS (
    SELECT DISTINCT p.placement_id, a.candidate_id
    FROM placements p
    JOIN offers o ON o.offer_id = p.offer_id
    JOIN applications a ON a.application_id = o.application_id
)
SELECT
    s.skill_name,
    COUNT(DISTINCT pc.candidate_id) AS candidates_with_skill,
    COUNT(DISTINCT pc.placement_id) AS placements,
    ROUND(
        COUNT(DISTINCT pc.placement_id)::numeric
        / NULLIF(COUNT(DISTINCT pc.candidate_id), 0) * 100, 2
    ) AS association_rate
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
JOIN placed pc ON pc.candidate_id = cs.candidate_id
GROUP BY s.skill_id, s.skill_name
ORDER BY association_rate DESC, placements DESC;


/* Query 15 - Skill Demand Conversion */
WITH demand AS (
    SELECT skill_id, COUNT(DISTINCT job_id) AS jobs_demanding
    FROM job_skills
    GROUP BY skill_id
),
accepted AS (
    SELECT js.skill_id, COUNT(DISTINCT o.offer_id) AS accepted_offers
    FROM job_skills js
    JOIN applications a ON a.job_id = js.job_id
    JOIN offers o ON o.application_id = a.application_id
    WHERE LOWER(TRIM(o.offer_status)) = 'accepted'
    GROUP BY js.skill_id
),
placed AS (
    SELECT js.skill_id, COUNT(DISTINCT p.placement_id) AS placements
    FROM job_skills js
    JOIN applications a ON a.job_id = js.job_id
    JOIN offers o ON o.application_id = a.application_id
    JOIN placements p ON p.offer_id = o.offer_id
    GROUP BY js.skill_id
)
SELECT
    s.skill_name,
    d.jobs_demanding,
    COALESCE(a.accepted_offers, 0) AS accepted_offers,
    COALESCE(p.placements, 0) AS placements,
    ROUND(
        COALESCE(a.accepted_offers, 0)::numeric
        / NULLIF(d.jobs_demanding, 0) * 100, 2
    ) AS offer_conversion_rate,
    ROUND(
        COALESCE(p.placements, 0)::numeric
        / NULLIF(d.jobs_demanding, 0) * 100, 2
    ) AS placement_conversion_rate
FROM skills s
JOIN demand d ON d.skill_id = s.skill_id
LEFT JOIN accepted a ON a.skill_id = s.skill_id
LEFT JOIN placed p ON p.skill_id = s.skill_id
ORDER BY placement_conversion_rate DESC, offer_conversion_rate DESC;


/* Query 16 - Top Skills by Placement Association */
WITH placed AS (
    SELECT DISTINCT p.placement_id, a.candidate_id
    FROM placements p
    JOIN offers o ON o.offer_id = p.offer_id
    JOIN applications a ON a.application_id = o.application_id
)
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(DISTINCT pc.placement_id) AS placements
FROM skills s
JOIN candidate_skills cs ON cs.skill_id = s.skill_id
JOIN placed pc ON pc.candidate_id = cs.candidate_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY placements DESC, s.skill_name
LIMIT 20;

/* =========================================================
   QUERY 17 — LOWEST CANDIDATE SUPPLY RELATIVE TO DEMAND
   ========================================================= */

WITH candidate_supply AS (
    SELECT
        skill_id,
        COUNT(DISTINCT candidate_id) AS candidate_supply
    FROM candidate_skills
    GROUP BY skill_id
),

job_demand AS (
    SELECT
        skill_id,
        COUNT(DISTINCT job_id) AS job_demand
    FROM job_skills
    GROUP BY skill_id
)

SELECT
    s.skill_name,
    s.skill_category,

    COALESCE(cs.candidate_supply, 0) AS candidate_supply,

    COALESCE(jd.job_demand, 0) AS job_demand,

    ROUND(
        COALESCE(cs.candidate_supply, 0)::numeric
        / NULLIF(jd.job_demand, 0),
        2
    ) AS candidate_to_job_ratio,

    CASE
        WHEN COALESCE(cs.candidate_supply, 0) = 0
            THEN 'CRITICAL'

        WHEN COALESCE(cs.candidate_supply, 0)::numeric
             / NULLIF(jd.job_demand, 0) < 2
            THEN 'LOW SUPPLY'

        WHEN COALESCE(cs.candidate_supply, 0)::numeric
             / NULLIF(jd.job_demand, 0) < 5
            THEN 'MODERATE SUPPLY'

        ELSE 'HIGH SUPPLY'
    END AS supply_status

FROM skills s

JOIN job_demand jd
    ON jd.skill_id = s.skill_id

LEFT JOIN candidate_supply cs
    ON cs.skill_id = s.skill_id

ORDER BY
    candidate_to_job_ratio ASC,
    s.skill_name

LIMIT 20;
/* =========================================================
   QUERY 18 — SKILLS WITH CANDIDATE SURPLUS
   ========================================================= */

WITH candidate_supply AS (
    SELECT
        skill_id,
        COUNT(DISTINCT candidate_id) AS candidate_supply
    FROM candidate_skills
    GROUP BY skill_id
),

job_demand AS (
    SELECT
        skill_id,
        COUNT(DISTINCT job_id) AS job_demand
    FROM job_skills
    GROUP BY skill_id
)

SELECT
    s.skill_name,
    s.skill_category,

    COALESCE(cs.candidate_supply, 0) AS candidate_supply,
    COALESCE(jd.job_demand, 0) AS job_demand,

    COALESCE(cs.candidate_supply, 0)
        - COALESCE(jd.job_demand, 0) AS surplus_amount

FROM skills s

LEFT JOIN candidate_supply cs
    ON cs.skill_id = s.skill_id

LEFT JOIN job_demand jd
    ON jd.skill_id = s.skill_id

WHERE COALESCE(cs.candidate_supply, 0)
      > COALESCE(jd.job_demand, 0)

ORDER BY
    surplus_amount DESC,
    s.skill_name;


/* Query 19 - Skill Coverage */
SELECT
    (SELECT COUNT(*) FROM skills) AS total_skills,
    (SELECT COUNT(DISTINCT skill_id) FROM candidate_skills)
        AS candidate_skills_used,
    (SELECT COUNT(DISTINCT skill_id) FROM job_skills)
        AS job_skills_used,
    ROUND(
        (SELECT COUNT(DISTINCT skill_id) FROM candidate_skills)::numeric
        / NULLIF((SELECT COUNT(*) FROM skills), 0) * 100, 2
    ) AS candidate_skill_coverage_pct,
    ROUND(
        (SELECT COUNT(DISTINCT skill_id) FROM job_skills)::numeric
        / NULLIF((SELECT COUNT(*) FROM skills), 0) * 100, 2
    ) AS job_skill_coverage_pct;


/* Query 20 - Skill Analysis Summary */
SELECT
    (SELECT COUNT(*) FROM skills) AS total_skills,
    (SELECT COUNT(DISTINCT candidate_id) FROM candidate_skills)
        AS candidates_with_skills,
    (SELECT COUNT(DISTINCT job_id) FROM job_skills)
        AS jobs_with_skills,
    (SELECT COUNT(DISTINCT skill_id) FROM candidate_skills)
        AS candidate_skills_used,
    (SELECT COUNT(DISTINCT skill_id) FROM job_skills)
        AS job_skills_used,
    (SELECT COUNT(*) FROM candidate_skills)
        AS candidate_skill_records,
    (SELECT COUNT(*) FROM job_skills)
        AS job_skill_records;
