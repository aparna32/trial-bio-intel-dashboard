import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trials + Bio Evidence", layout="wide")
st.title("Clinical Trials + Bio Evidence Dashboard")

def must_exist(path: str):
    if not os.path.exists(path):
        st.error(f"Missing file: {path}. Run the pipeline (Python + R) or wait for GitHub Actions refresh.")
        st.stop()

must_exist("data_processed/trials_clean.csv")
must_exist("data_processed/trial_status_summary.csv")

trials = pd.read_csv("data_processed/trials_clean.csv")
status_summary = pd.read_csv("data_processed/trial_status_summary.csv")

# ---- Sidebar filters
st.sidebar.header("Filters")

status_options = ["All"] + sorted([x for x in trials.get("status", pd.Series()).dropna().unique()])
phase_options = ["All"] + sorted([x for x in trials.get("phase", pd.Series()).dropna().unique()])

status_pick = st.sidebar.selectbox("Status", status_options, index=0)
phase_pick = st.sidebar.selectbox("Phase", phase_options, index=0)
sponsor_query = st.sidebar.text_input("Sponsor contains", "")

df = trials.copy()

if "status" in df.columns and status_pick != "All":
    df = df[df["status"] == status_pick]

if "phase" in df.columns and phase_pick != "All":
    df = df[df["phase"] == phase_pick]

if "sponsor" in df.columns and sponsor_query.strip():
    df = df[df["sponsor"].fillna("").str.contains(sponsor_query.strip(), case=False)]

# ---- Top metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Trials loaded", len(trials))
c2.metric("Filtered trials", len(df))
c3.metric("Unique sponsors", trials["sponsor"].nunique(dropna=True) if "sponsor" in trials.columns else 0)
c4.metric("Statuses", status_summary.shape[0])

st.divider()

# ---- Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Trial Finder", "Sponsors"])

with tab1:
    left, right = st.columns(2)

    with left:
        st.subheader("Trials by Status (R output)")
        if "status" in status_summary.columns and "n" in status_summary.columns:
            st.bar_chart(status_summary.set_index("status")["n"])
        else:
            st.dataframe(status_summary)

    with right:
        st.subheader("Trials by Phase (Python output)")
        if "phase" in trials.columns:
            phase_counts = trials["phase"].fillna("Unknown").value_counts()
            st.bar_chart(phase_counts)
        else:
            st.info("No phase column found.")

    st.caption("Data source: ClinicalTrials.gov API • Analytics: Python + R • Auto-refresh via GitHub Actions")

with tab2:
    st.subheader("Trial Finder (clickable NCT IDs)")
    show_cols = [c for c in ["nct_id", "title", "status", "phase", "sponsor", "conditions", "pulled_at"] if c in df.columns]
    view = df[show_cols].copy()

    if "nct_id" in view.columns:
        view["trial_link"] = view["nct_id"].apply(lambda x: f"https://clinicaltrials.gov/study/{x}" if pd.notna(x) else "")
        view = view.rename(columns={"trial_link": "link"})

    st.dataframe(view, use_container_width=True)

    st.download_button(
        "Download filtered trials (CSV)",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="filtered_trials.csv",
        mime="text/csv",
    )

with tab3:
    st.subheader("Top Sponsors (filtered view)")
    if "sponsor" in df.columns:
        sponsor_counts = df["sponsor"].fillna("Unknown").value_counts().head(20)
        st.bar_chart(sponsor_counts)
    else:
        st.info("No sponsor column found.")
