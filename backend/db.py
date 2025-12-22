"""Database configuration and session management."""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator


def _default_sqlite_url() -> str:
    """Return a SQLite URL pointing to a writable location."""
    data_dir = Path("/app/data")
    if data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        db_file = data_dir / "app.db"
    else:
        # Fallback for local runs outside Docker
        project_root = Path(__file__).resolve().parent.parent
        db_file = project_root / "app.db"
    return f"sqlite:///{db_file}"


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or _default_sqlite_url()

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Create engine with SQLite-specific configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,  # Required for FastAPI async compatibility on SQLite
    echo=False,  # Set to True for SQL query debugging
)

# Enable foreign key constraints for SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign key constraints on SQLite connection."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True,
)

# Create declarative base for ORM models
Base = declarative_base()


def get_db() -> Generator:
    """Get database session.
    
    Dependency injection function that yields a database session
    and ensures proper cleanup even on exceptions.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
