# Always use user library
.libPaths("~/R/library")

library(readr)
library(dplyr)
library(janitor)

# Read Python output
trials <- read_csv("data_processed/trials_clean.csv") |> clean_names()

# Simple analytics: trial count by status
status_summary <- trials |>
    mutate(status = ifelse(is.na(status), "Unknown", status)) |>
    count(status, sort = TRUE)

# Save output for dashboard
write_csv(status_summary, "data_processed/trial_status_summary.csv")

cat("Saved: data_processed/trial_status_summary.csv\n")
print(status_summary)