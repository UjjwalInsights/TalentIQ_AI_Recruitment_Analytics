

SET search_path TO recruitment, public;

/*
================================================================
                TALENTIQ - ADVANCED INSIGHTS
================================================================

Purpose:
    Executive-level recruitment analytics and business insights.

Confirmed tables used:
    candidates
    applications
    jobs
    offers
    placements
    skills
    candidate_skills
    job_skills

This file focuses on:
    1. Executive Snapshot
    2. Application Stage Distribution
    3. Application Status Distribution
    4. Recruitment Funnel
    5. Recruitment Cycle Time
    6. Recruiter Performance
    7. Job Performance
    8. Job Aging
    9. Application Aging / Pipeline Risk
   10. Candidate Source Effectiveness
   11. Repeat Candidate Analysis
   12. Salary Alignment
   13. Offer Acceptance by Salary Band
   14. Placement Analysis
   15. Job Conversion Analysis
   16. Recruitment Risk Analysis
   17. Executive Opportunity Analysis
   18. Final Executive Summary

================================================================
*/


/*
================================================================
SECTION 1 : EXECUTIVE RECRUITMENT SNAPSHOT
================================================================
*/

SELECT
    (SELECT COUNT(*) FROM candidates)
        AS total_candidates,

    (SELECT COUNT(*) FROM jobs)
        AS total_jobs,

    (SELECT COUNT(*) FROM applications)
        AS total_applications,

    (SELECT COUNT(*) FROM offers)
        AS total_offers,

    (SELECT COUNT(*)
     FROM offers
     WHERE LOWER(TRIM(offer_status)) = 'accepted')
        AS accepted_offers,

    (SELECT COUNT(*) FROM placements)
        AS total_placements,

    ROUND(
        (SELECT COUNT(*) FROM applications)::numeric
        / NULLIF((SELECT COUNT(*) FROM candidates), 0),
        2
    ) AS applications_per_candidate,

    ROUND(
        (SELECT COUNT(*) FROM offers)::numeric
        / NULLIF((SELECT COUNT(*) FROM applications), 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        (SELECT COUNT(*)
         FROM offers
         WHERE LOWER(TRIM(offer_status)) = 'accepted')::numeric
        / NULLIF((SELECT COUNT(*) FROM offers), 0) * 100,
        2
    ) AS offer_acceptance_pct,

    ROUND(
        (SELECT COUNT(*) FROM placements)::numeric
        / NULLIF(
            (SELECT COUNT(*)
             FROM offers
             WHERE LOWER(TRIM(offer_status)) = 'accepted'),
            0
        ) * 100,
        2
    ) AS accepted_offer_to_placement_pct;


/*
================================================================
SECTION 2 : APPLICATION STAGE DISTRIBUTION
================================================================

Shows where candidates currently sit in the recruitment pipeline.
================================================================
*/

SELECT
    COALESCE(NULLIF(TRIM(current_stage), ''), 'UNKNOWN')
        AS current_stage,

    COUNT(*) AS application_count,

    ROUND(
        COUNT(*)::numeric
        / NULLIF((SELECT COUNT(*) FROM applications), 0) * 100,
        2
    ) AS percentage_of_applications

FROM applications

GROUP BY
    COALESCE(NULLIF(TRIM(current_stage), ''), 'UNKNOWN')

ORDER BY
    application_count DESC;


/*
================================================================
SECTION 3 : APPLICATION STATUS DISTRIBUTION
================================================================
*/

SELECT
    COALESCE(NULLIF(TRIM(status), ''), 'UNKNOWN')
        AS application_status,

    COUNT(*) AS application_count,

    ROUND(
        COUNT(*)::numeric
        / NULLIF((SELECT COUNT(*) FROM applications), 0) * 100,
        2
    ) AS percentage_of_applications

FROM applications

GROUP BY
    COALESCE(NULLIF(TRIM(status), ''), 'UNKNOWN')

ORDER BY
    application_count DESC;


/*
================================================================
SECTION 4 : RECRUITMENT FUNNEL
================================================================

Measures the major measurable recruitment milestones.

Applications
      ↓
Submitted to Client
      ↓
Offer
      ↓
Accepted Offer
      ↓
Placement
================================================================
*/

WITH funnel AS (

    SELECT
        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT CASE
            WHEN a.submitted_to_client_date IS NOT NULL
            THEN a.application_id
        END)
            AS submitted_to_client,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
            THEN o.offer_id
        END)
            AS accepted_offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM applications a

    LEFT JOIN offers o
        ON o.application_id = a.application_id

    LEFT JOIN placements p
        ON p.offer_id = o.offer_id
)

