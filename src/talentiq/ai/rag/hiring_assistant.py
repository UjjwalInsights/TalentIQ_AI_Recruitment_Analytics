"""
================================================================
TALENTIQ AI RECRUITMENT PLATFORM
File: hiring_assistant.py

Purpose
-------
Hybrid hiring assistant combining:

1. PostgreSQL structured analytics
2. Semantic resume/document retrieval
3. Candidate/job matching context
4. Grounded, explainable answers

Architecture
------------
User Question
      |
      v
Intent Router
   /       \
SQL        Resume / Documents
 |               |
Exact SQL     Embeddings
Metrics       + Retrieval
   \           /
     Grounded Answer

This V1 deliberately avoids unrestricted AI-generated SQL.
Known analytical questions use validated PostgreSQL views.

================================================================
"""

from pathlib import Path
import sys
import argparse
import re
import json

import numpy as np
import pandas as pd

from sqlalchemy import text
from sentence_transformers import SentenceTransformer


# =============================================================
# PROJECT PATH
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

SRC_DIR = CURRENT_FILE.parents[3]
PROJECT_ROOT = CURRENT_FILE.parents[4]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR)
    )


from database.connection import get_connection

from talentiq.ai.rag.llm_client import generate_grounded_answer

# =============================================================
# CONFIGURATION
# =============================================================

MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)

RESUME_ANALYSIS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "resume_analysis"
)

CANDIDATE_MATCHING_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
    / "candidate_matching"
)

SEMANTIC_MATCHING_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
    / "semantic_matching"
)

RESUME_JOB_MATCHING_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
    / "resume_job_matching"
)


# =============================================================
# HELPERS
# =============================================================

