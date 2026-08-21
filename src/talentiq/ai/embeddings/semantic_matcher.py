"""
================================================================
TALENTIQ AI RECRUITMENT PLATFORM
File: semantic_matcher.py

Purpose
-------
Add semantic AI matching to the existing structured
Candidate Matching Engine.

Candidate Matching V2 combines:

1. Structured Matching
   - Must-have skills
   - Nice-to-have skills
   - Experience
   - Location

2. Semantic Matching
   - Transformer embeddings
   - Candidate profile meaning
   - Job profile meaning
   - Cosine similarity

3. Hybrid TalentIQ Score

Hybrid Score
------------
Structured Score : 70%
Semantic Score   : 30%

Embedding Model
---------------
sentence-transformers/all-MiniLM-L6-v2

This is the MVP semantic layer.

Later, Resume Analyzer will replace the simple candidate profile
text with actual resume content, making semantic matching much
more powerful.

================================================================
"""

from pathlib import Path
import sys
import argparse
import time

import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer


# =============================================================
# PROJECT PATH SETUP
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

# .../src
SRC_DIR = CURRENT_FILE.parents[3]

# Project root
PROJECT_ROOT = CURRENT_FILE.parents[4]


if str(SRC_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(SRC_DIR)
    )


# =============================================================
# IMPORT STRUCTURED MATCHING ENGINE
# =============================================================

from talentiq.ai.matching.candidate_matcher import (

    load_job,

    load_candidates,

    load_candidate_skills,

    load_job_skills,

    load_existing_applicants,

    build_candidate_skill_profiles,

    build_job_skill_profile,

    rank_candidates_for_job,

    show_open_jobs,
)


# =============================================================
# CONFIGURATION
# =============================================================

MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


STRUCTURED_WEIGHT = 0.70

SEMANTIC_WEIGHT = 0.30


OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
    / "semantic_matching"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =============================================================
# PRINT HELPER
# =============================================================

def print_section(title):

    print("\n")

    print(
        "=" * 80
    )

    print(title)

    print(
        "=" * 80
    )


# =============================================================
# BUILD JOB SEMANTIC PROFILE
# =============================================================

def build_job_text(
    job,
    job_profile
):

    """
    Convert structured job information into natural-language
    text that can be converted into an embedding.
    """

    must_have_skills = ", ".join(
        sorted(
            job_profile[
                "must_have_names"
            ]
        )
    )


    nice_to_have_skills = ", ".join(
        sorted(
            job_profile[
                "nice_to_have_names"
            ]
        )
    )


    if not must_have_skills:
        must_have_skills = "None specified"


    if not nice_to_have_skills:
        nice_to_have_skills = "None specified"


    job_text = f"""
    Job title: {job.job_title}.

    Must-have technical skills:
    {must_have_skills}.

    Nice-to-have technical skills:
    {nice_to_have_skills}.

    Required professional experience:
    {job.experience_required} years.

    Employment type:
    {job.employment_type}.

    Work mode:
    {job.work_mode}.

    The ideal candidate should have professional experience
    relevant to the job title and required technical skills.
    """


    # Remove unnecessary whitespace
    job_text = " ".join(
        job_text.split()
    )


    return job_text


# =============================================================
# BUILD CANDIDATE SEMANTIC PROFILE
# =============================================================

def build_candidate_text(
    candidate_id,
    candidate_experience,
    candidate_skill_names
):

    """
    Convert candidate structured data into natural-language
    profile text for semantic embedding.

    Candidate name is deliberately excluded because a person's
    name should not influence semantic job compatibility.
    """

    skills = candidate_skill_names.get(
        candidate_id,
        set()
    )


    skills_text = ", ".join(
        sorted(skills)
    )


    if not skills_text:
        skills_text = "No skills listed"


    if pd.isna(
        candidate_experience
    ):

        experience_text = (
            "Experience information unavailable"
        )

    else:

        experience_text = (
            f"{candidate_experience} years "
            f"of professional experience"
        )


    candidate_text = f"""
    Professional candidate profile.

    Technical and professional skills:
    {skills_text}.

    Professional experience:
    {experience_text}.

    The candidate has experience working with the listed
    technologies and professional skills.
    """


    candidate_text = " ".join(
        candidate_text.split()
    )


    return candidate_text


