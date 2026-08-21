/*
=====================================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 05_indexes.sql

        Purpose:
        --------
        Creates indexes for commonly searched and joined columns.

        Run AFTER:
        03_create_tables.sql
        04_constraints.sql

=====================================================================
*/

SET search_path TO recruitment;


/*
=====================================================================
COMPANIES
=====================================================================
*/

CREATE INDEX idx_companies_type
ON recruitment.companies(company_type);

CREATE INDEX idx_companies_country
ON recruitment.companies(country);

CREATE INDEX idx_companies_active
ON recruitment.companies(is_active);


/*
=====================================================================
RECRUITERS
=====================================================================
*/

CREATE INDEX idx_recruiters_company
ON recruitment.recruiters(company_id);

CREATE INDEX idx_recruiters_active
ON recruitment.recruiters(is_active);


/*
=====================================================================
DEPARTMENTS
=====================================================================
*/

CREATE INDEX idx_departments_company
ON recruitment.departments(company_id);


/*
=====================================================================
LOCATIONS
=====================================================================
*/

CREATE INDEX idx_locations_country
ON recruitment.locations(country);

CREATE INDEX idx_locations_work_mode
ON recruitment.locations(work_mode);


/*
=====================================================================
CANDIDATES
=====================================================================
*/

CREATE INDEX idx_candidates_source
ON recruitment.candidates(source_id);

CREATE INDEX idx_candidates_location
ON recruitment.candidates(location_id);

CREATE INDEX idx_candidates_work_authorization
ON recruitment.candidates(work_authorization_id);

CREATE INDEX idx_candidates_status
ON recruitment.candidates(status);

CREATE INDEX idx_candidates_experience
ON recruitment.candidates(experience_years);


/*
=====================================================================
JOBS
=====================================================================
*/

CREATE INDEX idx_jobs_end_client
ON recruitment.jobs(end_client_id);

CREATE INDEX idx_jobs_vendor
ON recruitment.jobs(vendor_id);

CREATE INDEX idx_jobs_department
ON recruitment.jobs(department_id);

CREATE INDEX idx_jobs_location
ON recruitment.jobs(location_id);

CREATE INDEX idx_jobs_recruiter
ON recruitment.jobs(assigned_recruiter_id);

CREATE INDEX idx_jobs_status
ON recruitment.jobs(job_status);

CREATE INDEX idx_jobs_opened_date
ON recruitment.jobs(opened_date);


/*
=====================================================================
APPLICATIONS
=====================================================================
*/

CREATE INDEX idx_applications_candidate
ON recruitment.applications(candidate_id);

CREATE INDEX idx_applications_job
ON recruitment.applications(job_id);

CREATE INDEX idx_applications_recruiter
ON recruitment.applications(recruiter_id);

CREATE INDEX idx_applications_stage
ON recruitment.applications(current_stage);

CREATE INDEX idx_applications_status
ON recruitment.applications(status);

CREATE INDEX idx_applications_date
ON recruitment.applications(applied_date);


/*
=====================================================================
INTERVIEWS
=====================================================================
*/

CREATE INDEX idx_interviews_application
ON recruitment.interviews(application_id);

CREATE INDEX idx_interviews_date
ON recruitment.interviews(interview_date);

CREATE INDEX idx_interviews_outcome
ON recruitment.interviews(outcome);


/*
=====================================================================
OFFERS
=====================================================================
*/

CREATE INDEX idx_offers_application
ON recruitment.offers(application_id);

CREATE INDEX idx_offers_status
ON recruitment.offers(offer_status);

CREATE INDEX idx_offers_date
ON recruitment.offers(offer_date);


/*
=====================================================================
PLACEMENTS
=====================================================================
*/

CREATE INDEX idx_placements_candidate
ON recruitment.placements(candidate_id);

CREATE INDEX idx_placements_job
ON recruitment.placements(job_id);

CREATE INDEX idx_placements_date
ON recruitment.placements(placement_date);

CREATE INDEX idx_placements_status
ON recruitment.placements(placement_status);


/*
=====================================================================
CANDIDATE SKILLS
=====================================================================
*/

CREATE INDEX idx_candidate_skills_skill
ON recruitment.candidate_skills(skill_id);


/*
=====================================================================
JOB SKILLS
=====================================================================
*/

CREATE INDEX idx_job_skills_skill
ON recruitment.job_skills(skill_id);

CREATE INDEX idx_job_skills_priority
ON recruitment.job_skills(priority);


/*
=====================================================================
INDEX CREATION COMPLETED
=====================================================================
*/