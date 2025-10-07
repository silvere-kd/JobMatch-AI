# streamlit_app/main.py
import asyncio
import os

import httpx
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="JobMatch-AI", layout="wide")
st.title("JobMatch-AI — Resume ↔ JD Matcher")

with st.sidebar:
    st.markdown("**Status**: Test (stub graph)")
    st.markdown("API: " + API_BASE)

resume_text = st.text_area("Paste your Resume (plain text)", height=220)
jd_text = st.text_area("Paste the Job Description (plain text)", height=220)
params_col1, params_col2 = st.columns(2)
with params_col1:
    threshold = st.slider("Minimum score threshold (UI only)", 0, 100, 65)

run_btn = st.button("Run Match", type="primary", use_container_width=True)

status_placeholder = st.empty()
artifacts_placeholder = st.empty()


async def poll_status(run_id: str):
    status_placeholder.info(f"Run `{run_id}` queued…")
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            r = await client.get(f"{API_BASE}/runs/{run_id}")
            r.raise_for_status()
            data = r.json()
            if data["status"] == "succeeded":
                status_placeholder.success(f"Run `{run_id}`: succeeded ✅")
                return data
            if data["status"] == "failed":
                status_placeholder.error(f"Run `{run_id}`: failed ❌ — {data.get('error')}")
                return data
            status_placeholder.info(f"Run `{run_id}`: {data['status']}…")
            await asyncio.sleep(1.0)


if run_btn:
    if not resume_text.strip() or not jd_text.strip():
        st.warning("Please paste both Resume and Job Description.")
    else:
        with st.spinner("Submitting…"):
            resp = httpx.post(
                f"{API_BASE}/runs",
                json={
                    "resume_text": resume_text,
                    "jd_text": jd_text,
                    "params": {"ui_threshold": threshold},
                },
            )
            if resp.status_code not in (200, 202):
                st.error(f"Error: {resp.text}")
            else:
                run_id = resp.json()["run_id"]
                data = asyncio.run(poll_status(run_id))
                if data and data.get("artifacts"):
                    with artifacts_placeholder.container():
                        st.subheader("Artifacts")
                        for a in data["artifacts"]:
                            url = f"{API_BASE}/artifacts/{run_id}/{a['name']}"
                            st.write(f"- **{a['name']}** ({a['mime']}) — [download]({url})")
