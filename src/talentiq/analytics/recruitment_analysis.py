"""
===============================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM
File: recruitment_analysis.py

Purpose
-------
Create the Python analytics layer for TalentIQ.

This script:
1. Loads validated PostgreSQL dashboard views
2. Calculates high-level recruitment insights
3. Identifies top recruiters and clients
4. Analyzes job aging
5. Analyzes salary patterns
6. Analyzes placement outcomes
7. Analyzes monthly recruitment trends
8. Generates CSV reports for later use in Streamlit / AI

Synthetic Dataset Snapshot
--------------------------
2026-12-31

Output Folder
-------------
outputs/reports/recruitment_analysis/

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

# /src
SRC_DIR = CURRENT_FILE.parents[2]

# Project root
PROJECT_ROOT = CURRENT_FILE.parents[3]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from database.connection import get_connection


# =============================================================
# CONFIGURATION
# =============================================================

SNAPSHOT_DATE = "2026-12-31"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "recruitment_analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def load_query(query):
    """
    Execute SQL query and return Pandas DataFrame.
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            text(query),
            connection
        )

    return df


def save_report(df, filename):
    """
    Save DataFrame as CSV.
    """

    output_file = OUTPUT_DIR / filename

    df.to_csv(
        output_file,
        index=False
    )

    return output_file


def print_section(title):
    """
    Print formatted terminal section.
    """

    print("\n")
    print("=" * 72)
    print(title)
    print("=" * 72)


# =============================================================
# 1. EXECUTIVE KPI ANALYSIS
# =============================================================

