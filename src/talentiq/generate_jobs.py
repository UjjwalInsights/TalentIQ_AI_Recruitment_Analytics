"""
===========================================================
TalentIQ - AI Recruitment Analytics Platform

File: generate_jobs.py

Purpose:
    Generate realistic synthetic IT recruitment jobs
    and associated job skills.

Tables populated:
    1. recruitment.jobs
    2. recruitment.job_skills

Run from project root:
    python src/talentiq/etl/generate_jobs.py
===========================================================
"""

import random
from datetime import date, timedelta

import psycopg2
from faker import Faker


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "recruitment_analytics",
    "user": "postgres",
    "password": "Just890",
}


# =========================================================
# GENERATION CONFIGURATION
# =========================================================

NUMBER_OF_JOBS = 1000

fake = Faker("en_US")

# Makes the generated dataset reproducible.
random.seed(42)
Faker.seed(42)


# =========================================================
# JOB TEMPLATES
# =========================================================

JOB_TEMPLATES = [

    {
        "title": "Data Analyst",
        "department": "Analytics",
        "experience": (2, 6),
        "skills": [
            "SQL",
            "Python",
            "Business Analysis"
        ]
    },

    {
        "title": "Senior Data Analyst",
        "department": "Analytics",
        "experience": (4, 8),
        "skills": [
            "SQL",
            "Python",
            "Tableau",
            "Business Analysis"
        ]
    },

    {
        "title": "Data Scientist",
        "department": "Analytics",
        "experience": (3, 8),
        "skills": [
            "Python",
            "SQL"
        ]
    },

    {
        "title": "AI Engineer",
        "department": "Artificial Intelligence",
        "experience": (3, 8),
        "skills": [
            "Python",
            "AWS",
            "Docker"
        ]
    },

    {
        "title": "ML Engineer",
        "department": "Artificial Intelligence",
        "experience": (4, 9),
        "skills": [
            "Python",
            "AWS",
            "Kubernetes"
        ]
    },

    {
        "title": "Java Developer",
        "department": "Engineering",
        "experience": (2, 7),
        "skills": [
            "Java",
            "SQL",
            "AWS"
        ]
    },

    {
        "title": "Senior Java Developer",
        "department": "Engineering",
        "experience": (5, 10),
        "skills": [
            "Java",
            "SQL",
            "AWS",
            "Docker"
        ]
    },

    {
        "title": "Full Stack Developer",
        "department": "Engineering",
        "experience": (3, 8),
        "skills": [
            "React",
            "Node.js",
            "SQL"
        ]
    },

    {
        "title": "DevOps Engineer",
        "department": "Infrastructure",
        "experience": (3, 8),
        "skills": [
            "AWS",
            "Docker",
            "Kubernetes"
        ]
    },

    {
        "title": "Business Analyst",
        "department": "Business",
        "experience": (2, 7),
        "skills": [
            "SQL",
            "Business Analysis",
            "Agile/Scrum"
        ]
    }
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def random_date(start_year=2025, end_year=2026):
    """
    Generate a random date between the supplied years.
    """

    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)

    days_between = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days_between)
    )


def generate_job_code(index):
    """
    Generate a unique job code.
    """

    return f"JOB-2026-{index:05d}"


def generate_salary(experience):
    """
    Generate a realistic salary range based
    on required experience.
    """

    minimum = experience * random.randint(
        10_000,
        15_000
    )

    maximum = minimum + random.randint(
        20_000,
        60_000
    )

    return minimum, maximum


def generate_job_description(job_title, experience):
    """
    Generate a simple job description.
    """

    return (
        f"We are looking for a {job_title} with "
        f"{experience}+ years of experience to join "
        f"our technology team."
    )


def generate_responsibilities(job_title):
    """
    Generate realistic responsibilities.
    """

    return (
        f"Work as a {job_title}, collaborate with "
        f"cross-functional teams, develop solutions, "
        f"participate in technical discussions, and "
        f"support project delivery."
    )


# =========================================================
# GET MASTER DATA
# =========================================================

