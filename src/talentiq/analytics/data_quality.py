"""
===============================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM
File: data_quality.py

Purpose
-------
Run automated data-quality checks against the TalentIQ
PostgreSQL recruitment database.

Validation Areas
----------------
1. Database connection
2. Table row counts
3. Primary-key duplicates
4. Business-key duplicates
5. Critical NULL values
6. Foreign-key / orphan records
7. Recruitment timeline integrity
8. Salary validation
9. Placement consistency
10. Dashboard view validation
11. Negative age validation
12. Final database health report

Synthetic Dataset Snapshot Date
-------------------------------
2026-12-31

Output
------
outputs/reports/data_quality_report.csv

===============================================================
"""

from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import text


# =============================================================
# PROJECT PATH SETUP
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

# .../TalentIQ_AI_Recruitment_Analytics/src
SRC_DIR = CURRENT_FILE.parents[2]

# .../TalentIQ_AI_Recruitment_Analytics
PROJECT_ROOT = CURRENT_FILE.parents[3]

# Allow imports from src/
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from database.connection import get_connection


# =============================================================
# CONFIGURATION
# =============================================================

SNAPSHOT_DATE = "2026-12-31"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

REPORT_FILE = REPORT_DIR / "data_quality_report.csv"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =============================================================
# TABLE CONFIGURATION
# =============================================================

TABLES = [
    "companies",
    "departments",
    "locations",
    "sources",
    "skills",
    "work_authorizations",
    "recruiters",
    "candidates",
    "candidate_skills",
    "jobs",
    "job_skills",
    "applications",
    "interviews",
    "offers",
    "placements",
]


PRIMARY_KEYS = {
    "companies": "company_id",
    "departments": "department_id",
    "locations": "location_id",
    "sources": "source_id",
    "skills": "skill_id",
    "work_authorizations": "work_authorization_id",
    "recruiters": "recruiter_id",
    "candidates": "candidate_id",
    "jobs": "job_id",
    "applications": "application_id",
    "interviews": "interview_id",
    "offers": "offer_id",
    "placements": "placement_id",
}


# =============================================================
# REPORT STORAGE
# =============================================================

results = []


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def execute_scalar(query):
    """
    Execute a SQL query and return the first scalar value.
    """

    with get_connection() as connection:

        result = connection.execute(
            text(query)
        )

        return result.scalar()


def execute_dataframe(query):
    """
    Execute a SQL query and return a Pandas DataFrame.
    """

    with get_connection() as connection:

        return pd.read_sql_query(
            text(query),
            connection
        )


def add_result(
    category,
    check_name,
    value,
    expected,
    status,
    notes=""
):
    """
    Add a validation result to the final report.
    """

    results.append(
        {
            "category": category,
            "check_name": check_name,
            "value": value,
            "expected": expected,
            "status": status,
            "notes": notes,
        }
    )


def run_zero_check(
    category,
    check_name,
    query,
    notes=""
):
    """
    Run a validation query where zero means PASS.
    """

    try:

        value = execute_scalar(query)

        status = (
            "PASS"
            if value == 0
            else "FAIL"
        )

        add_result(
            category=category,
            check_name=check_name,
            value=value,
            expected=0,
            status=status,
            notes=notes,
        )

    except Exception as error:

        add_result(
            category=category,
            check_name=check_name,
            value="ERROR",
            expected=0,
            status="ERROR",
            notes=str(error),
        )


# =============================================================
# 1. DATABASE CONNECTION
# =============================================================

def check_database_connection():

    print("\n[1/10] Checking database connection...")

    try:

        database_name = execute_scalar(
            "SELECT current_database();"
        )

        add_result(
            category="Database",
            check_name="Database Connection",
            value=database_name,
            expected="recruitment_analytics",
            status=(
                "PASS"
                if database_name == "recruitment_analytics"
                else "FAIL"
            ),
            notes="TalentIQ PostgreSQL database",
        )

    except Exception as error:

        add_result(
            category="Database",
            check_name="Database Connection",
            value="ERROR",
            expected="recruitment_analytics",
            status="ERROR",
            notes=str(error),
        )

        raise


