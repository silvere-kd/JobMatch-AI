# backend/app/core/run_manager.py

from __future__ import annotations

import datetime

from sqlalchemy.orm import Session

from backend.app.core.graph import run_minimal_graph, scorecard_markdown, trace_jsonl
from backend.app.storage.artifacts import write_artifact
from backend.app.storage.models import Run, RunStatus


class RunManager:
    def __init__(self, s: Session, run: Run):
        self.s = s
        self.run = run

    def _update_status(self, status: RunStatus, error: str | None = None):
        self.run.status = status
        self.run.error = error
        if status == RunStatus.running:
            self.run.started_at = datetime.datetime.now(datetime.UTC)
        if status in (RunStatus.succeeded, RunStatus.failed):
            self.run.finished_at = datetime.datetime.now(datetime.UTC)
        self.s.add(self.run)
        self.s.commit()

    def execute(self):
        self._update_status(RunStatus.running)

        state = run_minimal_graph(self.run.resume_text, self.run.jd_text)

        write_artifact(
            self.s, self.run.id, "scorecard.json", "scorecard", "application/json", state.scorecard
        )
        write_artifact(
            self.s,
            self.run.id,
            "scorecard.md",
            "scorecard",
            "text/markdown",
            scorecard_markdown(state),
        )
        write_artifact(
            self.s,
            self.run.id,
            "graph_trace.jsonl",
            "trace",
            "application/json",
            trace_jsonl(state),
        )

        self._update_status(RunStatus.succeeded)
