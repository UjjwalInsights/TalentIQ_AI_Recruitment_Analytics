/*
===========================================================
        TalentIQ AI Recruitment Analytics Platform

        File: 05_analytics_queries.sql

        Purpose:
        Business analysis queries for recruitment
        performance monitoring.

        Analysis Areas:

        1. Recruitment Overview KPIs
        2. Hiring Funnel Analysis
        3. Hiring Conversion Rate
        4. Recruitment Source Performance
        5. Job Performance Analysis
        6. Interview Effectiveness
        7. Salary Analysis
        8. Hiring Trend Analysis
        9. Candidate Drop-off Analysis
        10. Department Hiring Analysis

===========================================================
*/


SET search_path TO recruitment;



/*
===========================================================
SECTION 1 : TOTAL CANDIDATE COUNT

Business Question:
------------------
How many candidates entered the recruitment pipeline?

Metric:
Total Candidates

===========================================================
*/


SELECT

COUNT(*) AS total_candidates

FROM recruitment.candidates;




/*
===========================================================
SECTION 2 : RECRUITMENT FUNNEL ANALYSIS

Business Question:
------------------
How many candidates are present at each recruitment stage?

Recruitment Funnel:

Applied
  ↓
Screening
  ↓
Interview
  ↓
Offer
  ↓
Hired


===========================================================
*/


SELECT

current_stage,

COUNT(*) AS candidate_count


FROM recruitment.applications


GROUP BY current_stage


ORDER BY candidate_count DESC;





/*
===========================================================
SECTION 3 : HIRING CONVERSION RATE

Business Question:
------------------
What percentage of candidates became successful hires?


Formula:

Hiring Rate =
(Hired Candidates / Total Candidates) * 100


===========================================================
*/


SELECT

ROUND(

COUNT(*) FILTER(WHERE status='Hired')
*100.0
/
COUNT(*),

2

) AS hiring_rate_percentage


FROM recruitment.candidates;





/*
===========================================================
SECTION 4 : RECRUITMENT SOURCE PERFORMANCE

Business Question:
------------------
Which hiring channels provide the best candidates?


Examples:

LinkedIn
Indeed
Referral
Naukri


===========================================================
*/


SELECT

source,

COUNT(*) AS total_candidates,


COUNT(*) FILTER(WHERE status='Hired')
AS hired_candidates,


ROUND(

COUNT(*) FILTER(WHERE status='Hired')
*100.0
/
COUNT(*),

2

) AS conversion_rate


FROM recruitment.candidates


GROUP BY source


ORDER BY conversion_rate DESC;





/*
===========================================================
SECTION 5 : JOB APPLICATION ANALYSIS

Business Question:
------------------
Which job positions receive the highest interest?


===========================================================
*/


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
j.department


ORDER BY total_applications DESC;





/*
===========================================================
SECTION 6 : INTERVIEW SUCCESS ANALYSIS

Business Question:
------------------
How effective is the interview process?


Formula:

Interview Success Rate =
Passed Interviews / Total Interviews


===========================================================
*/


SELECT

ROUND(

COUNT(*) FILTER(WHERE result='Passed')
*100.0
/
COUNT(*),

2

)

AS interview_success_rate


FROM recruitment.interviews;





/*
===========================================================
SECTION 7 : OFFER & SALARY ANALYSIS

Business Question:
------------------
What compensation is being offered?


Metrics:

Average Salary
Highest Salary
Lowest Salary


===========================================================
*/


SELECT

AVG(offered_salary)
AS average_salary,


MAX(offered_salary)
AS highest_salary,


MIN(offered_salary)
AS lowest_salary


FROM recruitment.offers;





/*
===========================================================
SECTION 8 : MONTHLY HIRING TREND

Business Question:
------------------
How is hiring changing over time?


===========================================================
*/


SELECT

DATE_TRUNC('month',joining_date)
AS hiring_month,


COUNT(*) AS total_hires


FROM recruitment.employees


GROUP BY hiring_month


ORDER BY hiring_month;





/*
===========================================================
SECTION 9 : CANDIDATE DROP-OFF ANALYSIS

Business Question:
------------------
At which stage are candidates leaving?

Helps improve:
- Hiring speed
- Candidate experience
- Recruitment process


===========================================================
*/


SELECT

current_stage,


COUNT(*) AS candidates


FROM recruitment.applications


GROUP BY current_stage


ORDER BY candidates DESC;





/*
===========================================================
SECTION 10 : DEPARTMENT HIRING ANALYSIS

Business Question:
------------------
Which departments are growing?


===========================================================
*/


SELECT

department,


COUNT(*) AS employee_count


FROM recruitment.employees


GROUP BY department;



/*
===========================================================
END OF ANALYTICS QUERIES

Next:
06_views.sql

Purpose:
Create dashboard-ready tables/views
for Power BI, Tableau and Streamlit.

===========================================================
*/