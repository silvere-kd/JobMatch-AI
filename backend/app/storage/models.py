# backend/app/storage/models.py
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Enum, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payload_hash: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.queued)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # store normalized inputs (simple for M0-M3)
    resume_text: Mapped[str] = mapped_column(Text)
    jd_text: Mapped[str] = mapped_column(Text)
    params: Mapped[dict] = mapped_column(JSON, default=dict)

    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)  # filename
    kind: Mapped[str] = mapped_column(String)  # e.g., "scorecard", "trace"
    mime: Mapped[str] = mapped_column(String)  # e.g., "application/json"
    path: Mapped[str] = mapped_column(String)  # absolute or relative path on disk
