"""
=============================================================
TALENTIQ AI RECRUITMENT PLATFORM
File: app/app.py
Version: V6 - Final Polished UI

Main Streamlit application.

Current modules:
1. Executive Overview
2. AI Hiring Assistant
3. Candidate Matcher
4. Resume Analyzer
5. Resume → Job Matcher
6. Recruitment Analytics
=============================================================
"""

from pathlib import Path
import sys
import subprocess

import pandas as pd
import streamlit as st
from sqlalchemy import text


# =============================================================
# PROJECT PATH
# =============================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[1]

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR)
    )


# =============================================================
# TALENTIQ IMPORTS
# =============================================================

from database.connection import get_connection

from talentiq.ai.rag.hiring_assistant import (
    load_embedding_model,
    load_resume_documents,
    build_resume_index,
    answer_question,
)

from talentiq.ai.resume import resume_analyzer


# =============================================================
# PAGE CONFIGURATION
# =============================================================

st.set_page_config(
    page_title="TalentIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================
# CUSTOM CSS
# =============================================================

st.markdown(
    """
    <style>
    :root {
        --ti-accent: #ff4b4b;
        --ti-accent-soft: rgba(255, 75, 75, 0.10);
        --ti-border: rgba(148, 163, 184, 0.18);
        --ti-surface: rgba(148, 163, 184, 0.055);
        --ti-muted: rgba(226, 232, 240, 0.66);
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.35rem;
        padding-bottom: 4rem;
    }

    /* ---------- Brand header ---------- */
    .ti-brand {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.15rem 0 1.25rem 0;
        margin-bottom: 1.15rem;
        border-bottom: 1px solid var(--ti-border);
    }

    .ti-eyebrow {
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ti-accent);
        margin-bottom: 0.22rem;
    }

    .talentiq-title {
        font-size: clamp(2rem, 3.5vw, 2.8rem);
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.035em;
        margin: 0;
    }

    .talentiq-subtitle {
        font-size: 0.96rem;
        color: var(--ti-muted);
        margin-top: 0.42rem;
    }

    .ti-badges {
        display: flex;
        gap: 0.45rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .ti-badge {
        border: 1px solid var(--ti-border);
        background: var(--ti-surface);
        border-radius: 999px;
        padding: 0.36rem 0.68rem;
        font-size: 0.76rem;
        font-weight: 650;
        white-space: nowrap;
    }

    .ti-dot {
        color: #22c55e;
        margin-right: 0.28rem;
    }

    /* ---------- Typography ---------- */
    h1, h2, h3 {
        letter-spacing: -0.025em;
    }

    h1 {
        margin-bottom: 0.25rem !important;
    }

    h2 {
        margin-top: 1.4rem !important;
    }

    p, .stCaption {
        line-height: 1.55;
    }

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {
        background: var(--ti-surface);
        border: 1px solid var(--ti-border);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        min-height: 104px;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--ti-muted);
        font-weight: 650;
    }

    div[data-testid="stMetricValue"] {
        letter-spacing: -0.03em;
    }

    /* ---------- Buttons / inputs ---------- */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 2.6rem;
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
    }

    div[data-testid="stFileUploaderDropzone"] {
        border: 1px dashed rgba(148, 163, 184, 0.35);
        background: var(--ti-surface);
    }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] {
        font-weight: 650;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    /* ---------- Tables ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--ti-border);
        border-radius: 12px;
        overflow: hidden;
    }

    /* ---------- Expanders ---------- */
    div[data-testid="stExpander"] {
        border: 1px solid var(--ti-border);
        border-radius: 12px;
        background: var(--ti-surface);
    }

    /* ---------- Alerts ---------- */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--ti-border);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem;
    }

    .ti-sidebar-brand {
        padding: 0.25rem 0 0.55rem 0;
    }

    .ti-sidebar-brand strong {
        font-size: 1.35rem;
        letter-spacing: -0.02em;
    }

    .ti-sidebar-sub {
        color: var(--ti-muted);
        font-size: 0.78rem;
        margin-top: 0.15rem;
    }

    .ti-status {
        display: grid;
        gap: 0.46rem;
        margin-top: 0.35rem;
    }

    .ti-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        font-size: 0.78rem;
        padding: 0.42rem 0.55rem;
        border-radius: 9px;
        background: var(--ti-surface);
        border: 1px solid var(--ti-border);
    }

    .ti-status-online {
        color: #22c55e;
        font-weight: 750;
    }

    /* ---------- Chat ---------- */
    div[data-testid="stChatMessage"] {
        border: 1px solid var(--ti-border);
        border-radius: 14px;
        padding: 0.35rem 0.45rem;
        margin-bottom: 0.6rem;
        background: var(--ti-surface);
    }

    /* ---------- Footer ---------- */
    .ti-footer {
        margin-top: 3.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--ti-border);
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
        color: var(--ti-muted);
        font-size: 0.76rem;
    }

    @media (max-width: 900px) {
        .ti-brand {
            align-items: flex-start;
            flex-direction: column;
        }

        .ti-badges {
            justify-content: flex-start;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# DATABASE HELPERS
# =============================================================

@st.cache_data(
    ttl=60,
    show_spinner=False,
)
def load_executive_kpis():

    query = """
    SELECT *
    FROM vw_dashboard_executive_kpis;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            text(query),
            connection
        )

    if df.empty:

        return {}

    return df.iloc[0].to_dict()


@st.cache_data(
    ttl=60,
    show_spinner=False,
)
def load_funnel():

    query = """
    SELECT
        current_stage,
        application_count,
        percentage_of_total
    FROM vw_dashboard_recruitment_funnel
    ORDER BY application_count DESC;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            text(query),
            connection
        )

    return df


@st.cache_data(
    ttl=60,
    show_spinner=False,
)
def load_open_jobs():

    query = """
    SELECT
        job_id,
        job_code,
        job_title,
        job_status
    FROM jobs
    WHERE LOWER(job_status) = 'open'
    ORDER BY job_id;
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            text(query),
            connection
        )

    return df
@st.cache_data(
    ttl=60,
    show_spinner=False,
)

def load_dashboard_view(view_name):

    allowed_views = {
        "vw_dashboard_recruiter_performance",
        "vw_dashboard_job_aging",
        "vw_dashboard_client_analysis",
        "vw_dashboard_placement_analysis",
        "vw_dashboard_time_trends",
        "vw_dashboard_recruitment_funnel",
    }

    if view_name not in allowed_views:
        raise ValueError(
            f"Dashboard view not allowed: {view_name}"
        )

    query = f"""
    SELECT *
    FROM {view_name};
    """

    with get_connection() as connection:

        df = pd.read_sql_query(
            text(query),
            connection
        )

    return df


# =============================================================
# UI / DISPLAY HELPERS
# =============================================================

