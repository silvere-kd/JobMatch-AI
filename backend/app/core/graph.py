# backend/app/core/graph.py

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphState:
    resume_text: str
    jd_text: str
    skills_resume: list[str] = field(default_factory=list)
    skills_jd: list[str] = field(default_factory=list)
    coverage: float = 0.0
    scorecard: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)


SKILL_REGEX = re.compile(r"\b([A-Za-z][A-Za-z0-9\+\#\.]{1,30})\b")

COMMON_STOP = {
    "and",
    "or",
    "the",
    "a",
    "an",
    "with",
    "for",
    "to",
    "of",
    "in",
    "on",
    "at",
    "is",
    "are",
    "be",
    "experience",
    "team",
    "work",
    "project",
    "projects",
    "skills",
    "tool",
    "tools",
    "stack",
    "senior",
    "lead",
    "junior",
    "engineer",
    "developer",
    "manager",
    "product",
    "data",
}

ALIAS = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "node": "nodejs",
    "postgres": "postgresql",
    "xgboost": "xgboost",
    "ml": "machinelearning",
    "dl": "deep learning",
    "llm": "large language model",
    "ai": "ai",
}


def _norm_text(t: str) -> str:
    t = t.replace("\r\n", "\n")
    t = re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _extract_skills(text: str) -> list[str]:
    raw = [m.group(1).lower() for m in SKILL_REGEX.finditer(text)]
    mapped = [ALIAS.get(x, x) for x in raw]
    dedup = []
    for x in mapped:
        if x in COMMON_STOP:
            continue
        if x.isdigit():
            continue
        if len(x) < 2:
            continue
        if x not in dedup:
            dedup.append(x)
    return dedup[:128]  # cap for deterministic behavior


def _coverage(a: list[str], b: list[str]) -> float:
    if not b:
        return 0.0
    return round(100.0 * len(set(a) & set(b)) / len(set(b)), 1)


def node_normalize(state: GraphState) -> GraphState:
    state.resume_text = _norm_text(state.resume_text)
    state.jd_text = _norm_text(state.jd_text)
    state.logs.append({"node": "normalize_text", "ok": True})
    return state


def node_extract_skills(state: GraphState) -> GraphState:
    state.skills_resume = _extract_skills(state.resume_text)
    state.skills_jd = _extract_skills(state.jd_text)
    state.logs.append(
        {
            "node": "extract_skills_rule_based",
            "resume_count": len(state.skills_resume),
            "jd_count": len(state.skills_jd),
        }
    )
    return state


def node_score_rule_based(state: GraphState) -> GraphState:
    cov = _coverage(state.skills_resume, state.skills_jd)
    # very simple dimensions
    dims = {
        "skills_match": cov,
        "keyword_density": min(100.0, round(len(state.skills_resume) / 3, 1)),
        "ats_hygiene": 80.0,  # placeholder constant
    }
    overall = round(
        0.6 * dims["skills_match"] + 0.25 * dims["keyword_density"] + 0.15 * dims["ats_hygiene"], 1
    )
    state.coverage = cov
    state.scorecard = {
        "overall_score": overall,
        "dimensions": dims,
        "coverage_terms_overlap": sorted(list(set(state.skills_resume) & set(state.skills_jd)))[
            :25
        ],
    }
    state.logs.append({"node": "score_rule_based", "coverage": cov, "overall": overall})
    return state


def node_build_scorecard(state: GraphState) -> GraphState:
    # no-op here, but good place to format artifacts later
    state.logs.append({"node": "build_scorecard", "ok": True})
    return state


def run_minimal_graph(resume_text: str, jd_text: str) -> GraphState:
    state = GraphState(resume_text=resume_text, jd_text=jd_text)
    for step in (node_normalize, node_extract_skills, node_score_rule_based, node_build_scorecard):
        state = step(state)
    return state


def scorecard_markdown(state: GraphState) -> str:
    sc = state.scorecard
    dims = sc.get("dimensions", {})
    overlap = sc.get("coverage_terms_overlap", [])
    md = [
        "# Scorecard",
        f"**Overall**: {sc.get('overall_score', 0)}/100",
        "",
        "## Dimensions",
        f"- Skills Match: {dims.get('skills_match', 0)}",
        f"- Keyword Density: {dims.get('keyword_density', 0)}",
        f"- ATS Hygiene: {dims.get('ats_hygiene', 0)}",
        "",
        "## Overlap Terms",
        (", ".join(overlap) if overlap else "_none_"),
    ]
    return "\n".join(md)


def trace_jsonl(state: GraphState) -> str:
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in state.logs)
