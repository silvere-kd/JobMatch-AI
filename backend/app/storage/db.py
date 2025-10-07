# backend/app/storage/db.py

import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.storage.models import Base

DATA_DIR = os.environ.get("DATA_DIR", "./data")
DB_PATH = os.path.join(DATA_DIR, "app.sqlite3")
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=ENGINE)


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "artifacts"), exist_ok=True)
    init_db()


@contextmanager
def get_session():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