DISPLAY_COLUMN_NAMES = {
    "recruiter_id": "Recruiter ID",
    "client_id": "Client ID",
    "job_id": "Job ID",
    "job_code": "Job Code",
    "job_title": "Job Title",
    "job_status": "Status",
    "job_age_days": "Age (Days)",
    "aging_bucket": "Aging Bucket",
    "total_jobs": "Total Jobs",
    "open_jobs": "Open Jobs",
    "closed_jobs": "Closed Jobs",
    "filled_jobs": "Filled Jobs",
    "total_applications": "Applications",
    "application_count": "Applications",
    "total_interviews": "Interviews",
    "interview_count": "Interviews",
    "total_offers": "Offers",
    "offer_count": "Offers",
    "total_placements": "Placements",
    "placement_count": "Placements",
    "hired_count": "Hires",
    "hire_rate": "Hire Rate",
    "placement_rate": "Placement Rate",
    "average_offered_salary": "Average Offered Salary",
    "avg_offered_salary": "Average Offered Salary",
    "placement_status": "Placement Status",
    "status": "Status",
    "month": "Month",
    "screening": "Screening",
    "submitted_to_client": "Submitted to Client",
    "applications": "Applications",
    "interviews": "Interviews",
    "offers": "Offers",
    "hires": "Hires",
    "placements": "Placements",
}


def prettify_dataframe(dataframe):
    """Return a presentation-only copy with recruiter-friendly labels."""

    display_df = dataframe.copy()

    display_df = display_df.rename(
        columns={
            column: DISPLAY_COLUMN_NAMES.get(
                column,
                column.replace("_", " ").title(),
            )
            for column in display_df.columns
        }
    )

    for column in display_df.columns:

        normalized = column.lower()

        if (
            "rate" in normalized
            or "score" in normalized
            or "match %" in normalized
        ):

            if pd.api.types.is_numeric_dtype(display_df[column]):

                display_df[column] = display_df[column].map(
                    lambda value: (
                        f"{float(value):.2f}%"
                        if pd.notna(value)
                        else ""
                    )
                )

        elif "salary" in normalized:

            if pd.api.types.is_numeric_dtype(display_df[column]):

                display_df[column] = display_df[column].map(
                    lambda value: (
                        f"${float(value):,.0f}"
                        if pd.notna(value)
                        else ""
                    )
                )

    return display_df


# =============================================================
# AI RESOURCE LOADER
# =============================================================

@st.cache_resource(
    show_spinner=False
)
def load_ai_resources():

    model = load_embedding_model()

    documents = load_resume_documents()

    records, embeddings = build_resume_index(
        model,
        documents
    )

    return (
        model,
        documents,
        records,
        embeddings,
    )


# =============================================================
# HEADER
# =============================================================

st.markdown(
    """
    <div class="ti-brand">
        <div>
            <div class="ti-eyebrow">AI Recruitment Intelligence</div>
            <div class="talentiq-title">TalentIQ</div>
            <div class="talentiq-subtitle">
                Recruitment analytics, candidate intelligence and local AI —
                in one hiring workspace.
            </div>
        </div>
        <div class="ti-badges">
            <span class="ti-badge"><span class="ti-dot">●</span>AI Online</span>
            <span class="ti-badge"><span class="ti-dot">●</span>Database Connected</span>
            <span class="ti-badge">100% Local AI</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="ti-sidebar-brand">
            <strong>🧠 TalentIQ</strong>
            <div class="ti-sidebar-sub">AI Recruitment Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "AI Hiring Assistant",
            "Candidate Matcher",
            "Resume Analyzer",
            "Resume → Job Matcher",
            "Recruitment Analytics",
        ],
    )

    st.divider()

    st.caption("SYSTEM STATUS")

    st.markdown(
        """
        <div class="ti-status">
            <div class="ti-status-row">
                <span>AI Engine</span>
                <span class="ti-status-online">● Online</span>
            </div>
            <div class="ti-status-row">
                <span>PostgreSQL</span>
                <span class="ti-status-online">● Connected</span>
            </div>
            <div class="ti-status-row">
                <span>Embedding Model</span>
                <span class="ti-status-online">● Ready</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("TalentIQ v1.0 • Llama 3.2 • Local AI")


# =============================================================
# EXECUTIVE OVERVIEW PAGE
# =============================================================

if page == "Executive Overview":

    st.header(
        "Executive Recruitment Overview"
    )

    st.caption(
        "A live snapshot of hiring volume, conversion and funnel performance."
    )


    # ---------------------------------------------------------
    # LOAD KPIs
    # ---------------------------------------------------------

    try:

        kpis = load_executive_kpis()

    except Exception as error:

        st.error(
            "Unable to load executive KPIs."
        )

        st.exception(
            error
        )

        st.stop()


    if not kpis:

        st.warning(
            "No executive KPI data was found."
        )

        st.stop()


    # ---------------------------------------------------------
    # KPI ROW 1
    # ---------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Total Jobs",
            f"{int(kpis['total_jobs']):,}",
        )


    with col2:

        st.metric(
            "Open Jobs",
            f"{int(kpis['open_jobs']):,}",
        )


    with col3:

        st.metric(
            "Candidates",
            f"{int(kpis['total_candidates']):,}",
        )


    # ---------------------------------------------------------
    # KPI ROW 2
    # ---------------------------------------------------------

    col4, col5, col6 = st.columns(3)


    with col4:

        st.metric(
            "Applications",
            f"{int(kpis['total_applications']):,}",
        )


    with col5:

        st.metric(
            "Offers",
            f"{int(kpis['total_offers']):,}",
        )


    with col6:

        st.metric(
            "Placements",
            f"{int(kpis['total_placements']):,}",
        )


    st.divider()


    # ---------------------------------------------------------
    # CONVERSION METRICS
    # ---------------------------------------------------------

    st.subheader(
        "Recruitment Conversion"
    )

    application_to_offer = float(
        kpis["application_to_offer_rate"]
    )

    application_to_placement = float(
        kpis["application_to_placement_rate"]
    )

    offer_to_placement = kpis.get(
        "offer_to_placement_rate"
    )

    conv1, conv2, conv3 = st.columns(3)


    with conv1:

        st.metric(
            "Application → Offer",
            f"{application_to_offer:.2f}%",
        )


    with conv2:

        st.metric(
            "Application → Placement",
            f"{application_to_placement:.2f}%",
        )


    with conv3:

        if offer_to_placement is not None:

            offer_to_placement_value = (
                f"{float(offer_to_placement):.2f}%"
            )

        else:

            offer_to_placement_value = "N/A"

        st.metric(
            "Offer → Placement",
            offer_to_placement_value,
        )


    # ---------------------------------------------------------
    # FUNNEL
    # ---------------------------------------------------------

    st.divider()

    st.subheader(
        "Recruitment Funnel"
    )

    try:

        funnel_df = load_funnel()

        if not funnel_df.empty:

            funnel_chart = (
                funnel_df[
                    [
                        "current_stage",
                        "application_count",
                    ]
                ]
                .set_index(
                    "current_stage"
                )
            )

            st.bar_chart(
                funnel_chart
            )

            with st.expander(
                "View funnel data"
            ):

                display_funnel = (
                    funnel_df.copy()
                )

                display_funnel[
                    "percentage_of_total"
                ] = (
                    display_funnel[
                        "percentage_of_total"
                    ]
                    .map(
                        lambda x:
                        f"{float(x):.2f}%"
                    )
                )

                st.dataframe(
                    display_funnel,
                    width="stretch",
                    hide_index=True,
                )

    except Exception as error:

        st.warning(
            "Recruitment funnel could not be loaded."
        )

        st.exception(
            error
        )