# =============================================================
# 2. TABLE ROW COUNTS
# =============================================================

def check_table_row_counts():

    print("[2/10] Checking table row counts...")

    for table in TABLES:

        try:

            count = execute_scalar(
                f"SELECT COUNT(*) FROM {table};"
            )

            add_result(
                category="Row Count",
                check_name=f"{table} row count",
                value=count,
                expected="> 0",
                status=(
                    "PASS"
                    if count > 0
                    else "FAIL"
                ),
                notes="Table should contain data",
            )

        except Exception as error:

            add_result(
                category="Row Count",
                check_name=f"{table} row count",
                value="ERROR",
                expected="> 0",
                status="ERROR",
                notes=str(error),
            )


# =============================================================
# 3. PRIMARY KEY DUPLICATES
# =============================================================

def check_primary_key_duplicates():

    print("[3/10] Checking primary-key duplicates...")

    for table, primary_key in PRIMARY_KEYS.items():

        query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT
                {primary_key}
            FROM {table}
            GROUP BY {primary_key}
            HAVING COUNT(*) > 1
        ) duplicates;
        """

        run_zero_check(
            category="Duplicates",
            check_name=f"{table}.{primary_key} duplicates",
            query=query,
            notes="Primary identifier must be unique",
        )


# =============================================================
# 4. BUSINESS KEY DUPLICATES
# =============================================================

def check_business_key_duplicates():

    print("[4/10] Checking business-key duplicates...")

    # Job codes should be unique
    run_zero_check(
        category="Business Keys",
        check_name="Duplicate job codes",
        query="""
        SELECT COUNT(*)
        FROM (
            SELECT job_code
            FROM jobs
            WHERE job_code IS NOT NULL
            GROUP BY job_code
            HAVING COUNT(*) > 1
        ) duplicates;
        """,
        notes="Each job should have a unique job_code",
    )

    # Candidate emails should be unique after normalization
    run_zero_check(
        category="Business Keys",
        check_name="Duplicate candidate emails",
        query="""
        SELECT COUNT(*)
        FROM (
            SELECT LOWER(TRIM(email))
            FROM candidates
            WHERE email IS NOT NULL
            GROUP BY LOWER(TRIM(email))
            HAVING COUNT(*) > 1
        ) duplicates;
        """,
        notes="Candidate email checked case-insensitively",
    )


# =============================================================
# 5. CRITICAL NULL CHECKS
# =============================================================

def check_null_values():

    print("[5/10] Checking critical NULL values...")

    null_checks = {

        # Candidates
        "Missing candidate names":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE candidate_name IS NULL
           OR TRIM(candidate_name) = '';
        """,

        "Missing candidate emails":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE email IS NULL
           OR TRIM(email) = '';
        """,

        "Missing candidate experience":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE experience_years IS NULL;
        """,

        "Missing candidate location":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE location_id IS NULL;
        """,

        "Missing candidate work authorization":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE work_authorization_id IS NULL;
        """,

        "Missing candidate source":
        """
        SELECT COUNT(*)
        FROM candidates
        WHERE source_id IS NULL;
        """,


        # Jobs
        "Missing job titles":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE job_title IS NULL
           OR TRIM(job_title) = '';
        """,

        "Missing job departments":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE department_id IS NULL;
        """,

        "Missing job locations":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE location_id IS NULL;
        """,

        "Missing assigned recruiters":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE assigned_recruiter_id IS NULL;
        """,

        "Missing job opened dates":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE opened_date IS NULL;
        """,

        "Missing job statuses":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE job_status IS NULL
           OR TRIM(job_status) = '';
        """,


        # Applications
        "Missing application candidate IDs":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE candidate_id IS NULL;
        """,

        "Missing application job IDs":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE job_id IS NULL;
        """,

        "Missing application recruiter IDs":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE recruiter_id IS NULL;
        """,

        "Missing application dates":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE applied_date IS NULL;
        """,

        "Missing application stages":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE current_stage IS NULL
           OR TRIM(current_stage) = '';
        """,

        "Missing application statuses":
        """
        SELECT COUNT(*)
        FROM applications
        WHERE status IS NULL
           OR TRIM(status) = '';
        """,


        # Offers
        "Missing offer application IDs":
        """
        SELECT COUNT(*)
        FROM offers
        WHERE application_id IS NULL;
        """,

        "Missing offer dates":
        """
        SELECT COUNT(*)
        FROM offers
        WHERE offer_date IS NULL;
        """,

        "Missing offered salaries":
        """
        SELECT COUNT(*)
        FROM offers
        WHERE offered_salary IS NULL;
        """,

        "Missing offer statuses":
        """
        SELECT COUNT(*)
        FROM offers
        WHERE offer_status IS NULL
           OR TRIM(offer_status) = '';
        """,


        # Placements
        "Missing placement candidate IDs":
        """
        SELECT COUNT(*)
        FROM placements
        WHERE candidate_id IS NULL;
        """,

        "Missing placement job IDs":
        """
        SELECT COUNT(*)
        FROM placements
        WHERE job_id IS NULL;
        """,

        "Missing placement dates":
        """
        SELECT COUNT(*)
        FROM placements
        WHERE placement_date IS NULL;
        """,

        "Missing placement statuses":
        """
        SELECT COUNT(*)
        FROM placements
        WHERE placement_status IS NULL
           OR TRIM(placement_status) = '';
        """,
    }

    for check_name, query in null_checks.items():

        run_zero_check(
            category="NULL Validation",
            check_name=check_name,
            query=query,
        )


# =============================================================
# 6. FOREIGN KEY / ORPHAN VALIDATION
# =============================================================

def check_foreign_keys():

    print("[6/10] Checking foreign-key integrity...")

    foreign_key_checks = {

        "Applications → Candidates":
        """
        SELECT COUNT(*)
        FROM applications a
        LEFT JOIN candidates c
            ON a.candidate_id = c.candidate_id
        WHERE c.candidate_id IS NULL;
        """,

        "Applications → Jobs":
        """
        SELECT COUNT(*)
        FROM applications a
        LEFT JOIN jobs j
            ON a.job_id = j.job_id
        WHERE j.job_id IS NULL;
        """,

        "Applications → Recruiters":
        """
        SELECT COUNT(*)
        FROM applications a
        LEFT JOIN recruiters r
            ON a.recruiter_id = r.recruiter_id
        WHERE r.recruiter_id IS NULL;
        """,

        "Interviews → Applications":
        """
        SELECT COUNT(*)
        FROM interviews i
        LEFT JOIN applications a
            ON i.application_id = a.application_id
        WHERE a.application_id IS NULL;
        """,

        "Offers → Applications":
        """
        SELECT COUNT(*)
        FROM offers o
        LEFT JOIN applications a
            ON o.application_id = a.application_id
        WHERE a.application_id IS NULL;
        """,

        "Placements → Offers":
        """
        SELECT COUNT(*)
        FROM placements p
        LEFT JOIN offers o
            ON p.offer_id = o.offer_id
        WHERE o.offer_id IS NULL;
        """,

        "Placements → Candidates":
        """
        SELECT COUNT(*)
        FROM placements p
        LEFT JOIN candidates c
            ON p.candidate_id = c.candidate_id
        WHERE c.candidate_id IS NULL;
        """,

        "Placements → Jobs":
        """
        SELECT COUNT(*)
        FROM placements p
        LEFT JOIN jobs j
            ON p.job_id = j.job_id
        WHERE j.job_id IS NULL;
        """,

        "Candidate Skills → Candidates":
        """
        SELECT COUNT(*)
        FROM candidate_skills cs
        LEFT JOIN candidates c
            ON cs.candidate_id = c.candidate_id
        WHERE c.candidate_id IS NULL;
        """,

        "Candidate Skills → Skills":
        """
        SELECT COUNT(*)
        FROM candidate_skills cs
        LEFT JOIN skills s
            ON cs.skill_id = s.skill_id
        WHERE s.skill_id IS NULL;
        """,

        "Job Skills → Jobs":
        """
        SELECT COUNT(*)
        FROM job_skills js
        LEFT JOIN jobs j
            ON js.job_id = j.job_id
        WHERE j.job_id IS NULL;
        """,

        "Job Skills → Skills":
        """
        SELECT COUNT(*)
        FROM job_skills js
        LEFT JOIN skills s
            ON js.skill_id = s.skill_id
        WHERE s.skill_id IS NULL;
        """,

        "Jobs → Departments":
        """
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN departments d
            ON j.department_id = d.department_id
        WHERE d.department_id IS NULL;
        """,

        "Jobs → Locations":
        """
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN locations l
            ON j.location_id = l.location_id
        WHERE l.location_id IS NULL;
        """,

        "Jobs → Recruiters":
        """
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN recruiters r
            ON j.assigned_recruiter_id = r.recruiter_id
        WHERE r.recruiter_id IS NULL;
        """,

        "Candidates → Locations":
        """
        SELECT COUNT(*)
        FROM candidates c
        LEFT JOIN locations l
            ON c.location_id = l.location_id
        WHERE l.location_id IS NULL;
        """,

        "Candidates → Sources":
        """
        SELECT COUNT(*)
        FROM candidates c
        LEFT JOIN sources s
            ON c.source_id = s.source_id
        WHERE s.source_id IS NULL;
        """,

        "Candidates → Work Authorizations":
        """
        SELECT COUNT(*)
        FROM candidates c
        LEFT JOIN work_authorizations w
            ON c.work_authorization_id =
               w.work_authorization_id
        WHERE w.work_authorization_id IS NULL;
        """,
    }

    for check_name, query in foreign_key_checks.items():

        run_zero_check(
            category="Foreign Key",
            check_name=check_name,
            query=query,
            notes="Orphan record count",
        )


# =============================================================
# 7. RECRUITMENT TIMELINE VALIDATION
# =============================================================

def check_date_integrity():

    print("[7/10] Checking recruitment timeline integrity...")

    date_checks = {

        "Jobs closed before opened":
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE closed_date IS NOT NULL
          AND opened_date IS NOT NULL
          AND closed_date < opened_date;
        """,

        "Applications before job opened":
        """
        SELECT COUNT(*)
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.job_id
        WHERE a.applied_date IS NOT NULL
          AND j.opened_date IS NOT NULL
          AND a.applied_date < j.opened_date;
        """,

        "Interviews before application":
        """
        SELECT COUNT(*)
        FROM interviews i
        JOIN applications a
            ON i.application_id = a.application_id
        WHERE i.interview_date IS NOT NULL
          AND a.applied_date IS NOT NULL
          AND i.interview_date < a.applied_date;
        """,

        "Offers before application":
        """
        SELECT COUNT(*)
        FROM offers o
        JOIN applications a
            ON o.application_id = a.application_id
        WHERE o.offer_date IS NOT NULL
          AND a.applied_date IS NOT NULL
          AND o.offer_date < a.applied_date;
        """,

        "Placements before offer":
        """
        SELECT COUNT(*)
        FROM placements p
        JOIN offers o
            ON p.offer_id = o.offer_id
        WHERE p.placement_date IS NOT NULL
          AND o.offer_date IS NOT NULL
          AND p.placement_date < o.offer_date;
        """,

        "Joining before placement":
        """
        SELECT COUNT(*)
        FROM placements
        WHERE joining_date IS NOT NULL
          AND placement_date IS NOT NULL
          AND joining_date < placement_date;
        """,
    }

    for check_name, query in date_checks.items():

        run_zero_check(
            category="Date Integrity",
            check_name=check_name,
            query=query,
        )


