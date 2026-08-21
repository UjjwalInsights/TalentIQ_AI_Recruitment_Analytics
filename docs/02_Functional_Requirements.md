# TalentIQ AI Recruitment Analytics
## Functional Requirements Document (FRD)

**Version:** 1.0  
**Project:** TalentIQ AI Recruitment Analytics  
**Last Updated:** August 2026

---

# Table of Contents

1. Introduction
2. Purpose
3. User Roles
4. Functional Modules
5. User Workflows
6. Business Rules
7. Validation Rules
8. Dashboard Requirements
9. AI Functional Requirements
10. Reporting Requirements
11. Non-Functional Requirements
12. Future Enhancements

---

# 1. Introduction

This Functional Requirements Document (FRD) defines the complete functional behavior of the TalentIQ AI Recruitment Analytics platform.

The document translates the business requirements into detailed software features, workflows, modules, user interactions, and system behavior.

The FRD serves as the primary development blueprint for:

- PostgreSQL Database Design
- SQL Analytics
- Python ETL
- Power BI Dashboard
- Machine Learning Models
- AI Resume Parser
- Job Matching Engine
- Streamlit Application

---

# 2. Purpose

The primary objective of TalentIQ is to provide recruitment agencies and HR departments with a centralized platform capable of managing the complete recruitment lifecycle while providing advanced analytics and AI-powered hiring assistance.

The platform shall enable users to:

- Manage recruitment operations
- Track hiring progress
- Analyze recruitment KPIs
- Measure recruiter performance
- Identify sourcing effectiveness
- Analyze placement margins
- Match resumes against job requirements
- Generate recruitment insights using AI

---

# 3. User Roles

## 3.1 Recruitment Agency Owner

Responsibilities

- Monitor agency performance
- Monitor recruiter productivity
- View company revenue
- Analyze placement margins
- View executive dashboards
- Track business growth

Permissions

- Full system access
- View all analytics
- Manage recruiters
- Manage companies

---

## 3.2 HR Director

Responsibilities

- Monitor hiring trends
- View recruitment KPIs
- Monitor hiring costs
- Analyze hiring funnel
- Review recruiter performance

Permissions

- Dashboard access
- Analytics access
- Candidate reports

---

## 3.3 Recruiter

Responsibilities

- Create candidates
- Submit resumes
- Schedule interviews
- Track applications
- Update candidate stages
- Manage offers

Permissions

- Candidate Management
- Job Management
- Application Management

---

## 3.4 Hiring Manager

Responsibilities

- Review submitted candidates
- Record interview feedback
- Review offers
- Approve placements

Permissions

- Candidate Review
- Interview Feedback
- Offer Approval

---

# 4. Functional Modules

---

# Module 1 — Company Management

Purpose

Maintain company information including End Clients and Implementation Partners.

Functions

- Add Company
- Update Company
- Delete Company
- Search Company
- View Company Profile
- Track Active Jobs
- Track Placements
- View Revenue
- View Placement Margin

Data Captured

- Company Name
- Company Type
- Industry
- Country
- State
- Website
- Status

---

# Module 2 — Recruiter Management

Purpose

Maintain recruiter information and performance metrics.

Functions

- Add Recruiter
- Update Recruiter
- Delete Recruiter
- Assign Jobs
- Assign Candidates
- View Recruiter Dashboard
- Recruiter KPI Report

Metrics

- Placements
- Interviews
- Offers
- Time to Fill
- Offer Acceptance Rate

---

# Module 3 — Candidate Management

Purpose

Manage candidate information throughout the recruitment lifecycle.

Functions

- Add Candidate
- Update Candidate
- Delete Candidate
- Upload Resume
- Search Candidate
- Candidate Timeline
- Candidate Profile

Candidate Information

- Name
- Email
- Phone
- Skills
- Experience
- Current Company
- Current Location
- Preferred Location
- Visa Status
- Work Authorization
- Resume

---

# Module 4 — Job Management

Purpose

Manage client job requisitions.

Functions

- Create Job
- Update Job
- Close Job
- Assign Recruiter
- Assign Company
- Job Search

Job Information

- Job Title
- Client
- Vendor
- Location
- Employment Type
- Work Mode
- Bill Rate
- Pay Rate
- Priority
- Required Skills
- Nice-to-Have Skills
- Experience Required

---

# Module 5 — Application Management

Purpose

Track candidate applications.

Functions

- Submit Candidate
- Withdraw Application
- Reject Application
- Update Status
- View Timeline

Application Stages

- Applied
- Screening
- Submitted
- Interview
- Offer
- Hired
- Rejected

---

# Module 6 — Interview Management

Purpose

Manage interview process.

Functions

- Schedule Interview
- Update Interview
- Record Feedback
- Interview Result
- Final Decision

Interview Types

- HR
- Technical
- Client
- Final

---

# Module 7 — Offer Management

Purpose

Manage offers.

Functions

- Generate Offer
- Accept Offer
- Reject Offer
- Counter Offer
- Joining Date

Offer Details

- Salary
- Bill Rate
- Pay Rate
- Joining Date
- Status

---

# Module 8 — Placement Management

Purpose

Track successful hires.

Functions

- Confirm Placement
- Start Date
- End Date
- Margin Calculation
- Placement Status

Metrics

- Time to Fill
- Time to Hire
- Placement Margin

