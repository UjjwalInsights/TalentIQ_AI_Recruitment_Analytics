/*
=====================================================================
        TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM

        File: 06_seed_master_data.sql

        Purpose:
        --------
        Inserts realistic master/reference data required by
        the TalentIQ recruitment analytics platform.

        This file contains ONLY master data.

        Large transactional data such as:
        - Candidates
        - Jobs
        - Applications
        - Interviews
        - Offers
        - Placements

        will be generated later using Python.

        Run AFTER:
        03_create_tables.sql
        04_constraints.sql
        05_indexes.sql

=====================================================================
*/

SET search_path TO recruitment;


/*
=====================================================================
1. COMPANIES
=====================================================================

Company types:

- End Client
- Implementation Partner
- Recruitment Agency
- Direct Client

The same company can participate in different recruiting
relationships depending on the job.

Example:

Mphasis → vendor for a JPMC requirement
JPMC    → end client

=====================================================================
*/

INSERT INTO recruitment.companies
(
    company_name,
    company_type,
    industry,
    website,
    city,
    state,
    country,
    employee_size,
    founded_year,
    is_active
)
VALUES

-- ============================================================
-- END CLIENTS
-- ============================================================

(
    'JPMorgan Chase',
    'End Client',
    'Banking',
    'https://www.jpmorganchase.com',
    'New York',
    'NY',
    'USA',
    300000,
    1799,
    TRUE
),

(
    'Wells Fargo',
    'End Client',
    'Banking',
    'https://www.wellsfargo.com',
    'San Francisco',
    'CA',
    'USA',
    230000,
    1852,
    TRUE
),

(
    'Apple',
    'End Client',
    'Technology',
    'https://www.apple.com',
    'Cupertino',
    'CA',
    'USA',
    164000,
    1976,
    TRUE
),

(
    'Bank of America',
    'End Client',
    'Banking',
    'https://www.bankofamerica.com',
    'Charlotte',
    'NC',
    'USA',
    213000,
    1998,
    TRUE
),

(
    'Citigroup',
    'End Client',
    'Financial Services',
    'https://www.citigroup.com',
    'New York',
    'NY',
    'USA',
    239000,
    1998,
    TRUE
),

(
    'Capital One',
    'End Client',
    'Financial Services',
    'https://www.capitalone.com',
    'McLean',
    'VA',
    'USA',
    52000,
    1994,
    TRUE
),

(
    'Verizon',
    'End Client',
    'Telecommunications',
    'https://www.verizon.com',
    'New York',
    'NY',
    'USA',
    100000,
    2000,
    TRUE
),

(
    'AT&T',
    'End Client',
    'Telecommunications',
    'https://www.att.com',
    'Dallas',
    'TX',
    'USA',
    140000,
    1885,
    TRUE
),

(
    'UnitedHealth Group',
    'End Client',
    'Healthcare',
    'https://www.unitedhealthgroup.com',
    'Minnetonka',
    'MN',
    'USA',
    440000,
    1977,
    TRUE
),

(
    'The Home Depot',
    'End Client',
    'Retail',
    'https://www.homedepot.com',
    'Atlanta',
    'GA',
    'USA',
    470000,
    1978,
    TRUE
),


-- ============================================================
-- IMPLEMENTATION PARTNERS / VENDORS
-- ============================================================

(
    'Mphasis',
    'Implementation Partner',
    'Information Technology',
    'https://www.mphasis.com',
    'Bangalore',
    'Karnataka',
    'India',
    37000,
    2000,
    TRUE
),

(
    'HCL Technologies',
    'Implementation Partner',
    'Information Technology',
    'https://www.hcltech.com',
    'Noida',
    'Uttar Pradesh',
    'India',
    220000,
    1976,
    TRUE
),

(
    'Capgemini',
    'Implementation Partner',
    'Information Technology',
    'https://www.capgemini.com',
    'Paris',
    NULL,
    'France',
    340000,
    1967,
    TRUE
),

(
    'Cognizant',
    'Implementation Partner',
    'Information Technology',
    'https://www.cognizant.com',
    'Teaneck',
    'NJ',
    'USA',
    340000,
    1994,
    TRUE
),

(
    'Tata Consultancy Services',
    'Implementation Partner',
    'Information Technology',
    'https://www.tcs.com',
    'Mumbai',
    'Maharashtra',
    'India',
    600000,
    1968,
    TRUE
),

(
    'Infosys',
    'Implementation Partner',
    'Information Technology',
    'https://www.infosys.com',
    'Bangalore',
    'Karnataka',
    'India',
    320000,
    1981,
    TRUE
),

(
    'Accenture',
    'Implementation Partner',
    'Information Technology',
    'https://www.accenture.com',
    'Dublin',
    'Ireland',
    'USA',
    774000,
    1989,
    TRUE
),


-- ============================================================
-- RECRUITMENT AGENCIES
-- ============================================================

