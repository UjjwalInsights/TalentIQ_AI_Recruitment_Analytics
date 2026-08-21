from sqlalchemy import create_engine, text, URL
from dotenv import load_dotenv
import os


# Load variables from .env
load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# Validate environment variables
required_variables = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
}

missing_variables = [
    key
    for key, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        f"Missing environment variables: {', '.join(missing_variables)}"
    )


# Build database URL safely.
# URL.create handles special characters in passwords correctly.
database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_pre_ping=True
)


def get_connection():
    """
    Return a PostgreSQL connection using the recruitment schema.
    """

    connection = engine.connect()

    connection.execute(
        text("SET search_path TO recruitment")
    )

    return connection


def test_connection():
    """
    Test PostgreSQL connection and verify TalentIQ database access.
    """

    with get_connection() as connection:

        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar()

        job_count = connection.execute(
            text("SELECT COUNT(*) FROM jobs")
        ).scalar()

        candidate_count = connection.execute(
            text("SELECT COUNT(*) FROM candidates")
        ).scalar()

        application_count = connection.execute(
            text("SELECT COUNT(*) FROM applications")
        ).scalar()

        print("=" * 50)
        print("TALENTIQ DATABASE CONNECTION")
        print("=" * 50)

        print("Database connection successful.")
        print(f"Database: {database_name}")
        print(f"Jobs: {job_count}")
        print(f"Candidates: {candidate_count}")
        print(f"Applications: {application_count}")

        print("=" * 50)


if __name__ == "__main__":
    test_connection()