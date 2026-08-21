"""
================================================================
TALENTIQ AI RECRUITMENT PLATFORM
File: resume_analyzer.py

Purpose
-------
Extract and analyze candidate information from PDF/TXT resumes.

Features
--------
1. PDF / TXT text extraction
2. Text cleaning
3. Email extraction
4. Phone extraction
5. Candidate name estimation
6. Skill extraction using TalentIQ database skills
7. Years-of-experience estimation
8. Education detection
9. Role/title detection
10. Structured JSON output
11. Clean resume text output

Outputs
-------
outputs/reports/resume_analysis/

================================================================
"""

from pathlib import Path
import sys
import argparse
import json
import re

from pypdf import PdfReader
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
    sys.path.insert(
        0,
        str(SRC_DIR)
    )


from database.connection import get_connection


# =============================================================
# DIRECTORIES
# =============================================================

RESUME_DIR = (
    PROJECT_ROOT
    / "resumes"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "resume_analysis"
)

RESUME_DIR.mkdir(
    parents=True,
    exist_ok=True
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
    print("=" * 78)
    print(title)
    print("=" * 78)


# =============================================================
# DATABASE HELPER
# =============================================================

def load_query(query):

    with get_connection() as connection:

        result = connection.execute(
            text(query)
        )

        return result.fetchall()


# =============================================================
# LOAD TALENTIQ SKILLS
# =============================================================

def load_known_skills():

    rows = load_query(
        """
        SELECT
            skill_name
        FROM skills
        ORDER BY skill_name;
        """
    )

    skills = [
        row[0]
        for row in rows
        if row[0]
    ]

    return skills


# =============================================================
# LOAD TALENTIQ JOB TITLES
# =============================================================

def load_known_job_titles():

    rows = load_query(
        """
        SELECT DISTINCT
            job_title
        FROM jobs
        WHERE job_title IS NOT NULL
        ORDER BY job_title;
        """
    )

    titles = [
        row[0]
        for row in rows
        if row[0]
    ]

    return titles


# =============================================================
# PDF EXTRACTION
# =============================================================

def extract_pdf_text(file_path):

    reader = PdfReader(
        str(file_path)
    )

    if reader.is_encrypted:

        raise ValueError(
            "This PDF is encrypted/password protected."
        )


    pages = []


    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            page_text = (
                page.extract_text()
                or ""
            )

        except Exception as error:

            print(
                f"Warning: Could not extract "
                f"page {page_number}: {error}"
            )

            page_text = ""


        pages.append(
            page_text
        )


    full_text = "\n".join(
        pages
    )


    return (
        full_text,
        len(reader.pages)
    )


# =============================================================
# TXT EXTRACTION
# =============================================================

def extract_txt_text(file_path):

    text_content = (
        file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    )

    return (
        text_content,
        1
    )


# =============================================================
# EXTRACT RESUME TEXT
# =============================================================

def extract_resume_text(file_path):

    extension = (
        file_path.suffix.lower()
    )


    if extension == ".pdf":

        return extract_pdf_text(
            file_path
        )


    if extension == ".txt":

        return extract_txt_text(
            file_path
        )


    raise ValueError(
        "Unsupported resume format. "
        "Use PDF or TXT."
    )


# =============================================================
# CLEAN TEXT
# =============================================================

def clean_resume_text(raw_text):

    # Remove null characters
    text_value = raw_text.replace(
        "\x00",
        " "
    )


    # Normalize line endings
    text_value = text_value.replace(
        "\r\n",
        "\n"
    )

    text_value = text_value.replace(
        "\r",
        "\n"
    )


    # Clean repeated spaces
    text_value = re.sub(
        r"[ \t]+",
        " ",
        text_value
    )


    # Remove excessive blank lines
    text_value = re.sub(
        r"\n{3,}",
        "\n\n",
        text_value
    )


    return text_value.strip()


# =============================================================
# EMAIL EXTRACTION
# =============================================================

def extract_email(resume_text):

    pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b"
    )


    matches = re.findall(
        pattern,
        resume_text
    )


    if matches:

        return matches[0]


    return None


# =============================================================
# PHONE EXTRACTION
# =============================================================

def extract_phone(resume_text):

    pattern = (
        r"(?:\+?\d{1,3}[-.\s]?)?"
        r"(?:\(?\d{3}\)?[-.\s]?)?"
        r"\d{3}[-.\s]?\d{4}"
    )


    matches = re.findall(
        pattern,
        resume_text
    )


    for match in matches:

        digits = re.sub(
            r"\D",
            "",
            match
        )


        if 10 <= len(digits) <= 15:

            return match.strip()


    return None


