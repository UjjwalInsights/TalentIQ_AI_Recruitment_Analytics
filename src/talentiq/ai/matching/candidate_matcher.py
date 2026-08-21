"""
================================================================
TALENTIQ AI RECRUITMENT ANALYTICS PLATFORM
File: candidate_matcher.py

Purpose
-------
Rank TalentIQ candidates against a selected job using an
explainable structured matching algorithm.

Matching Factors
----------------
1. Must-have skills
2. Nice-to-have skills
3. Candidate experience
4. Candidate/job location

Final Structured Score
----------------------
Skill Match      : 70%
Experience Match : 20%
Location Match   : 10%

Within skill matching:
Must-have        : 75%
Nice-to-have     : 25%

The skill weights automatically adjust if a job contains only
one skill-priority category.

Outputs
-------
outputs/predictions/candidate_matching/

The engine is designed so that it can later be reused by:
- Semantic Matching
- Resume Analyzer
- Streamlit
- RAG Hiring Assistant

================================================================
"""

from pathlib import Path
import sys
import argparse

import pandas as pd
from sqlalchemy import text


# =============================================================
# PROJECT PATH SETUP
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

# .../src
SRC_DIR = CURRENT_FILE.parents[3]

# Project root
PROJECT_ROOT = CURRENT_FILE.parents[4]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from database.connection import get_connection


# =============================================================
# CONFIGURATION
# =============================================================

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
    / "candidate_matching"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


SKILL_WEIGHT = 0.70
EXPERIENCE_WEIGHT = 0.20
LOCATION_WEIGHT = 0.10

MUST_HAVE_WEIGHT = 0.75
NICE_TO_HAVE_WEIGHT = 0.25


# =============================================================
# DATABASE HELPER
# =============================================================

def load_query(query, params=None):
    """
    Execute SQL and return a Pandas DataFrame.
    """

    with get_connection() as connection:

        return pd.read_sql_query(
            text(query),
            connection,
            params=params
        )


# =============================================================
# DISPLAY HELPER
# =============================================================

def print_section(title):

    print("\n")
    print("=" * 78)
    print(title)
    print("=" * 78)


# =============================================================
# LOAD JOB
# =============================================================

def load_job(job_id):
    """
    Load one job from PostgreSQL.
    """

    query = """
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
    FROM jobs
    WHERE job_id = :job_id;
    """

    job_df = load_query(
        query,
        params={
            "job_id": job_id
        }
    )

    if job_df.empty:
        return None

    return job_df.iloc[0]


# =============================================================
# LOAD CANDIDATES
# =============================================================

def load_candidates():
    """
    Load all candidates.

    The matcher intentionally evaluates ALL candidates,
    not only candidates who already applied.
    """

    query = """
    SELECT
        candidate_id,
        candidate_name,
        experience_years,
        location_id,
        work_authorization_id
    FROM candidates;
    """

    return load_query(query)


# =============================================================
# LOAD CANDIDATE SKILLS
# =============================================================

def load_candidate_skills():

    query = """
    SELECT
        cs.candidate_id,
        cs.skill_id,
        s.skill_name
    FROM candidate_skills cs

    JOIN skills s
        ON cs.skill_id = s.skill_id;
    """

    return load_query(query)


# =============================================================
# LOAD JOB SKILLS
# =============================================================

def load_job_skills(job_id):

    query = """
    SELECT
        js.job_id,
        js.skill_id,
        s.skill_name,
        js.priority
    FROM job_skills js

    JOIN skills s
        ON js.skill_id = s.skill_id

    WHERE js.job_id = :job_id;
    """

    return load_query(
        query,
        params={
            "job_id": job_id
        }
    )


# =============================================================
# LOAD EXISTING APPLICANTS
# =============================================================

def load_existing_applicants(job_id):
    """
    Return candidates who already applied to the selected job.

    This does NOT restrict matching.
    It simply lets the recruiter know whether a ranked
    candidate has already applied.
    """

    query = """
    SELECT DISTINCT
        candidate_id
    FROM applications
    WHERE job_id = :job_id;
    """

    df = load_query(
        query,
        params={
            "job_id": job_id
        }
    )

    return set(
        df["candidate_id"].tolist()
    )