(
    'Precision Technologies',
    'Recruitment Agency',
    'Staffing & Recruiting',
    NULL,
    'Noida',
    'Uttar Pradesh',
    'India',
    500,
    2010,
    TRUE
),

(
    'TalentBridge Solutions',
    'Recruitment Agency',
    'Staffing & Recruiting',
    NULL,
    'Dallas',
    'TX',
    'USA',
    300,
    2012,
    TRUE
),

(
    'TechHire Solutions',
    'Recruitment Agency',
    'Staffing & Recruiting',
    NULL,
    'Chicago',
    'IL',
    'USA',
    250,
    2015,
    TRUE
),


-- ============================================================
-- DIRECT CLIENTS
-- ============================================================

(
    'FinTech Innovations',
    'Direct Client',
    'Financial Technology',
    NULL,
    'Austin',
    'TX',
    'USA',
    1200,
    2014,
    TRUE
),

(
    'HealthTech Systems',
    'Direct Client',
    'Healthcare Technology',
    NULL,
    'Boston',
    'MA',
    'USA',
    850,
    2016,
    TRUE
),

(
    'Retail Analytics Corp',
    'Direct Client',
    'Retail Technology',
    NULL,
    'Seattle',
    'WA',
    'USA',
    600,
    2018,
    TRUE
);


/*
=====================================================================
2. RECRUITMENT SOURCES
=====================================================================

These represent the channels recruiters use to find candidates.

Based on your real recruiting workflow:

- LinkedIn
- Dice
- Monster
- CareerBuilder
- Indeed
- Internal ATS
- Referral
- Career Fair

=====================================================================
*/

INSERT INTO recruitment.sources
(
    source_name,
    source_category
)
VALUES

('LinkedIn', 'Outbound'),
('Dice', 'Outbound'),
('Monster', 'Outbound'),
('CareerBuilder', 'Outbound'),
('Indeed', 'Outbound'),
('Internal ATS Database', 'Inbound'),
('Employee Referral', 'Referral'),
('Career Fair', 'Inbound'),
('Company Careers Page', 'Inbound');


/*
=====================================================================
3. SKILLS
=====================================================================

Technical skills commonly found in US IT recruitment.

=====================================================================
*/

INSERT INTO recruitment.skills
(
    skill_name,
    skill_category
)
VALUES

-- Programming
('Python', 'Technical'),
('Java', 'Technical'),
('JavaScript', 'Technical'),
('C#', 'Technical'),
('C++', 'Technical'),
('SQL', 'Technical'),
('R', 'Technical'),

-- Frontend
('React', 'Technical'),
('Angular', 'Technical'),
('Vue.js', 'Technical'),
('HTML', 'Technical'),
('CSS', 'Technical'),

-- Backend
('Node.js', 'Technical'),
('.NET', 'Technical'),
('Spring Boot', 'Technical'),
('Django', 'Technical'),
('FastAPI', 'Technical'),

-- Data
('Pandas', 'Technical'),
('NumPy', 'Technical'),
('PySpark', 'Technical'),
('Data Analysis', 'Technical'),
('Machine Learning', 'Technical'),
('Statistics', 'Technical'),

-- Cloud
('AWS', 'Tool'),
('Azure', 'Tool'),
('Google Cloud', 'Tool'),

-- DevOps
('Docker', 'Tool'),
('Kubernetes', 'Tool'),
('Jenkins', 'Tool'),
('Terraform', 'Tool'),
('Git', 'Tool'),
('GitHub', 'Tool'),

-- Databases
('PostgreSQL', 'Tool'),
('MySQL', 'Tool'),
('Oracle', 'Tool'),
('MongoDB', 'Tool'),
('SQL Server', 'Tool'),

-- Enterprise
('SAP', 'Tool'),
('Salesforce', 'Tool'),

-- Analytics / BI
('Tableau', 'Tool'),
('Power BI', 'Tool'),
('Excel', 'Tool'),

-- Business / Professional
('Business Analysis', 'Soft Skill'),
('Project Management', 'Soft Skill'),
('Agile', 'Soft Skill'),
('Scrum', 'Soft Skill'),

-- AI / LLM
('Natural Language Processing', 'Technical'),
('Large Language Models', 'Technical'),
('Generative AI', 'Technical'),
('LangChain', 'Tool'),
('OpenAI API', 'Tool'),

-- Certifications
('PMP', 'Certification'),
('AWS Certified', 'Certification'),
('Azure Certified', 'Certification');


/*
=====================================================================
4. WORK AUTHORIZATIONS
=====================================================================

US IT recruitment work authorization categories.

=====================================================================
*/

INSERT INTO recruitment.work_authorizations
(
    authorization_name,
    description
)
VALUES

(
    'US Citizen',
    'United States citizen authorized to work without sponsorship.'
),

(
    'Green Card',
    'Permanent resident authorized to work in the United States.'
),