SELECT
    applications,
    submitted_to_client,
    offers,
    accepted_offers,
    placements,

    ROUND(
        submitted_to_client::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_client_pct,

    ROUND(
        offers::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        accepted_offers::numeric
        / NULLIF(offers, 0) * 100,
        2
    ) AS offer_acceptance_pct,

    ROUND(
        placements::numeric
        / NULLIF(accepted_offers, 0) * 100,
        2
    ) AS accepted_to_placement_pct,

    ROUND(
        placements::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS overall_placement_rate_pct

FROM funnel;


/*
================================================================
SECTION 5 : RECRUITMENT CYCLE TIME
================================================================

Measures the time required to move candidates through
major recruitment milestones.
================================================================
*/

WITH application_to_client AS (

    SELECT
        AVG(
            submitted_to_client_date - applied_date
        ) AS avg_days

    FROM applications

    WHERE submitted_to_client_date IS NOT NULL
      AND applied_date IS NOT NULL
      AND submitted_to_client_date >= applied_date
),

application_to_offer AS (

    SELECT
        AVG(
            o.offer_date - a.applied_date
        ) AS avg_days

    FROM applications a

    JOIN offers o
        ON o.application_id = a.application_id

    WHERE o.offer_date IS NOT NULL
      AND a.applied_date IS NOT NULL
      AND o.offer_date >= a.applied_date
),

offer_to_joining AS (

    SELECT
        AVG(
            o.joining_date - o.offer_date
        ) AS avg_days

    FROM offers o

    WHERE o.joining_date IS NOT NULL
      AND o.offer_date IS NOT NULL
      AND o.joining_date >= o.offer_date
),

offer_to_placement AS (

    SELECT
        AVG(
            p.placement_date - o.offer_date
        ) AS avg_days

    FROM placements p

    JOIN offers o
        ON o.offer_id = p.offer_id

    WHERE p.placement_date IS NOT NULL
      AND o.offer_date IS NOT NULL
      AND p.placement_date >= o.offer_date
)

SELECT
    ROUND(
        (SELECT avg_days FROM application_to_client)::numeric,
        2
    ) AS avg_application_to_client_days,

    ROUND(
        (SELECT avg_days FROM application_to_offer)::numeric,
        2
    ) AS avg_application_to_offer_days,

    ROUND(
        (SELECT avg_days FROM offer_to_joining)::numeric,
        2
    ) AS avg_offer_to_joining_days,

    ROUND(
        (SELECT avg_days FROM offer_to_placement)::numeric,
        2
    ) AS avg_offer_to_placement_days;


/*
================================================================
SECTION 6 : RECRUITER PERFORMANCE
================================================================

Uses recruiter_id because the confirmed schema does not yet
include a recruiter-name table in the information provided.
================================================================
*/

SELECT
    COALESCE(a.recruiter_id::text, 'UNASSIGNED')
        AS recruiter_id,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT CASE
        WHEN a.submitted_to_client_date IS NOT NULL
        THEN a.application_id
    END)
        AS submitted_to_client,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
        THEN o.offer_id
    END)
        AS accepted_offers,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        COUNT(DISTINCT o.offer_id)::numeric
        / NULLIF(COUNT(DISTINCT a.application_id), 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
            THEN o.offer_id
        END)::numeric
        / NULLIF(COUNT(DISTINCT o.offer_id), 0) * 100,
        2
    ) AS offer_acceptance_pct,

    ROUND(
        COUNT(DISTINCT p.placement_id)::numeric
        / NULLIF(
            COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
                THEN o.offer_id
            END),
            0
        ) * 100,
        2
    ) AS placement_rate_pct

FROM applications a

LEFT JOIN offers o
    ON o.application_id = a.application_id

LEFT JOIN placements p
    ON p.offer_id = o.offer_id

GROUP BY
    a.recruiter_id

ORDER BY
    placements DESC,
    accepted_offers DESC,
    offers DESC;