# =============================================================
# POSSIBLE NAME
# =============================================================

def extract_possible_name(resume_text):

    """
    Simple heuristic only.

    Looks at the first few lines and selects a likely human name.
    This is deliberately labelled "possible_name" because
    deterministic name extraction is not guaranteed.
    """

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]


    blocked_words = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "summary",
        "professional summary",
    }


    for line in lines[:8]:

        lower_line = line.lower()


        if lower_line in blocked_words:
            continue


        if "@" in line:
            continue


        if re.search(
            r"\d{5,}",
            line
        ):
            continue


        words = line.split()


        if 2 <= len(words) <= 5:

            if all(
                re.fullmatch(
                    r"[A-Za-z.'-]+",
                    word
                )
                for word in words
            ):

                return line


    return None


# =============================================================
# PHRASE MATCHING
# =============================================================

def phrase_exists(
    resume_text_lower,
    phrase
):

    escaped = re.escape(
        phrase.lower()
    )


    pattern = (
        rf"(?<![a-z0-9])"
        rf"{escaped}"
        rf"(?![a-z0-9])"
    )


    return bool(
        re.search(
            pattern,
            resume_text_lower,
            flags=re.IGNORECASE
        )
    )


# =============================================================
# SKILL EXTRACTION
# =============================================================

def extract_skills(
    resume_text,
    known_skills
):

    resume_lower = (
        resume_text.lower()
    )


    detected = set()


    # ---------------------------------------------------------
    # Exact TalentIQ skill matching
    # ---------------------------------------------------------

    for skill in known_skills:

        if phrase_exists(
            resume_lower,
            skill
        ):

            detected.add(
                skill
            )


    # ---------------------------------------------------------
    # Common aliases
    # ---------------------------------------------------------

    aliases = {

        "postgres":
            "PostgreSQL",

        "postgres sql":
            "PostgreSQL",

        "gcp":
            "Google Cloud",

        "google cloud platform":
            "Google Cloud",

        "aws":
            "AWS",

        "amazon web services":
            "AWS",

        "azure":
            "Azure",

        "ms sql":
            "SQL Server",

        "mssql":
            "SQL Server",

        "sql server":
            "SQL Server",

        "sklearn":
            "scikit-learn",

        "scikit learn":
            "scikit-learn",

        "llm":
            "LLMs",

        "large language model":
            "LLMs",

        "large language models":
            "LLMs",

        "openai":
            "OpenAI API",

        "openai api":
            "OpenAI API",

        "powerbi":
            "Power BI",
    }


    known_lookup = {
        skill.lower():
        skill
        for skill in known_skills
    }


    for alias, canonical in aliases.items():

        if phrase_exists(
            resume_lower,
            alias
        ):

            canonical_key = (
                canonical.lower()
            )


            if canonical_key in known_lookup:

                detected.add(
                    known_lookup[
                        canonical_key
                    ]
                )


    return sorted(
        detected
    )


# =============================================================
# EXPERIENCE EXTRACTION
# =============================================================

def extract_experience_years(
    resume_text
):

    """
    Estimate explicitly stated years of experience.

    Examples:
        "5 years of experience"
        "8+ years experience"
        "10 yrs of professional experience"

    This is an estimate, not a guaranteed calculation.
    """

    patterns = [

        r"(\d{1,2}(?:\.\d+)?)"
        r"\s*\+?\s*"
        r"(?:years?|yrs?)"
        r"\s+(?:of\s+)?"
        r"(?:professional\s+)?"
        r"experience",

        r"experience\s+(?:of\s+)?"
        r"(\d{1,2}(?:\.\d+)?)"
        r"\s*\+?\s*"
        r"(?:years?|yrs?)",
    ]


    values = []


    for pattern in patterns:

        matches = re.findall(
            pattern,
            resume_text,
            flags=re.IGNORECASE
        )


        for match in matches:

            try:

                value = float(
                    match
                )


                if 0 <= value <= 40:

                    values.append(
                        value
                    )

            except ValueError:

                pass


    if not values:

        return None


    return max(
        values
    )


# =============================================================
# EDUCATION EXTRACTION
# =============================================================