# =============================================================
# BUILD ALL CANDIDATE TEXTS
# =============================================================

def build_candidate_texts(
    ranking,
    candidate_skill_names
):

    candidate_texts = []


    for row in ranking.itertuples(
        index=False
    ):

        candidate_text = (
            build_candidate_text(

                candidate_id=
                row.candidate_id,

                candidate_experience=
                row.candidate_experience,

                candidate_skill_names=
                candidate_skill_names,
            )
        )


        candidate_texts.append(
            candidate_text
        )


    return candidate_texts


# =============================================================
# LOAD EMBEDDING MODEL
# =============================================================

def load_embedding_model():

    print_section(
        "LOADING EMBEDDING MODEL"
    )


    print(
        f"Model: {MODEL_NAME}"
    )


    print(
        "\nLoading model..."
    )


    model = SentenceTransformer(
        MODEL_NAME
    )


    print(
        "Embedding model loaded successfully."
    )


    return model


# =============================================================
# GENERATE SEMANTIC SCORES
# =============================================================

def calculate_semantic_scores(
    model,
    job_text,
    candidate_texts
):

    print_section(
        "GENERATING SEMANTIC EMBEDDINGS"
    )


    print(
        "Encoding selected job..."
    )


    job_embedding = model.encode(

        [job_text],

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=False,
    )


    print(
        f"Encoding {len(candidate_texts):,} "
        f"candidate profiles..."
    )


    candidate_embeddings = model.encode(

        candidate_texts,

        batch_size=64,

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=True,
    )


    # ---------------------------------------------------------
    # COSINE SIMILARITY
    #
    # Because embeddings are normalized, their dot product
    # equals cosine similarity.
    # ---------------------------------------------------------

    cosine_similarities = (
        candidate_embeddings
        @
        job_embedding[0]
    )


    # ---------------------------------------------------------
    # Convert similarity to 0-100 semantic score.
    #
    # Negative similarities are treated as zero relevance.
    # ---------------------------------------------------------

    semantic_scores = (

        np.clip(
            cosine_similarities,
            0,
            1
        )

        *

        100

    )


    return (
        cosine_similarities,
        semantic_scores
    )


# =============================================================
# MATCH CATEGORY
# =============================================================

def get_hybrid_category(
    score
):

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
# HYBRID RECOMMENDATION
# =============================================================

def get_hybrid_recommendation(
    hybrid_score,
    must_have_match_rate,
    job_has_must_have_skills
):

    """
    Recruitment decision layer.

    Must-have skills act as a qualification gate.

    Semantic similarity can identify related experience,
    but it should not silently override missing mandatory
    technical requirements.
    """

    if (
        job_has_must_have_skills
        and
        must_have_match_rate < 100
    ):

        if hybrid_score >= 60:

            return (
                "REVIEW - MUST-HAVE SKILL GAP"
            )

        return "LOW PRIORITY"


    if hybrid_score >= 90:

        return "HIGHLY RECOMMENDED"


    if hybrid_score >= 75:

        return "RECOMMENDED"


    if hybrid_score >= 60:

        return "REVIEW"


    if hybrid_score >= 40:

        return "LOW PRIORITY"


    return "NOT RECOMMENDED"


# =============================================================
# CREATE HYBRID SCORES
# =============================================================

