# backend/app/storage/artifacts.py

import json
import os

from sqlalchemy.orm import Session

from backend.app.storage.models import Artifact

DATA_DIR = os.environ.get("DATA_DIR", "./data")


def run_dir(run_id: str) -> str:
    return os.path.join(DATA_DIR, "artifacts", run_id)


def write_artifact(s: Session, run_id: str, name: str, kind: str, mime: str, content: str | dict):
    os.makedirs(run_dir(run_id), exist_ok=True)
    fpath = os.path.join(run_dir(run_id), name)
    if isinstance(content, dict):
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

    else:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

    a = Artifact(run_id=run_id, name=name, kind=kind, mime=mime, path=fpath)
    s.add(a)
    s.commit()


def list_artifacts_for_run(s: Session, run_id: str) -> list[Artifact]:
    return s.query(Artifact).filter(Artifact.run_id == run_id).all()