# =============================================================
# AI HIRING ASSISTANT PAGE
# =============================================================

if page == "AI Hiring Assistant":

    st.header(
        "🤖 AI Hiring Assistant"
    )

    st.caption(
        "Ask natural-language questions across analytics, resumes, candidates, and job matches."
    )


    # ---------------------------------------------------------
    # LOAD AI
    # ---------------------------------------------------------

    with st.spinner(
        "Loading TalentIQ AI..."
    ):

        try:

            (
                model,
                documents,
                records,
                embeddings,

            ) = load_ai_resources()


        except Exception as error:

            st.error(
                "TalentIQ AI could not be loaded."
            )

            st.exception(
                error
            )

            st.stop()


    # ---------------------------------------------------------
    # AI STATUS
    # ---------------------------------------------------------

    status_col1, status_col2, status_col3 = (
        st.columns(3)
    )


    with status_col1:

        st.metric(
            "Analyzed Resumes",
            len(documents),
        )


    with status_col2:

        st.metric(
            "Resume Chunks",
            len(records),
        )


    with status_col3:

        st.metric(
            "LLM",
            "Llama 3.2 3B",
        )


    # ---------------------------------------------------------
    # EXAMPLE QUESTIONS
    # ---------------------------------------------------------

    with st.expander(
        "💡 Example questions"
    ):

        st.markdown(
            """
            **Recruitment Analytics**

            - How many applications are there?
            - How many applications are in Interview stage?
            - Who is the top recruiter?
            - How many open jobs are older than 90 days?
            - Show me the recruitment funnel.

            **Resume Intelligence**

            - Summarize Arjun Maske's resume.
            - What automation experience is mentioned in Arjun Maske's resume?

            **Candidate Matching**

            - Who are the best candidates for job 953?

            **Job Recommendations**

            - What are the best jobs for Arjun?
            """
        )


    # ---------------------------------------------------------
    # CHAT SESSION
    # ---------------------------------------------------------

    if "messages" not in st.session_state:

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello. I'm TalentIQ, your AI hiring "
                    "assistant. Ask me about recruitment "
                    "analytics, resumes, candidates, or jobs."
                ),
            }
        ]


    # ---------------------------------------------------------
    # CLEAR CHAT
    # ---------------------------------------------------------

    if st.button(
        "Clear conversation"
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Conversation cleared. "
                    "What would you like to analyze?"
                ),
            }
        ]

        st.rerun()


    st.divider()


    # ---------------------------------------------------------
    # DISPLAY CHAT HISTORY
    # ---------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # ---------------------------------------------------------
    # CHAT INPUT
    # ---------------------------------------------------------

    prompt = st.chat_input(
        "Ask TalentIQ a hiring or recruitment question..."
    )


    if prompt:

        # -----------------------------------------------------
        # USER MESSAGE
        # -----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )


        with st.chat_message(
            "user"
        ):

            st.markdown(
                prompt
            )


        # -----------------------------------------------------
        # TALENTIQ RESPONSE
        # -----------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "TalentIQ is analyzing..."
            ):

                try:

                    response = answer_question(

                        question=prompt,

                        model=model,

                        documents=documents,

                        records=records,

                        embeddings=embeddings,
                    )


                    st.markdown(
                        response
                    )


                except Exception as error:

                    response = (
                        "TalentIQ encountered an error "
                        "while processing this question."
                    )


                    st.error(
                        response
                    )


                    st.exception(
                        error
                    )


        # -----------------------------------------------------
        # SAVE ASSISTANT MESSAGE
        # -----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        # =============================================================
# CANDIDATE MATCHER PAGE
# =============================================================

