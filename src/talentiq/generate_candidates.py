"""
===========================================================
TalentIQ - Candidate Data Generator
===========================================================

Purpose:
--------
Generate realistic synthetic candidate data for the
TalentIQ AI Recruitment Analytics platform.

Creates:
    - Candidates
    - Candidate Skills

Existing master data used:
    - Locations
    - Sources
    - Skills
    - Work Authorizations

Target:
    10,000 candidates

Run:
    python src/talentiq/generate_candidates.py
===========================================================
"""

import random
from datetime import datetime, timedelta

import psycopg2


# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "recruitment_analytics",
    "user": "postgres",
    "password": "Just890",
}


# ==========================================================
# GENERATION CONFIGURATION
# ==========================================================

NUM_CANDIDATES = 10_000

BATCH_SIZE = 500


# ==========================================================
# SAMPLE DATA
# ==========================================================

FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William",
    "David", "Richard", "Joseph", "Thomas", "Charles",
    "Daniel", "Matthew", "Anthony", "Mark", "Donald",
    "Steven", "Paul", "Andrew", "Joshua", "Kevin",
    "Sarah", "Jennifer", "Jessica", "Emily", "Ashley",
    "Amanda", "Stephanie", "Melissa", "Michelle", "Laura",
    "Rachel", "Rebecca", "Elizabeth", "Lauren", "Megan",
    "Priya", "Neha", "Rahul", "Amit", "Arjun",
    "Ananya", "Rohan", "Vikram", "Karan", "Sneha",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones",
    "Garcia", "Miller", "Davis", "Wilson", "Anderson",
    "Taylor", "Thomas", "Moore", "Jackson", "Martin",
    "Lee", "Harris", "Clark", "Lewis", "Walker",
    "Hall", "Allen", "Young", "King", "Wright",
    "Sharma", "Patel", "Singh", "Gupta", "Verma",
    "Mehta", "Kumar", "Mishra", "Reddy", "Nair",
]


EDUCATION_OPTIONS = [
    "B.Tech",
    "B.E.",
    "BCA",
    "MCA",
    "M.Tech",
    "MBA",
    "MS",
    "BS Computer Science",
    "MS Computer Science",
    "Bachelor's Degree",
    "Master's Degree",
]


STATUS_OPTIONS = [
    "Active",
    "Screening",
    "Interview",
    "Offer",
    "Hired",
    "Rejected",
    "Withdrawn",
]


# ==========================================================
# ROLE → SKILL PREFERENCE
# ==========================================================

ROLE_SKILLS = {
    "Data Analyst": [
        "SQL",
        "Python",
        "Tableau",
        "Excel",
        "Business Analysis",
    ],

    "Business Analyst": [
        "SQL",
        "Business Analysis",
        "Excel",
        "Agile/Scrum",
        "Project Management",
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Machine Learning",
        "Statistics",
        "Tableau",
    ],

    "AI Engineer": [
        "Python",
        "AWS",
        "Docker",
        "Kubernetes",
        "Machine Learning",
    ],

    "ML Engineer": [
        "Python",
        "AWS",
        "Kubernetes",
        "Docker",
        "Machine Learning",
    ],

    "Java Developer": [
        "Java",
        "SQL",
        "AWS",
        "Docker",
        "Spring",
    ],

    "DevOps Engineer": [
        "AWS",
        "Docker",
        "Kubernetes",
        "Linux",
        "Azure",
    ],

    "Software Engineer": [
        "Python",
        "Java",
        "SQL",
        "AWS",
        "Docker",
    ],

    "Cloud Engineer": [
        "AWS",
        "Azure",
        "Docker",
        "Kubernetes",
        "Linux",
    ],

    "QA Engineer": [
        "SQL",
        "Python",
        "Selenium",
        "Java",
        "Agile/Scrum",
    ],
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def random_date(start_year=2024, end_year=2026):
    """
    Generate a random date between start_year and end_year.
    """

    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 8, 1)

    days = (end - start).days

    return (start + timedelta(days=random.randint(0, days))).date()


def generate_phone():
    """
    Generate a synthetic US-style phone number.
    """

    area_code = random.randint(201, 989)
    number = random.randint(1000000, 9999999)

    return f"+1-{area_code}-{number}"


def generate_email(first_name, last_name, number):
    """
    Generate unique synthetic email.
    """

    domains = [
        "gmail.com",
        "outlook.com",
        "yahoo.com",
        "hotmail.com",
    ]

    domain = random.choice(domains)

    return (
        f"{first_name.lower()}."
        f"{last_name.lower()}"
        f"{number}@{domain}"
    )


def choose_proficiency(experience):
    """
    Select proficiency based on experience.
    """

    if experience <= 2:
        return random.choice([
            "Beginner",
            "Intermediate"
        ])

    if experience <= 5:
        return random.choice([
            "Intermediate",
            "Advanced"
        ])

    if experience <= 9:
        return random.choice([
            "Advanced",
            "Expert"
        ])

    return "Expert"


# ==========================================================
# MAIN GENERATOR
# ==========================================================

