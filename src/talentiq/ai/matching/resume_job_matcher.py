"""
================================================================
TALENTIQ AI RECRUITMENT PLATFORM
File: resume_job_matcher.py

Purpose
-------
Match an uploaded resume against jobs in the TalentIQ database.

Pipeline
--------
PDF / TXT Resume
      ↓
Resume Text Extraction
      ↓
Structured Resume Profile
      ↓
Skill + Experience Matching
      ↓
Resume Semantic Embedding
      ↓
Job Semantic Embeddings
      ↓
Hybrid Match Score
      ↓
Rank Best Jobs
      ↓
Explain Recommendation

Structured Score
----------------
Skills      : 80%
Experience  : 20%

Within Skills
-------------
Must-Have    : 75%
Nice-to-Have : 25%

Hybrid Score
------------
Structured Score : 60%
Semantic Score   : 40%

Open jobs are ranked by default.

Use --all-jobs to rank all jobs.

================================================================
"""

from pathlib import Path
import sys
import argparse
import json
import re
import time

import numpy as np
import pandas as pd

from sqlalchemy import text
from sentence_transformers import SentenceTransformer


# =============================================================
# PROJECT PATH SETUP
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

SRC_DIR = CURRENT_FILE.parents[3]

PROJECT_ROOT = CURRENT_FILE.parents[4]


if str(SRC_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(SRC_DIR)
    )


# =============================================================
# IMPORT TALENTIQ COMPONENTS
# =============================================================

from database.connection import get_connection


from talentiq.ai.resume.resume_analyzer import (

    extract_resume_text,

    clean_resume_text,

    load_known_skills,

    load_known_job_titles,

    build_resume_profile,

    RESUME_DIR,
)


# =============================================================
# CONFIGURATION
# =============================================================

MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


SKILL_WEIGHT = 0.80

EXPERIENCE_WEIGHT = 0.20


MUST_HAVE_WEIGHT = 0.75

NICE_TO_HAVE_WEIGHT = 0.25


STRUCTURED_WEIGHT = 0.60

SEMANTIC_WEIGHT = 0.40