---

# Module 9 — Recruitment Analytics

Purpose

Provide recruitment intelligence using SQL and BI.

Analytics

- Recruitment Funnel
- Hiring Trends
- Time to Hire
- Time to Fill
- Recruiter Performance
- Offer Acceptance
- Source Performance
- Placement Trends
- Margin Analysis
- Skill Demand
- Client Performance
- Vendor Performance

---

# Module 10 — AI Resume Parser

Purpose

Extract structured information from resumes.

Functions

- Upload Resume
- Parse Resume
- Extract Skills
- Extract Experience
- Extract Education
- Extract Certifications
- Extract Contact Details
- Resume Summary

Output

- Structured Candidate Profile

---

# Module 11 — AI Job Matcher

Purpose

Compare candidate resumes against job descriptions.

Functions

- Upload Resume
- Select Job
- Calculate Match Score
- Identify Missing Skills
- Skill Similarity
- Candidate Ranking

Output

- Match Score
- Skill Gap Analysis
- Hiring Recommendation

---

# Module 12 — AI Recruitment Assistant

Purpose

Allow users to query recruitment data using natural language.

Example Questions

- Show top recruiters
- Show best hiring source
- Which jobs are difficult to fill?
- Highest placement margin
- Average hiring time
- Candidate status summary

Capabilities

- Natural Language Queries
- KPI Explanation
- Recruitment Insights
- AI Summary Generation

---

# Module 13 — Dashboard

Executive Dashboard

Visuals

- Total Jobs
- Open Jobs
- Closed Jobs
- Candidates
- Applications
- Interviews
- Offers
- Placements
- Revenue
- Margin

Recruiter Dashboard

- Recruiter Rankings
- Placement Count
- Offer Rate
- Interview Rate

Candidate Dashboard

- Pipeline
- Candidate Sources
- Skill Distribution

Company Dashboard

- Client Performance
- Vendor Performance

Analytics Dashboard

- Funnel
- Hiring Trend
- Source Effectiveness
- Placement Trend

AI Dashboard

- Resume Match Results
- Skill Gap Analysis
- Hiring Predictions

---

# Module 14 — Streamlit Application

Pages

Home

Dashboard

Companies

Recruiters

Candidates

Jobs

Applications

Interviews

Offers

Placements

Analytics

Resume Parser

Job Matcher

AI Assistant

Settings

About

---

# 5. User Workflow

Primary Recruitment Workflow

Client raises Job Requirement

↓

Implementation Partner

↓

Recruitment Agency

↓

Recruiter Assigned

↓

Candidate Sourcing

↓

Resume Screening

↓

Candidate Submission

↓

Interview

↓

Offer

↓

Placement

↓

Analytics Dashboard

↓

AI Insights

---

# 6. Business Rules

- Every Job belongs to one Company.
- One Company may have multiple Jobs.
- Every Candidate can apply to multiple Jobs.
- Every Application belongs to one Candidate.
- Every Application belongs to one Job.
- Offer cannot be generated without Interview.
- Placement cannot exist without Accepted Offer.
- Bill Rate must always exceed Pay Rate.
- Recruiter KPIs are calculated using successful placements.

---

# 7. Validation Rules

Candidate

- Email must be unique.
- Phone number must be valid.

Recruiter

- Employee ID must be unique.

Company

- Company Name cannot be empty.

Job

- Job ID must be unique.
- Bill Rate > Pay Rate

Resume

- PDF supported
- DOCX supported

Application

- Candidate cannot apply twice to the same Job.

Offer

- Offer Date cannot be before Interview Date.

Placement

- Start Date cannot be before Offer Acceptance.

---

# 8. Dashboard Requirements

Executive Dashboard

KPIs

- Total Jobs
- Active Jobs
- Placements
- Revenue
- Placement Margin
- Offer Acceptance
- Time to Hire
- Time to Fill

Charts

- Funnel
- Hiring Trend
- Recruiter Performance
- Source Effectiveness
- Company Performance
- Skill Demand

---

# 9. AI Functional Requirements

Resume Parser

Input

Resume PDF

Output

Structured Candidate Profile

Job Matcher

Input

Resume + Job Description

Output

- Match Score
- Missing Skills
- Recommendation

Recruitment Assistant

Input

Natural Language

Output

Analytics Summary

---

# 10. Reporting Requirements

Executive Report

Recruiter Report

Candidate Report

Company Report

Vendor Report

Client Report

Placement Report

Revenue Report

Margin Report

AI Report

---

# 11. Non-Functional Requirements

Performance

- Dashboard response under 5 seconds.

Scalability

- Support 100,000+ synthetic recruitment records.

Maintainability

- Modular architecture.

Security

- Role-based logical access.

Reliability

- Data consistency across modules.

Portability

- Deployable on Streamlit Cloud or local machine.

---

# 12. Future Enhancements

- ATS Integration (Ceipal, JobDiva)
- LinkedIn Integration
- Email Notifications
- Interview Scheduling
- Candidate Recommendation Engine
- AI Recruiter Copilot
- Resume Database Search
- Voice-based AI Assistant
- Multi-Agency Support
- Mobile Application

---

# Document Approval

| Version | Date | Status |
|----------|------|--------|
| 1.0 | August 2026 | Approved for Development |

---

## End of Document