def extract_education(
    resume_text
):

    education_terms = [

        "B.Tech",
        "BTech",
        "Bachelor of Technology",

        "B.E.",
        "Bachelor of Engineering",

        "B.Sc",
        "Bachelor of Science",

        "BCA",
        "Bachelor of Computer Applications",

        "M.Tech",
        "Master of Technology",

        "M.Sc",
        "Master of Science",

        "MCA",
        "Master of Computer Applications",

        "MBA",
        "Master of Business Administration",

        "PhD",
        "Doctor of Philosophy",
    ]


    detected = []


    for term in education_terms:

        if phrase_exists(
            resume_text.lower(),
            term
        ):

            detected.append(
                term
            )


    return sorted(
        set(detected)
    )


# =============================================================
# ROLE DETECTION
# =============================================================

def extract_roles(
    resume_text,
    known_job_titles
):

    detected_roles = []


    for title in known_job_titles:

        if phrase_exists(
            resume_text.lower(),
            title
        ):

            detected_roles.append(
                title
            )


    return sorted(
        set(detected_roles)
    )


# =============================================================
# EXTRACTION QUALITY
# =============================================================

def calculate_extraction_status(
    resume_text
):

    character_count = len(
        resume_text
    )


    word_count = len(
        resume_text.split()
    )


    if character_count < 100:

        return "INSUFFICIENT TEXT"


    if word_count < 50:

        return "LOW TEXT CONTENT"


    return "SUCCESS"


# =============================================================
# BUILD STRUCTURED PROFILE
# =============================================================

def build_resume_profile(
    file_path,
    resume_text,
    page_count,
    known_skills,
    known_job_titles
):

    skills = extract_skills(
        resume_text,
        known_skills
    )


    roles = extract_roles(
        resume_text,
        known_job_titles
    )


    education = extract_education(
        resume_text
    )


    profile = {

        "resume_file":
            file_path.name,

        "page_count":
            page_count,

        "character_count":
            len(resume_text),

        "word_count":
            len(resume_text.split()),

        "text_extraction_status":
            calculate_extraction_status(
                resume_text
            ),

        "possible_name":
            extract_possible_name(
                resume_text
            ),

        "email":
            extract_email(
                resume_text
            ),

        "phone":
            extract_phone(
                resume_text
            ),

        "estimated_experience_years":
            extract_experience_years(
                resume_text
            ),

        "skills":
            skills,

        "skill_count":
            len(skills),

        "detected_roles":
            roles,

        "education_keywords":
            education,

        # Reserved for later AI extraction
        "location":
            None,

        "work_authorization":
            None,
    }


    return profile


# =============================================================
# DISPLAY PROFILE
# =============================================================

def display_profile(profile):

    print_section(
        "RESUME ANALYSIS RESULT"
    )


    print(
        f"File                 : "
        f"{profile['resume_file']}"
    )

    print(
        f"Pages                : "
        f"{profile['page_count']}"
    )

    print(
        f"Words                : "
        f"{profile['word_count']:,}"
    )

    print(
        f"Extraction Status    : "
        f"{profile['text_extraction_status']}"
    )


    print(
        f"\nPossible Name        : "
        f"{profile['possible_name']}"
    )

    print(
        f"Email                : "
        f"{profile['email']}"
    )

    print(
        f"Phone                : "
        f"{profile['phone']}"
    )

    print(
        f"Experience Estimate  : "
        f"{profile['estimated_experience_years']}"
    )


    print(
        f"\nSkills Detected      : "
        f"{profile['skill_count']}"
    )


    if profile["skills"]:

        for skill in profile["skills"]:

            print(
                f"  • {skill}"
            )

    else:

        print(
            "  No TalentIQ skills detected."
        )


    print(
        "\nDetected Roles:"
    )


    if profile["detected_roles"]:

        for role in profile[
            "detected_roles"
        ]:

            print(
                f"  • {role}"
            )

    else:

        print(
            "  None detected"
        )


    print(
        "\nEducation:"
    )


    if profile[
        "education_keywords"
    ]:

        for education in profile[
            "education_keywords"
        ]:

            print(
                f"  • {education}"
            )

    else:

        print(
            "  None detected"
        )


# =============================================================
# SAVE RESULTS
# =============================================================

def save_results(
    file_path,
    resume_text,
    profile
):

    safe_name = (
        file_path.stem
        .replace(
            " ",
            "_"
        )
    )


    json_file = (
        OUTPUT_DIR
        /
        f"{safe_name}_profile.json"
    )


    text_file = (
        OUTPUT_DIR
        /
        f"{safe_name}_cleaned.txt"
    )


    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )


    text_file.write_text(
        resume_text,
        encoding="utf-8"
    )


    return (
        json_file,
        text_file
    )


# =============================================================
# AVAILABLE RESUMES
# =============================================================

