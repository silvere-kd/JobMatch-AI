# backend/app/core/queue.py
import os

from arq import create_pool
from arq.connections import RedisSettings

from backend.app.core.run_manager import RunManager
from backend.app.storage.db import ensure_dirs, get_session
from backend.app.storage.models import Run, RunStatus

REDIS_URL = os.environ.get("REDIS_URL", "redis://host.docker.internal:6379/0")


async def enqueue_run(run_id: str):
    redis = await create_pool(RedisSettings.from_dsn(REDIS_URL))
    await redis.enqueue_job("run_match_job", run_id=run_id)


async def run_match_job(ctx, run_id: str):
    ensure_dirs()
    # Do all heavy work here (worker process with its own loop)
    with get_session() as s:
        run = s.get(Run, run_id)
        if not run:
            return
        if run.status not in (RunStatus.queued, RunStatus.failed):
            return
        mgr = RunManager(s, run)
        try:
            mgr.execute()
        except Exception as e:
            run.status = RunStatus.failed
            run.error = str(e)
            s.add(run)
            s.commit()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    functions = [run_match_job]
    max_jobs = 10
    retry_jobs = True
