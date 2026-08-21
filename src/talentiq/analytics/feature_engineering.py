"""
===============================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM
File: feature_engineering.py

Purpose
-------
Create candidate-job matching features from the TalentIQ
PostgreSQL recruitment database.

This script prepares features for the future matching engine.

Main Features
-------------
1. Must-have skill match
2. Nice-to-have skill match
3. Overall weighted skill match
4. Candidate experience
5. Required job experience
6. Experience gap
7. Experience match score
8. Location match
9. Candidate skill count
10. Job required skill count

Output
------
outputs/reports/feature_engineering/

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

SRC_DIR = CURRENT_FILE.parents[2]
PROJECT_ROOT = CURRENT_FILE.parents[3]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from database.connection import get_connection


# =============================================================
# CONFIGURATION
# =============================================================

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "feature_engineering"
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
    Execute a SQL query and return a Pandas DataFrame.
    """

    with get_connection() as connection:

        return pd.read_sql_query(
            text(query),
            connection
        )


def save_report(df, filename):
    """
    Save DataFrame to CSV.
    """

    output_file = OUTPUT_DIR / filename

    df.to_csv(
        output_file,
        index=False
    )

    return output_file


def print_section(title):
    """
    Print formatted terminal heading.
    """

    print("\n")
    print("=" * 72)
    print(title)
    print("=" * 72)


# =============================================================
# 1. LOAD CORE DATA
# =============================================================

def load_core_data():

    print_section(
        "1. LOADING TALENTIQ DATA"
    )

    candidates = load_query(
        """
        SELECT
            candidate_id,
            candidate_name,
            experience_years,
            location_id,
            work_authorization_id
        FROM candidates;
        """
    )

    jobs = load_query(
        """
        SELECT
            job_id,
            job_code,
            job_title,
            job_status,
            experience_required,
            location_id,
            employment_type,
            work_mode,
            min_salary,
            max_salary
        FROM jobs;
        """
    )

    applications = load_query(
        """
        SELECT
            application_id,
            candidate_id,
            job_id,
            applied_date,
            current_stage,
            status
        FROM applications;
        """
    )

    candidate_skills = load_query(
        """
        SELECT
            cs.candidate_id,
            cs.skill_id,
            s.skill_name
        FROM candidate_skills cs

        JOIN skills s
            ON cs.skill_id = s.skill_id;
        """
    )

    job_skills = load_query(
        """
        SELECT
            js.job_id,
            js.skill_id,
            s.skill_name,
            js.priority
        FROM job_skills js

        JOIN skills s
            ON js.skill_id = s.skill_id;
        """
    )

    print(
        f"Candidates        : {len(candidates):,}"
    )

    print(
        f"Jobs              : {len(jobs):,}"
    )

    print(
        f"Applications      : {len(applications):,}"
    )

    print(
        f"Candidate Skills  : {len(candidate_skills):,}"
    )

    print(
        f"Job Skills        : {len(job_skills):,}"
    )

    return (
        candidates,
        jobs,
        applications,
        candidate_skills,
        job_skills,
    )


# =============================================================
# 2. CREATE SKILL SETS
# =============================================================

def build_candidate_skill_sets(
    candidate_skills
):

    print_section(
        "2. BUILDING CANDIDATE SKILL PROFILES"
    )

    candidate_skill_sets = (
        candidate_skills
        .groupby("candidate_id")["skill_id"]
        .apply(set)
        .to_dict()
    )

    candidate_skill_names = (
        candidate_skills
        .groupby("candidate_id")["skill_name"]
        .apply(
            lambda values:
            sorted(set(values))
        )
        .to_dict()
    )

    print(
        f"Candidate skill profiles created: "
        f"{len(candidate_skill_sets):,}"
    )

    return (
        candidate_skill_sets,
        candidate_skill_names,
    )