def get_available_resumes():

    supported_extensions = {
        ".pdf",
        ".txt",
    }


    files = [

        file

        for file in RESUME_DIR.iterdir()

        if (
            file.is_file()
            and
            file.suffix.lower()
            in supported_extensions
        )
    ]


    return sorted(
        files
    )


# =============================================================
# SELECT RESUME INTERACTIVELY
# =============================================================

def choose_resume():

    resumes = get_available_resumes()


    if not resumes:

        print(
            "\nNo resumes found."
        )

        print(
            f"Put a PDF or TXT resume inside:\n"
            f"{RESUME_DIR}"
        )

        return None


    print_section(
        "AVAILABLE RESUMES"
    )


    for index, resume in enumerate(
        resumes,
        start=1
    ):

        print(
            f"{index}. {resume.name}"
        )


    print()


    try:

        choice = int(
            input(
                "Select resume number: "
            )
        )

    except ValueError:

        print(
            "Invalid selection."
        )

        return None


    if (
        choice < 1
        or
        choice > len(resumes)
    ):

        print(
            "Invalid selection."
        )

        return None


    return resumes[
        choice - 1
    ]


# =============================================================
# RUN RESUME ANALYZER
# =============================================================

def analyze_resume(
    file_path
):

    file_path = Path(
        file_path
    ).expanduser().resolve()


    if not file_path.exists():

        print(
            f"ERROR: Resume not found:\n"
            f"{file_path}"
        )

        return None


    print("\n")
    print("=" * 78)
    print(
        "TALENTIQ AI RECRUITMENT PLATFORM"
    )
    print(
        "RESUME ANALYZER"
    )
    print("=" * 78)


    # ---------------------------------------------------------
    # LOAD DATABASE REFERENCE DATA
    # ---------------------------------------------------------

    print_section(
        "LOADING TALENTIQ REFERENCE DATA"
    )


    known_skills = (
        load_known_skills()
    )


    known_job_titles = (
        load_known_job_titles()
    )


    print(
        f"Known TalentIQ Skills : "
        f"{len(known_skills):,}"
    )

    print(
        f"Known Job Titles      : "
        f"{len(known_job_titles):,}"
    )


    # ---------------------------------------------------------
    # EXTRACT
    # ---------------------------------------------------------

    print_section(
        "EXTRACTING RESUME TEXT"
    )


    try:

        (
            raw_text,
            page_count

        ) = extract_resume_text(
            file_path
        )


    except Exception as error:

        print(
            f"ERROR: {error}"
        )

        return None


    resume_text = (
        clean_resume_text(
            raw_text
        )
    )


    print(
        f"Pages Extracted      : "
        f"{page_count}"
    )

    print(
        f"Characters Extracted : "
        f"{len(resume_text):,}"
    )

    print(
        f"Words Extracted      : "
        f"{len(resume_text.split()):,}"
    )


    # ---------------------------------------------------------
    # CHECK FOR EMPTY / SCANNED DOCUMENT
    # ---------------------------------------------------------

    if len(resume_text) < 50:

        print(
            "\nWARNING:"
        )

        print(
            "Very little text was extracted."
        )

        print(
            "The resume may be scanned/image-based "
            "or may contain an unsupported text layout."
        )


    # ---------------------------------------------------------
    # PROFILE
    # ---------------------------------------------------------

    profile = (
        build_resume_profile(

            file_path=
                file_path,

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


    display_profile(
        profile
    )


    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    (
        json_file,
        text_file

    ) = save_results(

        file_path=
            file_path,

        resume_text=
            resume_text,

        profile=
            profile,
    )


    print_section(
        "OUTPUT FILES"
    )


    print(
        f"Structured Profile:\n"
        f"{json_file}"
    )


    print(
        f"\nClean Resume Text:\n"
        f"{text_file}"
    )


    print("\n")
    print("=" * 78)
    print(
        "RESUME ANALYSIS COMPLETE"
    )
    print("=" * 78)


    return profile


# =============================================================
# COMMAND LINE
# =============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "TalentIQ Resume Analyzer"
        )
    )


    parser.add_argument(

        "--resume",

        type=str,

        help=(
            "Path to PDF or TXT resume"
        ),
    )


    args = parser.parse_args()


    # ---------------------------------------------------------
    # Direct file
    # ---------------------------------------------------------

    if args.resume:

        analyze_resume(
            args.resume
        )

        return


    # ---------------------------------------------------------
    # Interactive mode
    # ---------------------------------------------------------

    selected_resume = (
        choose_resume()
    )


    if selected_resume is None:

        return


    analyze_resume(
        selected_resume
    )


# =============================================================
# SCRIPT ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()
