"""
Database setup — SQLite via SQLAlchemy. Zero external setup: the database
is just a file (backend/app.db) created automatically the first time the
app runs. If you ever outgrow it, swapping DATABASE_URL for a real
Postgres connection string is the only change needed — no model/router
code changes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: ensures models are registered before create_all
    Base.metadata.create_all(bind=engine)