## 🧠 JobMatch-AI: LangGraph-based Agentic App for Resume vs Job Description matching

JobMatch-AI helps candidates tailor their resumes to job descriptions using an agentic LLM workflow built with LangGraph, FastAPI, and Streamlit.
The system parses and scores resumes, rewrites bullet points, and generates structured feedback — all asynchronously through a Redis-backed queue.



## 📂 Repository Structure
```cpp
backend/
  app/
    api/          ← FastAPI routes
    core/         ← queue, tasks, LangGraph agents
    models/       ← Pydantic + SQLAlchemy schemas
frontend/
  streamlit_app/
    main.py       ← Streamlit UI
tests/
  test_api_contract.py
Dockerfile
docker-compose.yml
Makefile
pyproject.toml
README.md
```

## 🚀 How to run

### 1. Local (dev)
```bash
# create venv + install deps
make setup
# run API
make run
# run worker
make worker
# open UI
streamlit run frontend/streamlit_app/main.py
```

### 2. Docker
```bash
make up          # build + run (api + worker + redis + streamlit)
make down        # stop and clean
```

## 🧪 Testing

Run all tests:

```bash
make test
```

or directly:

```bash
pytest -q
```

## 🧩 LangGraph Agents

| Agent	| Role |
|--------|--------|
|parse_resume_agent	| extract skills & experience |
|score_match_agent	| compute semantic alignment |
|rewrite_agent	| propose bullet point improvements |
|artifact_agent	| persist structured JSON/PDF artifacts |

Each agent operates in its own node within the LangGraph workflow, coordinated by GraphOrchestrator.


## 🔧 Tech Stack

- FastAPI / Pydantic v2 – REST API

- LangGraph – agentic orchestration

- ARQ + Redis – asynchronous task queue

- Streamlit – frontend UI

- SQLite / JSON artifacts – lightweight storage

- Docker & Makefile – portable dev environment

- Pytest + Ruff – tests & linting


## 🧭 Development Notes

- Type-safe I/O via Pydantic models.

- Background LLM runs via enqueue_run → Redis → ARQ worker.

- Results polled from /runs/{run_id} until status=succeeded.

- Editable installs (pip install -e .) for live code reload.


## 🛠 Future Improvements

- Add vector storage for semantic search

- Add MCP integration for external tools

- Expand evaluation suite for scoring accuracy

- Add artifact download ( PDF / Markdown )

- CI pipeline (GitHub Actions) for tests + lint on push