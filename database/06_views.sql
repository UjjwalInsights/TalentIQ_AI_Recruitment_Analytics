/*
===========================================================
        TalentIQ AI Recruitment Analytics Platform

        File: 06_views.sql

        Purpose:
        Create dashboard-ready views for BI tools.

        Views Created:

        1. Recruitment KPI Summary
        2. Candidate Funnel Analysis
        3. Source Performance Analysis
        4. Job Performance Analysis
        5. Interview Performance
        6. Hiring Trend Analysis
        7. Employee Department Analysis

===========================================================
*/


SET search_path TO recruitment;



/*
===========================================================
VIEW 1 : RECRUITMENT KPI SUMMARY

Purpose:
---------
Executive dashboard metrics.

Provides:

- Total candidates
- Total hired
- Total offers
- Hiring rate

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_recruitment_kpi
AS

SELECT

    COUNT(DISTINCT c.candidate_id)
    AS total_candidates,


    COUNT(DISTINCT CASE
        WHEN c.status='Hired'
        THEN c.candidate_id
    END)
    AS total_hired,


    COUNT(DISTINCT o.offer_id)
    AS total_offers,


    ROUND(

    COUNT(DISTINCT CASE
        WHEN c.status='Hired'
        THEN c.candidate_id
    END)
    *100.0
    /
    COUNT(DISTINCT c.candidate_id),

    2)

    AS hiring_rate_percentage


FROM recruitment.candidates c


LEFT JOIN recruitment.applications a

ON c.candidate_id=a.candidate_id


LEFT JOIN recruitment.offers o

ON a.application_id=o.application_id;





/*
===========================================================
VIEW 2 : CANDIDATE FUNNEL VIEW

Purpose:
---------
Recruitment pipeline visualization.

Used for:

- Funnel charts
- Drop-off analysis

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_candidate_funnel
AS

SELECT

current_stage,

COUNT(*) AS candidate_count


FROM recruitment.applications


GROUP BY current_stage;





/*
===========================================================
VIEW 3 : SOURCE PERFORMANCE VIEW

Purpose:
---------
Measures effectiveness of recruitment channels.

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_source_performance
AS

SELECT

source,


COUNT(*) AS total_candidates,


COUNT(*) FILTER
(
WHERE status='Hired'
)
AS hired_candidates,


ROUND(

COUNT(*) FILTER
(
WHERE status='Hired'
)
*100.0
/
COUNT(*),

2

)

AS hiring_conversion_rate


FROM recruitment.candidates


GROUP BY source;





/*
===========================================================
VIEW 4 : JOB PERFORMANCE VIEW

Purpose:
---------
Analyze demand for job positions.

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_job_performance
AS

SELECT

j.job_title,

j.department,

COUNT(a.application_id)
AS total_applications


FROM recruitment.jobs j


LEFT JOIN recruitment.applications a

ON j.job_id=a.job_id


GROUP BY

j.job_title,
j.department;





/*
===========================================================
VIEW 5 : INTERVIEW PERFORMANCE VIEW

Purpose:
---------
Measure interview efficiency.

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_interview_performance
AS

SELECT

interview_round,


COUNT(*) AS total_interviews,


COUNT(*) FILTER
(
WHERE result='Passed'
)
AS passed_interviews,


ROUND(

COUNT(*) FILTER
(
WHERE result='Passed'
)
*100.0
/
COUNT(*),

2

)

AS success_rate


FROM recruitment.interviews


GROUP BY interview_round;





/*
===========================================================
VIEW 6 : HIRING TREND VIEW

Purpose:
---------
Monthly hiring analysis.

Used for:

- Line charts
- Growth analysis

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_hiring_trend
AS

SELECT

DATE_TRUNC('month',joining_date)
AS hiring_month,


COUNT(*) AS hires


FROM recruitment.employees


GROUP BY hiring_month;





/*
===========================================================
VIEW 7 : DEPARTMENT ANALYSIS VIEW

Purpose:
---------
Workforce distribution.

===========================================================
*/


CREATE OR REPLACE VIEW recruitment.vw_department_analysis
AS

SELECT

department,


COUNT(*) AS employee_count


FROM recruitment.employees


GROUP BY department;



/*
===========================================================
VIEWS CREATED SUCCESSFULLY

Available Dashboard Views:

✔ vw_recruitment_kpi
✔ vw_candidate_funnel
✔ vw_source_performance
✔ vw_job_performance
✔ vw_interview_performance
✔ vw_hiring_trend
✔ vw_department_analysis

Next Step:
Connect PostgreSQL → Power BI/Tableau/Streamlit

===========================================================
*/
