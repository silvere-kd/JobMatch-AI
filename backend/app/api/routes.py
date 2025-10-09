# backend/app/api/routes.py
import hashlib
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from backend.app.core.queue import enqueue_run
from backend.app.models.schemas import ArtifactMeta, RunRequest, RunResponse, RunStatusResponse
from backend.app.storage.artifacts import list_artifacts_for_run
from backend.app.storage.db import ensure_dirs, get_session
from backend.app.storage.models import Run, RunStatus

router = APIRouter()

MAX_LEN = 2_000_000  # ~2MB chars


@router.post("/runs", response_model=RunResponse, status_code=202)
async def create_run(req: RunRequest) -> RunResponse:
    """Queue a new run. FastAPI will validate the body into RunRequest automatically."""

    if len(req.resume_text) > MAX_LEN or len(req.jd_text) > MAX_LEN:
        raise HTTPException(status_code=413, detail="payload too large")

    ensure_dirs()

    # Simple idempotency hash
    h = hashlib.sha256(
        (
            req.resume_text.strip()
            + "\n---\n"
            + req.jd_text.strip()
            + json.dumps(req.params or {}, sort_keys=True)
        ).encode("utf-8")
    ).hexdigest()

    with get_session() as s:
        existing = (
            s.execute(
                select(Run)
                .where(Run.payload_hash == h, Run.status == RunStatus.succeeded)
                .order_by(Run.finished_at.desc())  # take newest
            )
            .scalars()
            .first()
        )
        if existing:
            return RunResponse(run_id=existing.id, status=existing.status.value)

        run = Run(
            payload_hash=h,
            status=RunStatus.queued,
            resume_text=req.resume_text,
            jd_text=req.jd_text,
            params=req.params or {},
        )
        s.add(run)
        s.commit()
        s.refresh(run)

    # enqueue the job
    await enqueue_run(run_id=run.id)

    return RunResponse(run_id=run.id, status=str(RunStatus.queued.value))


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run(run_id: str) -> RunStatusResponse:
    with get_session() as s:
        run = s.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")

        artifacts = []
        if run.status == RunStatus.succeeded:
            artifacts = [
                ArtifactMeta(name=a.name, kind=a.kind, mime=a.mime, size_bytes=a.size_bytes)
                for a in list_artifacts_for_run(s, run_id)
            ]

        return RunStatusResponse(
            run_id=run.id, status=str(run.status.value), error=run.error, artifacts=artifacts
        )


@router.get("/artifacts/{run_id}")
async def list_artifacts(run_id: str):
    with get_session() as s:
        run = s.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        arts = list_artifacts_for_run(s, run_id)
        files = [
            {"name": a.name, "kind": a.kind, "mime": a.mime, "size_bytes": a.size_bytes}
            for a in arts
        ]
        return {"run_id": run_id, "files": files}


@router.get("/artifacts/{run_id}/{name}")
async def get_artifact(run_id: str, name: str):
    with get_session() as s:
        run = s.get(Run, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        arts = list_artifacts_for_run(s, run_id)
        for a in arts:
            if a.name == name:
                # Serve with content-disposition for nice filename in downloads
                return FileResponse(
                    a.path,
                    media_type=a.mime,
                    filename=a.name,
                )
    raise HTTPException(status_code=404, detail="artifact not found")