def build_job_skill_sets(
    job_skills
):

    print_section(
        "3. BUILDING JOB SKILL PROFILES"
    )

    must_have = (
        job_skills[
            job_skills["priority"]
            .str.lower()
            .eq("must-have")
        ]
        .groupby("job_id")["skill_id"]
        .apply(set)
        .to_dict()
    )

    nice_to_have = (
        job_skills[
            job_skills["priority"]
            .str.lower()
            .eq("nice-to-have")
        ]
        .groupby("job_id")["skill_id"]
        .apply(set)
        .to_dict()
    )

    all_skills = (
        job_skills
        .groupby("job_id")["skill_id"]
        .apply(set)
        .to_dict()
    )

    print(
        f"Jobs with skill profiles: "
        f"{len(all_skills):,}"
    )

    return (
        must_have,
        nice_to_have,
        all_skills,
    )


# =============================================================
# 4. SKILL MATCH FUNCTIONS
# =============================================================

def calculate_match_rate(
    candidate_skills,
    required_skills
):

    """
    Return percentage of required skills
    available in candidate profile.
    """

    if not required_skills:
        return 100.0

    matched = (
        candidate_skills
        .intersection(required_skills)
    )

    return round(
        len(matched)
        /
        len(required_skills)
        *
        100,
        2
    )


def count_matches(
    candidate_skills,
    required_skills
):

    return len(
        candidate_skills
        .intersection(required_skills)
    )


# =============================================================
# 5. EXPERIENCE FEATURES
# =============================================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):

    """
    Calculate an explainable 0-100 experience score.

    Candidate meets/exceeds requirement:
        100

    Candidate below requirement:
        proportional score.
    """

    if pd.isna(required_experience):
        return 100.0

    if pd.isna(candidate_experience):
        return 0.0

    required_experience = float(
        required_experience
    )

    candidate_experience = float(
        candidate_experience
    )

    if required_experience <= 0:
        return 100.0

    if (
        candidate_experience
        >= required_experience
    ):
        return 100.0

    return round(
        candidate_experience
        /
        required_experience
        *
        100,
        2
    )


# =============================================================
# 6. GENERATE MATCH FEATURES
# =============================================================