if page == "Candidate Matcher":

    st.header(
        "🎯 AI Candidate Matcher"
    )

    st.caption(
        "Select an open role and rank candidates using structured fit plus semantic similarity."
    )


    # ---------------------------------------------------------
    # LOAD OPEN JOBS
    # ---------------------------------------------------------

    try:

        jobs_df = load_open_jobs()

    except Exception as error:

        st.error(
            "Unable to load open jobs."
        )

        st.exception(
            error
        )

        st.stop()


    if jobs_df.empty:

        st.warning(
            "No open jobs were found."
        )

        st.stop()


    # ---------------------------------------------------------
    # JOB SELECTOR
    # ---------------------------------------------------------

    jobs_df["display_name"] = (
        jobs_df["job_code"]
        + " | "
        + jobs_df["job_title"]
    )


    selected_display = st.selectbox(
        "Select Job",
        jobs_df["display_name"].tolist(),
    )


    selected_job = jobs_df[
        jobs_df["display_name"]
        ==
        selected_display
    ].iloc[0]


    job_id = int(
        selected_job["job_id"]
    )

    job_code = selected_job[
        "job_code"
    ]

    job_title = selected_job[
        "job_title"
    ]


    # ---------------------------------------------------------
    # JOB INFORMATION
    # ---------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Job ID",
            job_id
        )


    with col2:

        st.metric(
            "Job Code",
            job_code
        )


    with col3:

        st.metric(
            "Position",
            job_title
        )


    st.divider()


    # ---------------------------------------------------------
    # OUTPUT FILE
    # ---------------------------------------------------------

    ranking_file = (
        PROJECT_ROOT
        / "outputs"
        / "predictions"
        / "semantic_matching"
        / f"{job_code}_top_20_hybrid.csv"
    )


    # ---------------------------------------------------------
    # CHECK EXISTING MATCH
    # ---------------------------------------------------------

    if ranking_file.exists():

        st.success(
            "A candidate ranking already exists "
            "for this job."
        )

        ranking_df = pd.read_csv(
            ranking_file
        )


    else:

        ranking_df = None

        st.info(
            "No semantic candidate ranking has "
            "been generated for this job yet."
        )


    # ---------------------------------------------------------
    # RUN MATCHING ENGINE
    # ---------------------------------------------------------

    run_matching = st.button(
        "🚀 Run / Refresh Candidate Matching",
        type="primary",
    )


    if run_matching:

        matcher_script = (
            PROJECT_ROOT
            / "src"
            / "talentiq"
            / "ai"
            / "embeddings"
            / "semantic_matcher.py"
        )


        with st.spinner(
            "TalentIQ is evaluating candidates. "
            "This may take around a minute..."
        ):

            result = subprocess.run(
                [
                    sys.executable,
                    str(matcher_script),
                    "--job-id",
                    str(job_id),
                ],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )


        if result.returncode == 0:

            st.success(
                "Candidate matching completed successfully."
            )


            if ranking_file.exists():

                ranking_df = pd.read_csv(
                    ranking_file
                )

            else:

                st.error(
                    "Matching completed, but the ranking "
                    "file was not found."
                )


        else:

            st.error(
                "Candidate matching failed."
            )

            with st.expander(
                "View error details"
            ):

                st.code(
                    result.stdout
                    + "\n"
                    + result.stderr
                )


    # ---------------------------------------------------------
    # DISPLAY RESULTS
    # ---------------------------------------------------------

    if ranking_df is not None:

        st.divider()

        st.subheader(
            "🏆 Top Candidate Matches"
        )


        # -----------------------------------------------------
        # SUMMARY METRICS
        # -----------------------------------------------------

        metric1, metric2, metric3 = st.columns(3)


        with metric1:

            st.metric(
                "Candidates Ranked",
                len(ranking_df),
            )


        with metric2:

            highest_score = float(
                ranking_df[
                    "hybrid_match_score"
                ].max()
            )

            st.metric(
                "Best Match",
                f"{highest_score:.2f}%",
            )


        with metric3:

            recommended_count = (
                ranking_df[
                    "hybrid_recommendation"
                ]
                .astype(str)
                .str.contains(
                    "RECOMMENDED",
                    case=False,
                    na=False,
                )
                .sum()
            )

            st.metric(
                "Recommended",
                int(recommended_count),
            )


        # -----------------------------------------------------
        # DISPLAY TABLE
        # -----------------------------------------------------

        display_columns = [
            "hybrid_rank",
            "candidate_name",
            "candidate_experience",
            "must_have_match_rate",
            "structured_match_score",
            "semantic_match_score",
            "hybrid_match_score",
            "hybrid_recommendation",
            "has_already_applied",
        ]


        available_columns = [
            column
            for column in display_columns
            if column in ranking_df.columns
        ]


        display_df = ranking_df[
            available_columns
        ].copy()


        rename_map = {
            "hybrid_rank": "Rank",
            "candidate_name": "Candidate",
            "candidate_experience": "Experience",
            "must_have_match_rate": "Must-Have Match %",
            "structured_match_score": "Structured %",
            "semantic_match_score": "Semantic %",
            "hybrid_match_score": "Hybrid %",
            "hybrid_recommendation": "Recommendation",
            "has_already_applied": "Already Applied",
        }


        display_df = display_df.rename(
            columns=rename_map
        )


        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
        )


        # -----------------------------------------------------
        # TOP CANDIDATE DETAILS
        # -----------------------------------------------------

        st.subheader(
            "🥇 Best Candidate"
        )

        st.caption(
            "Highest-ranked candidate after structured and semantic scoring."
        )


        best_candidate = (
            ranking_df.iloc[0]
        )


        best1, best2, best3 = (
            st.columns(3)
        )


        with best1:

            st.metric(
                "Candidate",
                best_candidate[
                    "candidate_name"
                ],
            )


        with best2:

            best_score = float(
                best_candidate[
                    "hybrid_match_score"
                ]
            )

            st.metric(
                "Hybrid Match",
                f"{best_score:.2f}%",
            )


        with best3:

            st.metric(
                "Recommendation",
                best_candidate[
                    "hybrid_recommendation"
                ],
            )


# =============================================================
# RESUME ANALYZER PAGE
# =============================================================

