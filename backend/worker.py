# backend/worker.py

# Convenient entrypoint to run worker without module path issues
from typing import cast

from arq import run_worker
from arq.typing import WorkerSettingsType

from backend.app.core.queue import WorkerSettings

if __name__ == "__main__":
    run_worker(cast(WorkerSettingsType, WorkerSettings))
