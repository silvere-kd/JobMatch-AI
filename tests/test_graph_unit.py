# tests/test_graph_unit.py

from backend.app.core.graph import run_minimal_graph


def test_graph_basic():
    resume = "Built APIs in Python & FastAPI. Used PostgreSQL and Docker. Deployed on AWS."
    jd = "Looking for a Python developer with FastAPI, PostgreSQL, and AWS experience."
    st = run_minimal_graph(resume, jd)
    assert st.scorecard["overall_score"] > 50
    assert "python" in st.skills_resume
    assert "fastapi" in st.skills_resume
    assert st.coverage >= 50.0
