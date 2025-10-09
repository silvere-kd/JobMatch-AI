# backend/app/storage/artifacts.py
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from .models import Artifact

DATA_DIR = os.environ.get("DATA_DIR", "./data")

MIME_BY_NAME = {
    "scorecard.json": "application/json",
    "scorecard.md": "text/markdown",
    "graph_trace.jsonl": "application/json",
    "gaps.csv": "text/csv",
    # add more as needed
}


def run_dir(run_id: str) -> str:
    base = os.path.join(DATA_DIR, "artifacts")
    path = os.path.join(base, run_id)
    # Ensure no path traversal
    os.makedirs(path, exist_ok=True)
    return path


def _safe_name(name: str) -> str:
    # Reject path separators and traversal
    bn = os.path.basename(name)
    if bn != name or ".." in name or "/" in name or "\\" in name:
        raise ValueError("invalid artifact name")
    return bn


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _to_bytes(content: str | dict) -> bytes:
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")
    return content.encode("utf-8")


def _atomic_write(target_path: str, data: bytes) -> None:
    # Write to temp file then rename to target (atomic on POSIX)
    d = os.path.dirname(target_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=d)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def write_artifact(
    s: Session,
    run_id: str,
    name: str,
    kind: str,
    mime: str | None,
    content: str | dict,
) -> Artifact:
    name = _safe_name(name)
    rd = run_dir(run_id)
    fpath = os.path.join(rd, name)
    data = _to_bytes(content)

    # write atomically
    _atomic_write(fpath, data)

    size = len(data)
    digest = _sha256_bytes(data)
    mime = mime or MIME_BY_NAME.get(name, "application/octet-stream")

    a = Artifact(
        run_id=run_id,
        name=name,
        kind=kind,
        mime=mime,
        path=fpath,
        size_bytes=size,
        sha256=digest,
        created_at=datetime.now(UTC),
    )
    s.add(a)
    s.commit()
    return a


def list_artifacts_for_run(s: Session, run_id: str) -> list[Artifact]:
    # sorted by created_at then name for stability
    return (
        s.query(Artifact)
        .filter(Artifact.run_id == run_id)
        .order_by(Artifact.created_at.asc(), Artifact.name.asc())
        .all()
    )