# =============================================================
# BUILD CANDIDATE SKILL PROFILES
# =============================================================

def build_candidate_skill_profiles(
    candidate_skills
):

    skill_ids = (
        candidate_skills
        .groupby("candidate_id")["skill_id"]
        .apply(set)
        .to_dict()
    )

    skill_names = (
        candidate_skills
        .groupby("candidate_id")["skill_name"]
        .apply(
            lambda values:
            set(values)
        )
        .to_dict()
    )

    return skill_ids, skill_names


# =============================================================
# BUILD JOB SKILL PROFILE
# =============================================================

def build_job_skill_profile(
    job_skills
):

    must_have_df = job_skills[
        job_skills["priority"]
        .str.strip()
        .str.lower()
        .eq("must-have")
    ]

    nice_to_have_df = job_skills[
        job_skills["priority"]
        .str.strip()
        .str.lower()
        .eq("nice-to-have")
    ]


    profile = {

        "must_have_ids":
            set(
                must_have_df[
                    "skill_id"
                ].tolist()
            ),

        "nice_to_have_ids":
            set(
                nice_to_have_df[
                    "skill_id"
                ].tolist()
            ),

        "must_have_names":
            set(
                must_have_df[
                    "skill_name"
                ].tolist()
            ),

        "nice_to_have_names":
            set(
                nice_to_have_df[
                    "skill_name"
                ].tolist()
            ),
    }

    profile["all_ids"] = (
        profile["must_have_ids"]
        |
        profile["nice_to_have_ids"]
    )

    profile["all_names"] = (
        profile["must_have_names"]
        |
        profile["nice_to_have_names"]
    )

    return profile


# =============================================================
# BASIC MATCH FUNCTIONS
# =============================================================

def calculate_percentage_match(
    candidate_skills,
    required_skills
):
    """
    Calculate percentage of required skills
    possessed by candidate.

    Returns None when there are no skills in that category.
    """

    if not required_skills:
        return None

    matched = (
        candidate_skills
        &
        required_skills
    )

    return round(
        len(matched)
        /
        len(required_skills)
        *
        100,
        2
    )


# =============================================================
# SKILL SCORE
# =============================================================

def calculate_skill_score(
    must_have_score,
    nice_to_have_score
):
    """
    Calculate skill score while avoiding score inflation
    when a job does not contain one priority category.
    """

    if (
        must_have_score is not None
        and
        nice_to_have_score is not None
    ):

        return round(

            must_have_score
            * MUST_HAVE_WEIGHT

            +

            nice_to_have_score
            * NICE_TO_HAVE_WEIGHT,

            2
        )


    if must_have_score is not None:

        return round(
            must_have_score,
            2
        )


    if nice_to_have_score is not None:

        return round(
            nice_to_have_score,
            2
        )


    # Cannot evaluate skill compatibility
    # when a job has no skill requirements.
    return 0.0


