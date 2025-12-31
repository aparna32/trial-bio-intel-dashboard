import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# Make sure folders exist
Path("data_raw").mkdir(exist_ok=True)
Path("data_processed").mkdir(exist_ok=True)

# What disease we are tracking
CONDITION = "breast cancer"

# ClinicalTrials.gov API (v2)
URL = "https://clinicaltrials.gov/api/v2/studies"

PARAMS = {
    "query.term": CONDITION,
    "pageSize": 100,
    "format": "json"
}

print("Fetching data from ClinicalTrials.gov...")

response = requests.get(URL, params=PARAMS, timeout=60)
response.raise_for_status()
data = response.json()

studies = data.get("studies", [])
print("Number of studies fetched:", len(studies))

rows = []

for study in studies:
    protocol = study.get("protocolSection", {})

    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})

    rows.append({
        "nct_id": identification.get("nctId"),
        "title": identification.get("briefTitle"),
        "status": status.get("overallStatus"),
        "study_type": design.get("studyType"),
        "phase": ", ".join(design.get("phases", [])) if isinstance(design.get("phases", []), list) else None,
        "conditions": ", ".join(conditions.get("conditions", [])) if isinstance(conditions.get("conditions", []), list) else None,
        "sponsor": sponsor.get("leadSponsor", {}).get("name"),
        "pulled_at": datetime.utcnow().isoformat()
    })

df = pd.DataFrame(rows)

# Save raw data
df.to_csv("data_raw/trials_raw.csv", index=False)

# Clean + save processed data
df = df.dropna(subset=["nct_id"]).drop_duplicates(subset=["nct_id"])
df.to_csv("data_processed/trials_clean.csv", index=False)

print("Saved files:")
print(" - data_raw/trials_raw.csv")
print(" - data_processed/trials_clean.csv")
print("Rows after cleaning:", len(df))