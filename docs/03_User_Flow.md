# TalentIQ AI Recruitment Analytics
## User Flow Document (UFD)

**Version:** 1.0  
**Project:** TalentIQ AI Recruitment Analytics  
**Last Updated:** August 2026

---

# Table of Contents

1. Introduction
2. User Roles
3. Overall System Workflow
4. Recruitment Workflow
5. User Flows
6. AI Workflows
7. Dashboard Navigation
8. Exception Flows
9. Future User Flows

---

# 1. Introduction

The User Flow Document (UFD) defines how different users interact with the TalentIQ AI Recruitment Analytics platform.

It describes the sequence of actions users perform while using the system, from creating a job requisition to successfully placing a candidate and analyzing recruitment performance.

This document serves as the foundation for:

- Database Design
- UI/UX Design
- Streamlit Application
- Backend Development
- AI Feature Integration

---

# 2. User Roles

The platform supports four primary user roles.

## Recruitment Agency Owner

Responsible for:

- Business performance
- Recruiter productivity
- Revenue analysis
- Client performance
- Executive dashboards

---

## HR Director

Responsible for:

- Recruitment analytics
- Hiring KPIs
- Team performance
- Hiring trends

---

## Recruiter

Responsible for:

- Managing jobs
- Managing candidates
- Resume submission
- Interview coordination
- Offer management

---

## Hiring Manager

Responsible for:

- Reviewing submitted candidates
- Conducting interviews
- Providing interview feedback
- Approving offers

---

# 3. Overall System Workflow

The TalentIQ platform follows the complete recruitment lifecycle.

```text
Client raises Job Requirement
            │
            ▼
Implementation Partner (Optional)
            │
            ▼
Recruitment Agency
            │
            ▼
Recruiter receives Job
            │
            ▼
Candidate Sourcing
            │
            ▼
Resume Upload
            │
            ▼
AI Resume Parsing
            │
            ▼
Resume-to-Job Matching
            │
            ▼
Candidate Submission
            │
            ▼
Interview Process
            │
            ▼
Offer Generation
            │
            ▼
Offer Acceptance
            │
            ▼
Placement
            │
            ▼
Analytics Dashboard
            │
            ▼
AI Recruitment Insights
```

---

# 4. End-to-End Recruitment Workflow

## Step 1 — Client Creates Job Requirement

Input

- Job Title
- Required Skills
- Experience
- Bill Rate
- Pay Rate
- Work Mode
- Employment Type
- End Client
- Vendor
- Location

Output

Job Requisition Created

---

## Step 2 — Recruiter Receives Job

Recruiter

- Reviews Job
- Understands Requirements
- Begins Candidate Search

Output

Recruitment Starts

---

## Step 3 — Candidate Sourcing

Candidates are sourced from

- LinkedIn
- Dice
- Monster
- CareerBuilder
- Indeed
- Internal Database
- Employee Referral

Output

Candidate Added to Pipeline

---

## Step 4 — Candidate Profile Creation

Recruiter enters

- Personal Information
- Contact Details
- Skills
- Experience
- Resume
- Work Authorization
- Preferred Location

Output

Candidate Profile Created

---

## Step 5 — Resume Upload

Recruiter uploads

- PDF Resume
- DOCX Resume

System

- Stores Resume
- Sends Resume to AI Parser

Output

Resume Ready for Processing

---

## Step 6 — AI Resume Parsing

System extracts

- Skills
- Experience
- Education
- Certifications
- Current Company
- Previous Companies
- Contact Information

Output

Structured Candidate Profile

---

## Step 7 — Resume Matching

Recruiter selects Job.

AI compares

Resume

↓

Job Description

AI calculates

- Match Score
- Missing Skills
- Skill Similarity
- Candidate Ranking

Output

AI Recommendation

---

## Step 8 — Candidate Submission

Recruiter submits candidate.

Application Status

Applied

↓

Screening

↓

Submitted

Output

Candidate Waiting for Interview

---

## Step 9 — Interview Process

Interview Types

- HR Interview
- Technical Interview
- Client Interview
- Final Round

Possible Results

- Selected
- Rejected
- Next Round

Output

Interview Completed

---

## Step 10 — Offer Process