def create_hybrid_ranking(
    structured_ranking,
    cosine_similarities,
    semantic_scores,
    job_profile
):

    print_section(
        "CALCULATING TALENTIQ HYBRID SCORES"
    )


    ranking = (
        structured_ranking.copy()
    )


    # ---------------------------------------------------------
    # RAW COSINE SIMILARITY
    # ---------------------------------------------------------

    ranking[
        "semantic_similarity"
    ] = np.round(
        cosine_similarities,
        4
    )


    # ---------------------------------------------------------
    # SEMANTIC SCORE
    # ---------------------------------------------------------

    ranking[
        "semantic_match_score"
    ] = np.round(
        semantic_scores,
        2
    )


    # ---------------------------------------------------------
    # HYBRID SCORE
    #
    # 70% Structured
    # 30% Semantic
    # ---------------------------------------------------------

    ranking[
        "hybrid_match_score"
    ] = (

        ranking[
            "structured_match_score"
        ]

        *

        STRUCTURED_WEIGHT

        +

        ranking[
            "semantic_match_score"
        ]

        *

        SEMANTIC_WEIGHT

    ).round(2)


    # ---------------------------------------------------------
    # MUST-HAVE COMPLETION
    # ---------------------------------------------------------

    job_has_must_have_skills = (
        len(
            job_profile[
                "must_have_ids"
            ]
        )
        >
        0
    )


    if job_has_must_have_skills:

        ranking[
            "must_have_complete"
        ] = (

            ranking[
                "must_have_match_rate"
            ]

            >=

            100
        )

    else:

        ranking[
            "must_have_complete"
        ] = True


    # ---------------------------------------------------------
    # CATEGORY
    # ---------------------------------------------------------

    ranking[
        "hybrid_match_category"
    ] = (

        ranking[
            "hybrid_match_score"
        ]

        .apply(
            get_hybrid_category
        )
    )


    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    ranking[
        "hybrid_recommendation"
    ] = ranking.apply(

        lambda row:

        get_hybrid_recommendation(

            hybrid_score=
            row[
                "hybrid_match_score"
            ],

            must_have_match_rate=
            row[
                "must_have_match_rate"
            ],

            job_has_must_have_skills=
            job_has_must_have_skills,
        ),

        axis=1
    )


    # ---------------------------------------------------------
    # FINAL RANKING
    #
    # Candidates satisfying all must-have requirements receive
    # priority. Within that group, hybrid score determines rank.
    # ---------------------------------------------------------

    ranking = (

        ranking

        .sort_values(

            by=[
                "must_have_complete",
                "hybrid_match_score",
                "semantic_match_score",
                "structured_match_score",
            ],

            ascending=[
                False,
                False,
                False,
                False,
            ]
        )

        .reset_index(
            drop=True
        )
    )


    # Remove old structured rank
    if "rank" in ranking.columns:

        ranking = ranking.drop(
            columns=[
                "rank"
            ]
        )


    ranking.insert(

        0,

        "hybrid_rank",

        range(
            1,
            len(ranking) + 1
        )
    )


    return ranking


# =============================================================
# DISPLAY JOB
# =============================================================

