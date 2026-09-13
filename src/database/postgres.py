import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_database_engine():
    """Create and return a PostgreSQL SQLAlchemy engine."""

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")

    database_url = (
        f"postgresql+psycopg://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    return create_engine(database_url)