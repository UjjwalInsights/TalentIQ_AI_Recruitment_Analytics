"""
===========================================================
TalentIQ - Offer Data Generator
===========================================================

Purpose:
--------
Generate realistic offer records from successful interview
journeys.

Flow:

Application
     ↓
Interview
     ↓
Passed
     ↓
Offer
     ↓
Accepted / Declined / Negotiating / Rescinded
     ↓
Placement

===========================================================
"""

import random
from datetime import timedelta

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
# OFFER SETTINGS
# ==========================================================

# Percentage of eligible applications receiving an offer
OFFER_RATE = 0.75


OFFER_STATUSES = [
    "Extended",
    "Accepted",
    "Declined",
    "Rescinded",
    "Negotiating",
]


OFFER_STATUS_WEIGHTS = [
    10,   # Extended
    55,   # Accepted
    20,   # Declined
    5,    # Rescinded
    10,   # Negotiating
]


# Salary ranges by experience
SALARY_RANGES = {
    "entry": (55000, 85000),
    "mid": (75000, 120000),
    "senior": (100000, 160000),
    "lead": (130000, 190000),
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def generate_salary(experience_years):
    """
    Generate realistic annual salary based on experience.
    """

    if experience_years <= 2:

        minimum, maximum = SALARY_RANGES["entry"]

    elif experience_years <= 5:

        minimum, maximum = SALARY_RANGES["mid"]

    elif experience_years <= 9:

        minimum, maximum = SALARY_RANGES["senior"]

    else:

        minimum, maximum = SALARY_RANGES["lead"]


    salary = random.randint(
        minimum // 1000,
        maximum // 1000
    ) * 1000


    return salary


def generate_offer_status():
    """
    Generate realistic offer status.
    """

    return random.choices(
        OFFER_STATUSES,
        weights=OFFER_STATUS_WEIGHTS,
        k=1,
    )[0]


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("TalentIQ - Offer Data Generator")
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
    # CHECK EXISTING OFFERS
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.offers
    """)

    existing_offers = cursor.fetchone()[0]


    if existing_offers > 0:

        print(
            f"\nWARNING: {existing_offers:,} offers "
            "already exist."
        )

        print(
            "Delete existing offers before running "
            "this generator."
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # FIND SUCCESSFUL INTERVIEW JOURNEYS
    # ======================================================
    #
    # We select applications that reached the Final round
    # and passed it.
    #
    # This prevents random offers being created for candidates
    # who never completed the interview process.
    #
    # ======================================================

    cursor.execute("""
        SELECT
            i.application_id,
            i.interview_date,
            a.applied_date,
            c.experience_years
        FROM recruitment.interviews i

        INNER JOIN recruitment.applications a
            ON i.application_id = a.application_id

        INNER JOIN recruitment.candidates c
            ON a.candidate_id = c.candidate_id

        WHERE i.interview_round = 'Final'
          AND i.outcome = 'Passed'

        ORDER BY i.application_id;
    """)

    eligible_candidates = cursor.fetchall()


    print(
        f"Final-round successful applications : "
        f"{len(eligible_candidates):,}"
    )


    if not eligible_candidates:

        print(
            "\nNo successful final interviews found ❌"
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # DETERMINE OFFER COUNT
    # ======================================================

    target_count = int(
        len(eligible_candidates) * OFFER_RATE
    )


    target_count = max(
        1,
        target_count
    )


    target_count = min(
        target_count,
        len(eligible_candidates)
    )


    selected_candidates = random.sample(
        eligible_candidates,
        target_count
    )


    print(
        f"Offers to create : "
        f"{target_count:,}"
    )


    # ======================================================
    # GENERATE OFFERS
    # ======================================================

    offer_records = []


    status_counts = {
        "Extended": 0,
        "Accepted": 0,
        "Declined": 0,
        "Rescinded": 0,
        "Negotiating": 0,
    }


    print("\nGenerating offers...")


    for (
        application_id,
        final_interview_date,
        applied_date,
        experience_years,
    ) in selected_candidates:


        # --------------------------------------------------
        # Offer date
        # --------------------------------------------------

        days_after_interview = random.randint(
            1,
            7
        )


        offer_date = (
            final_interview_date.date()
            + timedelta(
                days=days_after_interview
            )
        )


        # --------------------------------------------------
        # Salary
        # --------------------------------------------------

        offered_salary = generate_salary(
            experience_years
        )


        # --------------------------------------------------
        # Offer status
        # --------------------------------------------------

        offer_status = generate_offer_status()


        # --------------------------------------------------
        # Joining date
        # --------------------------------------------------

        if offer_status == "Accepted":

            joining_date = (
                offer_date
                + timedelta(
                    days=random.randint(
                        14,
                        60
                    )
                )
            )

        else:

            joining_date = None


        # --------------------------------------------------
        # Store
        # --------------------------------------------------

        offer_records.append(
            (
                application_id,
                offer_date,
                offered_salary,
                offer_status,
                joining_date,
            )
        )


        status_counts[
            offer_status
        ] += 1


    # ======================================================
    # INSERT OFFERS
    # ======================================================

    print("\nInserting offers...")


    insert_query = """
        INSERT INTO recruitment.offers
        (
            application_id,
            offer_date,
            offered_salary,
            offer_status,
            joining_date
        )
        VALUES
        (
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
            offer_records
        )

        connection.commit()


        print(
            f"Inserted {len(offer_records):,} "
            "offers successfully ✅"
        )


    except Exception as error:

        connection.rollback()

        print(
            "\nOffer insertion failed ❌"
        )

        print(error)

        cursor.close()
        connection.close()

        return


    # ======================================================
    # VERIFICATION
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.offers
    """)

    total_offers = cursor.fetchone()[0]


    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n" + "=" * 60)
    print("OFFER GENERATION COMPLETED")
    print("=" * 60)


    print(
        f"Total offers : "
        f"{total_offers:,}"
    )


    print("\nOffer Status Distribution:")


    for status, count in status_counts.items():

        print(
            f"{status:<15} : "
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