def engineer_application_features(
    candidates,
    jobs,
    applications,
    candidate_skill_sets,
    must_have_skill_sets,
    nice_to_have_skill_sets,
    all_job_skill_sets,
):

    print_section(
        "4. ENGINEERING CANDIDATE-JOB FEATURES"
    )

    # ---------------------------------------------------------
    # Join candidate + job information to applications
    # ---------------------------------------------------------

    candidate_columns = [
        "candidate_id",
        "candidate_name",
        "experience_years",
        "location_id",
        "work_authorization_id",
    ]

    candidate_data = (
        candidates[candidate_columns]
        .rename(
            columns={
                "location_id":
                "candidate_location_id"
            }
        )
    )


    job_columns = [
        "job_id",
        "job_code",
        "job_title",
        "job_status",
        "experience_required",
        "location_id",
        "employment_type",
        "work_mode",
        "min_salary",
        "max_salary",
    ]

    job_data = (
        jobs[job_columns]
        .rename(
            columns={
                "location_id":
                "job_location_id"
            }
        )
    )


    features = (
        applications
        .merge(
            candidate_data,
            on="candidate_id",
            how="left"
        )
        .merge(
            job_data,
            on="job_id",
            how="left"
        )
    )


    # ---------------------------------------------------------
    # Candidate skill count
    # ---------------------------------------------------------

    features[
        "candidate_skill_count"
    ] = (
        features["candidate_id"]
        .map(
            lambda candidate_id:
            len(
                candidate_skill_sets.get(
                    candidate_id,
                    set()
                )
            )
        )
    )


    # ---------------------------------------------------------
    # Job skill counts
    # ---------------------------------------------------------

    features[
        "must_have_skill_count"
    ] = (
        features["job_id"]
        .map(
            lambda job_id:
            len(
                must_have_skill_sets.get(
                    job_id,
                    set()
                )
            )
        )
    )


    features[
        "nice_to_have_skill_count"
    ] = (
        features["job_id"]
        .map(
            lambda job_id:
            len(
                nice_to_have_skill_sets.get(
                    job_id,
                    set()
                )
            )
        )
    )


    features[
        "total_job_skill_count"
    ] = (
        features["job_id"]
        .map(
            lambda job_id:
            len(
                all_job_skill_sets.get(
                    job_id,
                    set()
                )
            )
        )
    )


    # ---------------------------------------------------------
    # Must-have skill matches
    # ---------------------------------------------------------

    features[
        "must_have_matches"
    ] = features.apply(

        lambda row:

        count_matches(

            candidate_skill_sets.get(
                row["candidate_id"],
                set()
            ),

            must_have_skill_sets.get(
                row["job_id"],
                set()
            )
        ),

        axis=1
    )


    features[
        "must_have_match_rate"
    ] = features.apply(

        lambda row:

        calculate_match_rate(

            candidate_skill_sets.get(
                row["candidate_id"],
                set()
            ),

            must_have_skill_sets.get(
                row["job_id"],
                set()
            )
        ),

        axis=1
    )


    # ---------------------------------------------------------
    # Nice-to-have skill matches
    # ---------------------------------------------------------

    features[
        "nice_to_have_matches"
    ] = features.apply(

        lambda row:

        count_matches(

            candidate_skill_sets.get(
                row["candidate_id"],
                set()
            ),

            nice_to_have_skill_sets.get(
                row["job_id"],
                set()
            )
        ),

        axis=1
    )


    features[
        "nice_to_have_match_rate"
    ] = features.apply(

        lambda row:

        calculate_match_rate(

            candidate_skill_sets.get(
                row["candidate_id"],
                set()
            ),

            nice_to_have_skill_sets.get(
                row["job_id"],
                set()
            )
        ),

        axis=1
    )


    # ---------------------------------------------------------
    # Overall skill match
    # ---------------------------------------------------------

    features[
        "overall_skill_match_rate"
    ] = (

        features[
            "must_have_match_rate"
        ]
        *
        0.75

        +

        features[
            "nice_to_have_match_rate"
        ]
        *
        0.25

    ).round(2)


    # ---------------------------------------------------------
    # Experience gap
    # ---------------------------------------------------------

    features[
        "experience_gap"
    ] = (

        features[
            "experience_years"
        ]

        -

        features[
            "experience_required"
        ]

    )


    # ---------------------------------------------------------
    # Experience score
    # ---------------------------------------------------------

    features[
        "experience_match_score"
    ] = features.apply(

        lambda row:

        calculate_experience_score(

            row[
                "experience_years"
            ],

            row[
                "experience_required"
            ]

        ),

        axis=1
    )


    # ---------------------------------------------------------
    # Location match
    # ---------------------------------------------------------

    features[
        "location_match"
    ] = (

        features[
            "candidate_location_id"
        ]

        ==

        features[
            "job_location_id"
        ]

    ).astype(int)


    features[
        "location_match_score"
    ] = (

        features[
            "location_match"
        ]
        *
        100
    )


    # ---------------------------------------------------------
    # Preliminary structured match score
    #
    # This is NOT the final TalentIQ score.
    #
    # Final candidate matcher will combine:
    # - structured score
    # - semantic embedding score
    # ---------------------------------------------------------

    features[
        "structured_match_score"
    ] = (

        features[
            "overall_skill_match_rate"
        ]
        *
        0.70

        +

        features[
            "experience_match_score"
        ]
        *
        0.20

        +

        features[
            "location_match_score"
        ]
        *
        0.10

    ).round(2)


    print(
        f"Feature rows created: "
        f"{len(features):,}"
    )

    return features


# =============================================================
# 7. FEATURE SUMMARY
# =============================================================

