"""
===========================================================
TalentIQ - Application Data Generator
===========================================================

Purpose:
--------
Generate realistic recruitment application data.

Uses existing:
    - Candidates
    - Jobs
    - Recruiters

Creates:
    - Applications

Target:
    ~30,000 applications

Important:
    One candidate cannot apply to the same job twice.
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

TARGET_APPLICATIONS = 30_000
BATCH_SIZE = 1_000


# ==========================================================
# VALID APPLICATION STAGES
# Based on your database constraint
# ==========================================================

STAGES = [
    "Applied",
    "Screening",
    "Submitted to Client",
    "Interview",
    "Offer",
    "Hired",
    "Rejected",
    "Withdrawn",
]


# ==========================================================
# APPLICATION STAGE DISTRIBUTION
# ==========================================================

STAGE_WEIGHTS = [
    35,   # Applied
    20,   # Screening
    12,   # Submitted to Client
    10,   # Interview
    5,    # Offer
    4,    # Hired
    10,   # Rejected
    4,    # Withdrawn
]


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def random_date(start_date, end_date):
    """Generate a random date between two dates."""

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


def get_application_status(stage):
    """
    Convert recruitment stage into application status.

    Database allows:
        Active
        Rejected
        Withdrawn
        Hired
    """

    if stage == "Rejected":
        return "Rejected"

    if stage == "Withdrawn":
        return "Withdrawn"

    if stage == "Hired":
        return "Hired"

    return "Active"


def get_submitted_date(applied_date, stage):
    """
    Generate submitted_to_client_date only when
    candidate reaches client submission or beyond.
    """

    eligible_stages = [
        "Submitted to Client",
        "Interview",
        "Offer",
        "Hired",
    ]

    if stage not in eligible_stages:
        return None

    days_after_application = random.randint(1, 10)

    return applied_date + timedelta(
        days=days_after_application
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("TalentIQ - Application Data Generator")
    print("=" * 60)


    # ======================================================
    # DATABASE CONNECTION
    # ======================================================

    try:

        connection = psycopg2.connect(
            **DB_CONFIG
        )

        cursor = connection.cursor()

        print("\nConnected to PostgreSQL ✅")

    except Exception as error:

        print("\nDatabase connection failed ❌")
        print(error)

        return


    # ======================================================
    # LOAD CANDIDATES
    # ======================================================

    cursor.execute("""
        SELECT
            candidate_id,
            experience_years,
            applied_date,
            status
        FROM recruitment.candidates
    """)

    candidates = cursor.fetchall()


    # ======================================================
    # LOAD JOBS
    # ======================================================

    cursor.execute("""
        SELECT
            job_id,
            experience_required,
            assigned_recruiter_id,
            opened_date,
            job_status
        FROM recruitment.jobs
        WHERE job_status IN
        (
            'Open',
            'Filled',
            'Closed'
        )
    """)

    jobs = cursor.fetchall()


    # ======================================================
    # LOAD RECRUITERS
    # ======================================================

    cursor.execute("""
        SELECT recruiter_id
        FROM recruitment.recruiters
        WHERE is_active = TRUE
    """)

    recruiters = [
        row[0]
        for row in cursor.fetchall()
    ]


    print(
        f"Candidates available  : {len(candidates)}"
    )

    print(
        f"Jobs available        : {len(jobs)}"
    )

    print(
        f"Recruiters available  : {len(recruiters)}"
    )


    # ======================================================
    # VALIDATION
    # ======================================================

    if not candidates:

        print("No candidates found ❌")

        cursor.close()
        connection.close()

        return


    if not jobs:

        print("No jobs found ❌")

        cursor.close()
        connection.close()

        return


    if not recruiters:

        print("No active recruiters found ❌")

        cursor.close()
        connection.close()

        return


    # ======================================================
    # CHECK EXISTING APPLICATIONS
    # ======================================================

    cursor.execute("""
        SELECT
            candidate_id,
            job_id
        FROM recruitment.applications
    """)

    existing_applications = {
        (row[0], row[1])
        for row in cursor.fetchall()
    }


    print(
        f"Existing applications : "
        f"{len(existing_applications)}"
    )


    # ======================================================
    # GENERATE APPLICATIONS
    # ======================================================

    print("\nGenerating applications...")


    application_records = []

    used_pairs = set(existing_applications)


    attempts = 0

    max_attempts = TARGET_APPLICATIONS * 10


    while (
        len(application_records)
        < TARGET_APPLICATIONS
        and attempts < max_attempts
    ):

        attempts += 1


        # --------------------------------------------------
        # Select candidate
        # --------------------------------------------------

        candidate = random.choice(
            candidates
        )

        (
            candidate_id,
            candidate_experience,
            candidate_applied_date,
            candidate_status,
        ) = candidate


        # --------------------------------------------------
        # Select job
        # --------------------------------------------------

        job = random.choice(
            jobs
        )

        (
            job_id,
            experience_required,
            assigned_recruiter_id,
            opened_date,
            job_status,
        ) = job


        # --------------------------------------------------
        # Prevent duplicate application
        # --------------------------------------------------

        pair = (
            candidate_id,
            job_id
        )


        if pair in used_pairs:

            continue


        # --------------------------------------------------
        # Experience compatibility
        # --------------------------------------------------

        experience_difference = (
            candidate_experience
            - experience_required
        )


        # Avoid extremely unrealistic applications

        if experience_difference < -4:

            continue


        if experience_difference > 10:

            if random.random() > 0.30:

                continue


        # --------------------------------------------------
        # Application date
        # --------------------------------------------------

        start_date = max(
            datetime(2025, 1, 1).date(),
            opened_date
            if opened_date
            else datetime(2025, 1, 1).date()
        )


        end_date = datetime(
            2026,
            8,
            1
        ).date()


        if start_date > end_date:

            continue


        applied_date = random_date(
            start_date,
            end_date
        )


        # --------------------------------------------------
        # Stage
        # --------------------------------------------------

        stage = random.choices(
            STAGES,
            weights=STAGE_WEIGHTS,
            k=1
        )[0]


        # --------------------------------------------------
        # Application status
        # --------------------------------------------------

        status = get_application_status(
            stage
        )


        # --------------------------------------------------
        # Recruiter
        # --------------------------------------------------

        recruiter_id = (
            assigned_recruiter_id
            if assigned_recruiter_id
            else random.choice(recruiters)
        )


        # --------------------------------------------------
        # Submitted to client date
        # --------------------------------------------------

        submitted_to_client_date = (
            get_submitted_date(
                applied_date,
                stage
            )
        )


        # --------------------------------------------------
        # Store
        # --------------------------------------------------

        application_records.append(
            (
                candidate_id,
                job_id,
                recruiter_id,
                applied_date,
                stage,
                status,
                submitted_to_client_date,
            )
        )


        used_pairs.add(pair)


        # --------------------------------------------------
        # Progress
        # --------------------------------------------------

        if len(application_records) % 5_000 == 0:

            print(
                f"Generated "
                f"{len(application_records):,} "
                f"applications..."
            )


    # ======================================================
    # INSERT APPLICATIONS
    # ======================================================

    print("\nInserting applications...")


    insert_query = """
        INSERT INTO recruitment.applications
        (
            candidate_id,
            job_id,
            recruiter_id,
            applied_date,
            current_stage,
            status,
            submitted_to_client_date
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """


    try:

        for start in range(
            0,
            len(application_records),
            BATCH_SIZE
        ):

            batch = application_records[
                start:start + BATCH_SIZE
            ]


            cursor.executemany(
                insert_query,
                batch
            )


            connection.commit()


            print(
                f"Inserted "
                f"{min(start + BATCH_SIZE, len(application_records)):,}"
                f" / "
                f"{len(application_records):,}"
            )


    except Exception as error:

        connection.rollback()

        print(
            "\nApplication insertion failed ❌"
        )

        print(error)

        cursor.close()
        connection.close()

        return


    # ======================================================
    # FINAL VERIFICATION
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.applications
    """)

    total_applications = (
        cursor.fetchone()[0]
    )


    cursor.execute("""
        SELECT
            current_stage,
            COUNT(*)
        FROM recruitment.applications
        GROUP BY current_stage
        ORDER BY COUNT(*) DESC
    """)

    stage_summary = cursor.fetchall()


    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n" + "=" * 60)
    print("APPLICATION GENERATION COMPLETED")
    print("=" * 60)


    print(
        f"Applications created : "
        f"{total_applications:,}"
    )


    print("\nApplication Funnel:")

    for stage, count in stage_summary:

        print(
            f"{stage:<25} : {count:,}"
        )


    print("=" * 60)


    # ======================================================
    # CLOSE CONNECTION
    # ======================================================

    cursor.close()

    connection.close()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()