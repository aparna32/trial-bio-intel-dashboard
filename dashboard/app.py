import os
import pandas as pd
import numpy as np
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


# Required files
must_exist("data_processed/trials_clean.csv")
must_exist("data_processed/trial_status_summary.csv")
must_exist("data_processed/trial_bio_evidence.csv")

trials = pd.read_csv("data_processed/trials_clean.csv")
status_summary = pd.read_csv("data_processed/trial_status_summary.csv")
bio = pd.read_csv("data_processed/trial_bio_evidence.csv")

# Light cleanup for display
for df_ in (trials, bio):
    for col in ["status", "phase", "sponsor", "nct_id", "title", "conditions", "confidence", "evidence_reason"]:
        if col in df_.columns:
            df_[col] = df_[col].astype(str).replace("nan", "").replace("None", "")

# Ensure numeric score early (IMPORTANT)
if "bio_evidence_score" in bio.columns:
    bio["bio_evidence_score"] = pd.to_numeric(bio["bio_evidence_score"], errors="coerce").fillna(0)
else:
    bio["bio_evidence_score"] = 0

# Sidebar filters
st.sidebar.header("Filters")

status_options = ["All"] + safe_unique(bio["status"]) if "status" in bio.columns else ["All"]
phase_options = ["All"] + safe_unique(bio["phase"]) if "phase" in bio.columns else ["All"]

status_pick = st.sidebar.selectbox("Status", status_options, index=0)
phase_pick = st.sidebar.selectbox("Phase", phase_options, index=0)
sponsor_query = st.sidebar.text_input("Sponsor contains", "").strip()

# Smart default: median score, not 50
score_min = int(np.floor(bio["bio_evidence_score"].min()))
score_max = int(np.ceil(bio["bio_evidence_score"].max()))
score_default = int(np.round(bio["bio_evidence_score"].median())) if len(bio) else 0

min_score = st.sidebar.slider(
    "Min Bio Evidence Score",
    min_value=0,
    max_value=100,
    value=min(100, max(0, score_default)),
)

st.sidebar.caption(
    f"Score range (current data): {score_min}–{score_max} | "
    f">= {min_score}: {(bio['bio_evidence_score'] >= min_score).sum()}"
)

df = bio.copy()

if "status" in df.columns and status_pick != "All":
    df = df[df["status"] == status_pick]

if "phase" in df.columns and phase_pick != "All":
    df = df[df["phase"] == phase_pick]

if "sponsor" in df.columns and sponsor_query:
    df = df[df["sponsor"].fillna("").str.contains(sponsor_query, case=False, na=False)]

df["bio_evidence_score"] = pd.to_numeric(df["bio_evidence_score"], errors="coerce").fillna(0)
df = df[df["bio_evidence_score"] >= min_score]

# KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Trials loaded", len(trials))
c2.metric("Filtered trials", len(df))
c3.metric("Unique sponsors", trials["sponsor"].nunique(dropna=True) if "sponsor" in trials.columns else 0)
c4.metric("Statuses", status_summary.shape[0])

st.caption("Bio Evidence Score is an explainable heuristic (v1). It's a signal-strength indicator, not a prediction model.")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trial Finder", "Bio Evidence", "Sponsors"])

# -------------------------
# TAB 1: OVERVIEW
# -------------------------
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


# -------------------------
# TAB 2: TRIAL FINDER
# -------------------------
with tab2:
    st.subheader("Trial Finder (uses Bio table + sidebar filters)")
    st.write("This table respects your sidebar filters.")

    show_cols = [
        c
        for c in [
            "nct_id",
            "title",
            "status",
            "phase",
            "sponsor",
            "conditions",
            "bio_evidence_score",
            "confidence",
            "evidence_reason",
            "pulled_at",
        ]
        if c in df.columns
    ]
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


