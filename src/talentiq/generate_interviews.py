"""
===========================================================
TalentIQ - Interview Data Generator
===========================================================

Purpose:
--------
Generate realistic sequential interview records.

Interview funnel:

    Round 1
       |
       | Passed
       v
    Round 2
       |
       | Passed
       v
    Round 3
       |
       | Passed
       v
     Final
       |
       | Passed
       v
     Offer

Candidates who fail, cancel, or no-show stop progressing.

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
# INTERVIEW SETTINGS
# ==========================================================

# Maximum number of applications entering Round 1
TARGET_APPLICATIONS = 5554


INTERVIEWERS = [
    "John Smith",
    "Sarah Lee",
    "Michael Johnson",
    "David Wilson",
    "Jennifer Brown",
    "Robert Davis",
    "Emily Taylor",
    "Daniel Anderson",
    "Lisa Thomas",
    "James Martin",
    "Rachel Moore",
    "Kevin Jackson",
]


INTERVIEW_TYPES = [
    "Phone Screen",
    "Technical",
    "Panel",
    "Client",
    "Final",
]


INTERVIEW_TYPE_WEIGHTS = [
    25,
    35,
    15,
    15,
    10,
]


ROUNDS = [
    "Round 1",
    "Round 2",
    "Round 3",
    "Final",
]


# Probability of progressing to the next round
#
# Example:
# Round 1 Passed → 65% move to Round 2
# Round 2 Passed → 60% move to Round 3
# Round 3 Passed → 55% move to Final

PASS_RATE_BY_ROUND = {
    "Round 1": 0.65,
    "Round 2": 0.60,
    "Round 3": 0.55,
    "Final": 0.65,
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def generate_interview_type(round_name):
    """
    Generate interview type based on interview round.
    """

    if round_name == "Round 1":

        return random.choices(
            [
                "Phone Screen",
                "Technical",
            ],
            weights=[70, 30],
            k=1,
        )[0]

    if round_name == "Round 2":

        return random.choices(
            [
                "Technical",
                "Panel",
            ],
            weights=[70, 30],
            k=1,
        )[0]

    if round_name == "Round 3":

        return random.choices(
            [
                "Technical",
                "Panel",
                "Client",
            ],
            weights=[30, 30, 40],
            k=1,
        )[0]

    return "Final"


def generate_outcome(round_name):
    """
    Generate an outcome for the current interview.

    Passed probability is controlled by PASS_RATE_BY_ROUND.
    """

    pass_rate = PASS_RATE_BY_ROUND[round_name]

    random_value = random.random()

    if random_value < pass_rate:
        return "Passed"

    # Small chance of no-show / cancellation
    if random_value < pass_rate + 0.05:
        return "No Show"

    if random_value < pass_rate + 0.10:
        return "Cancelled"

    return "Failed"


def generate_feedback(outcome):

    if outcome == "Pending":
        return None

    if outcome == "No Show":
        return "Candidate did not attend the scheduled interview."

    if outcome == "Cancelled":
        return "Interview was cancelled."

    if outcome == "Passed":

        return random.choice([
            "Strong technical performance.",
            "Good communication and problem-solving skills.",
            "Candidate demonstrated relevant experience.",
            "Strong understanding of required skills.",
            "Good cultural and team fit.",
            "Excellent overall interview performance.",
        ])

    return random.choice([
        "Technical knowledge was below expectations.",
        "Candidate needs improvement in technical depth.",
        "Communication skills were below expectations.",
        "Candidate did not meet the required technical criteria.",
        "Experience did not sufficiently match the position.",
    ])


def generate_interview_date(applied_date, previous_date=None):
    """
    Generate interview date after application date.

    If a previous interview exists, the next interview
    occurs after that interview.
    """

    if previous_date is None:

        base_date = applied_date

    else:

        base_date = previous_date.date()


    days_after = random.randint(3, 14)

    interview_date = base_date + timedelta(
        days=days_after
    )


    hour = random.randint(9, 16)

    minute = random.choice([
        0,
        15,
        30,
        45,
    ])


    return datetime(
        interview_date.year,
        interview_date.month,
        interview_date.day,
        hour,
        minute,
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("TalentIQ - Sequential Interview Data Generator")
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
    # CHECK EXISTING INTERVIEWS
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.interviews
    """)

    existing_count = cursor.fetchone()[0]


    if existing_count > 0:

        print(
            f"\nWARNING: {existing_count:,} interviews "
            "already exist."
        )

        print(
            "Delete existing interview records before "
            "running this generator."
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # LOAD APPLICATIONS
    # ======================================================

    cursor.execute("""
        SELECT
            application_id,
            applied_date,
            current_stage,
            status
        FROM recruitment.applications
        WHERE current_stage IN
        (
            'Interview',
            'Offer',
            'Hired'
        )
        ORDER BY application_id
    """)

    applications = cursor.fetchall()


    print(
        f"Interview-eligible applications : "
        f"{len(applications):,}"
    )


    if not applications:

        print(
            "\nNo eligible applications found ❌"
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # LIMIT APPLICATIONS
    # ======================================================

    target = min(
        TARGET_APPLICATIONS,
        len(applications)
    )


    selected_applications = random.sample(
        applications,
        target
    )


    print(
        f"Applications entering Round 1 : "
        f"{target:,}"
    )


    # ======================================================
    # GENERATE INTERVIEW JOURNEYS
    # ======================================================

    interview_records = []


    round_counts = {
        "Round 1": 0,
        "Round 2": 0,
        "Round 3": 0,
        "Final": 0,
    }


    outcome_counts = {
        "Passed": 0,
        "Failed": 0,
        "No Show": 0,
        "Cancelled": 0,
    }


    print("\nGenerating sequential interview journeys...")


    for application in selected_applications:

        (
            application_id,
            applied_date,
            current_stage,
            application_status,
        ) = application


        previous_interview_date = None


        # --------------------------------------------------
        # Progress through each round
        # --------------------------------------------------

        for round_name in ROUNDS:

            # Generate date
            interview_date = generate_interview_date(
                applied_date,
                previous_interview_date,
            )


            # Generate interviewer
            interviewer = random.choice(
                INTERVIEWERS
            )


            # Generate type
            interview_type = generate_interview_type(
                round_name
            )


            # Generate outcome
            outcome = generate_outcome(
                round_name
            )


            # Generate feedback
            feedback = generate_feedback(
                outcome
            )


            # Add record
            interview_records.append(
                (
                    application_id,
                    interview_date,
                    interviewer,
                    interview_type,
                    round_name,
                    outcome,
                    feedback,
                )
            )


            # Update statistics
            round_counts[round_name] += 1
            outcome_counts[outcome] += 1


            previous_interview_date = interview_date


            # --------------------------------------------------
            # Stop if candidate does not pass
            # --------------------------------------------------

            if outcome != "Passed":

                break


    # ======================================================
    # INSERT INTERVIEWS
    # ======================================================

    print(
        f"\nTotal interviews generated : "
        f"{len(interview_records):,}"
    )


    print("\nInserting interviews...")


    insert_query = """
        INSERT INTO recruitment.interviews
        (
            application_id,
            interview_date,
            interviewer,
            interview_type,
            interview_round,
            outcome,
            feedback
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

        cursor.executemany(
            insert_query,
            interview_records
        )

        connection.commit()


        print(
            f"Inserted {len(interview_records):,} "
            "interviews successfully ✅"
        )


    except Exception as error:

        connection.rollback()

        print(
            "\nInterview insertion failed ❌"
        )

        print(error)

        cursor.close()
        connection.close()

        return


    # ======================================================
    # DATABASE VERIFICATION
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.interviews
    """)

    total_interviews = cursor.fetchone()[0]


    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n" + "=" * 60)
    print("INTERVIEW GENERATION COMPLETED")
    print("=" * 60)


    print(
        f"Total interviews : "
        f"{total_interviews:,}"
    )


    print("\nInterview Round Distribution:")

    for round_name in ROUNDS:

        print(
            f"{round_name:<12} : "
            f"{round_counts[round_name]:,}"
        )


    print("\nInterview Outcome Distribution:")

    for outcome, count in outcome_counts.items():

        print(
            f"{outcome:<12} : "
            f"{count:,}"
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