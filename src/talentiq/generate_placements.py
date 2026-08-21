"""
===========================================================
TalentIQ - Placement Data Generator
===========================================================

Purpose:
--------
Generate realistic placement records from accepted offers.

Flow:

Accepted Offer
      |
      +---- Joined ------> Placement
      |
      +---- Did not join -> Fell Through

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
# PLACEMENT SETTINGS
# ==========================================================

# Percentage of accepted offers that successfully become
# placements.

PLACEMENT_RATE = 0.90


PLACEMENT_STATUSES = [
    "Active",
    "Fell Through",
    "Completed Guarantee Period",
]


PLACEMENT_STATUS_WEIGHTS = [
    75,
    10,
    15,
]


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("TalentIQ - Placement Data Generator")
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
    # CHECK EXISTING PLACEMENTS
    # ======================================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM recruitment.placements
    """)

    existing_placements = cursor.fetchone()[0]


    if existing_placements > 0:

        print(
            f"\nWARNING: {existing_placements:,} placements "
            "already exist."
        )

        print(
            "Delete existing placements before running "
            "this generator."
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # GET ACCEPTED OFFERS
    # ======================================================

    cursor.execute("""
        SELECT
            o.offer_id,
            o.application_id,
            o.offer_date,
            o.joining_date,
            a.candidate_id,
            a.job_id,
            d.department_name,
            j.job_title

        FROM recruitment.offers o

        INNER JOIN recruitment.applications a
            ON o.application_id = a.application_id

        INNER JOIN recruitment.jobs j
            ON a.job_id = j.job_id

        LEFT JOIN recruitment.departments d
            ON j.department_id = d.department_id

        WHERE o.offer_status = 'Accepted'

        ORDER BY o.offer_id;
    """)

    accepted_offers = cursor.fetchall()


    print(
        f"\nAccepted offers available : "
        f"{len(accepted_offers):,}"
    )


    if not accepted_offers:

        print(
            "\nNo accepted offers found ❌"
        )

        cursor.close()
        connection.close()

        return


    # ======================================================
    # SELECT PLACEMENTS
    # ======================================================

    target_count = int(
        len(accepted_offers) * PLACEMENT_RATE
    )


    selected_offers = random.sample(
        accepted_offers,
        target_count
    )


    print(
        f"Placements to create : "
        f"{target_count:,}"
    )


    # ======================================================
    # GENERATE PLACEMENTS
    # ======================================================

    placement_records = []


    status_counts = {
        "Active": 0,
        "Fell Through": 0,
        "Completed Guarantee Period": 0,
    }


    print("\nGenerating placements...")


    for (
        offer_id,
        application_id,
        offer_date,
        offer_joining_date,
        candidate_id,
        job_id,
        department_name,
        job_title,
    ) in selected_offers:


        # --------------------------------------------------
        # Placement date
        # --------------------------------------------------

        placement_date = (
            offer_date
            + timedelta(
                days=random.randint(1, 7)
            )
        )


        # --------------------------------------------------
        # Placement status
        # --------------------------------------------------

        placement_status = random.choices(
            PLACEMENT_STATUSES,
            weights=PLACEMENT_STATUS_WEIGHTS,
            k=1,
        )[0]


        # --------------------------------------------------
        # Joining date
        # --------------------------------------------------

        if placement_status == "Fell Through":

            joining_date = None

        else:

            if offer_joining_date is not None:

                joining_date = offer_joining_date

            else:

                joining_date = (
                    placement_date
                    + timedelta(
                        days=random.randint(
                            14,
                            60
                        )
                    )
                )


        # --------------------------------------------------
        # Store placement
        # --------------------------------------------------

        placement_records.append(
            (
                offer_id,
                candidate_id,
                job_id,
                placement_date,
                joining_date,
                placement_status,
                department_name,
                job_title,
            )
        )


        status_counts[
            placement_status
        ] += 1


    # ======================================================
    # INSERT PLACEMENTS
    # ======================================================

    print("\nInserting placements...")


    insert_query = """
        INSERT INTO recruitment.placements
        (
            offer_id,
            candidate_id,
            job_id,
            placement_date,
            joining_date,
            placement_status,
            department,
            designation
        )
        VALUES
        (
            %s,
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
            placement_records
        )

        connection.commit()


        print(
            f"Inserted {len(placement_records):,} "
            "placements successfully ✅"
        )


    except Exception as error:

        connection.rollback()

        print(
            "\nPlacement insertion failed ❌"
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
        FROM recruitment.placements
    """)

    total_placements = cursor.fetchone()[0]


    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n" + "=" * 60)
    print("PLACEMENT GENERATION COMPLETED")
    print("=" * 60)


    print(
        f"Total placements : "
        f"{total_placements:,}"
    )


    print("\nPlacement Status Distribution:")


    for status, count in status_counts.items():

        print(
            f"{status:<28} : "
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