def analyze_features(
    features
):

    print_section(
        "5. FEATURE ENGINEERING SUMMARY"
    )

    columns = [

        "candidate_skill_count",
        "must_have_skill_count",
        "nice_to_have_skill_count",

        "must_have_match_rate",
        "nice_to_have_match_rate",
        "overall_skill_match_rate",

        "experience_match_score",
        "location_match_score",

        "structured_match_score",
    ]


    summary = (
        features[
            columns
        ]
        .describe()
        .T
        .reset_index()
        .rename(
            columns={
                "index":
                "feature"
            }
        )
    )


    summary = summary.round(2)


    print(
        summary.to_string(
            index=False
        )
    )

    save_report(
        summary,
        "02_feature_summary.csv"
    )

    return summary


# =============================================================
# 8. MATCH SCORE DISTRIBUTION
# =============================================================

def create_score_distribution(
    features
):

    print_section(
        "6. STRUCTURED MATCH SCORE DISTRIBUTION"
    )


    bins = [
        0,
        40,
        60,
        75,
        90,
        101
    ]


    labels = [
        "Very Low",
        "Low",
        "Moderate",
        "Strong",
        "Excellent"
    ]


    features[
        "match_category"
    ] = pd.cut(

        features[
            "structured_match_score"
        ],

        bins=bins,

        labels=labels,

        right=False
    )


    distribution = (

        features[
            "match_category"
        ]

        .value_counts(
            sort=False
        )

        .rename_axis(
            "match_category"
        )

        .reset_index(
            name="candidate_job_pairs"
        )

    )


    distribution[
        "percentage"
    ] = (

        distribution[
            "candidate_job_pairs"
        ]

        /

        len(features)

        *

        100

    ).round(2)


    print(
        distribution.to_string(
            index=False
        )
    )


    save_report(
        distribution,
        "03_match_score_distribution.csv"
    )

    return distribution


# =============================================================
# 9. TOP MATCHED APPLICATIONS
# =============================================================

def analyze_top_matches(
    features
):

    print_section(
        "7. TOP STRUCTURED CANDIDATE-JOB MATCHES"
    )


    top_matches = (

        features

        .sort_values(
            by=[
                "structured_match_score",
                "must_have_match_rate",
                "experience_match_score"
            ],
            ascending=False
        )

        .head(20)

    )


    display_columns = [

        "candidate_id",
        "candidate_name",

        "job_id",
        "job_code",
        "job_title",

        "experience_years",
        "experience_required",

        "must_have_match_rate",
        "nice_to_have_match_rate",
        "overall_skill_match_rate",

        "experience_match_score",
        "location_match_score",

        "structured_match_score",
        "match_category",
    ]


    print(
        top_matches[
            display_columns
        ].to_string(
            index=False
        )
    )


    save_report(
        top_matches[
            display_columns
        ],
        "04_top_candidate_job_matches.csv"
    )


    return top_matches


# =============================================================
# 10. SAVE FEATURE DATASET
# =============================================================

def save_feature_dataset(
    features
):

    print_section(
        "8. SAVING FEATURE DATASET"
    )


    output_file = save_report(
        features,
        "01_candidate_job_features.csv"
    )


    print(
        f"Feature dataset saved to:\n"
        f"{output_file}"
    )


# =============================================================
# 11. VALIDATE FEATURE DATASET
# =============================================================

