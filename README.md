# Clinical Trial Bio-Intel Dashboard 🧬📊

A **live, automated analytics dashboard** that tracks clinical trials from ClinicalTrials.gov and surfaces biologically meaningful signals using an **explainable Bio Evidence Score**.

This project is designed as a **research / risk-intelligence tool**, not a prediction model.

---

## 🔍 Problem Statement

Late-stage clinical trial failure is expensive and common.  
Analysts and researchers need **early, explainable signals** to prioritize trials with stronger biological grounding (biomarkers, transcriptomics, mechanisms of action).

This dashboard helps answer:
- Which trials show stronger biological evidence?
- Which late-phase trials may carry higher uncertainty?
- Which recruiting trials deserve closer monitoring?

---

## 🚀 Live Demo

- **Live App:** https://trial-bio-intel.streamlit.app/  
- **GitHub Repo:** https://github.com/aparna32/trial-bio-intel-dashboard  

---

## 🧠 What This Dashboard Does

- Pulls real clinical trial metadata from **ClinicalTrials.gov**
- Computes an **explainable Bio Evidence Score** using:
  - Trial phase
  - Recruitment status
  - Presence of biomarker / transcriptomic / mechanism keywords
- Provides:
  - Trial finder with filters
  - Score distribution & ranking
  - Risk flag (late phase + weak evidence)
  - Watchlist (high signal + recruiting + Phase 2/3)

---

## ⚙️ How It Works (Pipeline)

1. **Data Ingestion (Python)**  
   Fetches and cleans trial metadata from ClinicalTrials.gov

2. **Evidence Scoring (R)**  
   Assigns an interpretable Bio Evidence Score using rule-based heuristics

3. **Automation (GitHub Actions)**  
   Scheduled refresh to keep data up-to-date

4. **Visualization (Streamlit)**  
   Interactive dashboard for exploration and analyst triage

---

## 🛠 Tech Stack

- **Python** (data ingestion, processing)
- **R** (biological evidence scoring)
- **Streamlit** (interactive dashboard)
- **GitHub Actions** (automation)
- **Pandas / NumPy / tidyverse**

---

## 📌 Important Notes

- The **Bio Evidence Score is heuristic and explainable**  
- It is **not a machine-learning prediction model**
- Designed for **decision support**, not clinical conclusions

---

## 📷 Screenshots

_(Screenshots added in the next step)_

---

## 👤 Author

Built by **Aparna Bhardwaj**  
Focused on analytics, bioinformatics, and risk-driven decision systems


### 🚀 Live App
👉 https://trial-bio-intel.streamlit.app/
