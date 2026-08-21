/*
====================================================================
TALENTIQ - RECRUITMENT ANALYTICS
FILE: 09_salary_analysis.sql
Schema: recruitment
====================================================================
*/

SET search_path TO recruitment;

/* QUERY 1 - OVERALL SALARY SUMMARY */
SELECT COUNT(*) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_offered_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_offered_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_offered_salary,
       ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY o.offered_salary)::NUMERIC, 2) AS median_offered_salary
FROM offers o
WHERE o.offered_salary IS NOT NULL;

/* QUERY 2 - SALARY DISTRIBUTION */
WITH bands AS (
    SELECT CASE
        WHEN offered_salary < 75000 THEN 'Below 75K'
        WHEN offered_salary < 100000 THEN '75K-100K'
        WHEN offered_salary < 125000 THEN '100K-125K'
        WHEN offered_salary < 150000 THEN '125K-150K'
        WHEN offered_salary < 175000 THEN '150K-175K'
        ELSE '175K+'
    END AS salary_band,
    offered_salary
    FROM offers
    WHERE offered_salary IS NOT NULL
)
SELECT salary_band,
       COUNT(*) AS total_offers,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM bands
GROUP BY salary_band
ORDER BY MIN(offered_salary);

/* QUERY 3 - SALARY BY OFFER STATUS */
SELECT o.offer_status,
       COUNT(*) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
WHERE o.offered_salary IS NOT NULL
GROUP BY o.offer_status
ORDER BY average_salary DESC;

/* QUERY 4 - ACCEPTED VS NON-ACCEPTED SALARY */
SELECT CASE WHEN o.offer_status = 'Accepted' THEN 'Accepted' ELSE 'Not Accepted' END AS acceptance_group,
       COUNT(*) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
WHERE o.offered_salary IS NOT NULL
GROUP BY CASE WHEN o.offer_status = 'Accepted' THEN 'Accepted' ELSE 'Not Accepted' END
ORDER BY average_salary DESC;

/* QUERY 5 - SALARY BY DEPARTMENT */
SELECT d.department_name,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
JOIN departments d ON j.department_id = d.department_id
WHERE o.offered_salary IS NOT NULL
GROUP BY d.department_name
ORDER BY average_salary DESC;

/* QUERY 6 - DEPARTMENT ACCEPTANCE */
SELECT d.department_name,
       COUNT(o.offer_id) AS total_offers,
       COUNT(*) FILTER (WHERE o.offer_status = 'Accepted') AS accepted_offers,
       ROUND(COUNT(*) FILTER (WHERE o.offer_status = 'Accepted') * 100.0 / NULLIF(COUNT(o.offer_id), 0), 2) AS acceptance_rate
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
JOIN departments d ON j.department_id = d.department_id
GROUP BY d.department_name
ORDER BY acceptance_rate DESC;

/* QUERY 7 - SALARY BY JOB TITLE */
SELECT j.job_title,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
WHERE o.offered_salary IS NOT NULL
GROUP BY j.job_title
HAVING COUNT(o.offer_id) >= 5
ORDER BY average_salary DESC;