if page == "Resume Analyzer":

    st.header(
        "📄 AI Resume Analyzer"
    )

    st.caption(
        "Turn a PDF or TXT resume into a structured recruiter-ready candidate profile."
    )


    # ---------------------------------------------------------
    # RESUME UPLOAD
    # ---------------------------------------------------------

    uploaded_resume = st.file_uploader(
        "Upload Resume",
        type=["pdf", "txt"],
        accept_multiple_files=False,
        key="resume_analyzer_upload",
    )


    if uploaded_resume is None:

        st.info(
            "Upload a PDF or TXT resume to begin analysis."
        )


    else:

        # -----------------------------------------------------
        # FILE INFORMATION
        # -----------------------------------------------------

        file_col1, file_col2 = st.columns(2)


        with file_col1:

            st.metric(
                "File",
                uploaded_resume.name,
            )


        with file_col2:

            file_size_kb = (
                len(uploaded_resume.getvalue())
                / 1024
            )

            st.metric(
                "Size",
                f"{file_size_kb:.1f} KB",
            )


        # -----------------------------------------------------
        # SAVE UPLOADED RESUME
        # -----------------------------------------------------

        resumes_dir = (
            PROJECT_ROOT
            / "resumes"
        )

        resumes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


        safe_filename = Path(
            uploaded_resume.name
        ).name


        saved_resume_path = (
            resumes_dir
            / safe_filename
        )


        saved_resume_path.write_bytes(
            uploaded_resume.getvalue()
        )


        # -----------------------------------------------------
        # ANALYZE BUTTON
        # -----------------------------------------------------

        analyze_button = st.button(
            "🧠 Analyze Resume",
            type="primary",
            key="analyze_resume_button",
        )


        if analyze_button:

            with st.spinner(
                "TalentIQ is analyzing the resume..."
            ):

                try:

                    if not hasattr(
                        resume_analyzer,
                        "analyze_resume"
                    ):

                        raise AttributeError(
                            "resume_analyzer.py does not expose "
                            "an analyze_resume() function."
                        )


                    profile = (
                        resume_analyzer
                        .analyze_resume(
                            str(saved_resume_path)
                        )
                    )


                    st.session_state[
                        "resume_profile"
                    ] = profile


                    st.session_state[
                        "resume_filename"
                    ] = safe_filename


                    st.success(
                        "Resume analysis completed successfully."
                    )


                except Exception as error:

                    st.error(
                        "TalentIQ could not analyze this resume."
                    )

                    st.exception(
                        error
                    )


        # -----------------------------------------------------
        # DISPLAY PROFILE
        # -----------------------------------------------------

        profile = st.session_state.get(
            "resume_profile"
        )

        analyzed_filename = st.session_state.get(
            "resume_filename"
        )

        # Only display a stored profile when it belongs to the
        # resume currently selected in the uploader.
        if profile and analyzed_filename == safe_filename:

            st.divider()

            st.subheader(
                "👤 Candidate Profile"
            )


            # -------------------------------------------------
            # PROFILE METRICS
            # -------------------------------------------------

            candidate_name = profile.get(
                "possible_name"
            )

            if not candidate_name:

                candidate_name = (
                    Path(safe_filename)
                    .stem
                    .replace("_", " ")
                    .strip()
                )


            experience = profile.get(
                "estimated_experience_years"
            )


            skills = profile.get(
                "skills",
                [],
            )


            skill_count = profile.get(
                "skill_count",
                len(skills),
            )


            page_count = profile.get(
                "page_count",
                "N/A",
            )


            profile_col1, profile_col2, profile_col3, profile_col4 = (
                st.columns(4)
            )


            with profile_col1:

                st.metric(
                    "Candidate",
                    candidate_name or "Not detected",
                )


            with profile_col2:

                if experience is not None:

                    experience_display = (
                        f"{float(experience):.1f} years"
                    )

                else:

                    experience_display = "Not detected"


                st.metric(
                    "Experience",
                    experience_display,
                )


            with profile_col3:

                st.metric(
                    "Skills Detected",
                    int(skill_count),
                )


            with profile_col4:

                st.metric(
                    "Resume Pages",
                    page_count,
                )


            # -------------------------------------------------
            # CONTACT INFORMATION
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "📬 Contact Information"
            )


            contact_col1, contact_col2 = (
                st.columns(2)
            )


            with contact_col1:

                email = profile.get(
                    "email"
                )

                st.write(
                    "**Email:**",
                    email or "Not detected",
                )


            with contact_col2:

                phone = profile.get(
                    "phone"
                )

                st.write(
                    "**Phone:**",
                    phone or "Not detected",
                )


            # -------------------------------------------------
            # SKILLS
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "🛠️ Technical Skills"
            )


            if skills:

                skills_text = " • ".join(
                    skills
                )

                st.info(
                    skills_text
                )

            else:

                st.warning(
                    "No TalentIQ skills were detected "
                    "in this resume."
                )


            # -------------------------------------------------
            # EDUCATION
            # -------------------------------------------------

            st.subheader(
                "🎓 Education"
            )


            education = profile.get(
                "education_keywords",
                [],
            )


            if education:

                if isinstance(
                    education,
                    list
                ):

                    education_text = ", ".join(
                        education
                    )

                else:

                    education_text = str(
                        education
                    )


                st.write(
                    education_text
                )

            else:

                st.write(
                    "No education information detected."
                )


            # -------------------------------------------------
            # DETECTED ROLES
            # -------------------------------------------------

            st.subheader(
                "💼 Detected Roles"
            )


            roles = profile.get(
                "detected_roles",
                [],
            )


            if roles:

                for role in roles:

                    st.write(
                        f"• {role}"
                    )

            else:

                st.write(
                    "No TalentIQ job title was "
                    "matched exactly."
                )


            # -------------------------------------------------
            # ADDITIONAL INFORMATION
            # -------------------------------------------------

            with st.expander(
                "🔍 Additional Resume Details"
            ):

                detail_col1, detail_col2 = (
                    st.columns(2)
                )


                with detail_col1:

                    st.write(
                        "**Location:**",
                        profile.get(
                            "location"
                        )
                        or
                        "Not detected",
                    )


                    st.write(
                        "**Work Authorization:**",
                        profile.get(
                            "work_authorization"
                        )
                        or
                        "Not detected",
                    )


                with detail_col2:

                    st.write(
                        "**Characters Extracted:**",
                        profile.get(
                            "character_count",
                            "N/A",
                        ),
                    )


                    st.write(
                        "**Words Extracted:**",
                        profile.get(
                            "word_count",
                            "N/A",
                        ),
                    )


            # -------------------------------------------------
            # RAW PROFILE
            # -------------------------------------------------

            with st.expander(
                "🧾 View Structured TalentIQ Profile"
            ):

                st.json(
                    profile
                )



# =============================================================
# RESUME → JOB MATCHER PAGE
# =============================================================