(
    'H1B',
    'H-1B visa holder.'
),

(
    'EAD',
    'Employment Authorization Document holder.'
),

(
    'TN',
    'TN visa holder.'
),

(
    'OPT',
    'Optional Practical Training authorization.'
),

(
    'CPT',
    'Curricular Practical Training authorization.'
);


/*
=====================================================================
5. LOCATIONS
=====================================================================

Common US IT recruitment locations.

=====================================================================
*/

INSERT INTO recruitment.locations
(
    city,
    state,
    country,
    work_mode
)
VALUES

('New York', 'NY', 'USA', 'Onsite'),
('New York', 'NY', 'USA', 'Hybrid'),
('New York', 'NY', 'USA', 'Remote'),

('Jersey City', 'NJ', 'USA', 'Hybrid'),
('Jersey City', 'NJ', 'USA', 'Onsite'),

('Dallas', 'TX', 'USA', 'Onsite'),
('Dallas', 'TX', 'USA', 'Hybrid'),
('Dallas', 'TX', 'USA', 'Remote'),

('Austin', 'TX', 'USA', 'Hybrid'),

('Houston', 'TX', 'USA', 'Onsite'),

('Chicago', 'IL', 'USA', 'Hybrid'),
('Chicago', 'IL', 'USA', 'Onsite'),

('Atlanta', 'GA', 'USA', 'Hybrid'),

('Charlotte', 'NC', 'USA', 'Hybrid'),

('Boston', 'MA', 'USA', 'Hybrid'),

('Seattle', 'WA', 'USA', 'Hybrid'),

('San Francisco', 'CA', 'USA', 'Hybrid'),

('San Jose', 'CA', 'USA', 'Hybrid'),

('Los Angeles', 'CA', 'USA', 'Hybrid'),

('Cupertino', 'CA', 'USA', 'Onsite'),

('Remote', NULL, 'USA', 'Remote');


/*
=====================================================================
6. DEPARTMENTS
=====================================================================

Departments are linked to companies.

We first retrieve company IDs dynamically instead of assuming
specific SERIAL values.

=====================================================================
*/


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Information Technology'
FROM recruitment.companies
WHERE company_name = 'JPMorgan Chase';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Data & Analytics'
FROM recruitment.companies
WHERE company_name = 'JPMorgan Chase';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Information Technology'
FROM recruitment.companies
WHERE company_name = 'Wells Fargo';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Technology'
FROM recruitment.companies
WHERE company_name = 'Apple';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Information Technology'
FROM recruitment.companies
WHERE company_name = 'Mphasis';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Information Technology'
FROM recruitment.companies
WHERE company_name = 'HCL Technologies';


INSERT INTO recruitment.departments
(
    company_id,
    department_name
)
SELECT
    company_id,
    'Technology'
FROM recruitment.companies
WHERE company_name = 'Capgemini';

/*
=====================================================================
7. RECRUITERS
=====================================================================

Synthetic recruitment team working for Precision Technologies.

=====================================================================
*/


-- =========================================================
-- 1. ROHAN MEHTA
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Rohan Mehta',
    'rohan.mehta@talentiq.demo',
    '+1-555-100-0001',
    company_id,
    'IT Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 2. RAHUL SHARMA
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Rahul Sharma',
    'rahul.recruiter@talentiq.demo',
    '+1-555-100-0002',
    company_id,
    'Senior IT Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 3. PRIYA SINGH
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Priya Singh',
    'priya.recruiter@talentiq.demo',
    '+1-555-100-0003',
    company_id,
    'Technical Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 4. AMIT VERMA
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Amit Verma',
    'amit.recruiter@talentiq.demo',
    '+1-555-100-0004',
    company_id,
    'IT Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 5. NEHA KAPOOR
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Neha Kapoor',
    'neha.kapoor@talentiq.demo',
    '+1-555-100-0005',
    company_id,
    'Technical Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 6. SNEHA PATEL
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Sneha Patel',
    'sneha.patel@talentiq.demo',
    '+1-555-100-0006',
    company_id,
    'Senior IT Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 7. ADITYA RAO
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Aditya Rao',
    'aditya.rao@talentiq.demo',
    '+1-555-100-0007',
    company_id,
    'Technical Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';


-- =========================================================
-- 8. POOJA NAIR
-- =========================================================

INSERT INTO recruitment.recruiters
(
    recruiter_name,
    email,
    phone,
    company_id,
    designation
)
SELECT
    'Pooja Nair',
    'pooja.nair@talentiq.demo',
    '+1-555-100-0008',
    company_id,
    'IT Recruiter'
FROM recruitment.companies
WHERE company_name = 'Precision Technologies';

/*
=====================================================================
MASTER DATA INSERTION COMPLETED
=====================================================================

Companies              ✔
Sources                ✔
Skills                 ✔
Work Authorizations    ✔
Locations              ✔
Departments             ✔
Recruiters             ✔

=====================================================================
*/