OUTPUT_DIR = (

    PROJECT_ROOT

    / "outputs"

    / "predictions"

    / "resume_job_matching"
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =============================================================
# HELPERS
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


def load_dataframe(
    query,
    params=None
):

    with get_connection() as connection:

        return pd.read_sql_query(

            text(query),

            connection,

            params=params
        )


# =============================================================
# LOAD JOBS
# =============================================================

def load_jobs(
    all_jobs=False
):

    if all_jobs:

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
        ORDER BY job_id;
        """

    else:

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
        WHERE LOWER(job_status) = 'open'
        ORDER BY job_id;
        """


    return load_dataframe(
        query
    )


# =============================================================
# LOAD ALL JOB SKILLS
# =============================================================

def load_all_job_skills():

    query = """
    SELECT
        js.job_id,
        js.skill_id,
        s.skill_name,
        js.priority
    FROM job_skills js

    JOIN skills s
        ON js.skill_id = s.skill_id

    ORDER BY js.job_id;
    """


    return load_dataframe(
        query
    )


# =============================================================
# BUILD JOB SKILL PROFILES
# =============================================================

def build_job_skill_profiles(
    job_skills
):

    profiles = {}


    for job_id, group in job_skills.groupby(
        "job_id"
    ):

        must_have = group[

            group[
                "priority"
            ]

            .str.strip()

            .str.lower()

            .eq(
                "must-have"
            )
        ]


        nice_to_have = group[

            group[
                "priority"
            ]

            .str.strip()

            .str.lower()

            .eq(
                "nice-to-have"
            )
        ]


        profiles[job_id] = {

            "must_have":
                set(
                    must_have[
                        "skill_name"
                    ].tolist()
                ),

            "nice_to_have":
                set(
                    nice_to_have[
                        "skill_name"
                    ].tolist()
                ),
        }


        profiles[job_id][
            "all_skills"
        ] = (

            profiles[
                job_id
            ][
                "must_have"
            ]

            |

            profiles[
                job_id
            ][
                "nice_to_have"
            ]
        )


    return profiles


# =============================================================
# SKILL MATCH RATE
# =============================================================

def calculate_skill_match(
    resume_skills,
    required_skills
):

    if not required_skills:

        return None


    matched = (

        resume_skills

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
# WEIGHTED SKILL SCORE
# =============================================================

def calculate_weighted_skill_score(
    must_have_score,
    nice_to_have_score
):

    if (
        must_have_score is not None
        and
        nice_to_have_score is not None
    ):

        return round(

            must_have_score
            *
            MUST_HAVE_WEIGHT

            +

            nice_to_have_score
            *
            NICE_TO_HAVE_WEIGHT,

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


    return None


# =============================================================
# EXPERIENCE SCORE
# =============================================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):

    if pd.isna(
        required_experience
    ):

        return 100.0


    if (
        candidate_experience is None
        or
        pd.isna(candidate_experience)
    ):

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
        >=
        required_experience
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
# STRUCTURED SCORE
# =============================================================

def calculate_structured_score(
    skill_score,
    experience_score
):

    # If job has no skill requirements,
    # use experience alone.

    if skill_score is None:

        return round(
            experience_score,
            2
        )


    return round(

        skill_score
        *
        SKILL_WEIGHT

        +

        experience_score
        *
        EXPERIENCE_WEIGHT,

        2
    )


# =============================================================
# BUILD JOB TEXT FOR EMBEDDINGS
# =============================================================

def build_job_text(
    job,
    profile
):

    must_have = ", ".join(

        sorted(
            profile[
                "must_have"
            ]
        )
    )


    nice_to_have = ", ".join(

        sorted(
            profile[
                "nice_to_have"
            ]
        )
    )


    if not must_have:

        must_have = (
            "None specified"
        )


    if not nice_to_have:

        nice_to_have = (
            "None specified"
        )


    job_text = f"""
    Job title: {job.job_title}.

    Required professional experience:
    {job.experience_required} years.

    Must-have skills:
    {must_have}.

    Nice-to-have skills:
    {nice_to_have}.

    Employment type:
    {job.employment_type}.

    Work mode:
    {job.work_mode}.

    The ideal candidate should have professional experience
    relevant to this role and the listed technologies.
    """


    return " ".join(
        job_text.split()
    )


# =============================================================
# RESUME CHUNKING
# =============================================================

def chunk_resume_text(
    resume_text,
    words_per_chunk=180
):

    """
    Split a long resume into smaller semantic chunks.

    This avoids relying only on the beginning of a long resume
    when the embedding model has a limited context length.
    """

    words = (
        resume_text.split()
    )


    chunks = []


    for start in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk = " ".join(

            words[
                start:
                start + words_per_chunk
            ]
        )


        if chunk.strip():

            chunks.append(
                chunk
            )


    return chunks


# =============================================================
# EMBEDDING MODEL
# =============================================================

def load_embedding_model():

    print_section(
        "LOADING EMBEDDING MODEL"
    )


    print(
        f"Model: {MODEL_NAME}"
    )


    model = SentenceTransformer(
        MODEL_NAME
    )


    print(
        "Embedding model loaded successfully."
    )


    return model


# =============================================================
# RESUME EMBEDDING
# =============================================================

def create_resume_embedding(
    model,
    resume_text
):

    print_section(
        "CREATING RESUME EMBEDDING"
    )


    chunks = chunk_resume_text(
        resume_text
    )


    print(
        f"Resume chunks created : "
        f"{len(chunks):,}"
    )


    embeddings = model.encode(

        chunks,

        batch_size=32,

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=False,
    )


    # Average resume chunks
    resume_embedding = (
        embeddings.mean(
            axis=0
        )
    )


    # Normalize averaged vector
    norm = np.linalg.norm(
        resume_embedding
    )


    if norm > 0:

        resume_embedding = (
            resume_embedding
            /
            norm
        )


    print(
        "Resume embedding created."
    )


    return resume_embedding


# =============================================================
# JOB EMBEDDINGS
# =============================================================

def create_job_embeddings(
    model,
    job_texts
):

    print_section(
        "CREATING JOB EMBEDDINGS"
    )


    print(
        f"Encoding {len(job_texts):,} "
        f"jobs..."
    )


    embeddings = model.encode(

        job_texts,

        batch_size=64,

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=True,
    )


    return embeddings


# =============================================================
# MATCH CATEGORY
# =============================================================

def get_match_category(
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
# RECOMMENDATION
# =============================================================

def get_recommendation(
    hybrid_score,
    must_have_score,
    has_must_have
):

    # Mandatory technical requirements
    # remain a hard review signal.

    if (
        has_must_have
        and
        must_have_score < 100
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
# SCORE ALL JOBS
# =============================================================

def score_jobs(
    jobs,
    job_profiles,
    resume_profile
):

    print_section(
        "RUNNING STRUCTURED RESUME-JOB MATCHING"
    )


    resume_skills = set(

        resume_profile[
            "skills"
        ]
    )


    candidate_experience = (

        resume_profile[
            "estimated_experience_years"
        ]
    )


    results = []


    for job in jobs.itertuples(
        index=False
    ):

        profile = job_profiles.get(

            job.job_id,

            {
                "must_have": set(),
                "nice_to_have": set(),
                "all_skills": set(),
            }
        )


        must_have = profile[
            "must_have"
        ]


        nice_to_have = profile[
            "nice_to_have"
        ]


        # -----------------------------------------------------
        # MUST HAVE
        # -----------------------------------------------------

        must_have_score = (
            calculate_skill_match(

                resume_skills,

                must_have
            )
        )


        # -----------------------------------------------------
        # NICE TO HAVE
        # -----------------------------------------------------

        nice_to_have_score = (
            calculate_skill_match(

                resume_skills,

                nice_to_have
            )
        )


        # -----------------------------------------------------
        # SKILL SCORE
        # -----------------------------------------------------

        skill_score = (
            calculate_weighted_skill_score(

                must_have_score,

                nice_to_have_score
            )
        )


        # -----------------------------------------------------
        # EXPERIENCE
        # -----------------------------------------------------

        experience_score = (
            calculate_experience_score(

                candidate_experience,

                job.experience_required
            )
        )


        # -----------------------------------------------------
        # STRUCTURED SCORE
        # -----------------------------------------------------

        structured_score = (
            calculate_structured_score(

                skill_score,

                experience_score
            )
        )


        # -----------------------------------------------------
        # EXPLANATION
        # -----------------------------------------------------

        matched_must_have = (

            resume_skills

            &

            must_have
        )


        missing_must_have = (

            must_have

            -

            resume_skills
        )


        matched_nice = (

            resume_skills

            &

            nice_to_have
        )


        missing_nice = (

            nice_to_have

            -

            resume_skills
        )


        has_must_have = (
            len(must_have) > 0
        )


        must_have_complete = (

            True

            if not has_must_have

            else must_have_score == 100
        )


        results.append(
            {

                "job_id":
                    job.job_id,

                "job_code":
                    job.job_code,

                "job_title":
                    job.job_title,

                "job_status":
                    job.job_status,

                "experience_required":
                    job.experience_required,

                "candidate_experience":
                    candidate_experience,

                "employment_type":
                    job.employment_type,

                "work_mode":
                    job.work_mode,

                "min_salary":
                    job.min_salary,

                "max_salary":
                    job.max_salary,

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
                    (
                        skill_score
                        if skill_score
                        is not None
                        else 0.0
                    ),

                "experience_match_score":
                    experience_score,

                "structured_match_score":
                    structured_score,

                "must_have_complete":
                    must_have_complete,

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

                "job_text":
                    build_job_text(
                        job,
                        profile
                    ),
            }
        )


    ranking = pd.DataFrame(
        results
    )


    print(
        f"Structured jobs scored: "
        f"{len(ranking):,}"
    )


    return ranking


# =============================================================
# ADD SEMANTIC SCORES
# =============================================================

def add_semantic_scores(
    ranking,
    resume_embedding,
    job_embeddings
):

    print_section(
        "CALCULATING SEMANTIC SIMILARITY"
    )


    similarities = (

        job_embeddings

        @

        resume_embedding
    )


    semantic_scores = (

        np.clip(
            similarities,
            0,
            1
        )

        *

        100
    )


    ranking = (
        ranking.copy()
    )


    ranking[
        "semantic_similarity"
    ] = np.round(
        similarities,
        4
    )


    ranking[
        "semantic_match_score"
    ] = np.round(
        semantic_scores,
        2
    )


    # ---------------------------------------------------------
    # HYBRID
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


    ranking[
        "match_category"
    ] = (

        ranking[
            "hybrid_match_score"
        ]

        .apply(
            get_match_category
        )
    )


    ranking[
        "recommendation"
    ] = ranking.apply(

        lambda row:

        get_recommendation(

            hybrid_score=
                row[
                    "hybrid_match_score"
                ],

            must_have_score=
                row[
                    "must_have_match_rate"
                ],

            has_must_have=
                bool(
                    row[
                        "matched_must_have_skills"
                    ]

                    or

                    row[
                        "missing_must_have_skills"
                    ]
                ),
        ),

        axis=1
    )


    # ---------------------------------------------------------
    # FINAL RANK
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
# DISPLAY RESUME PROFILE
# =============================================================

def display_resume_profile(
    profile
):

    print_section(
        "CANDIDATE RESUME PROFILE"
    )


    print(
        f"Candidate          : "
        f"{profile['possible_name']}"
    )


    print(
        f"Experience         : "
        f"{profile['estimated_experience_years']} years"
    )


    print(
        f"Skills Detected    : "
        f"{profile['skill_count']}"
    )


    print(
        "Skills             : "
        +
        ", ".join(
            profile[
                "skills"
            ]
        )
    )


    print(
        f"Education          : "
        +
        (
            ", ".join(
                profile[
                    "education_keywords"
                ]
            )

            if profile[
                "education_keywords"
            ]

            else "Not detected"
        )
    )


# =============================================================
# DISPLAY TOP JOBS
# =============================================================

def display_top_jobs(
    ranking,
    top_n
):

    print_section(
        f"TOP {top_n} JOB MATCHES"
    )


    columns = [

        "rank",

        "job_id",

        "job_code",

        "job_title",

        "job_status",

        "experience_required",

        "must_have_match_rate",

        "skill_match_score",

        "experience_match_score",

        "structured_match_score",

        "semantic_match_score",

        "hybrid_match_score",

        "match_category",

        "recommendation",
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
# EXPLAIN TOP JOB
# =============================================================

def explain_best_job(
    ranking,
    resume_profile
):

    if ranking.empty:

        return


    job = ranking.iloc[0]


    print_section(
        "BEST JOB MATCH EXPLANATION"
    )


    print(
        f"Candidate          : "
        f"{resume_profile['possible_name']}"
    )


    print(
        f"Job               : "
        f"{job['job_title']}"
    )


    print(
        f"Job Code          : "
        f"{job['job_code']}"
    )


    print(
        f"Job Status        : "
        f"{job['job_status']}"
    )


    print(
        f"Hybrid Score      : "
        f"{job['hybrid_match_score']:.2f}%"
    )


    print(
        f"Category          : "
        f"{job['match_category']}"
    )


    print(
        f"Recommendation    : "
        f"{job['recommendation']}"
    )


    print("\nScore Breakdown")


    print(
        f"Structured Score  : "
        f"{job['structured_match_score']:.2f}%"
    )


    print(
        f"Semantic Score    : "
        f"{job['semantic_match_score']:.2f}%"
    )


    print(
        f"Skill Score       : "
        f"{job['skill_match_score']:.2f}%"
    )


    print(
        f"Must-Have Match   : "
        f"{job['must_have_match_rate']:.2f}%"
    )


    print(
        f"Experience Match  : "
        f"{job['experience_match_score']:.2f}%"
    )


    print("\nMatched Must-Have Skills")


    print(

        job[
            "matched_must_have_skills"
        ]

        if job[
            "matched_must_have_skills"
        ]

        else "None"
    )


    print("\nMissing Must-Have Skills")


    print(

        job[
            "missing_must_have_skills"
        ]

        if job[
            "missing_must_have_skills"
        ]

        else "None"
    )


    print("\nMatched Nice-to-Have Skills")


    print(

        job[
            "matched_nice_to_have_skills"
        ]

        if job[
            "matched_nice_to_have_skills"
        ]

        else "None"
    )


# =============================================================
# VALIDATION
# =============================================================

def validate_results(
    ranking
):

    print_section(
        "RESUME-JOB MATCHING VALIDATION"
    )


    checks = []


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
                )
        }
    )


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
                )
        }
    )


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
                )
        }
    )


    duplicate_jobs = (

        ranking[
            "job_id"
        ]

        .duplicated()

        .sum()
    )


    checks.append(
        {

            "check":
                "Duplicate job rankings",

            "value":
                duplicate_jobs,

            "status":
                (
                    "PASS"
                    if duplicate_jobs == 0
                    else "FAIL"
                )
        }
    )


    validation = pd.DataFrame(
        checks
    )


    print(
        validation.to_string(
            index=False
        )
    )


    return validation


