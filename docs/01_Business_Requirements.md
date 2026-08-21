# TalentIQ AI Recruitment Analytics
## Business Requirements Document (BRD)

**Version:** 1.0
**Project:** TalentIQ AI Recruitment Analytics
**Last Updated:** August 2026

---

# 1. Project Overview

TalentIQ is an AI-powered Recruitment Analytics Platform designed to help recruitment agencies, staffing companies, and HR teams make faster and smarter hiring decisions through data analytics and artificial intelligence.

The platform is modeled specifically on the **US IT staffing workflow**, where an agency receives job requisitions either directly from a client or through an **implementation partner** (e.g., Mphasis, Capgemini, HCL) representing an **end client** (e.g., JPMC, Wells Fargo, Apple). It provides recruitment analytics, recruiter performance tracking, hiring funnel analysis, resume-to-job matching, and executive dashboards.

---

# 2. Problem Statement

Recruitment agencies — especially those operating in the vendor/implementation-partner supply chain common to IT staffing — struggle with:

- Long hiring cycles across multi-tier vendor chains
- Poor candidate pipeline visibility across sourcing channels (Dice, Monster, CareerBuilder, Indeed, LinkedIn, referrals)
- Low interview-to-offer conversion rates
- No visibility into margin (bill rate vs. pay rate) on contract placements
- Manual resume screening against job requirements
- No centralized analytics dashboard
- Difficulty measuring individual recruiter performance and source ROI

TalentIQ solves these problems using SQL analytics, BI dashboards, machine learning, and AI-powered resume/job matching.

---

# 3. Scope

### In Scope
- Recruitment pipeline tracking: job requisition → application → interview → offer → placement
- Vendor/end-client supply chain modeling (implementation partner vs. direct client)
- Contract role economics: bill rate, pay rate, margin
- SQL-based business analytics (funnel, time-to-fill, source effectiveness, recruiter performance)
- BI dashboard (Power BI / Tableau)
- ML-based hiring outcome prediction
- AI resume parsing and resume-to-job match scoring
- Natural-language query assistant over recruitment data
- Streamlit multi-page application tying the above together

### Out of Scope
- Live integration with real ATS platforms (Ceipal, JobDiva) or job boards (Dice, Monster, Indeed) — the platform uses **synthetic, realistic data** modeled on these workflows, not live API integrations
- Payroll or invoicing processing
- Real candidate PII — all data is synthetically generated for portfolio/demo purposes

---

# 4. Target Users & Stakeholders

### Recruitment Agency Owner (Primary)
Needs: revenue and margin insights, recruiter performance, client/vendor analytics, hiring KPIs

### HR Director / Agency Leadership (Primary)
Needs: hiring trends, team performance, hiring cost, executive dashboard

### Recruiter (Primary)
Needs: candidate tracking, resume screening, interview management, candidate pipeline visibility

### Hiring Manager / Account Manager (Primary)
Needs: candidate shortlist, interview feedback, offer tracking, vendor-chain visibility (which partner/client a req came through)

### Candidates (Secondary — future version)
Not a direct platform user in v1; represented as data subjects only.

---

# 5. Business Objectives & Goals

TalentIQ exists to:

- Centralize recruitment operations into a single source of truth
- Enable data-driven recruitment decisions through analytics
- Reduce manual resume screening through AI-assisted matching
- Provide executive-level visibility into recruitment performance

Specifically, the platform should help organizations:

- Reduce Time to Hire and Time to Fill
- Improve candidate quality and interview conversion
- Increase Offer Acceptance Rate
- Improve recruiter productivity and accountability
- Increase visibility into placement margin (contract roles)
- Identify highest-performing sourcing channels
- Improve overall hiring pipeline visibility across the vendor chain

---

# 6. Success Metrics (KPIs)

These are the specific, measurable outputs the SQL Analytics and Dashboard modules must be able to produce:

| Metric | Definition |
|---|---|
| Time to Fill | Days from job `opened_date` to `placement.start_date` |
| Time to Hire | Days from candidate `applied_date` to offer acceptance |
| Offer Acceptance Rate | Accepted offers ÷ total offers extended |
| Recruitment Funnel Conversion | % of candidates surviving each stage (Applied → Screening → Interview → Offer → Hired) |
| Source Effectiveness | Hires per source (Dice, LinkedIn, Referral, etc.) ÷ candidates sourced |
| Recruiter Performance | Placements, time-to-fill, and offer-acceptance rate per recruiter |
| Placement Margin | Bill rate − pay rate, per contract placement |
| Skill Demand | Most frequently required skills across open jobs |
| Vendor/Client Performance | Fill rate and time-to-fill segmented by end client and implementation partner |

---

# 7. Data Sources (Modeled, Not Live-Integrated)

TalentIQ's synthetic data is designed to realistically mirror:

- **ATS-style tracking** (Ceipal / JobDiva-equivalent structure): job requisitions, candidate pipeline stages
- **Job boards**: Dice, Monster, CareerBuilder, Indeed
- **Professional networks**: LinkedIn
- **Referrals** and internal candidate database
- **Client/vendor requisition data**: Job ID, location/work mode, bill rate, must-have/nice-to-have skills, responsibilities — supplied through an implementation partner or directly by an end client

---

# 8. Functional Requirements (by Module)

| Module | Requirement |
|---|---|
| Database | Normalized PostgreSQL schema modeling companies (end client + vendor), jobs, candidates, applications, interviews, offers, and placements |
| SQL Analytics | Queries answering all KPIs in Section 6 using joins, CTEs, and window functions |
| Dashboard | Power BI/Tableau dashboard covering executive overview, funnel, recruiter performance, source analysis |
| Python/ETL | Synthetic data generation, cleaning, validation, KPI calculation |
| Machine Learning | Predictive model estimating likelihood of an application converting to a placement |
| AI — Resume Parser | Extract skills, experience, education, certifications, employment history |
| AI — Job Matcher | Match score, missing skills, skill similarity, candidate ranking against a job's required skills |
| AI — Recruitment Assistant | Natural-language queries over recruitment data, KPI explanations |
| Streamlit App | Unified interface: dashboard, candidate search, resume analyzer, job matching, AI assistant |

---

# 9. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Dashboard visuals should render within a few seconds against the generated dataset |
| Scalability | Schema and queries should remain performant with tens of thousands of synthetic records |
| Security | Role-aware design in the data model (recruiter-level access to their own pipeline); not enforced at the infra level in v1 |
| Maintainability | Modular Python package structure (`src/talentiq/`) with documented architecture |
| Extensibility | Schema designed so future ATS or job-board integrations could map onto existing tables without a redesign |

---

# 10. Possible Future Directions (Non-Binding)

These are ideas, not commitments — kept intentionally small so the current scope stays honest:

- Candidate recommendation engine (ranking candidates against multiple open jobs)
- Automated interview scheduling suggestions
- Expanded resume parsing (work authorization, certifications)

---

# 11. Assumptions & Constraints

- All candidate, job, and company data is **synthetically generated** — no real PII is used
- The platform is a **portfolio/demo system**, not a production tool processing live client data
- Vendor chain depth is assumed to be **at most two tiers** (end client → one implementation partner) unless a future revision extends this
- Database: PostgreSQL. Backend: Python. Dashboard: Power BI/Tableau. App: Streamlit

---

# 12. Expected Outcome

TalentIQ will be a complete Recruitment Intelligence Platform combining a normalized relational database, SQL analytics, BI dashboards, machine learning, and AI-powered resume/job matching — built to reflect the real operational workflow of a US IT staffing agency.