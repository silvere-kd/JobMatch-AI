# tests/test_api_contract.py
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.storage.db import ensure_dirs


@pytest.mark.anyio
async def test_healthz():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/healthz")
        assert r.status_code == 200
        assert r.json()["ok"] is True


@pytest.mark.anyio
async def test_create_and_poll_run(monkeypatch):
    ensure_dirs()

    async def _noop_enqueue_run(*args, **kwargs):
        return None

    import backend.app.core.queue as queue_mod

    monkeypatch.setattr(queue_mod, "enqueue_run", _noop_enqueue_run)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"resume_text": f"A B C {uuid.uuid4()}", "jd_text": "A B", "params": {}}
        r = await ac.post("/runs", json=payload)
        assert r.status_code in (200, 202)
        run_id = r.json()["run_id"]

        r2 = await ac.get(f"/runs/{run_id}")
        assert r2.status_code == 200
        body = r2.json()
        assert body["run_id"] == run_id
        assert body["status"] in ("queued", "running", "succeeded", "failed")