# =============================================================
# SAVE RESULTS
# =============================================================

def save_results(
    ranking,
    validation,
    resume_profile,
    resume_path
):

    print_section(
        "SAVING RESULTS"
    )


    safe_name = re.sub(

        r"[^A-Za-z0-9_-]+",

        "_",

        resume_path.stem
    )


    full_file = (

        OUTPUT_DIR

        /

        f"{safe_name}_job_ranking.csv"
    )


    top_file = (

        OUTPUT_DIR

        /

        f"{safe_name}_top_20_jobs.csv"
    )


    validation_file = (

        OUTPUT_DIR

        /

        f"{safe_name}_validation.csv"
    )


    profile_file = (

        OUTPUT_DIR

        /

        f"{safe_name}_resume_profile.json"
    )


    # job_text can make CSV unnecessarily huge
    export_ranking = (

        ranking.drop(
            columns=[
                "job_text"
            ],
            errors="ignore"
        )
    )


    export_ranking.to_csv(

        full_file,

        index=False
    )


    export_ranking.head(
        20
    ).to_csv(

        top_file,

        index=False
    )


    validation.to_csv(

        validation_file,

        index=False
    )


    with open(
        profile_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            resume_profile,

            file,

            indent=4,

            ensure_ascii=False
        )


    print(
        f"Full Job Ranking:\n"
        f"{full_file}"
    )


    print(
        f"\nTop 20 Jobs:\n"
        f"{top_file}"
    )


    print(
        f"\nValidation:\n"
        f"{validation_file}"
    )


    print(
        f"\nResume Profile:\n"
        f"{profile_file}"
    )


