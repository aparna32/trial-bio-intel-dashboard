# 🧬 Clinical Trials + Bio Evidence Intelligence Dashboard

An end-to-end analytics pipeline and interactive dashboard that combines **public clinical trial metadata** with **biological evidence signals** to surface early warning indicators of trial risk and opportunity.

🔗 **Live App:** https://trial-bio-intel.streamlit.app/  
🔗 **Repository:** https://github.com/aparna32/trial-bio-intel-dashboard

---

## 🎯 Why This Project

Late-stage clinical trial failure is expensive and often predictable.

This project demonstrates how **public clinical trial data + biological evidence heuristics** can be transformed into an **explainable intelligence dashboard** that helps analysts:
- Identify high-risk late-phase trials
- Surface high-signal recruiting studies
- Compare sponsors and pipelines at a glance

The focus is on **interpretability, auditability, and decision support** — not black-box prediction.

---

## 🧠 What This Is (and Is Not)

**This is:**
- A signals-based analytics system
- An explainable scoring framework
- A risk-triage and prioritization tool

**This is not:**
- A machine learning prediction model
- A financial or investment recommendation system
- A proprietary data product

---

## ⚙️ Project Architecture

```mermaid
flowchart TD
    A[ClinicalTrials.gov API] --> B[Python: Trial Ingestion & Cleaning]
    B --> C[Processed Trial Metadata]
    C --> D[R: Bio Evidence Scoring Heuristic]
    D --> E[Scored Trial Dataset]
    E --> F[Streamlit Dashboard]