# =============================================================
# EXPERIENCE SCORE
# =============================================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):
    """
    Return explainable 0-100 experience match score.
    """

    if pd.isna(required_experience):
        return 100.0

    if pd.isna(candidate_experience):
        return 0.0


    candidate_experience = float(
        candidate_experience
    )

    required_experience = float(
        required_experience
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
# LOCATION SCORE
# =============================================================

def calculate_location_score(
    candidate_location_id,
    job_location_id
):
    """
    Exact-location matching for MVP.

    Later this can be extended for:
    - Remote jobs
    - Hybrid jobs
    - Relocation preference
    - Geographic distance
    """

    if (
        pd.isna(candidate_location_id)
        or
        pd.isna(job_location_id)
    ):
        return 0.0


    if (
        candidate_location_id
        ==
        job_location_id
    ):
        return 100.0


    return 0.0


# =============================================================
# MATCH CATEGORY
# =============================================================

def get_match_category(score):

    if score >= 90:
        return "Excellent"

    if score >= 75:
        return "Strong"

    if score >= 60:
        return "Moderate"

    if score >= 40:
        return "Low"

    return "Very Low"


# =============================================================
# RECOMMENDATION
# =============================================================

def get_recommendation(
    score,
    must_have_score
):

    # Strong protection around genuine must-have skills.
    if (
        must_have_score is not None
        and
        must_have_score < 50
    ):

        if score >= 60:
            return "REVIEW - MUST-HAVE SKILL GAP"

        return "LOW PRIORITY"


    if score >= 90:
        return "HIGHLY RECOMMENDED"

    if score >= 75:
        return "RECOMMENDED"

    if score >= 60:
        return "REVIEW"

    if score >= 40:
        return "LOW PRIORITY"

    return "NOT RECOMMENDED"


# =============================================================
# SCORE ALL CANDIDATES
# =============================================================

def rank_candidates_for_job(
    job,
    candidates,
    candidate_skill_ids,
    candidate_skill_names,
    job_profile,
    existing_applicants
):
    """
    Score every candidate against one selected job.
    """

    results = []


    for candidate in candidates.itertuples(
        index=False
    ):

        candidate_id = (
            candidate.candidate_id
        )


        candidate_ids = (
            candidate_skill_ids.get(
                candidate_id,
                set()
            )
        )


        candidate_names = (
            candidate_skill_names.get(
                candidate_id,
                set()
            )
        )


        # -----------------------------------------------------
        # SKILL MATCHING
        # -----------------------------------------------------

        must_have_score = (
            calculate_percentage_match(
                candidate_ids,
                job_profile[
                    "must_have_ids"
                ]
            )
        )


        nice_to_have_score = (
            calculate_percentage_match(
                candidate_ids,
                job_profile[
                    "nice_to_have_ids"
                ]
            )
        )


        skill_score = (
            calculate_skill_score(
                must_have_score,
                nice_to_have_score
            )
        )


        # -----------------------------------------------------
        # MATCHED / MISSING SKILLS
        # -----------------------------------------------------

        matched_must_have = (
            candidate_names
            &
            job_profile[
                "must_have_names"
            ]
        )


        missing_must_have = (
            job_profile[
                "must_have_names"
            ]
            -
            candidate_names
        )


        matched_nice = (
            candidate_names
            &
            job_profile[
                "nice_to_have_names"
            ]
        )


        missing_nice = (
            job_profile[
                "nice_to_have_names"
            ]
            -
            candidate_names
        )


        # -----------------------------------------------------
        # EXPERIENCE
        # -----------------------------------------------------

        experience_score = (
            calculate_experience_score(
                candidate.experience_years,
                job.experience_required
            )
        )


        if (
            pd.notna(
                candidate.experience_years
            )
            and
            pd.notna(
                job.experience_required
            )
        ):

            experience_gap = round(
                float(
                    candidate.experience_years
                )
                -
                float(
                    job.experience_required
                ),
                2
            )

        else:

            experience_gap = None


        # -----------------------------------------------------
        # LOCATION
        # -----------------------------------------------------

        location_score = (
            calculate_location_score(
                candidate.location_id,
                job.location_id
            )
        )


        # -----------------------------------------------------
        # FINAL STRUCTURED SCORE
        # -----------------------------------------------------

        structured_score = round(

            skill_score
            * SKILL_WEIGHT

            +

            experience_score
            * EXPERIENCE_WEIGHT

            +

            location_score
            * LOCATION_WEIGHT,

            2
        )


        category = (
            get_match_category(
                structured_score
            )
        )


        recommendation = (
            get_recommendation(
                structured_score,
                must_have_score
            )
        )


        # -----------------------------------------------------
        # HAS ALREADY APPLIED?
        # -----------------------------------------------------

        has_applied = (
            candidate_id
            in
            existing_applicants
        )


        # -----------------------------------------------------
        # SAVE RESULT
        # -----------------------------------------------------

        results.append(
            {

                "candidate_id":
                    candidate_id,

                "candidate_name":
                    candidate.candidate_name,

                "candidate_experience":
                    candidate.experience_years,

                "required_experience":
                    job.experience_required,

                "experience_gap":
                    experience_gap,

                "candidate_location_id":
                    candidate.location_id,

                "job_location_id":
                    job.location_id,

                "must_have_match_rate":
                    (
                        must_have_score
                        if must_have_score
                        is not None
                        else 0.0
                    ),

                "nice_to_have_match_rate":
                    (
                        nice_to_have_score
                        if nice_to_have_score
                        is not None
                        else 0.0
                    ),

                "skill_match_score":
                    skill_score,

                "experience_match_score":
                    experience_score,

                "location_match_score":
                    location_score,

                "structured_match_score":
                    structured_score,

                "match_category":
                    category,

                "recommendation":
                    recommendation,

                "matched_must_have_skills":
                    ", ".join(
                        sorted(
                            matched_must_have
                        )
                    ),

                "missing_must_have_skills":
                    ", ".join(
                        sorted(
                            missing_must_have
                        )
                    ),

                "matched_nice_to_have_skills":
                    ", ".join(
                        sorted(
                            matched_nice
                        )
                    ),

                "missing_nice_to_have_skills":
                    ", ".join(
                        sorted(
                            missing_nice
                        )
                    ),

                "candidate_skills":
                    ", ".join(
                        sorted(
                            candidate_names
                        )
                    ),

                "has_already_applied":
                    has_applied,
            }
        )


    ranking = pd.DataFrame(
        results
    )


    ranking = (
        ranking
        .sort_values(
            by=[
                "structured_match_score",
                "skill_match_score",
                "experience_match_score",
            ],
            ascending=False
        )
        .reset_index(drop=True)
    )


    ranking.insert(
        0,
        "rank",
        range(
            1,
            len(ranking) + 1
        )
    )


    return ranking


# =============================================================
# JOB INFORMATION
# =============================================================

def print_job_summary(
    job,
    job_profile
):

    print_section(
        "SELECTED JOB"
    )


    print(
        f"Job ID              : "
        f"{job.job_id}"
    )

    print(
        f"Job Code            : "
        f"{job.job_code}"
    )

    print(
        f"Job Title           : "
        f"{job.job_title}"
    )

    print(
        f"Status              : "
        f"{job.job_status}"
    )

    print(
        f"Experience Required : "
        f"{job.experience_required} years"
    )

    print(
        f"Location ID         : "
        f"{job.location_id}"
    )

    print(
        f"Employment Type     : "
        f"{job.employment_type}"
    )

    print(
        f"Work Mode           : "
        f"{job.work_mode}"
    )


    print("\nMust-Have Skills:")

    if job_profile["must_have_names"]:

        for skill in sorted(
            job_profile[
                "must_have_names"
            ]
        ):
            print(
                f"  • {skill}"
            )

    else:
        print(
            "  None specified"
        )


    print("\nNice-to-Have Skills:")

    if job_profile[
        "nice_to_have_names"
    ]:

        for skill in sorted(
            job_profile[
                "nice_to_have_names"
            ]
        ):
            print(
                f"  • {skill}"
            )

    else:
        print(
            "  None specified"
        )


# =============================================================
# DISPLAY TOP CANDIDATES
# =============================================================

def display_top_candidates(
    ranking,
    top_n
):

    print_section(
        f"TOP {top_n} CANDIDATES"
    )


    display_columns = [

        "rank",

        "candidate_id",

        "candidate_name",

        "candidate_experience",

        "skill_match_score",

        "experience_match_score",

        "location_match_score",

        "structured_match_score",

        "match_category",

        "recommendation",

        "has_already_applied",
    ]


    print(
        ranking[
            display_columns
        ]
        .head(top_n)
        .to_string(
            index=False
        )
    )


# =============================================================
# EXPLAIN BEST MATCH
# =============================================================

def explain_top_candidate(
    ranking
):

    if ranking.empty:
        return


    candidate = ranking.iloc[0]


    print_section(
        "BEST CANDIDATE EXPLANATION"
    )


    print(
        f"Candidate       : "
        f"{candidate['candidate_name']}"
    )

    print(
        f"Candidate ID    : "
        f"{candidate['candidate_id']}"
    )

    print(
        f"Overall Score   : "
        f"{candidate['structured_match_score']:.2f}%"
    )

    print(
        f"Category        : "
        f"{candidate['match_category']}"
    )

    print(
        f"Recommendation  : "
        f"{candidate['recommendation']}"
    )


    print("\nScore Breakdown")

    print(
        f"Skill Match     : "
        f"{candidate['skill_match_score']:.2f}%"
    )

    print(
        f"Must-Have Match : "
        f"{candidate['must_have_match_rate']:.2f}%"
    )

    print(
        f"Nice-to-Have    : "
        f"{candidate['nice_to_have_match_rate']:.2f}%"
    )

    print(
        f"Experience      : "
        f"{candidate['experience_match_score']:.2f}%"
    )

    print(
        f"Location        : "
        f"{candidate['location_match_score']:.2f}%"
    )


    print("\nMatched Must-Have Skills")

    matched = (
        candidate[
            "matched_must_have_skills"
        ]
    )

    print(
        matched
        if matched
        else "None"
    )


    print("\nMissing Must-Have Skills")

    missing = (
        candidate[
            "missing_must_have_skills"
        ]
    )

    print(
        missing
        if missing
        else "None"
    )


    print("\nMatched Nice-to-Have Skills")

    matched_nice = (
        candidate[
            "matched_nice_to_have_skills"
        ]
    )

    print(
        matched_nice
        if matched_nice
        else "None"
    )


# =============================================================
# SAVE RESULTS
# =============================================================

def save_results(
    ranking,
    job
):

    safe_job_code = str(
        job.job_code
    ).replace(
        "/",
        "-"
    )


    full_file = (

        OUTPUT_DIR
        /
        f"{safe_job_code}_candidate_ranking.csv"
    )


    ranking.to_csv(
        full_file,
        index=False
    )


    top_file = (

        OUTPUT_DIR
        /
        f"{safe_job_code}_top_20_candidates.csv"
    )


    ranking.head(20).to_csv(
        top_file,
        index=False
    )


    return (
        full_file,
        top_file
    )


# =============================================================
# MATCHING SUMMARY
# =============================================================

def print_matching_summary(
    ranking,
    existing_applicants
):

    print_section(
        "MATCHING SUMMARY"
    )


    total = len(ranking)


    excellent = (
        ranking[
            "match_category"
        ]
        .eq("Excellent")
        .sum()
    )


    strong = (
        ranking[
            "match_category"
        ]
        .eq("Strong")
        .sum()
    )


    moderate = (
        ranking[
            "match_category"
        ]
        .eq("Moderate")
        .sum()
    )


    recommended = (
        ranking[
            "recommendation"
        ]
        .isin(
            [
                "HIGHLY RECOMMENDED",
                "RECOMMENDED"
            ]
        )
        .sum()
    )


    print(
        f"Candidates Evaluated    : "
        f"{total:,}"
    )

    print(
        f"Already Applied         : "
        f"{len(existing_applicants):,}"
    )

    print(
        f"Excellent Matches       : "
        f"{excellent:,}"
    )

    print(
        f"Strong Matches          : "
        f"{strong:,}"
    )

    print(
        f"Moderate Matches        : "
        f"{moderate:,}"
    )

    print(
        f"Recommended Candidates  : "
        f"{recommended:,}"
    )


    print(
        "Average Match Score     : "
        f"{ranking['structured_match_score'].mean():.2f}%"
    )


    print(
        "Highest Match Score     : "
        f"{ranking['structured_match_score'].max():.2f}%"
    )


# =============================================================
# SHOW AVAILABLE OPEN JOBS
# =============================================================

def show_open_jobs():

    print_section(
        "AVAILABLE OPEN JOBS"
    )


    query = """
    SELECT
        job_id,
        job_code,
        job_title,
        experience_required,
        work_mode
    FROM jobs
    WHERE LOWER(job_status) = 'open'
    ORDER BY job_id
    LIMIT 20;
    """


    jobs = load_query(
        query
    )


    print(
        jobs.to_string(
            index=False
        )
    )


    print(
        "\nShowing first 20 open jobs."
    )


# =============================================================
# MAIN MATCHING ENGINE
# =============================================================

def run_matcher(
    job_id,
    top_n=10
):

    print("\n")
    print("=" * 78)
    print(
        "TALENTIQ AI RECRUITMENT PLATFORM"
    )
    print(
        "CANDIDATE MATCHING ENGINE"
    )
    print("=" * 78)


    # ---------------------------------------------------------
    # JOB
    # ---------------------------------------------------------

    job = load_job(
        job_id
    )


    if job is None:

        print(
            f"\nERROR: Job ID "
            f"{job_id} was not found."
        )

        return None


    # ---------------------------------------------------------
    # JOB SKILLS
    # ---------------------------------------------------------

    job_skills = load_job_skills(
        job_id
    )


    job_profile = (
        build_job_skill_profile(
            job_skills
        )
    )


    print_job_summary(
        job,
        job_profile
    )


    # ---------------------------------------------------------
    # CANDIDATES
    # ---------------------------------------------------------

    print_section(
        "LOADING CANDIDATES"
    )


    candidates = (
        load_candidates()
    )


    candidate_skills = (
        load_candidate_skills()
    )


    (
        candidate_skill_ids,
        candidate_skill_names

    ) = (
        build_candidate_skill_profiles(
            candidate_skills
        )
    )


    existing_applicants = (
        load_existing_applicants(
            job_id
        )
    )


    print(
        f"Candidates loaded       : "
        f"{len(candidates):,}"
    )

    print(
        f"Skill profiles loaded   : "
        f"{len(candidate_skill_ids):,}"
    )

    print(
        f"Existing applicants     : "
        f"{len(existing_applicants):,}"
    )


    # ---------------------------------------------------------
    # MATCHING
    # ---------------------------------------------------------

    print_section(
        "SCORING ALL CANDIDATES"
    )


    ranking = (
        rank_candidates_for_job(

            job=job,

            candidates=candidates,

            candidate_skill_ids=
            candidate_skill_ids,

            candidate_skill_names=
            candidate_skill_names,

            job_profile=
            job_profile,

            existing_applicants=
            existing_applicants
        )
    )


    print(
        f"Candidates scored: "
        f"{len(ranking):,}"
    )


    # ---------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------

    display_top_candidates(
        ranking,
        top_n
    )


    explain_top_candidate(
        ranking
    )


    print_matching_summary(
        ranking,
        existing_applicants
    )


    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    (
        full_file,
        top_file

    ) = save_results(
        ranking,
        job
    )


    print_section(
        "OUTPUT FILES"
    )


    print(
        "Full Candidate Ranking:"
    )

    print(
        full_file
    )


    print(
        "\nTop 20 Candidates:"
    )

    print(
        top_file
    )


    print("\n")
    print("=" * 78)

    print(
        "CANDIDATE MATCHING COMPLETE"
    )

    print("=" * 78)


    return ranking


# =============================================================
# COMMAND LINE
# =============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "TalentIQ Candidate Matching Engine"
        )
    )


    parser.add_argument(

        "--job-id",

        type=int,

        help=(
            "Job ID to rank candidates against"
        ),
    )


    parser.add_argument(

        "--top-n",

        type=int,

        default=10,

        help=(
            "Number of top candidates to display"
        ),
    )


    args = parser.parse_args()


    job_id = args.job_id


    # ---------------------------------------------------------
    # Interactive mode
    # ---------------------------------------------------------

    if job_id is None:

        show_open_jobs()

        print()

        try:

            job_id = int(
                input(
                    "Enter Job ID: "
                )
            )

        except ValueError:

            print(
                "Invalid Job ID. "
                "Please enter a number."
            )

            return


    run_matcher(
        job_id=job_id,
        top_n=args.top_n
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()