# =============================================================
# ANALYZE RESUME
# =============================================================

def prepare_resume(
    resume_path
):

    print_section(
        "ANALYZING RESUME"
    )


    raw_text, page_count = (

        extract_resume_text(
            resume_path
        )
    )


    resume_text = (

        clean_resume_text(
            raw_text
        )
    )


    known_skills = (
        load_known_skills()
    )


    known_job_titles = (
        load_known_job_titles()
    )


    profile = (

        build_resume_profile(

            file_path=
                resume_path,

            resume_text=
                resume_text,

            page_count=
                page_count,

            known_skills=
                known_skills,

            known_job_titles=
                known_job_titles,
        )
    )


    print(
        f"Pages              : "
        f"{page_count}"
    )


    print(
        f"Words              : "
        f"{len(resume_text.split()):,}"
    )


    print(
        f"Skills detected    : "
        f"{profile['skill_count']}"
    )


    return (
        resume_text,
        profile
    )


# =============================================================
# INTERACTIVE RESUME SELECTOR
# =============================================================

def choose_resume():

    files = [

        file

        for file in RESUME_DIR.iterdir()

        if (
            file.is_file()

            and

            file.suffix.lower()

            in {
                ".pdf",
                ".txt"
            }
        )
    ]


    files = sorted(
        files
    )


    if not files:

        print(
            f"No resumes found in:\n"
            f"{RESUME_DIR}"
        )

        return None


    print_section(
        "AVAILABLE RESUMES"
    )


    for index, file in enumerate(
        files,
        start=1
    ):

        print(
            f"{index}. {file.name}"
        )


    try:

        choice = int(

            input(
                "\nSelect resume number: "
            )
        )

    except ValueError:

        return None


    if (
        choice < 1

        or

        choice > len(files)
    ):

        return None


    return files[
        choice - 1
    ]