/*
================================================================
SECTION 7 : JOB PERFORMANCE
================================================================
*/

SELECT
    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
        THEN o.offer_id
    END)
        AS accepted_offers,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        COUNT(DISTINCT o.offer_id)::numeric
        / NULLIF(COUNT(DISTINCT a.application_id), 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        COUNT(DISTINCT p.placement_id)::numeric
        / NULLIF(COUNT(DISTINCT a.application_id), 0) * 100,
        2
    ) AS application_to_placement_pct

FROM jobs j

LEFT JOIN applications a
    ON a.job_id = j.job_id

LEFT JOIN offers o
    ON o.application_id = a.application_id

LEFT JOIN placements p
    ON p.offer_id = o.offer_id

GROUP BY
    j.job_id,
    j.job_code,
    j.job_title,
    j.job_status

ORDER BY
    placements DESC,
    accepted_offers DESC,
    applications DESC;


/*
================================================================
SECTION 8 : JOB AGING ANALYSIS
================================================================

Uses the latest job opened date as the dataset snapshot date.
This avoids depending on the actual current calendar date.
================================================================
*/

WITH snapshot AS (

    SELECT
        MAX(opened_date) AS snapshot_date
    FROM jobs

),

job_age AS (

    SELECT
        j.job_id,
        j.job_code,
        j.job_title,
        j.job_status,
        j.opened_date,

        s.snapshot_date,

        s.snapshot_date - j.opened_date
            AS age_days

    FROM jobs j

    CROSS JOIN snapshot s

    WHERE j.opened_date IS NOT NULL

)

SELECT
    job_id,
    job_code,
    job_title,
    job_status,
    opened_date,
    age_days,

    CASE
        WHEN age_days <= 30
            THEN '0-30 DAYS'

        WHEN age_days <= 60
            THEN '31-60 DAYS'

        WHEN age_days <= 90
            THEN '61-90 DAYS'

        ELSE '90+ DAYS'
    END AS aging_bucket

FROM job_age

ORDER BY
    age_days DESC,
    job_title;


/*
================================================================
SECTION 9 : APPLICATION AGING / PIPELINE RISK
================================================================

Measures how long applications have remained without an update.

Uses the latest application date as the dataset snapshot.
================================================================
*/

WITH snapshot AS (

    SELECT
        MAX(applied_date) AS snapshot_date
    FROM applications

),

pipeline AS (

    SELECT
        a.application_id,
        a.candidate_id,
        a.job_id,
        a.recruiter_id,
        a.current_stage,
        a.status,
        a.applied_date,
        a.updated_at,

        s.snapshot_date,

        s.snapshot_date
        - COALESCE(a.updated_at::date, a.applied_date)
            AS inactive_days

    FROM applications a

    CROSS JOIN snapshot s

)

SELECT
    application_id,
    candidate_id,
    job_id,
    recruiter_id,
    current_stage,
    status,
    applied_date,
    updated_at,
    inactive_days,

    CASE
        WHEN inactive_days <= 15
            THEN 'LOW RISK'

        WHEN inactive_days <= 30
            THEN 'MEDIUM RISK'

        WHEN inactive_days <= 60
            THEN 'HIGH RISK'

        ELSE 'CRITICAL RISK'
    END AS pipeline_risk

FROM pipeline

ORDER BY
    inactive_days DESC,
    application_id

LIMIT 100;


/*
================================================================
SECTION 10 : CANDIDATE SOURCE EFFECTIVENESS
================================================================

Uses source_id because the confirmed candidate schema contains
source_id but the source lookup table was not provided.
================================================================
*/