/* QUERY 8 - SALARY BY EXPERIENCE LEVEL */
WITH salary_data AS (
    SELECT CASE
        WHEN c.experience_years <= 1 THEN '0-1 Years'
        WHEN c.experience_years BETWEEN 2 AND 4 THEN '2-4 Years'
        WHEN c.experience_years BETWEEN 5 AND 7 THEN '5-7 Years'
        WHEN c.experience_years BETWEEN 8 AND 10 THEN '8-10 Years'
        ELSE '11+ Years'
    END AS experience_group,
    c.experience_years,
    o.offered_salary
    FROM offers o
    JOIN applications a ON o.application_id = a.application_id
    JOIN candidates c ON a.candidate_id = c.candidate_id
    WHERE o.offered_salary IS NOT NULL
)
SELECT experience_group,
       COUNT(*) AS total_offers,
       ROUND(AVG(offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(offered_salary)::NUMERIC, 2) AS maximum_salary
FROM salary_data
GROUP BY experience_group
ORDER BY MIN(experience_years);

/* QUERY 9 - SALARY BY EMPLOYMENT TYPE */
SELECT j.employment_type,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
WHERE o.offered_salary IS NOT NULL
GROUP BY j.employment_type
ORDER BY average_salary DESC;

/* QUERY 10 - SALARY BY WORK MODE */
SELECT j.work_mode,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
WHERE o.offered_salary IS NOT NULL
GROUP BY j.work_mode
ORDER BY average_salary DESC;

/* QUERY 11 - COMPANY SALARY ANALYSIS
   IMPORTANT: jobs uses end_client_id, NOT company_id. */
SELECT c.company_name,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
JOIN companies c ON j.end_client_id = c.company_id
WHERE o.offered_salary IS NOT NULL
GROUP BY c.company_name
ORDER BY average_salary DESC;

/* QUERY 12 - COMPANY ACCEPTANCE */
SELECT c.company_name,
       COUNT(o.offer_id) AS total_offers,
       COUNT(*) FILTER (WHERE o.offer_status = 'Accepted') AS accepted_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(COUNT(*) FILTER (WHERE o.offer_status = 'Accepted') * 100.0 / NULLIF(COUNT(o.offer_id), 0), 2) AS acceptance_rate
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
JOIN companies c ON j.end_client_id = c.company_id
WHERE o.offered_salary IS NOT NULL
GROUP BY c.company_name
HAVING COUNT(o.offer_id) >= 5
ORDER BY acceptance_rate DESC;

/* QUERY 13 - OFFERED SALARY VS JOB SALARY RANGE */
SELECT COUNT(*) AS total_offers,
       COUNT(*) FILTER (WHERE o.offered_salary < j.min_salary) AS below_job_range,
       COUNT(*) FILTER (WHERE o.offered_salary BETWEEN j.min_salary AND j.max_salary) AS within_job_range,
       COUNT(*) FILTER (WHERE o.offered_salary > j.max_salary) AS above_job_range,
       ROUND(COUNT(*) FILTER (WHERE o.offered_salary < j.min_salary) * 100.0 / NULLIF(COUNT(*), 0), 2) AS below_range_percentage,
       ROUND(COUNT(*) FILTER (WHERE o.offered_salary BETWEEN j.min_salary AND j.max_salary) * 100.0 / NULLIF(COUNT(*), 0), 2) AS within_range_percentage,
       ROUND(COUNT(*) FILTER (WHERE o.offered_salary > j.max_salary) * 100.0 / NULLIF(COUNT(*), 0), 2) AS above_range_percentage
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
WHERE o.offered_salary IS NOT NULL
  AND j.min_salary IS NOT NULL
  AND j.max_salary IS NOT NULL;

/* QUERY 14 - SALARY DIFFERENCE FROM JOB MIDPOINT */
SELECT j.job_title,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary - ((j.min_salary + j.max_salary) / 2.0))::NUMERIC, 2) AS average_difference_from_midpoint,
       ROUND(AVG(((o.offered_salary - ((j.min_salary + j.max_salary) / 2.0)) / NULLIF(((j.min_salary + j.max_salary) / 2.0), 0)) * 100)::NUMERIC, 2) AS average_percentage_difference
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN jobs j ON a.job_id = j.job_id
WHERE o.offered_salary IS NOT NULL
  AND j.min_salary IS NOT NULL
  AND j.max_salary IS NOT NULL
GROUP BY j.job_title
HAVING COUNT(o.offer_id) >= 5
ORDER BY average_percentage_difference DESC;

/* QUERY 15 - SALARY BAND BY OFFER STATUS */
WITH bands AS (
    SELECT CASE
        WHEN offered_salary < 75000 THEN 'Below 75K'
        WHEN offered_salary < 100000 THEN '75K-100K'
        WHEN offered_salary < 125000 THEN '100K-125K'
        WHEN offered_salary < 150000 THEN '125K-150K'
        WHEN offered_salary < 175000 THEN '150K-175K'
        ELSE '175K+'
    END AS salary_band,
    offered_salary,
    offer_status
    FROM offers
    WHERE offered_salary IS NOT NULL
)
SELECT salary_band,
       COUNT(*) AS total_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Accepted') AS accepted_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Declined') AS declined_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Negotiating') AS negotiating_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Extended') AS extended_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Rescinded') AS rescinded_offers
FROM bands
GROUP BY salary_band
ORDER BY MIN(offered_salary);

/* QUERY 16 - SALARY BY CANDIDATE STATUS */
SELECT c.status AS candidate_status,
       COUNT(o.offer_id) AS total_offers,
       ROUND(AVG(o.offered_salary)::NUMERIC, 2) AS average_salary,
       ROUND(MIN(o.offered_salary)::NUMERIC, 2) AS minimum_salary,
       ROUND(MAX(o.offered_salary)::NUMERIC, 2) AS maximum_salary
FROM offers o
JOIN applications a ON o.application_id = a.application_id
JOIN candidates c ON a.candidate_id = c.candidate_id
WHERE o.offered_salary IS NOT NULL
GROUP BY c.status
ORDER BY average_salary DESC;

/* QUERY 17 - ACCEPTANCE RATE BY SALARY BAND */
WITH bands AS (
    SELECT CASE
        WHEN offered_salary < 75000 THEN 'Below 75K'
        WHEN offered_salary < 100000 THEN '75K-100K'
        WHEN offered_salary < 125000 THEN '100K-125K'
        WHEN offered_salary < 150000 THEN '125K-150K'
        WHEN offered_salary < 175000 THEN '150K-175K'
        ELSE '175K+'
    END AS salary_band,
    offered_salary,
    offer_status
    FROM offers
    WHERE offered_salary IS NOT NULL
)
SELECT salary_band,
       COUNT(*) AS total_offers,
       COUNT(*) FILTER (WHERE offer_status = 'Accepted') AS accepted_offers,
       ROUND(COUNT(*) FILTER (WHERE offer_status = 'Accepted') * 100.0 / NULLIF(COUNT(*), 0), 2) AS acceptance_rate
FROM bands
GROUP BY salary_band
ORDER BY MIN(offered_salary);

/* END OF 09_salary_analysis.sql */