# =============================================================
# MAIN ENGINE
# =============================================================

def run_resume_job_matcher(
    resume_path,
    top_n=10,
    all_jobs=False
):

    start_time = time.time()


    resume_path = Path(
        resume_path
    ).expanduser().resolve()


    if not resume_path.exists():

        print(
            f"ERROR: Resume not found:\n"
            f"{resume_path}"
        )

        return None


    print("\n")

    print(
        "=" * 80
    )

    print(
        "TALENTIQ AI RECRUITMENT PLATFORM"
    )

    print(
        "RESUME → JOB MATCHING ENGINE"
    )

    print(
        "=" * 80
    )


    # =========================================================
    # RESUME
    # =========================================================

    (
        resume_text,
        resume_profile

    ) = prepare_resume(
        resume_path
    )


    display_resume_profile(
        resume_profile
    )


    # =========================================================
    # JOB DATA
    # =========================================================

    print_section(
        "LOADING TALENTIQ JOBS"
    )


    jobs = load_jobs(
        all_jobs=
            all_jobs
    )


    job_skills = (
        load_all_job_skills()
    )


    job_profiles = (
        build_job_skill_profiles(
            job_skills
        )
    )


    print(
        f"Jobs loaded          : "
        f"{len(jobs):,}"
    )


    print(
        f"Job skill profiles   : "
        f"{len(job_profiles):,}"
    )


    if all_jobs:

        print(
            "Job Scope            : ALL JOBS"
        )

    else:

        print(
            "Job Scope            : OPEN JOBS"
        )


    # =========================================================
    # STRUCTURED
    # =========================================================

    ranking = score_jobs(

        jobs=
            jobs,

        job_profiles=
            job_profiles,

        resume_profile=
            resume_profile,
    )


    # =========================================================
    # SEMANTIC MODEL
    # =========================================================

    model = (
        load_embedding_model()
    )


    # =========================================================
    # RESUME EMBEDDING
    # =========================================================

    resume_embedding = (
        create_resume_embedding(

            model=
                model,

            resume_text=
                resume_text,
        )
    )


    # =========================================================
    # JOB EMBEDDINGS
    # =========================================================

    job_texts = (

        ranking[
            "job_text"
        ]

        .tolist()
    )


    job_embeddings = (

        create_job_embeddings(

            model=
                model,

            job_texts=
                job_texts,
        )
    )


    # =========================================================
    # HYBRID
    # =========================================================

    ranking = (

        add_semantic_scores(

            ranking=
                ranking,

            resume_embedding=
                resume_embedding,

            job_embeddings=
                job_embeddings,
        )
    )


    # =========================================================
    # DISPLAY
    # =========================================================

    display_top_jobs(

        ranking=
            ranking,

        top_n=
            top_n,
    )


    explain_best_job(

        ranking=
            ranking,

        resume_profile=
            resume_profile,
    )


    # =========================================================
    # VALIDATION
    # =========================================================

    validation = (
        validate_results(
            ranking
        )
    )


    # =========================================================
    # SAVE
    # =========================================================

    save_results(

        ranking=
            ranking,

        validation=
            validation,

        resume_profile=
            resume_profile,

        resume_path=
            resume_path,
    )


    # =========================================================
    # SUMMARY
    # =========================================================

    failed = (

        validation[
            "status"
        ]

        .ne(
            "PASS"
        )

        .sum()
    )


    elapsed = (

        time.time()

        -

        start_time
    )


    print("\n")

    print(
        "=" * 80
    )

    print(
        "TALENTIQ RESUME-JOB MATCHING COMPLETE"
    )

    print(
        "=" * 80
    )


    print(
        f"Resume              : "
        f"{resume_path.name}"
    )


    print(
        f"Jobs Evaluated      : "
        f"{len(ranking):,}"
    )


    print(
        f"Highest Match       : "
        f"{ranking['hybrid_match_score'].max():.2f}%"
    )


    print(
        f"Validation Failures : "
        f"{failed}"
    )


    print(
        f"Processing Time     : "
        f"{elapsed:.2f} seconds"
    )


    print(
        f"STATUS              : "
        f"{'PASS' if failed == 0 else 'REVIEW'}"
    )


    print(
        "=" * 80
    )


    return ranking


# =============================================================
# COMMAND LINE
# =============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "TalentIQ Resume to Job Matching Engine"
        )
    )


    parser.add_argument(

        "--resume",

        type=str,

        help=(
            "Resume PDF or TXT path"
        )
    )


    parser.add_argument(

        "--top-n",

        type=int,

        default=10,

        help=(
            "Number of job matches to display"
        )
    )


    parser.add_argument(

        "--all-jobs",

        action="store_true",

        help=(
            "Rank all jobs instead of only open jobs"
        )
    )


    args = parser.parse_args()


    resume_path = (
        args.resume
    )


    if resume_path is None:

        resume_path = (
            choose_resume()
        )


        if resume_path is None:

            print(
                "No valid resume selected."
            )

            return


    run_resume_job_matcher(

        resume_path=
            resume_path,

        top_n=
            args.top_n,

        all_jobs=
            args.all_jobs,
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":

    main()