def get_master_data(cursor):

    # -----------------------------------------------------
    # End Clients
    # -----------------------------------------------------

    cursor.execute("""
        SELECT company_id
        FROM recruitment.companies
        WHERE company_type IN (
            'End Client',
            'Direct Client'
        )
        AND is_active = TRUE;
    """)

    end_clients = [
        row[0]
        for row in cursor.fetchall()
    ]


    # -----------------------------------------------------
    # Implementation Partners / Vendors
    # -----------------------------------------------------

    cursor.execute("""
        SELECT company_id
        FROM recruitment.companies
        WHERE company_type = 'Implementation Partner'
        AND is_active = TRUE;
    """)

    vendors = [
        row[0]
        for row in cursor.fetchall()
    ]


    # -----------------------------------------------------
    # Recruiters
    # -----------------------------------------------------

    cursor.execute("""
        SELECT recruiter_id
        FROM recruitment.recruiters
        WHERE is_active = TRUE;
    """)

    recruiters = [
        row[0]
        for row in cursor.fetchall()
    ]


    # -----------------------------------------------------
    # Locations
    # -----------------------------------------------------

    cursor.execute("""
        SELECT location_id
        FROM recruitment.locations;
    """)

    locations = [
        row[0]
        for row in cursor.fetchall()
    ]


    # -----------------------------------------------------
    # Departments
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM recruitment.departments;
    """)

    departments = {
        name: department_id
        for department_id, name in cursor.fetchall()
    }


    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            skill_id,
            skill_name
        FROM recruitment.skills;
    """)

    skills = {
        name: skill_id
        for skill_id, name in cursor.fetchall()
    }


    return (
        end_clients,
        vendors,
        recruiters,
        locations,
        departments,
        skills
    )


# =========================================================
# GENERATE JOBS
# =========================================================

