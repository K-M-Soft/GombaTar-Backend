import os
from sqlalchemy import create_engine, text


def get_engine(database_url=None):
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    # Avoid stale connections in serverless environments.
    return create_engine(url, pool_pre_ping=True)


def check_database_connection(database_url=None):
    engine = get_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
