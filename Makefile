# Makefile (replace the top with this)
PY=python
UV?=uv
COMPOSE ?= docker compose  # v2 plugin; change to 'docker-compose' if on v1

.PHONY: setup run worker dev up down logs test fmt lint typecheck

setup:
	$(UV) venv
	$(UV) pip install -e .[dev]

run:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	arq backend.app.core.queue.WorkerSettings

dev: up

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

test:
	pytest -q

fmt:
	ruff check --fix .
	black .

lint:
	ruff check .
	black --check .

typecheck:
	mypy backend