def analyze_executive_kpis():

    print_section(
        "1. EXECUTIVE KPI ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_executive_kpis;
    """

    df = load_query(query)

    if df.empty:

        print("No executive KPI data found.")

        return df

    row = df.iloc[0]

    print(
        f"Total Jobs                 : "
        f"{int(row['total_jobs']):,}"
    )

    print(
        f"Open Jobs                  : "
        f"{int(row['open_jobs']):,}"
    )

    print(
        f"Total Candidates           : "
        f"{int(row['total_candidates']):,}"
    )

    print(
        f"Total Applications         : "
        f"{int(row['total_applications']):,}"
    )

    print(
        f"Total Offers               : "
        f"{int(row['total_offers']):,}"
    )

    print(
        f"Total Placements           : "
        f"{int(row['total_placements']):,}"
    )

    print(
        f"Hired Applications         : "
        f"{int(row['hired_applications']):,}"
    )

    print(
        f"Application → Offer Rate   : "
        f"{row['application_to_offer_rate']:.2f}%"
    )

    print(
        f"Application → Placement    : "
        f"{row['application_to_placement_rate']:.2f}%"
    )

    print(
        f"Offer → Placement Rate     : "
        f"{row['offer_to_placement_rate']:.2f}%"
    )

    print(
        f"Avg Days to Placement      : "
        f"{row['avg_days_to_placement']:.2f}"
    )

    save_report(
        df,
        "01_executive_kpis.csv"
    )

    return df


# =============================================================
# 2. RECRUITMENT FUNNEL ANALYSIS
# =============================================================

def analyze_recruitment_funnel():

    print_section(
        "2. RECRUITMENT FUNNEL ANALYSIS"
    )

    query = """
    SELECT
        current_stage,
        application_count,
        percentage_of_total
    FROM vw_dashboard_recruitment_funnel;
    """

    df = load_query(query)

    if df.empty:

        print("No funnel data found.")

        return df

    df = df.sort_values(
        by="application_count",
        ascending=False
    )

    print(
        df.to_string(
            index=False
        )
    )

    save_report(
        df,
        "02_recruitment_funnel.csv"
    )

    return df


# =============================================================
# 3. APPLICATION STATUS ANALYSIS
# =============================================================

def analyze_application_status():

    print_section(
        "3. APPLICATION STATUS ANALYSIS"
    )

    query = """
    SELECT
        status,
        application_count,
        percentage_of_total
    FROM vw_dashboard_application_status;
    """

    df = load_query(query)

    print(
        df.to_string(
            index=False
        )
    )

    save_report(
        df,
        "03_application_status.csv"
    )

    return df


# =============================================================
# 4. RECRUITER PERFORMANCE ANALYSIS
# =============================================================

def analyze_recruiters():

    print_section(
        "4. RECRUITER PERFORMANCE ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_recruiter_performance;
    """

    df = load_query(query)

    if df.empty:

        print("No recruiter data found.")

        return df

    # ---------------------------------------------------------
    # Recruiter ranking score
    #
    # Placement performance receives the largest weight because
    # placements represent the final business outcome.
    # ---------------------------------------------------------

    df["performance_score"] = (
        df["hire_rate"] * 0.40
        +
        df["placement_rate"] * 0.60
    ).round(2)

    df = df.sort_values(
        by=[
            "performance_score",
            "placement_count"
        ],
        ascending=False
    )

    df["recruiter_rank"] = range(
        1,
        len(df) + 1
    )

    columns = [
        "recruiter_rank",
        "recruiter_id",
        "total_applications",
        "interview_count",
        "offer_count",
        "hired_count",
        "placement_count",
        "hire_rate",
        "placement_rate",
        "performance_score",
        "avg_application_age_days",
    ]

    print(
        df[columns].to_string(
            index=False
        )
    )

    top_recruiter = df.iloc[0]

    print("\nTop Recruiter")

    print(
        f"Recruiter ID      : "
        f"{int(top_recruiter['recruiter_id'])}"
    )

    print(
        f"Placements        : "
        f"{int(top_recruiter['placement_count'])}"
    )

    print(
        f"Hire Rate         : "
        f"{top_recruiter['hire_rate']:.2f}%"
    )

    print(
        f"Placement Rate    : "
        f"{top_recruiter['placement_rate']:.2f}%"
    )

    print(
        f"Performance Score : "
        f"{top_recruiter['performance_score']:.2f}"
    )

    save_report(
        df,
        "04_recruiter_performance.csv"
    )

    return df


# =============================================================
# 5. CLIENT PERFORMANCE ANALYSIS
# =============================================================

def analyze_clients():

    print_section(
        "5. CLIENT PERFORMANCE ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_client_analysis;
    """

    df = load_query(query)

    if df.empty:

        print("No client data found.")

        return df

    df = df.sort_values(
        by=[
            "total_placements",
            "placement_rate"
        ],
        ascending=False
    )

    df["client_rank"] = range(
        1,
        len(df) + 1
    )

    columns = [
        "client_rank",
        "client_id",
        "total_jobs",
        "open_jobs",
        "filled_jobs",
        "total_applications",
        "total_offers",
        "total_placements",
        "placement_rate",
        "average_offered_salary",
    ]

    print(
        df[columns].to_string(
            index=False
        )
    )

    top_client = df.iloc[0]

    print("\nTop Client by Placements")

    print(
        f"Client ID         : "
        f"{int(top_client['client_id'])}"
    )

    print(
        f"Jobs              : "
        f"{int(top_client['total_jobs'])}"
    )

    print(
        f"Placements        : "
        f"{int(top_client['total_placements'])}"
    )

    print(
        f"Placement Rate    : "
        f"{top_client['placement_rate']:.2f}%"
    )

    save_report(
        df,
        "05_client_performance.csv"
    )

    return df


# =============================================================
# 6. JOB AGING ANALYSIS
# =============================================================

def analyze_job_aging():

    print_section(
        "6. JOB AGING ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_job_aging;
    """

    jobs = load_query(query)

    if jobs.empty:

        print("No job aging data found.")

        return jobs, pd.DataFrame()

    # ---------------------------------------------------------
    # ACTIVE AGING ANALYSIS
    #
    # Dashboard view retains every job for compatibility.
    # Python analysis focuses specifically on Open jobs.
    # ---------------------------------------------------------

    open_jobs = jobs[
        jobs["job_status"]
        .str.lower()
        .eq("open")
    ].copy()

    aging_summary = (
        open_jobs
        .groupby(
            "aging_bucket",
            dropna=False
        )
        .agg(
            job_count=("job_id", "count"),
            applications=(
                "total_applications",
                "sum"
            ),
            offers=(
                "offer_count",
                "sum"
            ),
            hires=(
                "hired_count",
                "sum"
            ),
            placements=(
                "placement_count",
                "sum"
            ),
            average_age_days=(
                "job_age_days",
                "mean"
            ),
        )
        .reset_index()
    )

    aging_summary[
        "average_age_days"
    ] = (
        aging_summary[
            "average_age_days"
        ]
        .round(2)
    )

    print(
        f"Total Open Jobs: "
        f"{len(open_jobs):,}"
    )

    print("\nOpen Job Aging Distribution")

    print(
        aging_summary.to_string(
            index=False
        )
    )


    # ---------------------------------------------------------
    # Oldest open jobs
    # ---------------------------------------------------------

    oldest_jobs = (
        open_jobs
        .sort_values(
            by="job_age_days",
            ascending=False
        )
        .head(10)
    )

    print("\nTop 10 Oldest Open Jobs")

    print(
        oldest_jobs[
            [
                "job_code",
                "job_title",
                "job_age_days",
                "aging_bucket",
                "total_applications",
                "offer_count",
                "hired_count",
                "placement_count",
            ]
        ].to_string(
            index=False
        )
    )

    save_report(
        aging_summary,
        "06_job_aging_summary.csv"
    )

    save_report(
        oldest_jobs,
        "07_oldest_open_jobs.csv"
    )

    return open_jobs, aging_summary


# =============================================================
# 7. SALARY ANALYSIS
# =============================================================

def analyze_salary():

    print_section(
        "7. SALARY ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_salary_analysis;
    """

    df = load_query(query)

    if df.empty:

        print("No salary data found.")

        return df, pd.DataFrame()

    salary_summary = pd.DataFrame(
        {
            "metric": [
                "Total Offers",
                "Minimum Offer",
                "Maximum Offer",
                "Average Offer",
                "Median Offer",
            ],

            "value": [
                len(df),
                df["offered_salary"].min(),
                df["offered_salary"].max(),
                df["offered_salary"].mean(),
                df["offered_salary"].median(),
            ],
        }
    )

    salary_summary["value"] = (
        salary_summary["value"]
        .round(2)
    )

    print(
        salary_summary.to_string(
            index=False
        )
    )


    position_summary = (
        df["salary_position"]
        .value_counts()
        .rename_axis(
            "salary_position"
        )
        .reset_index(
            name="offer_count"
        )
    )

    position_summary[
        "percentage"
    ] = (
        position_summary[
            "offer_count"
        ]
        /
        len(df)
        *
        100
    ).round(2)

    print("\nSalary Position")

    print(
        position_summary.to_string(
            index=False
        )
    )

    save_report(
        salary_summary,
        "08_salary_summary.csv"
    )

    save_report(
        position_summary,
        "09_salary_position.csv"
    )

    return df, salary_summary


# =============================================================
# 8. PLACEMENT ANALYSIS
# =============================================================

def analyze_placements():

    print_section(
        "8. PLACEMENT ANALYSIS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_placement_analysis;
    """

    df = load_query(query)

    if df.empty:

        print("No placement data found.")

        return df, pd.DataFrame()

    outcome_summary = (
        df
        .groupby(
            "placement_outcome",
            dropna=False
        )
        .agg(
            placement_count=(
                "placement_id",
                "count"
            )
        )
        .reset_index()
    )

    outcome_summary[
        "percentage"
    ] = (
        outcome_summary[
            "placement_count"
        ]
        /
        len(df)
        *
        100
    ).round(2)

    print(
        outcome_summary.to_string(
            index=False
        )
    )


    successful = (
        df["placement_outcome"]
        .eq("SUCCESSFUL")
        .sum()
    )

    success_rate = round(
        successful
        /
        len(df)
        *
        100,
        2
    )

    print(
        f"\nPlacement Success Rate: "
        f"{success_rate:.2f}%"
    )

    print(
        "Average Days to Placement: "
        f"{df['days_to_placement'].mean():.2f}"
    )

    print(
        "Average Placement → Joining: "
        f"{df['days_from_placement_to_joining'].mean():.2f}"
    )

    save_report(
        outcome_summary,
        "10_placement_outcomes.csv"
    )

    return df, outcome_summary


# =============================================================
# 9. MONTHLY TREND ANALYSIS
# =============================================================

def analyze_monthly_trends():

    print_section(
        "9. MONTHLY RECRUITMENT TRENDS"
    )

    query = """
    SELECT *
    FROM vw_dashboard_time_trends
    ORDER BY month;
    """

    df = load_query(query)

    if df.empty:

        print("No trend data found.")

        return df

    df["month"] = pd.to_datetime(
        df["month"]
    )

    # ---------------------------------------------------------
    # Month-over-month application growth
    # ---------------------------------------------------------

    df["application_mom_growth_pct"] = (
        df["applications"]
        .pct_change()
        .mul(100)
        .round(2)
    )

    # ---------------------------------------------------------
    # Placement conversion per month
    # ---------------------------------------------------------

    df[
        "application_to_placement_rate"
    ] = (
        df["placements"]
        /
        df["applications"]
        .replace(0, pd.NA)
        *
        100
    ).round(2)

    print(
        df.to_string(
            index=False
        )
    )


    peak_month = df.loc[
        df["applications"].idxmax()
    ]

    print("\nPeak Application Month")

    print(
        f"Month        : "
        f"{peak_month['month'].strftime('%Y-%m')}"
    )

    print(
        f"Applications : "
        f"{int(peak_month['applications']):,}"
    )

    save_report(
        df,
        "11_monthly_recruitment_trends.csv"
    )

    return df


# =============================================================
# 10. BUSINESS INSIGHTS
# =============================================================

def generate_business_insights(
    executive_df,
    recruiter_df,
    client_df,
    open_jobs,
    salary_df,
    placement_df,
    trend_df
):

    print_section(
        "10. TALENTIQ BUSINESS INSIGHTS"
    )

    insights = []

    # ---------------------------------------------------------
    # Executive conversion
    # ---------------------------------------------------------

    if not executive_df.empty:

        executive = executive_df.iloc[0]

        placement_rate = float(
            executive[
                "application_to_placement_rate"
            ]
        )

        insights.append(
            {
                "insight":
                "Overall Application-to-Placement Rate",

                "value":
                f"{placement_rate:.2f}%",

                "interpretation":
                (
                    "Measures how many applications "
                    "ultimately result in placements."
                )
            }
        )


    # ---------------------------------------------------------
    # Top recruiter
    # ---------------------------------------------------------

    if not recruiter_df.empty:

        top = recruiter_df.iloc[0]

        insights.append(
            {
                "insight":
                "Top Recruiter",

                "value":
                f"Recruiter {int(top['recruiter_id'])}",

                "interpretation":
                (
                    f"{int(top['placement_count'])} placements "
                    f"with a {top['placement_rate']:.2f}% "
                    f"placement rate."
                )
            }
        )


    # ---------------------------------------------------------
    # Top client
    # ---------------------------------------------------------

    if not client_df.empty:

        top = client_df.iloc[0]

        insights.append(
            {
                "insight":
                "Top Client by Placements",

                "value":
                f"Client {int(top['client_id'])}",

                "interpretation":
                (
                    f"{int(top['total_placements'])} placements "
                    f"from {int(top['total_jobs'])} jobs."
                )
            }
        )


    # ---------------------------------------------------------
    # Critical open jobs
    # ---------------------------------------------------------

    if not open_jobs.empty:

        critical_jobs = (
            open_jobs[
                open_jobs[
                    "job_age_days"
                ] >= 90
            ]
        )

        insights.append(
            {
                "insight":
                "Open Jobs Aged 90+ Days",

                "value":
                f"{len(critical_jobs):,}",

                "interpretation":
                (
                    "These jobs represent the highest "
                    "aging-priority requirements."
                )
            }
        )


    # ---------------------------------------------------------
    # Salary above range
    # ---------------------------------------------------------

    if not salary_df.empty:

        above_range = (
            salary_df[
                "salary_position"
            ]
            .eq("ABOVE RANGE")
            .sum()
        )

        above_rate = round(
            above_range
            /
            len(salary_df)
            *
            100,
            2
        )

        insights.append(
            {
                "insight":
                "Offers Above Job Salary Range",

                "value":
                f"{above_rate:.2f}%",

                "interpretation":
                (
                    "High values may indicate salary-range "
                    "alignment issues in the synthetic dataset "
                    "or aggressive compensation."
                )
            }
        )


    # ---------------------------------------------------------
    # Placement success
    # ---------------------------------------------------------

    if not placement_df.empty:

        successful = (
            placement_df[
                "placement_outcome"
            ]
            .eq("SUCCESSFUL")
            .sum()
        )

        success_rate = round(
            successful
            /
            len(placement_df)
            *
            100,
            2
        )

        insights.append(
            {
                "insight":
                "Placement Success Rate",

                "value":
                f"{success_rate:.2f}%",

                "interpretation":
                (
                    "Percentage of placements classified "
                    "as active or having completed the "
                    "guarantee period."
                )
            }
        )


    # ---------------------------------------------------------
    # Peak recruitment month
    # ---------------------------------------------------------

    if not trend_df.empty:

        peak = trend_df.loc[
            trend_df[
                "applications"
            ].idxmax()
        ]

        insights.append(
            {
                "insight":
                "Peak Recruitment Month",

                "value":
                peak[
                    "month"
                ].strftime("%Y-%m"),

                "interpretation":
                (
                    f"{int(peak['applications']):,} "
                    f"applications were recorded."
                )
            }
        )


    insights_df = pd.DataFrame(
        insights
    )

    print(
        insights_df.to_string(
            index=False
        )
    )

    save_report(
        insights_df,
        "12_business_insights.csv"
    )

    return insights_df


# =============================================================
# FINAL SUMMARY
# =============================================================

def print_final_summary():

    print("\n")
    print("=" * 72)
    print("TALENTIQ RECRUITMENT ANALYSIS COMPLETE")
    print("=" * 72)

    print(
        "Reports created in:"
    )

    print(
        OUTPUT_DIR
    )

    print()

    print(
        "Python Analytics Layer: COMPLETE"
    )

    print("=" * 72)


# =============================================================
# MAIN PIPELINE
# =============================================================

def main():

    print("\n")
    print("=" * 72)
    print("TALENTIQ AI RECRUITMENT ANALYTICS")
    print("PYTHON RECRUITMENT ANALYSIS ENGINE")
    print("=" * 72)

    print(
        f"Synthetic Dataset Snapshot: "
        f"{SNAPSHOT_DATE}"
    )

    print("=" * 72)


    executive_df = (
        analyze_executive_kpis()
    )

    funnel_df = (
        analyze_recruitment_funnel()
    )

    application_status_df = (
        analyze_application_status()
    )

    recruiter_df = (
        analyze_recruiters()
    )

    client_df = (
        analyze_clients()
    )

    open_jobs, aging_summary = (
        analyze_job_aging()
    )

    salary_df, salary_summary = (
        analyze_salary()
    )

    placement_df, placement_summary = (
        analyze_placements()
    )

    trend_df = (
        analyze_monthly_trends()
    )


    generate_business_insights(
        executive_df=executive_df,
        recruiter_df=recruiter_df,
        client_df=client_df,
        open_jobs=open_jobs,
        salary_df=salary_df,
        placement_df=placement_df,
        trend_df=trend_df,
    )


    print_final_summary()


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()