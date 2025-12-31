.libPaths("~/R/library")

library(readr)
library(dplyr)
library(stringr)
library(janitor)

trials <- read_csv("data_processed/trials_clean.csv") |> clean_names()

score_row <- function(title, conditions, phase, status) {
  txt <- paste(title, conditions) |> tolower()

  bio_terms <- c(
    "biomarker","transcript","rna","mrna","gene","genomic","proteomic",
    "pathway","expression","signature","multi-omic","omics","metabolomic"
  )

  mech_terms <- c(
    "mechanism","target","inhibitor","agonist","antagonist","monoclonal",
    "antibody","checkpoint","kinase","therapy","immunotherapy"
  )

  bio_hits  <- sum(str_detect(txt, bio_terms))
  mech_hits <- sum(str_detect(txt, mech_terms))

  phase_txt <- ifelse(is.na(phase), "unknown", tolower(phase))
  phase_score <- case_when(
    str_detect(phase_txt, "phase 4") ~ 30,
    str_detect(phase_txt, "phase 3") ~ 24,
    str_detect(phase_txt, "phase 2") ~ 18,
    str_detect(phase_txt, "phase 1") ~ 10,
    TRUE ~ 8
  )

  status_txt <- ifelse(is.na(status), "unknown", tolower(status))
  status_score <- case_when(
    str_detect(status_txt, "completed") ~ 12,
    str_detect(status_txt, "recruit") ~ 10,
    str_detect(status_txt, "active") ~ 9,
    str_detect(status_txt, "not yet") ~ 7,
    TRUE ~ 6
  )

  keyword_score <- pmin(25, bio_hits * 6 + mech_hits * 3)

  total <- phase_score + status_score + keyword_score
  total <- max(0, min(100, total))

  conf <- case_when(
    total >= 70 ~ "High",
    total >= 45 ~ "Medium",
    TRUE ~ "Low"
  )

  reason <- paste0(
    "phase=", phase_score, ", status=", status_score,
    ", bio_hits=", bio_hits, ", mech_hits=", mech_hits
  )

  list(total=total, confidence=conf, reason=reason)
}

scored <- trials %>%
  mutate(
    title = ifelse(is.na(title), "", title),
    conditions = ifelse(is.na(conditions), "", conditions)
  ) %>%
  rowwise() %>%
  mutate(
    tmp = list(score_row(title, conditions, phase, status)),
    bio_evidence_score = tmp$total,
    confidence = tmp$confidence,
    evidence_reason = tmp$reason
  ) %>%
  ungroup() %>%
  select(-tmp)

write_csv(scored, "data_processed/trial_bio_evidence.csv")

cat("Saved: data_processed/trial_bio_evidence.csv\n")
cat("Rows:", nrow(scored), "\n")