# =============================================================
# 8. SALARY VALIDATION
# =============================================================

def check_salary_quality():

    print("[8/10] Checking salary data...")

    run_zero_check(
        category="Salary",
        check_name="Negative offered salaries",
        query="""
        SELECT COUNT(*)
        FROM offers
        WHERE offered_salary < 0;
        """,
    )

    run_zero_check(
        category="Salary",
        check_name="Jobs with negative minimum salary",
        query="""
        SELECT COUNT(*)
        FROM jobs
        WHERE min_salary < 0;
        """,
    )

    run_zero_check(
        category="Salary",
        check_name="Jobs with negative maximum salary",
        query="""
        SELECT COUNT(*)
        FROM jobs
        WHERE max_salary < 0;
        """,
    )

    run_zero_check(
        category="Salary",
        check_name="Jobs where minimum salary exceeds maximum",
        query="""
        SELECT COUNT(*)
        FROM jobs
        WHERE min_salary IS NOT NULL
          AND max_salary IS NOT NULL
          AND min_salary > max_salary;
        """,
    )


# =============================================================
# 9. PLACEMENT CONSISTENCY
# =============================================================

def check_placement_consistency():

    print("[9/10] Checking placement consistency...")

    run_zero_check(
        category="Placement Integrity",
        check_name="Placement candidate mismatch",
        query="""
        SELECT COUNT(*)
        FROM placements p
        JOIN offers o
            ON p.offer_id = o.offer_id
        JOIN applications a
            ON o.application_id = a.application_id
        WHERE p.candidate_id <> a.candidate_id;
        """,
        notes=(
            "Placement candidate should match the candidate "
            "from the linked application"
        ),
    )

    run_zero_check(
        category="Placement Integrity",
        check_name="Placement job mismatch",
        query="""
        SELECT COUNT(*)
        FROM placements p
        JOIN offers o
            ON p.offer_id = o.offer_id
        JOIN applications a
            ON o.application_id = a.application_id
        WHERE p.job_id <> a.job_id;
        """,
        notes=(
            "Placement job should match the job "
            "from the linked application"
        ),
    )

    run_zero_check(
        category="Placement Integrity",
        check_name="Placement linked to non-accepted offer",
        query="""
        SELECT COUNT(*)
        FROM placements p
        JOIN offers o
            ON p.offer_id = o.offer_id
        WHERE LOWER(o.offer_status) <> 'accepted';
        """,
        notes="Placements should normally originate from accepted offers",
    )


