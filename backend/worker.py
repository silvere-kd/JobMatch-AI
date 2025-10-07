# backend/worker.py
# Convenient entrypoint to run worker without module path issues
from arq import run_worker

from backend.app.core.queue import WorkerSettings

if __name__ == "__main__":
    run_worker(WorkerSettings)