if page == "Resume → Job Matcher":

    st.header(
        "🔎 Resume → Job Matcher"
    )

    st.caption(
        "Upload a resume and rank the strongest open-job matches using hybrid AI scoring."
    )


    # ---------------------------------------------------------
    # RESUME UPLOAD
    # ---------------------------------------------------------

    uploaded_match_resume = st.file_uploader(
        "Upload Resume for Job Matching",
        type=["pdf", "txt"],
        accept_multiple_files=False,
        key="resume_job_matcher_upload",
    )


    if uploaded_match_resume is None:

        st.info(
            "Upload a PDF or TXT resume to find matching jobs."
        )


    else:

        # -----------------------------------------------------
        # FILE INFORMATION
        # -----------------------------------------------------

        match_file_col1, match_file_col2 = st.columns(2)

        with match_file_col1:

            st.metric(
                "Resume",
                uploaded_match_resume.name,
            )

        with match_file_col2:

            match_file_size_kb = (
                len(uploaded_match_resume.getvalue())
                / 1024
            )

            st.metric(
                "Size",
                f"{match_file_size_kb:.1f} KB",
            )


        # -----------------------------------------------------
        # SAVE UPLOADED RESUME
        # -----------------------------------------------------

        resumes_dir = PROJECT_ROOT / "resumes"

        resumes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_match_filename = Path(
            uploaded_match_resume.name
        ).name

        saved_match_resume_path = (
            resumes_dir
            / safe_match_filename
        )

        saved_match_resume_path.write_bytes(
            uploaded_match_resume.getvalue()
        )


        # If the user uploads a different resume, do not show an
        # old ranking from the previous upload.
        previous_match_name = st.session_state.get(
            "resume_job_uploaded_name"
        )

        if (
            previous_match_name is not None
            and previous_match_name != safe_match_filename
        ):

            st.session_state.pop(
                "resume_job_ranking_path",
                None,
            )


        # -----------------------------------------------------
        # MATCHING SCOPE
        # -----------------------------------------------------

        match_all_jobs = st.checkbox(
            "Include closed / non-open jobs",
            value=False,
            help=(
                "By default TalentIQ matches the resume only "
                "against currently open jobs."
            ),
        )


        # -----------------------------------------------------
        # RUN MATCHING ENGINE
        # -----------------------------------------------------

        run_resume_matching = st.button(
            "🚀 Find Best Jobs",
            type="primary",
            key="run_resume_job_matching",
        )


        if run_resume_matching:

            matcher_script = (
                PROJECT_ROOT
                / "src"
                / "talentiq"
                / "ai"
                / "matching"
                / "resume_job_matcher.py"
            )

            output_dir = (
                PROJECT_ROOT
                / "outputs"
                / "predictions"
                / "resume_job_matching"
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            before_files = {
                file_path: file_path.stat().st_mtime
                for file_path in output_dir.glob(
                    "*_top_20_jobs.csv"
                )
            }

            command = [
                sys.executable,
                str(matcher_script),
                "--resume",
                str(saved_match_resume_path),
            ]

            if match_all_jobs:

                command.append(
                    "--all-jobs"
                )


            with st.spinner(
                "TalentIQ is analyzing the resume and ranking jobs. "
                "This can take several seconds..."
            ):

                result = subprocess.run(
                    command,
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                )


            if result.returncode == 0:

                top_files = list(
                    output_dir.glob(
                        "*_top_20_jobs.csv"
                    )
                )

                changed_files = []

                for file_path in top_files:

                    old_mtime = before_files.get(
                        file_path
                    )

                    new_mtime = file_path.stat().st_mtime

                    if (
                        old_mtime is None
                        or new_mtime > old_mtime
                    ):

                        changed_files.append(
                            file_path
                        )


                if changed_files:

                    ranking_file = max(
                        changed_files,
                        key=lambda path: path.stat().st_mtime,
                    )

                elif top_files:

                    ranking_file = max(
                        top_files,
                        key=lambda path: path.stat().st_mtime,
                    )

                else:

                    ranking_file = None


                if ranking_file is not None:

                    st.session_state[
                        "resume_job_ranking_path"
                    ] = str(ranking_file)

                    st.session_state[
                        "resume_job_uploaded_name"
                    ] = safe_match_filename

                    st.success(
                        "Resume-to-job matching completed successfully."
                    )

                else:

                    st.error(
                        "Matching completed, but TalentIQ could not "
                        "locate the top-job ranking output."
                    )


                with st.expander(
                    "View matching engine output"
                ):

                    st.code(
                        result.stdout
                        or "Matching completed without console output."
                    )


            else:

                st.error(
                    "Resume-to-job matching failed."
                )

                with st.expander(
                    "View error details"
                ):

                    st.code(
                        result.stdout
                        + "\n"
                        + result.stderr
                    )


        # -----------------------------------------------------
        # LOAD SAVED RANKING
        # -----------------------------------------------------

        ranking_path_value = st.session_state.get(
            "resume_job_ranking_path"
        )

        ranking_df = None

        if ranking_path_value:

            ranking_path = Path(
                ranking_path_value
            )

            if ranking_path.exists():

                try:

                    ranking_df = pd.read_csv(
                        ranking_path
                    )

                except Exception as error:

                    st.error(
                        "TalentIQ could not read the saved job ranking."
                    )

                    st.exception(
                        error
                    )


        # -----------------------------------------------------
        # DISPLAY RESULTS
        # -----------------------------------------------------

        if ranking_df is not None and not ranking_df.empty:

            st.divider()

            st.subheader(
                "🏆 Best Matching Jobs"
            )


            # -------------------------------------------------
            # SUMMARY METRICS
            # -------------------------------------------------

            summary1, summary2, summary3 = st.columns(3)

            with summary1:

                st.metric(
                    "Top Results",
                    len(ranking_df),
                )


            hybrid_column = (
                "hybrid_match_score"
                if "hybrid_match_score" in ranking_df.columns
                else None
            )

            recommendation_column = (
                "recommendation"
                if "recommendation" in ranking_df.columns
                else None
            )


            with summary2:

                if hybrid_column:

                    best_match_score = float(
                        ranking_df[
                            hybrid_column
                        ].max()
                    )

                    best_match_display = (
                        f"{best_match_score:.2f}%"
                    )

                else:

                    best_match_display = "N/A"

                st.metric(
                    "Best Match",
                    best_match_display,
                )


            with summary3:

                if recommendation_column:

                    recommended_jobs = (
                        ranking_df[
                            recommendation_column
                        ]
                        .astype(str)
                        .str.fullmatch(
                            "RECOMMENDED",
                            case=False,
                            na=False,
                        )
                        .sum()
                    )

                    recommended_display = int(
                        recommended_jobs
                    )

                else:

                    recommended_display = "N/A"

                st.metric(
                    "Recommended",
                    recommended_display,
                )


            # -------------------------------------------------
            # BEST JOB CARD
            # -------------------------------------------------

            best_job = ranking_df.iloc[0]

            st.subheader(
                "🥇 Best Job Match"
            )

            st.caption(
                "Highest-ranked role after skill, experience, and semantic-fit scoring."
            )

            best_job_col1, best_job_col2, best_job_col3 = (
                st.columns(3)
            )

            with best_job_col1:

                st.metric(
                    "Position",
                    best_job.get(
                        "job_title",
                        "N/A",
                    ),
                )

            with best_job_col2:

                st.metric(
                    "Job Code",
                    best_job.get(
                        "job_code",
                        "N/A",
                    ),
                )

            with best_job_col3:

                if hybrid_column:

                    top_score = float(
                        best_job[
                            hybrid_column
                        ]
                    )

                    top_score_display = (
                        f"{top_score:.2f}%"
                    )

                else:

                    top_score_display = "N/A"

                st.metric(
                    "Hybrid Match",
                    top_score_display,
                )


            if recommendation_column:

                st.write(
                    "**Recommendation:**",
                    best_job.get(
                        recommendation_column,
                        "N/A",
                    ),
                )


            # -------------------------------------------------
            # RANKING TABLE
            # -------------------------------------------------

            st.subheader(
                "📋 Job Ranking"
            )

            display_columns = [
                "hybrid_rank",
                "job_code",
                "job_title",
                "job_status",
                "required_experience",
                "must_have_match_rate",
                "skill_match_score",
                "experience_score",
                "structured_match_score",
                "semantic_match_score",
                "hybrid_match_score",
                "recommendation",
            ]

            available_columns = [
                column
                for column in display_columns
                if column in ranking_df.columns
            ]

            if available_columns:

                display_df = ranking_df[
                    available_columns
                ].copy()

            else:

                display_df = ranking_df.copy()


            rename_map = {
                "hybrid_rank": "Rank",
                "job_code": "Job Code",
                "job_title": "Job Title",
                "job_status": "Status",
                "required_experience": "Required Experience",
                "must_have_match_rate": "Must-Have Match %",
                "skill_match_score": "Skill Match %",
                "experience_score": "Experience %",
                "structured_match_score": "Structured %",
                "semantic_match_score": "Semantic %",
                "hybrid_match_score": "Hybrid %",
                "recommendation": "Recommendation",
            }

            display_df = display_df.rename(
                columns=rename_map
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True,
            )


            # -------------------------------------------------
            # SCORE EXPLANATION
            # -------------------------------------------------

            with st.expander(
                "How TalentIQ calculates job matches"
            ):

                st.markdown(
                    """
                    TalentIQ combines two matching layers:

                    - **Structured matching** checks detected resume skills,
                      must-have job requirements, and experience alignment.
                    - **Semantic matching** compares the meaning of the resume
                      with each job profile using sentence-transformer embeddings.
                    - **Hybrid score** combines both signals while preserving
                      the must-have skill gate used by the matching engine.
                    """
                )

# =============================================================
# RECRUITMENT ANALYTICS PAGE
# =============================================================

if page == "Recruitment Analytics":

    st.header(
        "📊 Recruitment Analytics"
    )

    st.caption(
        "Explore recruiter performance, job aging, client outcomes, placements, and hiring trends."
    )

    # =========================================================
    # ANALYTICS TABS
    # =========================================================

    (
        recruiter_tab,
        aging_tab,
        client_tab,
        placement_tab,
        trends_tab,

    ) = st.tabs(
        [
            "👥 Recruiters",
            "⏳ Job Aging",
            "🏢 Clients",
            "🎯 Placements",
            "📈 Trends",
        ]
    )


    # =========================================================
    # 1. RECRUITER PERFORMANCE
    # =========================================================

    with recruiter_tab:

        st.subheader(
            "👥 Recruiter Performance"
        )

        st.caption(
            "Compare recruiter workload, hiring outcomes, "
            "and placement performance."
        )

        try:

            recruiter_df = load_dashboard_view(
                "vw_dashboard_recruiter_performance"
            )

            if recruiter_df.empty:

                st.info(
                    "No recruiter performance data found."
                )

            else:

                # ---------------------------------------------
                # SUMMARY METRICS
                # ---------------------------------------------

                total_recruiters = len(
                    recruiter_df
                )

                total_placements = (
                    recruiter_df[
                        "placement_count"
                    ].sum()
                    if "placement_count"
                    in recruiter_df.columns
                    else 0
                )

                total_hired = (
                    recruiter_df[
                        "hired_count"
                    ].sum()
                    if "hired_count"
                    in recruiter_df.columns
                    else 0
                )

                r1, r2, r3 = st.columns(3)

                with r1:

                    st.metric(
                        "Recruiters",
                        f"{total_recruiters:,}",
                    )

                with r2:

                    st.metric(
                        "Total Hires",
                        f"{int(total_hired):,}",
                    )

                with r3:

                    st.metric(
                        "Total Placements",
                        f"{int(total_placements):,}",
                    )


                st.divider()


                # ---------------------------------------------
                # RECRUITER CHART
                # ---------------------------------------------

                if (
                    "recruiter_id"
                    in recruiter_df.columns
                    and
                    "placement_count"
                    in recruiter_df.columns
                ):

                    chart_df = recruiter_df[
                        [
                            "recruiter_id",
                            "placement_count",
                        ]
                    ].copy()

                    chart_df[
                        "recruiter_id"
                    ] = (
                        "Recruiter "
                        +
                        chart_df[
                            "recruiter_id"
                        ].astype(str)
                    )

                    chart_df = (
                        chart_df
                        .set_index(
                            "recruiter_id"
                        )
                    )

                    st.subheader(
                        "Placements by Recruiter"
                    )

                    st.bar_chart(
                        chart_df
                    )


                # ---------------------------------------------
                # TABLE
                # ---------------------------------------------

                st.subheader(
                    "Recruiter Details"
                )

                recruiter_display = (
                    recruiter_df.copy()
                )

                recruiter_display = (
                    recruiter_display
                    .sort_values(
                        by=(
                            "placement_count"
                            if "placement_count"
                            in recruiter_display.columns
                            else recruiter_display.columns[0]
                        ),
                        ascending=False,
                    )
                )

                recruiter_display = prettify_dataframe(
                    recruiter_display
                )

                st.dataframe(
                    recruiter_display,
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            st.error(
                "Recruiter analytics could not be loaded."
            )

            st.exception(
                error
            )


    # =========================================================
    # 2. JOB AGING
    # =========================================================

    with aging_tab:

        st.subheader(
            "⏳ Job Aging Analysis"
        )

        st.caption(
            "Identify open positions that may require "
            "recruitment attention."
        )

        try:

            aging_df = load_dashboard_view(
                "vw_dashboard_job_aging"
            )

            if aging_df.empty:

                st.info(
                    "No job aging data found."
                )

            else:

                # ---------------------------------------------
                # OPEN JOBS ONLY
                # ---------------------------------------------

                if "job_status" in aging_df.columns:

                    open_aging_df = aging_df[
                        aging_df[
                            "job_status"
                        ]
                        .astype(str)
                        .str.lower()
                        ==
                        "open"
                    ].copy()

                else:

                    open_aging_df = (
                        aging_df.copy()
                    )


                # ---------------------------------------------
                # METRICS
                # ---------------------------------------------

                total_open = len(
                    open_aging_df
                )

                if "job_age_days" in open_aging_df.columns:

                    jobs_90_plus = (
                        open_aging_df[
                            "job_age_days"
                        ]
                        .ge(90)
                        .sum()
                    )

                    avg_age = (
                        open_aging_df[
                            "job_age_days"
                        ]
                        .mean()
                    )

                    oldest_age = (
                        open_aging_df[
                            "job_age_days"
                        ]
                        .max()
                    )

                else:

                    jobs_90_plus = 0
                    avg_age = 0
                    oldest_age = 0


                a1, a2, a3, a4 = (
                    st.columns(4)
                )

                with a1:

                    st.metric(
                        "Open Jobs",
                        f"{total_open:,}",
                    )

                with a2:

                    st.metric(
                        "90+ Day Jobs",
                        f"{int(jobs_90_plus):,}",
                    )

                with a3:

                    st.metric(
                        "Average Age",
                        f"{avg_age:.1f} days",
                    )

                with a4:

                    st.metric(
                        "Oldest Job",
                        f"{int(oldest_age)} days",
                    )


                st.divider()


                # ---------------------------------------------
                # AGING BUCKETS
                # ---------------------------------------------

                if "aging_bucket" in open_aging_df.columns:

                    bucket_df = (
                        open_aging_df[
                            "aging_bucket"
                        ]
                        .value_counts()
                        .rename_axis(
                            "Aging Bucket"
                        )
                        .reset_index(
                            name="Jobs"
                        )
                    )

                    bucket_order = [
                        "0-29 DAYS",
                        "30-59 DAYS",
                        "60-89 DAYS",
                        "90+ DAYS",
                    ]

                    bucket_df[
                        "sort_order"
                    ] = (
                        bucket_df[
                            "Aging Bucket"
                        ]
                        .map(
                            {
                                value: index
                                for index, value
                                in enumerate(
                                    bucket_order
                                )
                            }
                        )
                        .fillna(99)
                    )

                    bucket_df = (
                        bucket_df
                        .sort_values(
                            "sort_order"
                        )
                        .drop(
                            columns=[
                                "sort_order"
                            ]
                        )
                    )

                    st.subheader(
                        "Open Jobs by Aging Bucket"
                    )

                    st.bar_chart(
                        bucket_df.set_index(
                            "Aging Bucket"
                        )
                    )


                # ---------------------------------------------
                # OLDEST OPEN JOBS
                # ---------------------------------------------

                st.subheader(
                    "Oldest Open Jobs"
                )

                if "job_age_days" in open_aging_df.columns:

                    oldest_jobs = (
                        open_aging_df
                        .sort_values(
                            "job_age_days",
                            ascending=False,
                        )
                        .head(20)
                    )

                else:

                    oldest_jobs = (
                        open_aging_df
                        .head(20)
                    )

                oldest_jobs_display = prettify_dataframe(
                    oldest_jobs
                )

                st.dataframe(
                    oldest_jobs_display,
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            st.error(
                "Job aging analytics could not be loaded."
            )

            st.exception(
                error
            )


    # =========================================================
    # 3. CLIENT PERFORMANCE
    # =========================================================

    with client_tab:

        st.subheader(
            "🏢 Client Performance"
        )

        st.caption(
            "Review recruitment activity and placement "
            "performance across clients."
        )

        try:

            client_df = load_dashboard_view(
                "vw_dashboard_client_analysis"
            )

            if client_df.empty:

                st.info(
                    "No client analytics data found."
                )

            else:

                # ---------------------------------------------
                # SUMMARY
                # ---------------------------------------------

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "Clients",
                        f"{len(client_df):,}",
                    )

                if "total_jobs" in client_df.columns:

                    client_jobs = (
                        client_df[
                            "total_jobs"
                        ].sum()
                    )

                else:

                    client_jobs = 0


                if "total_placements" in client_df.columns:

                    client_placements = (
                        client_df[
                            "total_placements"
                        ].sum()
                    )

                elif "placements" in client_df.columns:

                    client_placements = (
                        client_df[
                            "placements"
                        ].sum()
                    )

                elif "placement_count" in client_df.columns:

                    client_placements = (
                        client_df[
                            "placement_count"
                        ].sum()
                    )

                else:

                    client_placements = 0


                with c2:

                    st.metric(
                        "Jobs",
                        f"{int(client_jobs):,}",
                    )


                with c3:

                    st.metric(
                        "Placements",
                        f"{int(client_placements):,}",
                    )


                st.divider()


                # ---------------------------------------------
                # TABLE
                # ---------------------------------------------

                st.subheader(
                    "Client Performance Details"
                )

                client_display = prettify_dataframe(
                    client_df
                )

                st.dataframe(
                    client_display,
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            st.error(
                "Client analytics could not be loaded."
            )

            st.exception(
                error
            )


    # =========================================================
    # 4. PLACEMENT ANALYSIS
    # =========================================================

    with placement_tab:

        st.subheader(
            "🎯 Placement Analysis"
        )

        st.caption(
            "Monitor placement outcomes and placement "
            "performance."
        )

        try:

            placement_df = load_dashboard_view(
                "vw_dashboard_placement_analysis"
            )

            if placement_df.empty:

                st.info(
                    "No placement analytics data found."
                )

            else:

                st.metric(
                    "Placement Records",
                    f"{len(placement_df):,}",
                )

                st.divider()


                # ---------------------------------------------
                # STATUS DISTRIBUTION
                # ---------------------------------------------

                status_column = None

                for candidate_column in [
                    "placement_status",
                    "status",
                ]:

                    if (
                        candidate_column
                        in placement_df.columns
                    ):

                        status_column = (
                            candidate_column
                        )

                        break


                if status_column:

                    placement_status = (
                        placement_df[
                            status_column
                        ]
                        .value_counts()
                        .rename_axis(
                            "Placement Status"
                        )
                        .reset_index(
                            name="Placements"
                        )
                    )

                    st.subheader(
                        "Placement Outcomes"
                    )

                    st.bar_chart(
                        placement_status
                        .set_index(
                            "Placement Status"
                        )
                    )


                st.subheader(
                    "Placement Details"
                )

                placement_display = prettify_dataframe(
                    placement_df
                )

                st.dataframe(
                    placement_display,
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            st.error(
                "Placement analytics could not be loaded."
            )

            st.exception(
                error
            )


    # =========================================================
    # 5. RECRUITMENT TRENDS
    # =========================================================

    with trends_tab:

        st.subheader(
            "📈 Recruitment Trends"
        )

        st.caption(
            "Analyze recruitment activity over time."
        )

        try:

            trends_df = load_dashboard_view(
                "vw_dashboard_time_trends"
            )

            if trends_df.empty:

                st.info(
                    "No recruitment trend data found."
                )

            else:

                # ---------------------------------------------
                # FIND DATE COLUMN
                # ---------------------------------------------

                date_column = None

                possible_date_columns = [
                    "month",
                    "application_month",
                    "trend_month",
                    "month_start",
                ]

                for candidate_column in (
                    possible_date_columns
                ):

                    if (
                        candidate_column
                        in trends_df.columns
                    ):

                        date_column = (
                            candidate_column
                        )

                        break


                # ---------------------------------------------
                # FIND NUMERIC METRICS
                # ---------------------------------------------

                numeric_columns = (
                    trends_df
                    .select_dtypes(
                        include="number"
                    )
                    .columns
                    .tolist()
                )


                if (
                    date_column
                    and
                    numeric_columns
                ):

                    trend_chart = (
                        trends_df[
                            [
                                date_column,
                                *numeric_columns[
                                    :4
                                ],
                            ]
                        ]
                        .copy()
                    )

                    trend_chart[
                        date_column
                    ] = (
                        trend_chart[
                            date_column
                        ]
                        .astype(str)
                    )

                    trend_chart = (
                        trend_chart
                        .set_index(
                            date_column
                        )
                    )

                    st.subheader(
                        "Monthly Recruitment Activity"
                    )

                    st.line_chart(
                        trend_chart
                    )


                st.subheader(
                    "Monthly Recruitment Data"
                )

                trends_display = prettify_dataframe(
                    trends_df
                )

                st.dataframe(
                    trends_display,
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            st.error(
                "Recruitment trends could not be loaded."
            )

            st.exception(
                error
            )

# =============================================================
# GLOBAL FOOTER
# =============================================================

st.markdown(
    """
    <div class="ti-footer">
        <span><strong>TalentIQ v1.0</strong> · AI Recruitment Intelligence</span>
        <span>PostgreSQL · Sentence Transformers · Hybrid RAG · Llama 3.2 · Streamlit</span>
    </div>
    """,
    unsafe_allow_html=True,
)