SELECT
    COALESCE(c.source_id::text, 'UNASSIGNED')
        AS source_id,

    COUNT(DISTINCT c.candidate_id)
        AS candidates,

    COUNT(DISTINCT a.application_id)
        AS applications,

    COUNT(DISTINCT o.offer_id)
        AS offers,

    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
        THEN o.offer_id
    END)
        AS accepted_offers,

    COUNT(DISTINCT p.placement_id)
        AS placements,

    ROUND(
        COUNT(DISTINCT o.offer_id)::numeric
        / NULLIF(COUNT(DISTINCT a.application_id), 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        COUNT(DISTINCT p.placement_id)::numeric
        / NULLIF(COUNT(DISTINCT a.application_id), 0) * 100,
        2
    ) AS application_to_placement_pct

FROM candidates c

LEFT JOIN applications a
    ON a.candidate_id = c.candidate_id

LEFT JOIN offers o
    ON o.application_id = a.application_id

LEFT JOIN placements p
    ON p.offer_id = o.offer_id

GROUP BY
    c.source_id

ORDER BY
    placements DESC,
    accepted_offers DESC,
    offers DESC;


/*
================================================================
SECTION 11 : REPEAT CANDIDATE ANALYSIS
================================================================

Identifies candidates who applied to multiple jobs.
================================================================
*/

SELECT
    c.candidate_id,
    c.candidate_name,

    COUNT(DISTINCT a.application_id)
        AS application_count,

    COUNT(DISTINCT a.job_id)
        AS jobs_applied_to,

    COUNT(DISTINCT o.offer_id)
        AS offers_received,

    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
        THEN o.offer_id
    END)
        AS accepted_offers,

    COUNT(DISTINCT p.placement_id)
        AS placements

FROM candidates c

JOIN applications a
    ON a.candidate_id = c.candidate_id

LEFT JOIN offers o
    ON o.application_id = a.application_id

LEFT JOIN placements p
    ON p.offer_id = o.offer_id

GROUP BY
    c.candidate_id,
    c.candidate_name

HAVING
    COUNT(DISTINCT a.application_id) > 1

ORDER BY
    application_count DESC,
    placements DESC

LIMIT 100;


/*
================================================================
SECTION 12 : SALARY ALIGNMENT
================================================================

Compares offered salary with the job's salary range.

The result is useful for identifying:
    - Below-range offers
    - Within-range offers
    - Above-range offers
================================================================
*/

SELECT
    o.offer_id,
    a.application_id,
    a.job_id,

    j.job_title,

    j.min_salary,
    j.max_salary,

    o.offered_salary,

    CASE
        WHEN o.offered_salary IS NULL
            THEN 'SALARY NOT PROVIDED'

        WHEN j.min_salary IS NOT NULL
             AND o.offered_salary < j.min_salary
            THEN 'BELOW RANGE'

        WHEN j.max_salary IS NOT NULL
             AND o.offered_salary > j.max_salary
            THEN 'ABOVE RANGE'

        WHEN j.min_salary IS NOT NULL
             AND j.max_salary IS NOT NULL
             AND o.offered_salary BETWEEN j.min_salary AND j.max_salary
            THEN 'WITHIN RANGE'

        ELSE 'RANGE NOT AVAILABLE'
    END AS salary_alignment,

    o.offer_status

FROM offers o

JOIN applications a
    ON a.application_id = o.application_id

JOIN jobs j
    ON j.job_id = a.job_id

ORDER BY
    o.offered_salary DESC;


/*
================================================================
SECTION 13 : OFFER ACCEPTANCE BY SALARY BAND
================================================================
*/

WITH offer_bands AS (

    SELECT
        o.offer_id,
        o.offer_status,
        o.offered_salary,

        CASE
            WHEN o.offered_salary IS NULL
                THEN 'SALARY UNKNOWN'

            WHEN o.offered_salary < 50000
                THEN 'BELOW 50K'

            WHEN o.offered_salary < 75000
                THEN '50K-75K'

            WHEN o.offered_salary < 100000
                THEN '75K-100K'

            WHEN o.offered_salary < 125000
                THEN '100K-125K'

            ELSE '125K+'
        END AS salary_band

    FROM offers o

)

