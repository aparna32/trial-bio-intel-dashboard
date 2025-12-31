import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trials + Bio Evidence", layout="wide")
st.title("Clinical Trials + Bio Evidence Dashboard")

def must_exist(path: str):
    if not os.path.exists(path):
        st.error(
            f"Missing file: `{path}`.\n\n"
            "Fix: Run the pipeline in Codespaces (Python fetch + R scripts) or wait for GitHub Actions refresh."
        )
        st.stop()

def safe_unique(series: pd.Series):
    if series is None or series.empty:
        return []
    return sorted([x for x in series.dropna().unique()])

must_exist("data_processed/trials_clean.csv")
must_exist("data_processed/trial_status_summary.csv")
must_exist("data_processed/trial_bio_evidence.csv")

trials = pd.read_csv("data_processed/trials_clean.csv")
status_summary = pd.read_csv("data_processed/trial_status_summary.csv")
bio = pd.read_csv("data_processed/trial_bio_evidence.csv")

for df in (trials, bio):
    for col in ["status", "phase", "sponsor", "nct_id", "title", "conditions"]:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "").replace("None", "")

st.sidebar.header("Filters")

status_options = ["All"] + safe_unique(bio["status"]) if "status" in bio.columns else ["All"]
phase_options = ["All"] + safe_unique(bio["phase"]) if "phase" in bio.columns else ["All"]

status_pick = st.sidebar.selectbox("Status", status_options, index=0)
phase_pick = st.sidebar.selectbox("Phase", phase_options, index=0)
sponsor_query = st.sidebar.text_input("Sponsor contains", "").strip()

min_score = 0
if "bio_evidence_score" in bio.columns:
    bio["bio_evidence_score"] = pd.to_numeric(bio["bio_evidence_score"], errors="coerce").fillna(0)
    min_score = st.sidebar.slider("Min Bio Evidence Score", 0, 100, 50)

df = bio.copy()

if "status" in df.columns and status_pick != "All":
    df = df[df["status"] == status_pick]

if "phase" in df.columns and phase_pick != "All":
    df = df[df["phase"] == phase_pick]

if "sponsor" in df.columns and sponsor_query:
    df = df[df["sponsor"].fillna("").str.contains(sponsor_query, case=False, na=False)]

if "bio_evidence_score" in df.columns:
    df = df[df["bio_evidence_score"] >= min_score]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Trials loaded", len(trials))
c2.metric("Filtered trials", len(df))
c3.metric("Unique sponsors", trials["sponsor"].nunique(dropna=True) if "sponsor" in trials.columns else 0)
c4.metric("Statuses", status_summary.shape[0])

st.caption("Bio Evidence Score is an explainable heuristic (v1). It's a signal-strength indicator, not a prediction model.")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trial Finder", "Bio Evidence", "Sponsors"])

with tab1:
    left, right = st.columns(2)

    with left:
        st.subheader("Trials by Status (R output)")
        if "status" in status_summary.columns and "n" in status_summary.columns:
            tmp = status_summary.copy()
            tmp["n"] = pd.to_numeric(tmp["n"], errors="coerce").fillna(0)
            st.bar_chart(tmp.set_index("status")["n"])
        else:
            st.dataframe(status_summary, use_container_width=True)

    with right:
        st.subheader("Trials by Phase (Python output)")
        if "phase" in trials.columns:
            phase_counts = trials["phase"].fillna("Unknown").replace("", "Unknown").value_counts()
            st.bar_chart(phase_counts)
        else:
            st.info("No `phase` column found in trials_clean.csv.")

    st.caption("Source: ClinicalTrials.gov • Pipeline: Python + R • Automation: GitHub Actions • UI: Streamlit")

with tab2:
    st.subheader("Trial Finder (clickable NCT IDs) — uses Bio table + filters")
    st.write("This table respects your sidebar filters.")

    show_cols = [c for c in ["nct_id", "title", "status", "phase", "sponsor", "conditions", "bio_evidence_score", "confidence", "pulled_at"] if c in df.columns]
    view = df[show_cols].copy() if show_cols else df.copy()

    if "nct_id" in view.columns:
        view["link"] = view["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

    st.dataframe(view.head(300), use_container_width=True)

    st.download_button(
        "Download current view (CSV)",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="filtered_trials.csv",
        mime="text/csv",
    )

with tab3:
    st.subheader("Bio Evidence Ranking (signals-based, explainable)")

    if "bio_evidence_score" not in df.columns:
        st.error("Missing `bio_evidence_score` column in trial_bio_evidence.csv.")
        st.stop()

    cols = [c for c in ["nct_id", "title", "bio_evidence_score", "confidence", "evidence_reason", "status", "phase", "sponsor"] if c in df.columns]
    rank = df[cols].sort_values("bio_evidence_score", ascending=False).head(50).copy()

    if "nct_id" in rank.columns:
        rank["link"] = rank["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

    st.markdown("### Top 50 by Bio Evidence Score")
    st.dataframe(rank, use_container_width=True)

    st.markdown("### Watchlist (High/Medium signal + Recruiting + Phase 2/3)")
    watch = df.copy()

    if "confidence" in watch.columns:
        watch = watch[watch["confidence"].isin(["High", "Medium"])]

    if "status" in watch.columns:
        watch = watch[watch["status"].fillna("").str.contains("Recruit", case=False, na=False)]

    if "phase" in watch.columns:
        watch = watch[watch["phase"].fillna("").str.contains("Phase 2|Phase 3", case=False, regex=True, na=False)]

    wcols = [c for c in ["nct_id", "title", "bio_evidence_score", "confidence", "status", "phase", "sponsor"] if c in watch.columns]
    watch = watch[wcols].sort_values("bio_evidence_score", ascending=False).head(30).copy()

    if "nct_id" in watch.columns:
        watch["link"] = watch["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

    st.dataframe(watch, use_container_width=True)

with tab4:
    st.subheader("Top Sponsors (filtered view)")
    if "sponsor" in df.columns:
        sponsor_counts = df["sponsor"].fillna("Unknown").replace("", "Unknown").value_counts().head(25)
        st.bar_chart(sponsor_counts)
    else:
        st.info("No sponsor column found.")