# =============================================================
# 10. DASHBOARD VIEW VALIDATION
# =============================================================

def check_dashboard_views():

    print("[10/10] Checking dashboard views...")

    dashboard_views = [
        "vw_dashboard_executive_kpis",
        "vw_dashboard_recruitment_funnel",
        "vw_dashboard_application_status",
        "vw_dashboard_job_performance",
        "vw_dashboard_job_aging",
        "vw_dashboard_recruiter_performance",
        "vw_dashboard_time_trends",
        "vw_dashboard_salary_analysis",
        "vw_dashboard_placement_analysis",
        "vw_dashboard_candidate_analysis",
        "vw_dashboard_client_analysis",
        "vw_dashboard_executive_job_summary",
        "vw_dashboard_master",
    ]

    for view in dashboard_views:

        try:

            count = execute_scalar(
                f"SELECT COUNT(*) FROM {view};"
            )

            add_result(
                category="Dashboard Views",
                check_name=f"{view} row count",
                value=count,
                expected="> 0",
                status=(
                    "PASS"
                    if count > 0
                    else "FAIL"
                ),
                notes="Dashboard view should return data",
            )

        except Exception as error:

            add_result(
                category="Dashboard Views",
                check_name=f"{view} row count",
                value="ERROR",
                expected="> 0",
                status="ERROR",
                notes=str(error),
            )


    # ---------------------------------------------------------
    # Negative job ages
    # ---------------------------------------------------------

    run_zero_check(
        category="Dashboard Views",
        check_name="Negative job ages",
        query="""
        SELECT COUNT(*)
        FROM vw_dashboard_job_performance
        WHERE job_age_days < 0;
        """,
        notes=(
            f"Job age uses synthetic snapshot date "
            f"{SNAPSHOT_DATE}"
        ),
    )


    # ---------------------------------------------------------
    # Negative candidate ages
    # ---------------------------------------------------------

    run_zero_check(
        category="Dashboard Views",
        check_name="Negative candidate ages",
        query="""
        SELECT COUNT(*)
        FROM vw_dashboard_candidate_analysis
        WHERE candidate_age_days < 0;
        """,
        notes=(
            f"Candidate age uses synthetic snapshot date "
            f"{SNAPSHOT_DATE}"
        ),
    )


    # ---------------------------------------------------------
    # Invalid funnel percentages
    # ---------------------------------------------------------

    run_zero_check(
        category="Dashboard Views",
        check_name="Invalid funnel percentages",
        query="""
        SELECT COUNT(*)
        FROM vw_dashboard_recruitment_funnel
        WHERE percentage_of_total < 0
           OR percentage_of_total > 100;
        """,
    )


    # ---------------------------------------------------------
    # Invalid recruiter hire rates
    # ---------------------------------------------------------

    run_zero_check(
        category="Dashboard Views",
        check_name="Invalid recruiter hire rates",
        query="""
        SELECT COUNT(*)
        FROM vw_dashboard_recruiter_performance
        WHERE hire_rate < 0
           OR hire_rate > 100;
        """,
    )


    # ---------------------------------------------------------
    # Invalid recruiter placement rates
    # ---------------------------------------------------------

    run_zero_check(
        category="Dashboard Views",
        check_name="Invalid recruiter placement rates",
        query="""
        SELECT COUNT(*)
        FROM vw_dashboard_recruiter_performance
        WHERE placement_rate < 0
           OR placement_rate > 100;
        """,
    )