SELECT
    salary_band,

    COUNT(*) AS total_offers,

    COUNT(*) FILTER (
        WHERE LOWER(TRIM(offer_status)) = 'accepted'
    ) AS accepted_offers,

    COUNT(*) FILTER (
        WHERE LOWER(TRIM(offer_status)) <> 'accepted'
           OR offer_status IS NULL
    ) AS non_accepted_offers,

    ROUND(
        COUNT(*) FILTER (
            WHERE LOWER(TRIM(offer_status)) = 'accepted'
        )::numeric
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS acceptance_rate_pct

FROM offer_bands

GROUP BY
    salary_band

ORDER BY
    CASE salary_band
        WHEN 'BELOW 50K' THEN 1
        WHEN '50K-75K' THEN 2
        WHEN '75K-100K' THEN 3
        WHEN '100K-125K' THEN 4
        WHEN '125K+' THEN 5
        ELSE 6
    END;


/*
================================================================
SECTION 14 : PLACEMENT ANALYSIS
================================================================
*/

SELECT
    COALESCE(
        NULLIF(TRIM(p.placement_status), ''),
        'UNKNOWN'
    ) AS placement_status,

    COUNT(DISTINCT p.placement_id)
        AS placement_count,

    COUNT(DISTINCT p.candidate_id)
        AS unique_candidates,

    COUNT(DISTINCT p.job_id)
        AS unique_jobs,

    ROUND(
        AVG(
            CASE
                WHEN p.joining_date IS NOT NULL
                 AND p.placement_date IS NOT NULL
                 AND p.joining_date >= p.placement_date
                THEN p.joining_date - p.placement_date
            END
        )::numeric,
        2
    ) AS avg_placement_to_joining_days

FROM placements p

GROUP BY
    COALESCE(
        NULLIF(TRIM(p.placement_status), ''),
        'UNKNOWN'
    )

ORDER BY
    placement_count DESC;


/*
================================================================
SECTION 15 : JOB CONVERSION ANALYSIS
================================================================

Ranks jobs according to their ability to convert applications
into accepted offers and placements.
================================================================
*/

WITH job_metrics AS (

    SELECT
        j.job_id,
        j.job_code,
        j.job_title,
        j.job_status,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
            THEN o.offer_id
        END)
            AS accepted_offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM jobs j

    LEFT JOIN applications a
        ON a.job_id = j.job_id

    LEFT JOIN offers o
        ON o.application_id = a.application_id

    LEFT JOIN placements p
        ON p.offer_id = o.offer_id

    GROUP BY
        j.job_id,
        j.job_code,
        j.job_title,
        j.job_status

)

