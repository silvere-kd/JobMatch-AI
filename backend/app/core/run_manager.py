# backend/app/core/run_manager.py

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.storage.artifacts import write_artifact
from backend.app.storage.models import Run, RunStatus


class RunManager:
    """
    Minimal run executor.
    For now it writes mock artifacts.
    """

    def __init__(self, s: Session, run: Run):
        self.s = s
        self.run = run

    def _update_status(self, status: RunStatus, error: str | None = None):
        self.run.status = status
        self.run.error = error
        if status == RunStatus.running:
            self.run.started_at = datetime.utcnow()
        if status in (RunStatus.succeeded, RunStatus.failed):
            self.run.finished_at = datetime.utcnow()
        self.s.add(self.run)
        self.s.commit()

    def execute(self):
        # 1) running
        self._update_status(RunStatus.running)

        # 2) mock "processing" (normalize/score)
        resume_len = len(self.run.resume_text.split())
        jd_len = len(self.run.jd_text.split())
        score = max(10, min(95, int(100 * min(resume_len, jd_len) / (resume_len + jd_len))))

        # 3) write artifacts
        scorecard = {
            "run_id": self.run.id,
            "overall_score": score,
            "dimensions": {
                "skills_match": score - 5,
                "seniority_alignment": score - 10,
                "keyword_density": score - 8,
            },
            "notes": "Mock scorecard.",
        }
        write_artifact(
            self.s, self.run.id, "scorecard.json", "scorecard", "application/json", scorecard
        )
        write_artifact(
            self.s,
            self.run.id,
            "scorecard.md",
            "scorecard",
            "text/markdown",
            f"# Scorecard (Mock)\n\n**Overall**: {score}/100\n\n_This is a stub artifact._\n",
        )
        write_artifact(
            self.s,
            self.run.id,
            "graph_trace.jsonl",
            "trace",
            "application/json",
            {"trace": [{"node": "mock", "status": "ok"}]},
        )

        # 4) succeeded
        self._update_status(RunStatus.succeeded)
