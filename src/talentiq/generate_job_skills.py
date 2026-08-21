import os
import random
from collections import Counter, defaultdict

import psycopg2
from psycopg2.extras import execute_batch


# ============================================================
# TalentIQ - Job Skills Generator
# Regenerates recruitment.job_skills using the existing
# recruitment.jobs and recruitment.skills tables.
# ============================================================

SCHEMA = "recruitment"
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "recruitment_analytics",
    "user": "postgres",
    "password": "Just890",
}

# Skill pools are based on job title / department.
TECHNOLOGY = {
    "Java": 5, "Spring Boot": 4, "C#": 4, ".NET": 4,
    "C++": 3, "JavaScript": 5, "React": 5, "Node.js": 5,
    "Angular": 4, "Vue.js": 3, "HTML": 3, "CSS": 3,
    "Python": 5, "Django": 4, "FastAPI": 4, "SQL": 5,
    "MySQL": 3, "PostgreSQL": 4, "SQL Server": 4, "Oracle": 3,
    "MongoDB": 3, "Git": 4, "GitHub": 3, "Jenkins": 3,
    "Docker": 5, "Kubernetes": 5, "Terraform": 4,
}

DATA = {
    "Python": 5, "SQL": 5, "PostgreSQL": 4, "Pandas": 4,
    "NumPy": 4, "PySpark": 4, "Statistics": 4,
    "Data Analysis": 5, "Machine Learning": 4, "R": 3,
    "Tableau": 4, "Power BI": 4, "Excel": 4,
    "AWS": 3, "Azure": 3, "Google Cloud": 3,
}

AI = {
    "Python": 5, "SQL": 4, "Machine Learning": 5,
    "Large Language Models": 5, "Generative AI": 5,
    "Natural Language Processing": 5, "OpenAI API": 5,
    "LangChain": 5, "FastAPI": 4, "Pandas": 3, "NumPy": 3,
    "PySpark": 3, "Statistics": 3, "AWS": 3, "Azure": 3,
    "Docker": 4, "Kubernetes": 3, "Git": 3,
}

BUSINESS = {
    "Business Analysis": 5, "Project Management": 4, "Agile": 4,
    "Scrum": 4, "SQL": 4, "Excel": 4, "Tableau": 3,
    "Power BI": 3, "Salesforce": 3, "PMP": 2,
}

DEVOPS = {
    "AWS": 5, "Azure": 5, "Google Cloud": 4, "Docker": 5,
    "Kubernetes": 5, "Terraform": 5, "Jenkins": 4, "Git": 4,
    "GitHub": 3, "Python": 3, "Java": 2, "SQL": 2,
}

ERP = {
    "SAP": 5, "Oracle": 4, "SQL": 3, "Java": 2,
    "Python": 2, "Salesforce": 3, "Excel": 3,
    "Business Analysis": 4, "Project Management": 3,
}

SALESFORCE = {
    "Salesforce": 5, "Business Analysis": 4, "SQL": 3,
    "JavaScript": 3, "HTML": 2, "CSS": 2,
    "Project Management": 3, "Agile": 3,
}

GENERIC = {
    "SQL": 4, "Python": 3, "Excel": 3, "Git": 3,
    "GitHub": 2, "AWS": 2, "Business Analysis": 3,
    "Data Analysis": 3, "JavaScript": 2, "Docker": 2,
}


def norm(value):
    return (value or "").strip().lower()


def weighted_sample(pool, count):
    names = list(pool)
    selected = []

    for _ in range(min(count, len(names))):
        remaining = [x for x in names if x not in selected]
        weights = [pool[x] for x in remaining]
        chosen = random.choices(remaining, weights=weights, k=1)[0]
        selected.append(chosen)

    return selected


def choose_pool(title, department):
    title = norm(title)
    department = norm(department)

    if any(x in title for x in (
        "ai", "machine learning", "ml engineer", "llm",
        "nlp", "generative", "artificial intelligence",
        "data scientist",
    )):
        return AI

    if any(x in title for x in (
        "devops", "cloud", "site reliability", "sre",
        "infrastructure",
    )):
        return DEVOPS

    if any(x in title for x in (
        "data analyst", "data analytics", "analytics",
        "data engineer", "bi developer", "business intelligence",
    )):
        return DATA

    if any(x in title for x in (
        "business analyst", "project manager", "product manager",
        "scrum", "program manager",
    )):
        return BUSINESS

    if "salesforce" in title:
        return SALESFORCE

    if any(x in title for x in ("sap", "oracle", "erp")):
        return ERP

    if "data" in department or "analytics" in department:
        return DATA

    if "information technology" in department or "technology" in department:
        return TECHNOLOGY

    return GENERIC


def choose_priority(skill, pool):
    weight = pool.get(skill, 2)

    if weight >= 5:
        return random.choices(
            ["Must-have", "Nice-to-have"], [70, 30], k=1
        )[0]

    if weight == 4:
        return random.choices(
            ["Must-have", "Nice-to-have"], [50, 50], k=1
        )[0]

    return random.choices(
        ["Must-have", "Nice-to-have"], [20, 80], k=1
    )[0]