Recruiter generates Offer.

Candidate

- Accepts
- Rejects
- Negotiates

Output

Offer Status Updated

---

## Step 11 — Placement

If Offer Accepted

Placement Created

Information

- Joining Date
- Bill Rate
- Pay Rate
- Placement Status

Output

Successful Hire

---

## Step 12 — Analytics

System updates

- Time to Hire
- Time to Fill
- Recruiter Performance
- Offer Rate
- Hiring Funnel
- Margin
- Revenue

Output

Executive Dashboard Updated

---

# 5. User Flows

---

## Recruitment Agency Owner Flow

Login

↓

Executive Dashboard

↓

Business KPIs

↓

Recruiter Performance

↓

Client Performance

↓

Revenue Analysis

↓

Placement Margin

↓

Analytics Reports

↓

Logout

---

## HR Director Flow

Login

↓

Hiring Dashboard

↓

Hiring Funnel

↓

Time to Hire

↓

Offer Acceptance

↓

Skill Demand

↓

Recruitment Reports

↓

Logout

---

## Recruiter Flow

Login

↓

Dashboard

↓

View Assigned Jobs

↓

Candidate Search

↓

Add Candidate

↓

Upload Resume

↓

AI Resume Analysis

↓

Submit Candidate

↓

Schedule Interview

↓

Generate Offer

↓

Placement

↓

Logout

---

## Hiring Manager Flow

Login

↓

Candidate Review

↓

Interview Feedback

↓

Approve Candidate

↓

Approve Offer

↓

Placement Confirmation

↓

Logout

---

# 6. AI Workflows

---

## Resume Parser Workflow

Upload Resume

↓

Extract Skills

↓

Extract Experience

↓

Extract Education

↓

Extract Certifications

↓

Generate Candidate Summary

↓

Store Results

---

## Job Matcher Workflow

Select Resume

↓

Select Job

↓

Compare Skills

↓

Calculate Match Score

↓

Identify Missing Skills

↓

Generate Recommendation

↓

Display Results

---

## AI Recruitment Assistant Workflow

User asks Question

↓

AI Understands Query

↓

Generate SQL / Retrieve Data

↓

Analyze Results

↓

Generate Natural Language Response

↓

Display Answer

Example Questions

- Show best recruiters
- Show hiring trend
- Which source generates highest placements?
- Highest margin client?
- Average hiring time?

---

# 7. Dashboard Navigation

Home

↓

Executive Dashboard

↓

Recruiter Dashboard

↓

Candidate Dashboard

↓

Client Dashboard

↓

Analytics Dashboard

↓

AI Dashboard

↓

Settings

↓

Logout

---

# 8. Exception Flows

## Resume Upload Failure

Resume Upload

↓

Invalid Format

↓

Display Error

↓

Upload Again

---

## Duplicate Candidate

Add Candidate

↓

Email Exists

↓

Show Duplicate Warning

↓

Merge or Cancel

---

## Offer Rejected

Offer Generated

↓

Candidate Rejects

↓

Application Closed

↓

Recruiter Continues Search

---

## Candidate Withdraws

Application Active

↓

Candidate Withdraws

↓

Status Updated

↓

Pipeline Updated

---

## Job Closed

Job Filled

↓

Close Job

↓

Prevent New Applications

↓

Archive Job

---

# 9. Future User Flows

Future releases may include:

- Candidate Portal
- Recruiter Mobile App
- Email Automation
- ATS Integration
- LinkedIn Integration
- AI Candidate Recommendation
- AI Interview Scheduling
- Recruiter Copilot
- Multi-Tenant SaaS
- Client Self-Service Portal

---

# User Flow Summary

The TalentIQ platform follows a complete recruitment lifecycle beginning with job creation, continuing through sourcing, resume parsing, AI-powered job matching, interviews, offers, placements, and ending with recruitment analytics and AI-generated business insights.

The user flows defined in this document will directly drive the application's UI design, PostgreSQL database schema, API design, Streamlit navigation, SQL analytics, Power BI dashboards, and AI modules.

---

# Document Approval

| Version | Date | Status |
|----------|------|--------|
| 1.0 | August 2026 | Approved for System Design |

---

## End of Document