def display_job(
    job,
    job_profile,
    job_text
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


    must_have = ", ".join(
        sorted(
            job_profile[
                "must_have_names"
            ]
        )
    )


    nice_to_have = ", ".join(
        sorted(
            job_profile[
                "nice_to_have_names"
            ]
        )
    )


    print(
        f"Must-Have Skills     : "
        f"{must_have if must_have else 'None'}"
    )


    print(
        f"Nice-to-Have Skills  : "
        f"{nice_to_have if nice_to_have else 'None'}"
    )


    print(
        "\nSemantic Job Profile:"
    )


    print(
        job_text
    )


# =============================================================
# DISPLAY TOP CANDIDATES
# =============================================================

def display_top_candidates(
    ranking,
    top_n
):

    print_section(
        f"TOP {top_n} HYBRID CANDIDATE MATCHES"
    )


    columns = [

        "hybrid_rank",

        "candidate_id",

        "candidate_name",

        "candidate_experience",

        "must_have_match_rate",

        "skill_match_score",

        "experience_match_score",

        "location_match_score",

        "structured_match_score",

        "semantic_match_score",

        "hybrid_match_score",

        "hybrid_match_category",

        "hybrid_recommendation",

        "has_already_applied",
    ]


    print(

        ranking[
            columns
        ]

        .head(
            top_n
        )

        .to_string(
            index=False
        )
    )


# =============================================================
# EXPLAIN BEST CANDIDATE
# =============================================================

def explain_best_candidate(
    ranking
):

    if ranking.empty:
        return


    candidate = (
        ranking.iloc[0]
    )


    print_section(
        "BEST HYBRID MATCH EXPLANATION"
    )


    print(
        f"Candidate            : "
        f"{candidate['candidate_name']}"
    )


    print(
        f"Candidate ID         : "
        f"{candidate['candidate_id']}"
    )


    print(
        f"Hybrid Rank          : "
        f"{candidate['hybrid_rank']}"
    )


    print(
        f"Hybrid Score         : "
        f"{candidate['hybrid_match_score']:.2f}%"
    )


    print(
        f"Category             : "
        f"{candidate['hybrid_match_category']}"
    )


    print(
        f"Recommendation       : "
        f"{candidate['hybrid_recommendation']}"
    )


    print(
        f"Already Applied      : "
        f"{candidate['has_already_applied']}"
    )


    print("\nScore Breakdown")


    print(
        f"Structured Score     : "
        f"{candidate['structured_match_score']:.2f}%"
    )


    print(
        f"Semantic Score       : "
        f"{candidate['semantic_match_score']:.2f}%"
    )


    print(
        f"Skill Match          : "
        f"{candidate['skill_match_score']:.2f}%"
    )


    print(
        f"Must-Have Match      : "
        f"{candidate['must_have_match_rate']:.2f}%"
    )


    print(
        f"Experience Match     : "
        f"{candidate['experience_match_score']:.2f}%"
    )


    print(
        f"Location Match       : "
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


    print("\nCandidate Skills")


    print(
        candidate[
            "candidate_skills"
        ]
    )


# =============================================================
# MATCHING SUMMARY
# =============================================================

def print_matching_summary(
    ranking
):

    print_section(
        "HYBRID MATCHING SUMMARY"
    )


    total = len(
        ranking
    )


    excellent = (

        ranking[
            "hybrid_match_category"
        ]

        .eq(
            "Excellent"
        )

        .sum()
    )


    strong = (

        ranking[
            "hybrid_match_category"
        ]

        .eq(
            "Strong"
        )

        .sum()
    )


    moderate = (

        ranking[
            "hybrid_match_category"
        ]

        .eq(
            "Moderate"
        )

        .sum()
    )


    full_must_have = (

        ranking[
            "must_have_complete"
        ]

        .sum()
    )


    recommended = (

        ranking[
            "hybrid_recommendation"
        ]

        .isin(
            [
                "HIGHLY RECOMMENDED",
                "RECOMMENDED",
            ]
        )

        .sum()
    )


    print(
        f"Candidates Evaluated       : "
        f"{total:,}"
    )


    print(
        f"Full Must-Have Match       : "
        f"{full_must_have:,}"
    )


    print(
        f"Excellent Hybrid Matches   : "
        f"{excellent:,}"
    )


    print(
        f"Strong Hybrid Matches      : "
        f"{strong:,}"
    )


    print(
        f"Moderate Hybrid Matches    : "
        f"{moderate:,}"
    )


    print(
        f"Recommended Candidates     : "
        f"{recommended:,}"
    )


    print(
        "Average Structured Score  : "
        f"{ranking['structured_match_score'].mean():.2f}%"
    )


    print(
        "Average Semantic Score    : "
        f"{ranking['semantic_match_score'].mean():.2f}%"
    )


    print(
        "Average Hybrid Score      : "
        f"{ranking['hybrid_match_score'].mean():.2f}%"
    )


    print(
        "Highest Hybrid Score      : "
        f"{ranking['hybrid_match_score'].max():.2f}%"
    )


# =============================================================
# VALIDATE RESULTS
# =============================================================

def validate_results(
    ranking,
    expected_candidate_count
):

    print_section(
        "SEMANTIC MATCHING VALIDATION"
    )


    checks = []


    # ---------------------------------------------------------
    # Candidate count
    # ---------------------------------------------------------

    candidate_count_valid = (
        len(ranking)
        ==
        expected_candidate_count
    )


    checks.append(
        {
            "check":
                "All candidates ranked",

            "value":
                len(ranking),

            "status":
                (
                    "PASS"
                    if candidate_count_valid
                    else "FAIL"
                ),
        }
    )


    # ---------------------------------------------------------
    # Structured score validity
    # ---------------------------------------------------------

    invalid_structured = (

        (
            ranking[
                "structured_match_score"
            ] < 0
        )

        |

        (
            ranking[
                "structured_match_score"
            ] > 100
        )

    ).sum()


    checks.append(
        {
            "check":
                "Invalid structured scores",

            "value":
                invalid_structured,

            "status":
                (
                    "PASS"
                    if invalid_structured == 0
                    else "FAIL"
                ),
        }
    )


    # ---------------------------------------------------------
    # Semantic score validity
    # ---------------------------------------------------------

    invalid_semantic = (

        (
            ranking[
                "semantic_match_score"
            ] < 0
        )

        |

        (
            ranking[
                "semantic_match_score"
            ] > 100
        )

    ).sum()


    checks.append(
        {
            "check":
                "Invalid semantic scores",

            "value":
                invalid_semantic,

            "status":
                (
                    "PASS"
                    if invalid_semantic == 0
                    else "FAIL"
                ),
        }
    )


    # ---------------------------------------------------------
    # Hybrid score validity
    # ---------------------------------------------------------

    invalid_hybrid = (

        (
            ranking[
                "hybrid_match_score"
            ] < 0
        )

        |

        (
            ranking[
                "hybrid_match_score"
            ] > 100
        )

    ).sum()


    checks.append(
        {
            "check":
                "Invalid hybrid scores",

            "value":
                invalid_hybrid,

            "status":
                (
                    "PASS"
                    if invalid_hybrid == 0
                    else "FAIL"
                ),
        }
    )


    # ---------------------------------------------------------
    # Candidate duplicates
    # ---------------------------------------------------------

    duplicate_candidates = (

        ranking[
            "candidate_id"
        ]

        .duplicated()

        .sum()
    )


    checks.append(
        {
            "check":
                "Duplicate candidate rankings",

            "value":
                duplicate_candidates,

            "status":
                (
                    "PASS"
                    if duplicate_candidates == 0
                    else "FAIL"
                ),
        }
    )


    validation = (
        pd.DataFrame(
            checks
        )
    )


    print(
        validation.to_string(
            index=False
        )
    )


    return validation


# =============================================================
# SAVE OUTPUTS
# =============================================================

def save_results(
    ranking,
    validation,
    job
):

    print_section(
        "SAVING SEMANTIC MATCHING RESULTS"
    )


    safe_job_code = str(
        job.job_code
    ).replace(
        "/",
        "-"
    )


    full_file = (

        OUTPUT_DIR
        /
        f"{safe_job_code}_hybrid_ranking.csv"
    )


    top_file = (

        OUTPUT_DIR
        /
        f"{safe_job_code}_top_20_hybrid.csv"
    )


    validation_file = (

        OUTPUT_DIR
        /
        f"{safe_job_code}_validation.csv"
    )


    ranking.to_csv(
        full_file,
        index=False
    )


    ranking.head(
        20
    ).to_csv(
        top_file,
        index=False
    )


    validation.to_csv(
        validation_file,
        index=False
    )


    print(
        f"Full Hybrid Ranking:\n"
        f"{full_file}"
    )


    print(
        f"\nTop 20 Hybrid Candidates:\n"
        f"{top_file}"
    )


    print(
        f"\nValidation Report:\n"
        f"{validation_file}"
    )


# =============================================================
# MAIN SEMANTIC MATCHER
# =============================================================

def run_semantic_matcher(
    job_id,
    top_n=10
):

    start_time = (
        time.time()
    )


    print("\n")

    print(
        "=" * 80
    )

    print(
        "TALENTIQ AI RECRUITMENT PLATFORM"
    )

    print(
        "SEMANTIC + HYBRID CANDIDATE MATCHING ENGINE"
    )

    print(
        "=" * 80
    )


    # =========================================================
    # 1. LOAD JOB
    # =========================================================

    job = load_job(
        job_id
    )


    if job is None:

        print(
            f"\nERROR: Job ID "
            f"{job_id} does not exist."
        )

        return None


    job_skills = (
        load_job_skills(
            job_id
        )
    )


    job_profile = (
        build_job_skill_profile(
            job_skills
        )
    )


    job_text = (
        build_job_text(
            job,
            job_profile
        )
    )


    display_job(
        job,
        job_profile,
        job_text
    )


    # =========================================================
    # 2. LOAD CANDIDATES
    # =========================================================

    print_section(
        "LOADING TALENTIQ CANDIDATES"
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
        f"Candidates            : "
        f"{len(candidates):,}"
    )


    print(
        f"Candidate skill sets  : "
        f"{len(candidate_skill_ids):,}"
    )


    print(
        f"Existing applicants   : "
        f"{len(existing_applicants):,}"
    )


    # =========================================================
    # 3. STRUCTURED MATCHING
    # =========================================================

    print_section(
        "RUNNING STRUCTURED MATCHING"
    )


    structured_ranking = (
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
                existing_applicants,
        )
    )


    print(
        f"Structured candidates scored: "
        f"{len(structured_ranking):,}"
    )


    # =========================================================
    # 4. CREATE SEMANTIC TEXT
    # =========================================================

    print_section(
        "BUILDING SEMANTIC PROFILES"
    )


    candidate_texts = (
        build_candidate_texts(

            ranking=
                structured_ranking,

            candidate_skill_names=
                candidate_skill_names,
        )
    )


    print(
        f"Candidate semantic profiles: "
        f"{len(candidate_texts):,}"
    )


    # =========================================================
    # 5. LOAD EMBEDDING MODEL
    # =========================================================

    model = (
        load_embedding_model()
    )


    # =========================================================
    # 6. EMBEDDINGS + SIMILARITY
    # =========================================================

    (
        cosine_similarities,
        semantic_scores

    ) = (

        calculate_semantic_scores(

            model=
                model,

            job_text=
                job_text,

            candidate_texts=
                candidate_texts,
        )
    )


    # =========================================================
    # 7. HYBRID RANKING
    # =========================================================

    hybrid_ranking = (
        create_hybrid_ranking(

            structured_ranking=
                structured_ranking,

            cosine_similarities=
                cosine_similarities,

            semantic_scores=
                semantic_scores,

            job_profile=
                job_profile,
        )
    )


    # =========================================================
    # 8. DISPLAY
    # =========================================================

    display_top_candidates(
        hybrid_ranking,
        top_n
    )


    explain_best_candidate(
        hybrid_ranking
    )


    print_matching_summary(
        hybrid_ranking
    )


    # =========================================================
    # 9. VALIDATION
    # =========================================================

    validation = (
        validate_results(

            ranking=
                hybrid_ranking,

            expected_candidate_count=
                len(candidates),
        )
    )


    # =========================================================
    # 10. SAVE
    # =========================================================

    save_results(

        ranking=
            hybrid_ranking,

        validation=
            validation,

        job=
            job,
    )


    # =========================================================
    # FINAL
    # =========================================================

    elapsed_time = (
        time.time()
        -
        start_time
    )


    failed_checks = (

        validation[
            "status"
        ]

        .ne(
            "PASS"
        )

        .sum()
    )


    print("\n")

    print(
        "=" * 80
    )

    print(
        "TALENTIQ SEMANTIC MATCHING COMPLETE"
    )

    print(
        "=" * 80
    )


    print(
        f"Candidates Evaluated : "
        f"{len(hybrid_ranking):,}"
    )


    print(
        f"Validation Failures  : "
        f"{failed_checks}"
    )


    print(
        f"Processing Time      : "
        f"{elapsed_time:.2f} seconds"
    )


    if failed_checks == 0:

        print(
            "STATUS               : PASS"
        )

    else:

        print(
            "STATUS               : REVIEW REQUIRED"
        )


    print(
        "=" * 80
    )


    return hybrid_ranking


# =============================================================
# COMMAND LINE
# =============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "TalentIQ Semantic + Hybrid "
            "Candidate Matching Engine"
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
            "Number of candidates to display"
        ),
    )


    args = (
        parser.parse_args()
    )


    job_id = (
        args.job_id
    )


    # ---------------------------------------------------------
    # INTERACTIVE MODE
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


    run_semantic_matcher(

        job_id=
            job_id,

        top_n=
            args.top_n,
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":

    main()