# =============================================================
# REPORT GENERATION
# =============================================================

def generate_report():

    report = pd.DataFrame(results)

    report.to_csv(
        REPORT_FILE,
        index=False
    )

    return report


def print_report(report):

    print("\n")
    print("=" * 72)
    print("TALENTIQ DATA QUALITY REPORT")
    print("=" * 72)

    total_checks = len(report)

    passed = (
        report["status"] == "PASS"
    ).sum()

    failed = (
        report["status"] == "FAIL"
    ).sum()

    errors = (
        report["status"] == "ERROR"
    ).sum()


    print(f"Total Checks : {total_checks}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {failed}")
    print(f"Errors       : {errors}")


    if total_checks > 0:

        health_score = round(
            passed / total_checks * 100,
            2
        )

    else:

        health_score = 0


    print(f"Health Score : {health_score}%")
    print("-" * 72)


    # ---------------------------------------------------------
    # FAILED CHECKS
    # ---------------------------------------------------------

    problems = report[
        report["status"].isin(
            ["FAIL", "ERROR"]
        )
    ]


    if problems.empty:

        print("STATUS: PASS")
        print(
            "All automated data-quality checks passed."
        )

    else:

        print("STATUS: REVIEW REQUIRED")
        print()

        print(
            problems[
                [
                    "category",
                    "check_name",
                    "value",
                    "status",
                ]
            ].to_string(
                index=False
            )
        )


    print("-" * 72)

    print(
        f"Report saved to:\n{REPORT_FILE}"
    )

    print("=" * 72)


# =============================================================
# MAIN PIPELINE
# =============================================================

def main():

    print("\n")
    print("=" * 72)
    print("TALENTIQ AI RECRUITMENT ANALYTICS")
    print("PYTHON DATA QUALITY ENGINE")
    print("=" * 72)

    print(
        f"Synthetic Dataset Snapshot: "
        f"{SNAPSHOT_DATE}"
    )

    print("=" * 72)


    check_database_connection()

    check_table_row_counts()

    check_primary_key_duplicates()

    check_business_key_duplicates()

    check_null_values()

    check_foreign_keys()

    check_date_integrity()

    check_salary_quality()

    check_placement_consistency()

    check_dashboard_views()


    report = generate_report()

    print_report(report)


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()