# -------------------------
# TAB 3: BIO EVIDENCE
# -------------------------
with tab3:
    st.subheader("Bio Evidence (signals-based, explainable)")

    if "bio_evidence_score" not in df.columns:
        st.error("Missing `bio_evidence_score` column in trial_bio_evidence.csv.")
        st.stop()

    # Tab-level controls
    cA, cB, cC, cD = st.columns([1, 1, 1, 2])

    with cA:
        min_score_tab = st.slider("Min score (tab)", 0, 100, max(0, int(np.round(df["bio_evidence_score"].median()))))

    with cB:
        conf_opts = ["All"]
        if "confidence" in df.columns:
            conf_opts += sorted(df["confidence"].replace("", pd.NA).dropna().unique().tolist())
        conf_pick = st.selectbox("Confidence", conf_opts, index=0)

    with cC:
        top_n = st.selectbox("Top N", [25, 50, 100, 200], index=1)

    with cD:
        text_q = st.text_input("Search title/conditions/sponsor", "").strip()

    # Apply tab-level filters
    dfx = df[df["bio_evidence_score"] >= min_score_tab].copy()

    if "confidence" in dfx.columns and conf_pick != "All":
        dfx = dfx[dfx["confidence"] == conf_pick]

    if text_q:
        hay_parts = []
        for col in ["title", "conditions", "sponsor"]:
            if col in dfx.columns:
                hay_parts.append(dfx[col].fillna("").astype(str))
        if hay_parts:
            hay = hay_parts[0]
            for s in hay_parts[1:]:
                hay = hay + " " + s
            dfx = dfx[hay.str.contains(text_q, case=False, na=False)]

    if len(dfx) == 0:
        st.warning("No trials match the current Bio Evidence filters. Lower the min score or clear filters.")
        st.stop()

    # Dynamic cutoffs (percentile-based)
    p20 = float(np.percentile(dfx["bio_evidence_score"], 20))
    p80 = float(np.percentile(dfx["bio_evidence_score"], 80))

    # 1) Score distribution
    st.markdown("### Score distribution")
    st.caption("Sanity check: do we see a spread of signal strength, or everything clumped?")

    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    hist = pd.cut(dfx["bio_evidence_score"], bins=bins, include_lowest=True).value_counts().sort_index()
    hist_df = hist.reset_index()
    hist_df.columns = ["score_bin", "count"]
    hist_df["score_bin"] = hist_df["score_bin"].astype(str)
    st.bar_chart(hist_df.set_index("score_bin")["count"])

    st.info(f"Dynamic cutoffs (based on current filtered set): Low≈<= {p20:.0f} | High≈>= {p80:.0f}")

    st.divider()

    # 2) Top ranked trials
    st.markdown(f"### Top {int(top_n)} trials by Bio Evidence Score")
    cols = [
        c for c in
        ["nct_id", "title", "bio_evidence_score", "confidence", "status", "phase", "sponsor", "evidence_reason"]
        if c in dfx.columns
    ]
    rank = dfx[cols].sort_values("bio_evidence_score", ascending=False).head(int(top_n)).copy()

    if "nct_id" in rank.columns:
        rank["link"] = rank["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

    st.dataframe(rank, use_container_width=True)

    st.download_button(
        "Download ranked trials (CSV)",
        data=rank.to_csv(index=False).encode("utf-8"),
        file_name="ranked_trials_bio_evidence.csv",
        mime="text/csv",
    )

    st.divider()

    # 3) Risk flag: late-phase + low evidence (dynamic)
    st.markdown("### Risk flag: late-phase trials with low biological evidence")
    st.caption("Heuristic flag: Phase 3/4 + bottom-quintile evidence suggests higher uncertainty. Not a prediction.")

    late = dfx.copy()
    if "phase" in late.columns:
        late = late[late["phase"].fillna("").str.contains("Phase 3|Phase 4|PHASE3|PHASE4", case=False, regex=True, na=False)]

    late = late[late["bio_evidence_score"] <= p20].copy()

    if len(late) == 0:
        st.warning("No trials match the Risk Flag criteria under current filters (try widening filters).")
    else:
        rcols = [
            c for c in
            ["nct_id", "title", "bio_evidence_score", "confidence", "status", "phase", "sponsor", "evidence_reason"]
            if c in late.columns
        ]
        late = late[rcols].sort_values("bio_evidence_score", ascending=True).head(50).copy()

        if "nct_id" in late.columns:
            late["link"] = late["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

        st.dataframe(late, use_container_width=True)

    st.divider()

    # 4) Watchlist: high evidence + recruiting + phase 2/3 (dynamic)
    st.markdown("### Watchlist: High signal + Recruiting + Phase 2/3")

    watch = dfx.copy()

    # high evidence = top quintile (>= p80)
    watch = watch[watch["bio_evidence_score"] >= p80]

    if "status" in watch.columns:
        watch = watch[watch["status"].fillna("").str.contains("Recruit", case=False, na=False)]

    if "phase" in watch.columns:
        watch = watch[watch["phase"].fillna("").str.contains("Phase 2|Phase 3|PHASE2|PHASE3", case=False, regex=True, na=False)]

    if len(watch) == 0:
        st.warning("No trials match the Watchlist criteria under current filters (try lowering min score or clearing filters).")
    else:
        wcols = [
            c for c in
            ["nct_id", "title", "bio_evidence_score", "confidence", "status", "phase", "sponsor", "evidence_reason"]
            if c in watch.columns
        ]
        watch = watch[wcols].sort_values("bio_evidence_score", ascending=False).head(50).copy()

        if "nct_id" in watch.columns:
            watch["link"] = watch["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if str(x).strip() else "")

        st.dataframe(watch, use_container_width=True)

    st.caption("Score = phase weight + status weight + keyword evidence (bio + mechanism terms). Explainable by design; intentionally not ML.")


# -------------------------
# TAB 4: SPONSORS
# -------------------------
with tab4:
    st.subheader("Top Sponsors (filtered view)")
    if "sponsor" in df.columns:
        sponsor_counts = df["sponsor"].fillna("Unknown").replace("", "Unknown").value_counts().head(25)
        st.bar_chart(sponsor_counts)
    else:
        st.info("No sponsor column found.")