def validate_features(
    features
):

    print_section(
        "9. FEATURE VALIDATION"
    )


    validation_results = []


    # ---------------------------------------------------------
    # Missing candidate IDs
    # ---------------------------------------------------------

    missing_candidate_ids = (
        features[
            "candidate_id"
        ]
        .isna()
        .sum()
    )


    validation_results.append(
        {
            "check":
            "Missing candidate IDs",

            "value":
            missing_candidate_ids,

            "status":
            (
                "PASS"
                if missing_candidate_ids == 0
                else "FAIL"
            )
        }
    )


    # ---------------------------------------------------------
    # Missing job IDs
    # ---------------------------------------------------------

    missing_job_ids = (
        features[
            "job_id"
        ]
        .isna()
        .sum()
    )


    validation_results.append(
        {
            "check":
            "Missing job IDs",

            "value":
            missing_job_ids,

            "status":
            (
                "PASS"
                if missing_job_ids == 0
                else "FAIL"
            )
        }
    )


    # ---------------------------------------------------------
    # Invalid structured match scores
    # ---------------------------------------------------------

    invalid_scores = (

        (
            features[
                "structured_match_score"
            ] < 0
        )

        |

        (
            features[
                "structured_match_score"
            ] > 100
        )

    ).sum()


    validation_results.append(
        {
            "check":
            "Invalid structured match scores",

            "value":
            invalid_scores,

            "status":
            (
                "PASS"
                if invalid_scores == 0
                else "FAIL"
            )
        }
    )


    # ---------------------------------------------------------
    # Invalid must-have rates
    # ---------------------------------------------------------

    invalid_must_have = (

        (
            features[
                "must_have_match_rate"
            ] < 0
        )

        |

        (
            features[
                "must_have_match_rate"
            ] > 100
        )

    ).sum()


    validation_results.append(
        {
            "check":
            "Invalid must-have match rates",

            "value":
            invalid_must_have,

            "status":
            (
                "PASS"
                if invalid_must_have == 0
                else "FAIL"
            )
        }
    )


    validation = pd.DataFrame(
        validation_results
    )


    print(
        validation.to_string(
            index=False
        )
    )


    save_report(
        validation,
        "05_feature_validation.csv"
    )


    return validation


# =============================================================
# FINAL SUMMARY
# =============================================================

def print_final_summary(
    features,
    validation
):

    print("\n")
    print("=" * 72)

    print(
        "TALENTIQ FEATURE ENGINEERING COMPLETE"
    )

    print("=" * 72)


    print(
        f"Candidate-Job Feature Rows : "
        f"{len(features):,}"
    )


    print(
        "Average Structured Match  : "
        f"{features['structured_match_score'].mean():.2f}%"
    )


    print(
        "Highest Structured Match  : "
        f"{features['structured_match_score'].max():.2f}%"
    )


    failed = (
        validation[
            "status"
        ]
        .ne("PASS")
        .sum()
    )


    print(
        f"Validation Failures        : "
        f"{failed}"
    )


    print()


    if failed == 0:

        print(
            "STATUS: PASS"
        )

        print(
            "Feature dataset is ready "
            "for Candidate Matching."
        )

    else:

        print(
            "STATUS: REVIEW REQUIRED"
        )


    print()

    print(
        f"Reports saved to:\n"
        f"{OUTPUT_DIR}"
    )

    print("=" * 72)


# =============================================================
# MAIN PIPELINE
# =============================================================

def main():

    print("\n")
    print("=" * 72)

    print(
        "TALENTIQ AI RECRUITMENT ANALYTICS"
    )

    print(
        "FEATURE ENGINEERING ENGINE"
    )

    print("=" * 72)


    (
        candidates,
        jobs,
        applications,
        candidate_skills,
        job_skills,

    ) = load_core_data()


    (
        candidate_skill_sets,
        candidate_skill_names,

    ) = build_candidate_skill_sets(
        candidate_skills
    )


    (
        must_have_skill_sets,
        nice_to_have_skill_sets,
        all_job_skill_sets,

    ) = build_job_skill_sets(
        job_skills
    )


    features = engineer_application_features(

        candidates=candidates,

        jobs=jobs,

        applications=applications,

        candidate_skill_sets=
        candidate_skill_sets,

        must_have_skill_sets=
        must_have_skill_sets,

        nice_to_have_skill_sets=
        nice_to_have_skill_sets,

        all_job_skill_sets=
        all_job_skill_sets,
    )


    analyze_features(
        features
    )


    create_score_distribution(
        features
    )


    analyze_top_matches(
        features
    )


    save_feature_dataset(
        features
    )


    validation = validate_features(
        features
    )


    print_final_summary(
        features,
        validation
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()