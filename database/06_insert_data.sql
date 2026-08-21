/*
===========================================================
        TalentIQ AI Recruitment Analytics Platform

        File: 04_insert_data.sql

        Purpose:
        This file loads initial recruitment data into
        the database tables.

        Data Flow:

        Candidates
             |
             |
        Applications
          /      \
         /        \
   Interviews    Offers
                    |
                Employees

===========================================================
*/


SET search_path TO recruitment;



/*
===========================================================
SECTION 1 : INSERT CANDIDATE DATA

Purpose:
---------
Adding candidate profiles entering recruitment pipeline.

===========================================================
*/


INSERT INTO recruitment.candidates
(
    candidate_name,
    email,
    phone,
    experience_years,
    education,
    location,
    applied_date,
    source,
    status
)

VALUES

('Rahul Sharma',
 'rahul@gmail.com',
 '9999999991',
 3,
 'B.Tech',
 'Delhi',
 '2026-01-05',
 'LinkedIn',
 'Hired'),


('Amit Verma',
 'amit@gmail.com',
 '9999999992',
 5,
 'MCA',
 'Noida',
 '2026-01-10',
 'Indeed',
 'Interview'),


('Priya Singh',
 'priya@gmail.com',
 '9999999993',
 2,
 'BCA',
 'Mumbai',
 '2026-01-15',
 'Referral',
 'Screening'),


('Neha Gupta',
 'neha@gmail.com',
 '9999999994',
 4,
 'B.Tech',
 'Pune',
 '2026-01-20',
 'LinkedIn',
 'Rejected'),


('Arjun Mehta',
 'arjun@gmail.com',
 '9999999995',
 6,
 'MBA',
 'Bangalore',
 '2026-01-25',
 'Naukri',
 'Offer');





/*
===========================================================
SECTION 2 : INSERT JOB DATA

Purpose:
---------
Adding available job positions.

===========================================================
*/


INSERT INTO recruitment.jobs
(
    job_title,
    department,
    experience_required,
    location,
    salary_range,
    job_status
)

VALUES

('Data Analyst',
 'Analytics',
 2,
 'Remote',
 '8-12 LPA',
 'Open'),


('AI Engineer',
 'Artificial Intelligence',
 3,
 'Bangalore',
 '15-25 LPA',
 'Open'),


('Machine Learning Engineer',
 'Artificial Intelligence',
 4,
 'Hyderabad',
 '18-30 LPA',
 'Closed');





/*
===========================================================
SECTION 3 : INSERT APPLICATION DATA

Purpose:
---------
Connecting candidates with applied job positions.

===========================================================
*/


INSERT INTO recruitment.applications
(
    candidate_id,
    job_id,
    applied_date,
    current_stage
)

VALUES

(1,1,'2026-01-05','Hired'),

(2,1,'2026-01-10','Interview'),

(3,1,'2026-01-15','Screening'),

(4,2,'2026-01-20','Rejected'),

(5,3,'2026-01-25','Offer');





/*
===========================================================
SECTION 4 : INSERT INTERVIEW DATA

Purpose:
---------
Tracking candidate interview performance.

===========================================================
*/


INSERT INTO recruitment.interviews
(
    application_id,
    interview_date,
    interviewer,
    interview_round,
    result
)

VALUES

(2,
 '2026-01-20',
 'John Smith',
 'Technical',
 'Passed'),


(3,
 '2026-01-22',
 'Sarah Lee',
 'HR',
 'Pending'),


(5,
 '2026-01-28',
 'Mike Johnson',
 'Technical',
 'Passed');





/*
===========================================================
SECTION 5 : INSERT OFFER DATA

Purpose:
---------
Tracking compensation offers.

===========================================================
*/


INSERT INTO recruitment.offers
(
    application_id,
    offer_date,
    offered_salary,
    offer_status
)

VALUES

(5,
 '2026-01-30',
 1800000,
 'Accepted'),


(1,
 '2026-01-15',
 1200000,
 'Accepted');





/*
===========================================================
SECTION 6 : INSERT EMPLOYEE DATA

Purpose:
---------
Tracking successful hires.

===========================================================
*/


INSERT INTO recruitment.employees
(
    candidate_id,
    joining_date,
    department,
    designation
)

VALUES

(1,
 '2026-02-15',
 'Analytics',
 'Data Analyst'),


(5,
 '2026-02-20',
 'Artificial Intelligence',
 'AI Engineer');



/*
===========================================================
DATA LOADING COMPLETED

Inserted:

✔ Candidates
✔ Jobs
✔ Applications
✔ Interviews
✔ Offers
✔ Employees

===========================================================
*/