def print_section(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


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


def execute_scalar(
    query,
    params=None
):

    with get_connection() as connection:

        result = connection.execute(
            text(query),
            params or {}
        )

        return result.scalar()


# =============================================================
# LOAD EMBEDDING MODEL
# =============================================================

def load_embedding_model():

    print(
        f"Loading embedding model: "
        f"{MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    return model


# =============================================================
# QUESTION ROUTER
# =============================================================

def classify_question(question):

    """
    Lightweight intent router.

    Returns:
        database
        resume
        candidate_matching
        job_matching
        general
    """

    q = question.lower()


    # ---------------------------------------------------------
    # RESUME
    # ---------------------------------------------------------

    resume_words = [
        "resume",
        "cv",

        "skills of",
        "skills does",
        "skill set of",

        "experience of",
        "experience does",

        "education of",
        "education does",

        "background of",

        "summarize arjun",
        "summarise arjun",

        "summarize priya",
        "summarise priya",
    ]


    if any(
        word in q
        for word in resume_words
    ):

        return "resume"


    # ---------------------------------------------------------
    # CANDIDATE MATCHING
    # ---------------------------------------------------------

    if (
        "best candidate" in q
        or
        "top candidate" in q
        or
        "candidates for job" in q
        or
        "candidate match" in q
    ):

        return "candidate_matching"


    # ---------------------------------------------------------
    # RESUME → JOB MATCHING
    # ---------------------------------------------------------

    if (
        "best job" in q
        or
        "jobs for" in q
        or
        "job match" in q
        or
        "suitable job" in q
    ):

        return "job_matching"


    # ---------------------------------------------------------
    # STRUCTURED DATABASE ANALYTICS
    # ---------------------------------------------------------

    database_words = [

        "application",
        "applications",

        "offer",
        "offers",

        "placement",
        "placements",

        "recruiter",
        "recruiters",

        "open jobs",
        "job aging",

        "candidate",
        "candidates",

        "funnel",
        "interview",
        "interviews",

        "salary",
        "client",

        "hire rate",
        "placement rate",
    ]


    if any(
        word in q
        for word in database_words
    ):

        return "database"


    return "general"


# =============================================================
# DATABASE QUESTION HANDLER
# =============================================================

def  answer_database_question(question):

    q = question.lower()


    # ---------------------------------------------------------
    # INTERVIEW STAGE
    # ---------------------------------------------------------

    if (
        "interview stage" in q
        or
        "in interview" in q
    ):

        df = load_dataframe(
            """
            SELECT
                current_stage,
                application_count,
                percentage_of_total
            FROM vw_dashboard_recruitment_funnel
            WHERE LOWER(current_stage) = 'interview';
            """
        )

        if df.empty:
            return "No Interview-stage data was found."

        row = df.iloc[0]

        return (
            f"{int(row['application_count']):,} "
            f"applications are currently in the "
            f"Interview stage, representing "
            f"{row['percentage_of_total']:.2f}% "
            f"of all applications."
        )


    # ---------------------------------------------------------
    # OPEN JOBS 90+ DAYS
    # ---------------------------------------------------------

    if (
        "90 days" in q
        or
        "90+ days" in q
        or
        "older than 90" in q
        or
        "old jobs" in q
        or
        "aging jobs" in q
    ):

        value = execute_scalar(
            """
            SELECT COUNT(*)
            FROM vw_dashboard_job_aging
            WHERE LOWER(job_status) = 'open'
              AND job_age_days >= 90;
            """
        )

        return (
            f"{value:,} open jobs have been "
            f"open for at least 90 days."
        )


    # ---------------------------------------------------------
    # TOTAL APPLICATIONS
    # ---------------------------------------------------------

    if (
        "how many applications" in q
        or
        "total applications" in q
    ):

        value = execute_scalar(
            """
            SELECT total_applications
            FROM vw_dashboard_executive_kpis;
            """
        )

        return (
            f"TalentIQ currently contains "
            f"{value:,} applications."
        )


    # ---------------------------------------------------------
    # TOTAL CANDIDATES
    # ---------------------------------------------------------

    if (
        "how many candidates" in q
        or
        "total candidates" in q
    ):

        value = execute_scalar(
            """
            SELECT total_candidates
            FROM vw_dashboard_executive_kpis;
            """
        )

        return (
            f"TalentIQ contains "
            f"{value:,} candidates."
        )


    # ---------------------------------------------------------
    # OPEN JOBS
    # ---------------------------------------------------------

    if (
        "how many open jobs" in q
        or
        "total open jobs" in q
    ):

        value = execute_scalar(
            """
            SELECT open_jobs
            FROM vw_dashboard_executive_kpis;
            """
        )

        return (
            f"There are currently "
            f"{value:,} open jobs "
            f"in the TalentIQ dataset."
        )


    # ---------------------------------------------------------
    # TOTAL OFFERS
    # ---------------------------------------------------------

    if (
        "how many offers" in q
        or
        "total offers" in q
    ):

        value = execute_scalar(
            """
            SELECT total_offers
            FROM vw_dashboard_executive_kpis;
            """
        )

        return (
            f"TalentIQ contains "
            f"{value:,} offers."
        )


    # ---------------------------------------------------------
    # TOTAL PLACEMENTS
    # ---------------------------------------------------------

    if (
        "how many placements" in q
        or
        "total placements" in q
    ):

        value = execute_scalar(
            """
            SELECT total_placements
            FROM vw_dashboard_executive_kpis;
            """
        )

        return (
            f"TalentIQ contains "
            f"{value:,} placements."
        )


    # ---------------------------------------------------------
    # INTERVIEW STAGE
    # ---------------------------------------------------------

    if (
        "interview stage" in q
        or
        "in interview" in q
    ):

        df = load_dataframe(
            """
            SELECT
                current_stage,
                application_count,
                percentage_of_total
            FROM vw_dashboard_recruitment_funnel
            WHERE LOWER(current_stage) = 'interview';
            """
        )


        if df.empty:

            return (
                "No Interview-stage data was found."
            )


        row = df.iloc[0]


        return (
            f"{int(row['application_count']):,} "
            f"applications are currently in the "
            f"Interview stage, representing "
            f"{row['percentage_of_total']:.2f}% "
            f"of all applications."
        )


    # ---------------------------------------------------------
    # TOP RECRUITER
    # ---------------------------------------------------------

    if (
        "best recruiter" in q
        or
        "top recruiter" in q
        or
        "highest placement rate" in q
    ):

        df = load_dataframe(
            """
            SELECT
                recruiter_id,
                total_applications,
                hired_count,
                placement_count,
                hire_rate,
                placement_rate
            FROM vw_dashboard_recruiter_performance
            ORDER BY
                placement_count DESC,
                placement_rate DESC
            LIMIT 1;
            """
        )


        if df.empty:

            return (
                "Recruiter performance data "
                "was not found."
            )


        row = df.iloc[0]


        return (
            f"Recruiter {int(row['recruiter_id'])} "
            f"is currently the strongest by total "
            f"placements with "
            f"{int(row['placement_count'])} placements. "
            f"Hire rate: {row['hire_rate']:.2f}%. "
            f"Placement rate: "
            f"{row['placement_rate']:.2f}%."
        )


    # ---------------------------------------------------------
    # 90+ DAY JOBS
    # ---------------------------------------------------------

    if (
        "90 days" in q
        or
        "90+ days" in q
        or
        "old jobs" in q
        or
        "aging jobs" in q
    ):

        value = execute_scalar(
            """
            SELECT COUNT(*)
            FROM vw_dashboard_job_aging
            WHERE LOWER(job_status) = 'open'
              AND job_age_days >= 90;
            """
        )


        return (
            f"{value:,} open jobs have been "
            f"open for at least 90 days."
        )


    # ---------------------------------------------------------
    # RECRUITMENT FUNNEL
    # ---------------------------------------------------------

    if "funnel" in q:

        df = load_dataframe(
            """
            SELECT
                current_stage,
                application_count,
                percentage_of_total
            FROM vw_dashboard_recruitment_funnel
            ORDER BY application_count DESC;
            """
        )


        lines = [
            "Recruitment funnel:"
        ]


        for row in df.itertuples():

            lines.append(
                f"- {row.current_stage}: "
                f"{row.application_count:,} "
                f"({row.percentage_of_total:.2f}%)"
            )


        return "\n".join(
            lines
        )


    # ---------------------------------------------------------
    # EXECUTIVE KPIs
    # ---------------------------------------------------------

    if (
        "executive kpi" in q
        or
        "overall recruitment" in q
        or
        "recruitment summary" in q
    ):

        df = load_dataframe(
            """
            SELECT *
            FROM vw_dashboard_executive_kpis;
            """
        )


        row = df.iloc[0]


        return (
            "TalentIQ recruitment summary:\n"
            f"- Jobs: {int(row['total_jobs']):,}\n"
            f"- Open Jobs: {int(row['open_jobs']):,}\n"
            f"- Candidates: "
            f"{int(row['total_candidates']):,}\n"
            f"- Applications: "
            f"{int(row['total_applications']):,}\n"
            f"- Offers: "
            f"{int(row['total_offers']):,}\n"
            f"- Placements: "
            f"{int(row['total_placements']):,}\n"
            f"- Application → Offer: "
            f"{row['application_to_offer_rate']:.2f}%\n"
            f"- Application → Placement: "
            f"{row['application_to_placement_rate']:.2f}%"
        )


    return (
        "I recognized this as a database question, "
        "but this exact analytical intent is not yet "
        "implemented in Hiring Assistant V1."
    )


# =============================================================
# RESUME DOCUMENT LOADER
# =============================================================

def load_resume_documents():

    documents = []


    if not RESUME_ANALYSIS_DIR.exists():

        return documents


    text_files = list(
        RESUME_ANALYSIS_DIR.glob(
            "*_cleaned.txt"
        )
    )


    for text_file in text_files:

        text_value = text_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )


        # Try corresponding profile
        base_name = text_file.name.replace(
            "_cleaned.txt",
            ""
        )


        profile_file = (
            RESUME_ANALYSIS_DIR
            /
            f"{base_name}_profile.json"
        )


        profile = {}


        if profile_file.exists():

            try:

                profile = json.loads(
                    profile_file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                profile = {}


        documents.append(
            {
                "name":
                    base_name.replace(
                        "_",
                        " "
                    ),

                "text":
                    text_value,

                "profile":
                    profile,

                "source":
                    str(text_file),
            }
        )


    return documents


# =============================================================
# CHUNK DOCUMENTS
# =============================================================

def chunk_text(
    text_value,
    chunk_size=180,
    overlap=40
):

    words = text_value.split()


    chunks = []


    step = (
        chunk_size
        -
        overlap
    )


    for start in range(
        0,
        len(words),
        step
    ):

        chunk = " ".join(
            words[
                start:
                start + chunk_size
            ]
        )


        if chunk:

            chunks.append(
                chunk
            )


    return chunks


# =============================================================
# BUILD RESUME INDEX
# =============================================================

def build_resume_index(
    model,
    documents
):

    records = []


    for document in documents:

        chunks = chunk_text(
            document[
                "text"
            ]
        )


        for index, chunk in enumerate(
            chunks
        ):

            records.append(
                {
                    "candidate":
                        document[
                            "name"
                        ],

                    "chunk_id":
                        index + 1,

                    "text":
                        chunk,

                    "source":
                        document[
                            "source"
                        ],

                    "profile":
                        document[
                            "profile"
                        ],
                }
            )


    if not records:

        return [], None


    texts = [
        record["text"]
        for record in records
    ]


    embeddings = model.encode(

        texts,

        batch_size=64,

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=False,
    )


    return (
        records,
        embeddings
    )


# =============================================================
# DETECT CANDIDATE NAME
# =============================================================

def detect_candidate_filter(
    question,
    documents
):

    question_lower = (
        question.lower()
    )


    for document in documents:

        name = document[
            "name"
        ]


        # Full name
        if name.lower() in question_lower:

            return name


        # First name
        first_name = (
            name.split()[0]
        )


        if (
            len(first_name) >= 3
            and
            first_name.lower()
            in question_lower
        ):

            return name


    return None


# =============================================================
# RETRIEVE RESUME CHUNKS
# =============================================================

def retrieve_resume_chunks(
    question,
    model,
    records,
    embeddings,
    candidate_filter=None,
    top_k=4
):

    if not records:

        return []


    question_embedding = model.encode(

        [question],

        convert_to_numpy=True,

        normalize_embeddings=True,

        show_progress_bar=False,
    )[0]


    similarities = (
        embeddings
        @
        question_embedding
    )


    results = []


    for index, similarity in enumerate(
        similarities
    ):

        record = records[index]


        if (
            candidate_filter
            and
            record["candidate"]
            !=
            candidate_filter
        ):

            continue


        results.append(
            {
                **record,

                "similarity":
                    float(
                        similarity
                    ),
            }
        )


    results = sorted(

        results,

        key=lambda x:
        x["similarity"],

        reverse=True
    )


    return results[
        :top_k
    ]


# =============================================================
# RESUME SUMMARY
# =============================================================

def build_profile_summary(
    candidate_name,
    documents
):

    for document in documents:

        if (
            document[
                "name"
            ]
            ==
            candidate_name
        ):

            profile = document.get(
                "profile",
                {}
            )


            if not profile:

                return None


            skills = profile.get(
                "skills",
                []
            )


            education = profile.get(
                "education_keywords",
                []
            )


            return (
                f"{candidate_name} resume profile:\n"
                f"- Experience: "
                f"{profile.get('estimated_experience_years')} years\n"
                f"- Skills detected: "
                f"{profile.get('skill_count', len(skills))}\n"
                f"- Skills: "
                f"{', '.join(skills)}\n"
                f"- Education: "
                f"{', '.join(education) if education else 'Not detected'}\n"
                f"- Email: "
                f"{profile.get('email')}"
            )


    return None


# =============================================================
# ANSWER RESUME QUESTION
# =============================================================

def answer_resume_question(
    question,
    model,
    documents,
    records,
    embeddings
):

    if not documents:

        return (
            "No analyzed resumes were found. "
            "Run resume_analyzer.py first."
        )


    candidate_filter = (
        detect_candidate_filter(
            question,
            documents
        )
    )


    q = question.lower()


    # ---------------------------------------------------------
    # STRUCTURED SUMMARY
    # ---------------------------------------------------------

    if (
        candidate_filter
        and
        (
            "summary" in q
            or
            "summarize" in q
            or
            "summarise" in q
            or
            "profile" in q
        )
    ):

        summary = build_profile_summary(
            candidate_filter,
            documents
        )


        if summary:

            return summary


    # ---------------------------------------------------------
    # SEMANTIC RETRIEVAL
    # ---------------------------------------------------------

    retrieved = retrieve_resume_chunks(

        question=
            question,

        model=
            model,

        records=
            records,

        embeddings=
            embeddings,

        candidate_filter=
            candidate_filter,

        top_k=4
    )


    if not retrieved:

        return (
            "I could not find relevant resume "
            "content for that question."
        )


    lines = [
        "Most relevant resume evidence:"
    ]


    for index, item in enumerate(
        retrieved,
        start=1
    ):

        snippet = item[
            "text"
        ]


        if len(snippet) > 450:

            snippet = (
                snippet[:450]
                +
                "..."
            )


        lines.append(
            f"\n[{index}] "
            f"{item['candidate']} "
            f"(similarity "
            f"{item['similarity']:.2f})\n"
            f"{snippet}"
        )


    return "\n".join(
        lines
    )


# =============================================================
# FIND JOB ID
# =============================================================

def extract_job_id(question):

    patterns = [

        r"job\s+(?:id\s*)?(\d+)",

        r"job-id\s+(\d+)",
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            question.lower()
        )


        if match:

            return int(
                match.group(1)
            )


    return None


# =============================================================
# CANDIDATE MATCHING FILE ANSWER
# =============================================================

def answer_candidate_matching_question(
    question
):

    job_id = extract_job_id(
        question
    )


    if job_id is None:

        return (
            "Please include a numeric job ID, "
            "for example: "
            "'Who are the best candidates for job 953?'"
        )


    job_code = (
        execute_scalar(
            """
            SELECT job_code
            FROM jobs
            WHERE job_id = :job_id;
            """,
            {
                "job_id":
                    job_id
            }
        )
    )


    if job_code is None:

        return (
            f"Job {job_id} was not found."
        )


    possible_files = [

        SEMANTIC_MATCHING_DIR
        /
        f"{job_code}_top_20_hybrid.csv",

        CANDIDATE_MATCHING_DIR
        /
        f"{job_code}_top_20_candidates.csv",
    ]


    ranking_file = None


    for file in possible_files:

        if file.exists():

            ranking_file = file

            break


    if ranking_file is None:

        return (
            f"No saved candidate ranking exists "
            f"for {job_code}. Run the candidate "
            f"matching engine for job {job_id} first."
        )


    df = pd.read_csv(
        ranking_file
    )


    score_column = (

        "hybrid_match_score"

        if "hybrid_match_score"
        in df.columns

        else
        "structured_match_score"
    )


    recommendation_column = (

        "hybrid_recommendation"

        if "hybrid_recommendation"
        in df.columns

        else
        "recommendation"
    )


    top = df.head(5)


    lines = [
        f"Top candidates for {job_code}:"
    ]


    for index, row in top.iterrows():

        recommendation = (
            row.get(
                recommendation_column,
                ""
            )
        )


        lines.append(
            f"{index + 1}. "
            f"{row['candidate_name']} "
            f"- {row[score_column]:.2f}% "
            f"- {recommendation}"
        )


    return "\n".join(
        lines
    )


# =============================================================
# RESUME → JOB MATCHING FILE ANSWER
# =============================================================

def answer_job_matching_question(
    question
):

    if not RESUME_JOB_MATCHING_DIR.exists():

        return (
            "No saved resume-to-job matching "
            "results were found."
        )


    files = list(
        RESUME_JOB_MATCHING_DIR.glob(
            "*_top_20_jobs.csv"
        )
    )


    if not files:

        return (
            "No resume-to-job rankings were found. "
            "Run resume_job_matcher.py first."
        )


    q = question.lower()


    selected = None


    for file in files:

        readable = (
            file.stem
            .replace(
                "_top_20_jobs",
                ""
            )
            .replace(
                "_",
                " "
            )
        )


        first_name = (
            readable.split()[0]
            .lower()
        )


        if (
            readable.lower()
            in q
            or
            first_name
            in q
        ):

            selected = file

            break


    if selected is None:

        if len(files) == 1:

            selected = files[0]

        else:

            names = [

                file.stem
                .replace(
                    "_top_20_jobs",
                    ""
                )
                .replace(
                    "_",
                    " "
                )

                for file in files
            ]


            return (
                "Please specify the candidate. "
                "Available resume rankings: "
                +
                ", ".join(
                    names
                )
            )


    df = pd.read_csv(
        selected
    )


    candidate_name = (

        selected.stem
        .replace(
            "_top_20_jobs",
            ""
        )
        .replace(
            "_",
            " "
        )
    )


    lines = [
        f"Top job matches for "
        f"{candidate_name}:"
    ]


    for index, row in df.head(
        5
    ).iterrows():

        lines.append(
            f"{index + 1}. "
            f"{row['job_title']} "
            f"({row['job_code']}) "
            f"- {row['hybrid_match_score']:.2f}% "
            f"- {row['recommendation']}"
        )


    return "\n".join(
        lines
    )


# =============================================================
# MAIN QUESTION ANSWER
# =============================================================
def answer_question(
    question,
    model,
    documents,
    records,
    embeddings
):

    # ---------------------------------------------------------
    # DETECT INTENT
    # ---------------------------------------------------------

    intent = classify_question(
        question
    )

    print(
        f"\nDetected Intent: "
        f"{intent}"
    )


    # ---------------------------------------------------------
    # DATABASE
    # Keep exact SQL/database answers deterministic
    # ---------------------------------------------------------

    if intent == "database":

        return answer_database_question(
            question
        )


    # ---------------------------------------------------------
    # RESUME RAG
    # Retrieval + Local LLM generation
    # ---------------------------------------------------------

    if intent == "resume":

        context = answer_resume_question(

            question=question,

            model=model,

            documents=documents,

            records=records,

            embeddings=embeddings,
        )

        print(
            "Generating grounded AI answer..."
        )

        return generate_grounded_answer(
            question=question,
            context=context,
            answer_type="resume_analysis",
        )


    # ---------------------------------------------------------
    # CANDIDATE MATCHING
    # Preserve exact ranking / scores
    # ---------------------------------------------------------

    if intent == "candidate_matching":

        return answer_candidate_matching_question(
            question
        )


    # ---------------------------------------------------------
    # RESUME → JOB MATCHING
    # Preserve exact ranking / scores
    # ---------------------------------------------------------

    if intent == "job_matching":

        return answer_job_matching_question(
            question
        )


    # ---------------------------------------------------------
    # UNSUPPORTED
    # ---------------------------------------------------------

    return (
        "I can currently help with:\n"
        "- recruitment KPIs\n"
        "- recruitment funnel analysis\n"
        "- recruiter performance\n"
        "- job aging\n"
        "- resume analysis\n"
        "- candidate-job matching\n"
        "- resume-job matching\n\n"
        "Try asking a recruitment or hiring question."
    )


# =============================================================
# INTERACTIVE ASSISTANT
# =============================================================

def run_assistant():

    print("\n")
    print("=" * 80)

    print(
        "TALENTIQ AI RECRUITMENT PLATFORM"
    )

    print(
        "HYBRID RAG HIRING ASSISTANT"
    )

    print("=" * 80)


    # ---------------------------------------------------------
    # MODEL
    # ---------------------------------------------------------

    model = load_embedding_model()


    # ---------------------------------------------------------
    # RESUME DOCUMENTS
    # ---------------------------------------------------------

    documents = (
        load_resume_documents()
    )


    print(
        f"Analyzed resumes loaded: "
        f"{len(documents)}"
    )


    (
        records,
        embeddings

    ) = build_resume_index(
        model,
        documents
    )


    print(
        f"Resume chunks indexed: "
        f"{len(records):,}"
    )


    print("\nExamples:")

    print(
        "- How many applications are there?"
    )

    print(
        "- How many applications are in Interview stage?"
    )

    print(
        "- Who is the top recruiter?"
    )

    print(
        "- How many open jobs are older than 90 days?"
    )

    print(
        "- Summarize Arjun Maske's resume."
    )

    print(
        "- What automation experience does Arjun have?"
    )

    print(
        "- Who are the best candidates for job 953?"
    )

    print(
        "- What are the best jobs for Arjun?"
    )


    print(
        "\nType 'exit' to close TalentIQ."
    )


    # ---------------------------------------------------------
    # CHAT LOOP
    # ---------------------------------------------------------

    while True:

        print()

        question = input(
            "You: "
        ).strip()


        if not question:

            continue


        if question.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print(
                "\nTalentIQ Assistant closed."
            )

            break


        try:

            answer = answer_question(

                question=
                    question,

                model=
                    model,

                documents=
                    documents,

                records=
                    records,

                embeddings=
                    embeddings,
            )


            print(
                "\nTalentIQ:"
            )

            print(
                answer
            )


        except Exception as error:

            print(
                "\nTalentIQ encountered an error:"
            )

            print(
                error
            )


# =============================================================
# SINGLE QUESTION MODE
# =============================================================

def run_single_question(
    question
):

    model = load_embedding_model()


    documents = (
        load_resume_documents()
    )


    (
        records,
        embeddings

    ) = build_resume_index(
        model,
        documents
    )


    answer = answer_question(

        question=
            question,

        model=
            model,

        documents=
            documents,

        records=
            records,

        embeddings=
            embeddings,
    )


    print("\nTalentIQ:")

    print(
        answer
    )


# =============================================================
# COMMAND LINE
# =============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "TalentIQ Hybrid RAG Hiring Assistant"
        )
    )


    parser.add_argument(

        "--question",

        type=str,

        help=(
            "Ask a single TalentIQ question"
        ),
    )


    args = (
        parser.parse_args()
    )


    if args.question:

        run_single_question(
            args.question
        )

    else:

        run_assistant()


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":

    main()