def generate_jobs(
    cursor,
    end_clients,
    vendors,
    recruiters,
    locations,
    departments,
    skills
):

    jobs_created = 0
    job_skills_created = 0


    for index in range(
        1,
        NUMBER_OF_JOBS + 1
    ):

        # -------------------------------------------------
        # Select job template
        # -------------------------------------------------

        template = random.choice(
            JOB_TEMPLATES
        )


        # -------------------------------------------------
        # Experience
        # -------------------------------------------------

        experience = random.randint(
            template["experience"][0],
            template["experience"][1]
        )


        # -------------------------------------------------
        # Salary
        # -------------------------------------------------

        min_salary, max_salary = generate_salary(
            experience
        )


        # -------------------------------------------------
        # Job metadata
        # -------------------------------------------------

        job_code = generate_job_code(index)

        opened_date = random_date()

        work_mode = random.choice([
            "Onsite",
            "Hybrid",
            "Remote"
        ])

        employment_type = random.choice([
            "Full-time",
            "Contract",
            "Contract-to-Hire"
        ])

        job_status = random.choices(
            [
                "Open",
                "Closed",
                "Filled",
                "On Hold"
            ],
            weights=[
                35,
                25,
                30,
                10
            ],
            k=1
        )[0]


        # -------------------------------------------------
        # Closed date
        # -------------------------------------------------

        closed_date = None

        if job_status in [
            "Closed",
            "Filled"
        ]:

            closed_date = opened_date + timedelta(
                days=random.randint(15, 120)
            )


        # -------------------------------------------------
        # Company / recruiter / location
        # -------------------------------------------------

        end_client_id = random.choice(
            end_clients
        )

        vendor_id = random.choice(
            vendors
        )

        recruiter_id = random.choice(
            recruiters
        )

        location_id = random.choice(
            locations
        )


        # -------------------------------------------------
        # Department
        # -------------------------------------------------

        department_id = departments.get(
            template["department"]
        )

        if department_id is None:

            department_id = random.choice(
                list(departments.values())
            )


        # -------------------------------------------------
        # Bill rate
        # -------------------------------------------------

        bill_rate = round(
            random.uniform(
                40,
                120
            ),
            2
        )


        # -------------------------------------------------
        # Insert Job
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO recruitment.jobs
            (
                job_code,
                job_title,
                department_id,
                end_client_id,
                vendor_id,
                location_id,
                assigned_recruiter_id,
                experience_required,
                employment_type,
                work_mode,
                bill_rate,
                bill_rate_type,
                min_salary,
                max_salary,
                job_description,
                responsibilities,
                job_status,
                opened_date,
                closed_date
            )

            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )

            RETURNING job_id;
            """,

            (
                job_code,
                template["title"],
                department_id,
                end_client_id,
                vendor_id,
                location_id,
                recruiter_id,
                experience,
                employment_type,
                work_mode,
                bill_rate,
                "Hourly",
                min_salary,
                max_salary,
                generate_job_description(
                    template["title"],
                    experience
                ),
                generate_responsibilities(
                    template["title"]
                ),
                job_status,
                opened_date,
                closed_date
            )
        )


        job_id = cursor.fetchone()[0]

        jobs_created += 1


        # -------------------------------------------------
        # Insert Job Skills
        # -------------------------------------------------

        for skill_name in template["skills"]:

            skill_id = skills.get(
                skill_name
            )

            if skill_id is None:
                continue


            priority = random.choices(
                [
                    "Must-have",
                    "Nice-to-have"
                ],
                weights=[
                    70,
                    30
                ],
                k=1
            )[0]


            cursor.execute(
                """
                INSERT INTO recruitment.job_skills
                (
                    job_id,
                    skill_id,
                    priority
                )

                VALUES
                (
                    %s,
                    %s,
                    %s
                )

                ON CONFLICT DO NOTHING;
                """,

                (
                    job_id,
                    skill_id,
                    priority
                )
            )


            job_skills_created += 1


    return (
        jobs_created,
        job_skills_created
    )


# =========================================================
# MAIN
# =========================================================

def main():

    connection = None

    try:

        print()
        print("=" * 50)
        print("TalentIQ - Job Data Generator")
        print("=" * 50)
        print()


        # -------------------------------------------------
        # Connect to PostgreSQL
        # -------------------------------------------------

        connection = psycopg2.connect(
            **DB_CONFIG
        )

        cursor = connection.cursor()

        print(
            "Connected to PostgreSQL ✅"
        )


        # -------------------------------------------------
        # Load master data
        # -------------------------------------------------

        (
            end_clients,
            vendors,
            recruiters,
            locations,
            departments,
            skills
        ) = get_master_data(
            cursor
        )


        print(
            f"End clients available : {len(end_clients)}"
        )

        print(
            f"Vendors available     : {len(vendors)}"
        )

        print(
            f"Recruiters available  : {len(recruiters)}"
        )

        print(
            f"Locations available   : {len(locations)}"
        )

        print(
            f"Departments available : {len(departments)}"
        )

        print(
            f"Skills available      : {len(skills)}"
        )


        # -------------------------------------------------
        # Validate master data
        # -------------------------------------------------

        if not end_clients:
            raise ValueError(
                "No active end clients found."
            )

        if not vendors:
            raise ValueError(
                "No active vendors found."
            )

        if not recruiters:
            raise ValueError(
                "No active recruiters found."
            )

        if not locations:
            raise ValueError(
                "No locations found."
            )

        if not departments:
            raise ValueError(
                "No departments found."
            )


        # -------------------------------------------------
        # Generate jobs
        # -------------------------------------------------

        (
            jobs_created,
            job_skills_created
        ) = generate_jobs(
            cursor,
            end_clients,
            vendors,
            recruiters,
            locations,
            departments,
            skills
        )


        # -------------------------------------------------
        # Commit transaction
        # -------------------------------------------------

        connection.commit()


        print()
        print("=" * 50)
        print("JOB GENERATION COMPLETED")
        print("=" * 50)

        print(
            f"Jobs created       : {jobs_created}"
        )

        print(
            f"Job skills created : {job_skills_created}"
        )

        print("=" * 50)
        print()


    except Exception as error:

        if connection:
            connection.rollback()

        print()
        print("❌ ERROR")
        print(error)
        print()


    finally:

        if connection:
            connection.close()

        print(
            "Database connection closed."
        )


# =========================================================
# SCRIPT ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()