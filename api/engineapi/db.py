"""
Engine database connection.
"""
from contextlib import contextmanager
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

ENGINE_DB_URI = os.environ.get("ENGINE_DB_URI")
if ENGINE_DB_URI is None:
    raise ValueError("ENGINE_DB_URI environment variable must be set")


ENGINE_POOL_SIZE_RAW = os.environ.get("ENGINE_POOL_SIZE", 0)
try:
    if ENGINE_POOL_SIZE_RAW is not None:
        ENGINE_POOL_SIZE = int(ENGINE_POOL_SIZE_RAW)
except:
    raise Exception(f"Could not parse ENGINE_POOL_SIZE as int: {ENGINE_POOL_SIZE_RAW}")

ENGINE_DB_STATEMENT_TIMEOUT_MILLIS_RAW = os.environ.get(
    "ENGINE_DB_STATEMENT_TIMEOUT_MILLIS"
)
ENGINE_DB_STATEMENT_TIMEOUT_MILLIS = 30000
try:
    if ENGINE_DB_STATEMENT_TIMEOUT_MILLIS_RAW is not None:
        ENGINE_DB_STATEMENT_TIMEOUT_MILLIS = int(ENGINE_DB_STATEMENT_TIMEOUT_MILLIS_RAW)
except:
    raise ValueError(
        f"ENGINE_DB_STATEMENT_TIMEOUT_MILLIOS must be an integer: {ENGINE_DB_STATEMENT_TIMEOUT_MILLIS_RAW}"
    )

# Pooling: https://docs.sqlalchemy.org/en/14/core/pooling.html#sqlalchemy.pool.QueuePool
# Statement timeout: https://stackoverflow.com/a/44936982
engine = create_engine(
    ENGINE_DB_URI,
    pool_size=ENGINE_POOL_SIZE,
    pool_pre_ping=True,
    connect_args={
        "options": f"-c statement_timeout={ENGINE_DB_STATEMENT_TIMEOUT_MILLIS}"
    },
)
SessionLocal = sessionmaker(bind=engine)


def yield_db_session() -> Session:
    """
    Yields a database connection (created using environment variables).
    As per FastAPI docs:
    https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


yield_db_session_ctx = contextmanager(yield_db_session)
