import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trials + Bio Evidence", layout="wide")
st.title("Clinical Trials + Bio Evidence Dashboard")

# Load data
trials = pd.read_csv("data_processed/trials_clean.csv")
status_summary = pd.read_csv("data_processed/trial_status_summary.csv")

# Top metrics
c1, c2, c3 = st.columns(3)
c1.metric("Trials loaded", len(trials))
c2.metric("Unique sponsors", trials["sponsor"].nunique(dropna=True) if "sponsor" in trials.columns else 0)
c3.metric("Statuses", status_summary.shape[0])

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Trials by Status (R output)")
    # Ensure correct column names
    if "status" in status_summary.columns and "n" in status_summary.columns:
        chart_df = status_summary.set_index("status")["n"]
        st.bar_chart(chart_df)
    else:
        st.write("Status summary columns not found. Showing table:")
        st.dataframe(status_summary)

with right:
    st.subheader("Trials by Phase (Python output)")
    phase_counts = trials["phase"].fillna("Unknown").value_counts()
    st.bar_chart(phase_counts)

st.divider()

st.subheader("Preview: Trials table")
st.dataframe(trials.head(50))