SELECT
    job_id,
    job_code,
    job_title,
    job_status,

    applications,
    offers,
    accepted_offers,
    placements,

    ROUND(
        offers::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        accepted_offers::numeric
        / NULLIF(offers, 0) * 100,
        2
    ) AS offer_acceptance_pct,

    ROUND(
        placements::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_placement_pct,

    CASE
        WHEN applications = 0
            THEN 'NO APPLICATIONS'

        WHEN placements > 0
            THEN 'SUCCESSFUL'

        WHEN accepted_offers > 0
            THEN 'ACCEPTED OFFER - PENDING PLACEMENT'

        WHEN offers > 0
            THEN 'OFFER STAGE'

        ELSE 'NO OFFERS'
    END AS job_outcome

FROM job_metrics

ORDER BY
    placements DESC,
    accepted_offers DESC,
    offers DESC,
    applications DESC;


/*
================================================================
SECTION 16 : RECRUITMENT RISK ANALYSIS
================================================================

Identifies jobs that have high application volume but weak
conversion into offers / placements.
================================================================
*/

WITH job_metrics AS (

    SELECT
        j.job_id,
        j.job_code,
        j.job_title,

        COUNT(DISTINCT a.application_id)
            AS applications,

        COUNT(DISTINCT o.offer_id)
            AS offers,

        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(o.offer_status)) = 'accepted'
            THEN o.offer_id
        END)
            AS accepted_offers,

        COUNT(DISTINCT p.placement_id)
            AS placements

    FROM jobs j

    LEFT JOIN applications a
        ON a.job_id = j.job_id

    LEFT JOIN offers o
        ON o.application_id = a.application_id

    LEFT JOIN placements p
        ON p.offer_id = o.offer_id

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
    offers,
    accepted_offers,
    placements,

    ROUND(
        offers::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        placements::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_placement_pct,

    CASE

        WHEN applications >= 20
             AND offers = 0
            THEN 'CRITICAL - HIGH APPLICATIONS NO OFFERS'

        WHEN applications >= 20
             AND placements = 0
            THEN 'HIGH RISK - NO PLACEMENTS'

        WHEN applications >= 10
             AND offers::numeric
                 / NULLIF(applications, 0) < 0.05
            THEN 'HIGH RISK - LOW OFFER CONVERSION'

        WHEN applications >= 10
             AND placements = 0
            THEN 'MEDIUM RISK'

        WHEN placements > 0
            THEN 'LOW RISK'

        ELSE 'MONITOR'

    END AS recruitment_risk

FROM job_metrics

ORDER BY
    CASE
        WHEN applications >= 20 AND offers = 0
            THEN 1
        WHEN applications >= 20 AND placements = 0
            THEN 2
        WHEN applications >= 10
             AND offers::numeric
                 / NULLIF(applications, 0) < 0.05
            THEN 3
        WHEN applications >= 10 AND placements = 0
            THEN 4
        ELSE 5
    END,
    applications DESC;


/*
================================================================
SECTION 17 : EXECUTIVE OPPORTUNITY ANALYSIS
================================================================

Provides high-level indicators that management can act upon.
================================================================
*/

WITH metrics AS (

    SELECT

        (SELECT COUNT(*) FROM applications)
            AS applications,

        (SELECT COUNT(*) FROM offers)
            AS offers,

        (SELECT COUNT(*)
         FROM offers
         WHERE LOWER(TRIM(offer_status)) = 'accepted')
            AS accepted_offers,

        (SELECT COUNT(*) FROM placements)
            AS placements,

        (SELECT COUNT(DISTINCT candidate_id)
         FROM applications)
            AS candidates_with_applications,

        (SELECT COUNT(DISTINCT job_id)
         FROM applications)
            AS jobs_with_applications

)

SELECT
    applications,
    offers,
    accepted_offers,
    placements,
    candidates_with_applications,
    jobs_with_applications,

    ROUND(
        offers::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS application_to_offer_pct,

    ROUND(
        accepted_offers::numeric
        / NULLIF(offers, 0) * 100,
        2
    ) AS offer_acceptance_pct,

    ROUND(
        placements::numeric
        / NULLIF(accepted_offers, 0) * 100,
        2
    ) AS accepted_to_placement_pct,

    ROUND(
        placements::numeric
        / NULLIF(applications, 0) * 100,
        2
    ) AS overall_application_to_placement_pct

FROM metrics;


/*
================================================================
SECTION 18 : FINAL EXECUTIVE SUMMARY
================================================================

One-row management summary for dashboard/reporting.
================================================================
*/

WITH summary AS (

    SELECT

        (SELECT COUNT(*) FROM candidates)
            AS total_candidates,

        (SELECT COUNT(*) FROM jobs)
            AS total_jobs,

        (SELECT COUNT(*) FROM applications)
            AS total_applications,

        (SELECT COUNT(*) FROM offers)
            AS total_offers,

        (SELECT COUNT(*)
         FROM offers
         WHERE LOWER(TRIM(offer_status)) = 'accepted')
            AS accepted_offers,

        (SELECT COUNT(*) FROM placements)
            AS total_placements,

        (SELECT COUNT(*)
         FROM applications
         WHERE submitted_to_client_date IS NOT NULL)
            AS submitted_to_client,

        (SELECT COUNT(DISTINCT recruiter_id)
         FROM applications
         WHERE recruiter_id IS NOT NULL)
            AS active_recruiters,

        (SELECT COUNT(DISTINCT source_id)
         FROM candidates
         WHERE source_id IS NOT NULL)
            AS candidate_sources

)

SELECT
    total_candidates,
    total_jobs,
    total_applications,
    submitted_to_client,
    total_offers,
    accepted_offers,
    total_placements,
    active_recruiters,
    candidate_sources,

    ROUND(
        submitted_to_client::numeric
        / NULLIF(total_applications, 0) * 100,
        2
    ) AS client_submission_rate_pct,

    ROUND(
        total_offers::numeric
        / NULLIF(total_applications, 0) * 100,
        2
    ) AS offer_rate_pct,

    ROUND(
        accepted_offers::numeric
        / NULLIF(total_offers, 0) * 100,
        2
    ) AS offer_acceptance_rate_pct,

    ROUND(
        total_placements::numeric
        / NULLIF(accepted_offers, 0) * 100,
        2
    ) AS placement_after_acceptance_pct,

    ROUND(
        total_placements::numeric
        / NULLIF(total_applications, 0) * 100,
        2
    ) AS overall_placement_rate_pct

FROM summary;


/*
================================================================
                    END OF ADVANCED INSIGHTS
================================================================
*/