def main():

    print("=" * 58)
    print("TalentIQ - Candidate Data Generator")
    print("=" * 58)

    # ------------------------------------------------------
    # CONNECT TO DATABASE
    # ------------------------------------------------------

    try:

        connection = psycopg2.connect(**DB_CONFIG)

        cursor = connection.cursor()

        print("\nConnected to PostgreSQL ✅")

    except Exception as error:

        print("\nDatabase connection failed ❌")
        print(error)

        return


    # ------------------------------------------------------
    # LOAD MASTER DATA
    # ------------------------------------------------------

    cursor.execute("""
        SELECT location_id
        FROM recruitment.locations
    """)

    locations = [row[0] for row in cursor.fetchall()]


    cursor.execute("""
        SELECT source_id
        FROM recruitment.sources
    """)

    sources = [row[0] for row in cursor.fetchall()]


    cursor.execute("""
        SELECT skill_id, skill_name
        FROM recruitment.skills
    """)

    skills = cursor.fetchall()


    cursor.execute("""
        SELECT work_authorization_id
        FROM recruitment.work_authorizations
    """)

    work_authorizations = [
        row[0]
        for row in cursor.fetchall()
    ]


    print(f"Locations available        : {len(locations)}")
    print(f"Sources available          : {len(sources)}")
    print(f"Skills available           : {len(skills)}")
    print(
        f"Work authorizations        : "
        f"{len(work_authorizations)}"
    )


    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if not locations:
        print("No locations found ❌")
        cursor.close()
        connection.close()
        return

    if not sources:
        print("No sources found ❌")
        cursor.close()
        connection.close()
        return

    if not skills:
        print("No skills found ❌")
        cursor.close()
        connection.close()
        return

    if not work_authorizations:
        print("No work authorizations found ❌")
        cursor.close()
        connection.close()
        return


    # ------------------------------------------------------
    # CREATE SKILL LOOKUP
    # ------------------------------------------------------

    skill_lookup = {
        skill_name.lower(): skill_id
        for skill_id, skill_name in skills
    }


    all_skill_ids = [
        skill_id
        for skill_id, skill_name in skills
    ]


    # ------------------------------------------------------
    # GENERATE CANDIDATES
    # ------------------------------------------------------

    candidate_records = []

    candidate_skill_records = []


    print("\nGenerating candidates...")


    for i in range(1, NUM_CANDIDATES + 1):

        first_name = random.choice(FIRST_NAMES)

        last_name = random.choice(LAST_NAMES)

        candidate_name = (
            f"{first_name} {last_name}"
        )


        experience = random.randint(1, 15)


        education = random.choice(
            EDUCATION_OPTIONS
        )


        location_id = random.choice(
            locations
        )


        source_id = random.choice(
            sources
        )


        work_authorization_id = random.choice(
            work_authorizations
        )


        status = random.choices(
            STATUS_OPTIONS,
weights=[
    25,   # Active
    15,   # Screening
    12,   # Interview
    6,    # Offer
    8,    # Hired
    26,   # Rejected
    8,    # Withdrawn
],
            k=1
        )[0]


        applied_date = random_date(
            2025,
            2026
        )


        email = generate_email(
            first_name,
            last_name,
            i
        )


        phone = generate_phone()


        resume_path = (
            f"data/sample/resumes/"
            f"candidate_{i:05d}.pdf"
        )


        candidate_records.append(
            (
                candidate_name,
                email,
                phone,
                experience,
                education,
                location_id,
                work_authorization_id,
                source_id,
                resume_path,
                applied_date,
                status,
            )
        )


    # ------------------------------------------------------
    # INSERT CANDIDATES
    # ------------------------------------------------------

    print("Inserting candidates...")


    insert_candidate_query = """
        INSERT INTO recruitment.candidates
        (
            candidate_name,
            email,
            phone,
            experience_years,
            education,
            location_id,
            work_authorization_id,
            source_id,
            resume_path,
            applied_date,
            status
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        RETURNING candidate_id
    """


    candidate_ids = []


    for record in candidate_records:

        cursor.execute(
            insert_candidate_query,
            record
        )

        candidate_id = cursor.fetchone()[0]

        candidate_ids.append(candidate_id)


    connection.commit()


    # ------------------------------------------------------
    # GENERATE CANDIDATE SKILLS
    # ------------------------------------------------------

    print("Generating candidate skills...")


    for candidate_id in candidate_ids:

        # Choose a random number of skills
        skill_count = random.randint(3, 8)


        selected_skills = random.sample(
            all_skill_ids,
            min(
                skill_count,
                len(all_skill_ids)
            )
        )


        for skill_id in selected_skills:

            skill_experience = random.randint(
                1,
                10
            )


            proficiency = choose_proficiency(
                skill_experience
            )


            candidate_skill_records.append(
                (
                    candidate_id,
                    skill_id,
                    proficiency,
                    skill_experience,
                )
            )


    # ------------------------------------------------------
    # INSERT CANDIDATE SKILLS
    # ------------------------------------------------------

    insert_skill_query = """
        INSERT INTO recruitment.candidate_skills
        (
            candidate_id,
            skill_id,
            proficiency_level,
            years_experience
        )
        VALUES
        (
            %s, %s, %s, %s
        )
    """


    cursor.executemany(
        insert_skill_query,
        candidate_skill_records
    )


    connection.commit()


    # ------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.candidates
    """)

    total_candidates = cursor.fetchone()[0]


    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.candidate_skills
    """)

    total_candidate_skills = cursor.fetchone()[0]


    print("\n" + "=" * 58)
    print("CANDIDATE GENERATION COMPLETED")
    print("=" * 58)

    print(
        f"Candidates created     : "
        f"{total_candidates}"
    )

    print(
        f"Candidate skills       : "
        f"{total_candidate_skills}"
    )

    print("=" * 58)


    # ------------------------------------------------------
    # CLOSE CONNECTION
    # ------------------------------------------------------

    cursor.close()

    connection.close()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()