def main():
    print("=" * 65)
    print("TalentIQ - Job Skills Data Generator")
    print("=" * 65)

    conn = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connected to PostgreSQL ✅")

        with conn.cursor() as cur:

            # ------------------------------------------------
            # Load skills
            # ------------------------------------------------
            cur.execute(f"""
                SELECT skill_id, skill_name
                FROM {SCHEMA}.skills
                ORDER BY skill_id;
            """)
            skill_rows = cur.fetchall()

            if not skill_rows:
                raise RuntimeError("No skills found.")

            skill_id = {name: sid for sid, name in skill_rows}

            print(f"Skills available              : {len(skill_rows)}")

            # ------------------------------------------------
            # Load jobs
            # ------------------------------------------------
            cur.execute(f"""
                SELECT
                    j.job_id,
                    j.job_title,
                    COALESCE(d.department_name, '')
                FROM {SCHEMA}.jobs j
                LEFT JOIN {SCHEMA}.departments d
                    ON j.department_id = d.department_id
                ORDER BY j.job_id;
            """)
            jobs = cur.fetchall()

            if not jobs:
                raise RuntimeError("No jobs found.")

            print(f"Jobs available                : {len(jobs)}")

            # ------------------------------------------------
            # Validate configured skill names
            # ------------------------------------------------
            configured = set().union(
                TECHNOLOGY, DATA, AI, BUSINESS,
                DEVOPS, ERP, SALESFORCE, GENERIC
            )

            missing = sorted(x for x in configured if x not in skill_id)

            if missing:
                raise RuntimeError(
                    "Configured skills missing from database: "
                    + ", ".join(missing)
                )

            # ------------------------------------------------
            # Clear old generated job-skill relationships
            # ------------------------------------------------
            cur.execute(f"DELETE FROM {SCHEMA}.job_skills;")
            print(f"Old job-skill records removed : {cur.rowcount}")

            # ------------------------------------------------
            # Generate records
            # ------------------------------------------------
            records = []
            priority_counts = Counter()

            # Guarantee every skill appears at least once.
            forced = defaultdict(list)

            for index, (_, name) in enumerate(skill_rows):
                job_id = jobs[index % len(jobs)][0]
                forced[job_id].append(name)

            for job_id, title, department in jobs:
                pool = choose_pool(title, department)

                # 3-7 skills per job.
                count = random.randint(3, 7)
                selected = weighted_sample(pool, count)

                # Guarantee catalogue coverage.
                if forced[job_id]:
                    selected.append(random.choice(forced[job_id]))

                selected = list(dict.fromkeys(selected))

                for name in selected:
                    priority = choose_priority(name, pool)

                    records.append(
                        (job_id, skill_id[name], priority)
                    )

                    priority_counts[priority] += 1

            # ------------------------------------------------
            # Insert
            # ------------------------------------------------
            insert_sql = f"""
                INSERT INTO {SCHEMA}.job_skills
                    (job_id, skill_id, priority)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_id, skill_id)
                DO UPDATE SET priority = EXCLUDED.priority;
            """

            execute_batch(
                cur,
                insert_sql,
                records,
                page_size=1000,
            )

            conn.commit()

            # ------------------------------------------------
            # Validation
            # ------------------------------------------------
            cur.execute(f"""
                SELECT COUNT(*)
                FROM {SCHEMA}.job_skills;
            """)
            total_records = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(DISTINCT job_id)
                FROM {SCHEMA}.job_skills;
            """)
            jobs_with_skills = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(DISTINCT skill_id)
                FROM {SCHEMA}.job_skills;
            """)
            skills_used = cur.fetchone()[0]

            cur.execute(f"""
                SELECT
                    s.skill_name,
                    COUNT(*) AS job_demand
                FROM {SCHEMA}.job_skills js
                JOIN {SCHEMA}.skills s
                    ON js.skill_id = s.skill_id
                GROUP BY s.skill_id, s.skill_name
                ORDER BY job_demand DESC, s.skill_name
                LIMIT 15;
            """)
            top_skills = cur.fetchall()

        print()
        print("=" * 65)
        print("JOB SKILLS GENERATION COMPLETE ✅")
        print("=" * 65)
        print(f"Jobs processed               : {len(jobs)}")
        print(f"Job-skill records created    : {total_records}")
        print(f"Jobs with skills             : {jobs_with_skills}")
        print(f"Skills used                  : {skills_used}/{len(skill_rows)}")

        print()
        print("Priority distribution:")
        for priority, count in sorted(priority_counts.items()):
            print(f"{priority:<10} {count}")

        print()
        print("Top demanded skills:")
        for name, demand in top_skills:
            print(f"{name:<30} {demand}")

        print()
        print("Expected:")
        print("- All jobs have 3-7 skill requirements.")
        print("- Most/all of the 54 skills are represented.")
        print("- SQL, Python and AWS remain highly demanded.")
        print("- AI/LLM skills appear in relevant AI jobs.")
        print("- Data skills appear in data/analytics jobs.")
        print("- Cloud/DevOps skills appear in DevOps/cloud jobs.")

    except Exception as exc:
        if conn:
            conn.rollback()

        print()
        print("JOB SKILLS GENERATION FAILED ❌")
        print(exc)
        raise

    finally:
        if conn:
            conn.close()
            print("PostgreSQL connection closed.")


if __name__ == "__main__":
    main()
