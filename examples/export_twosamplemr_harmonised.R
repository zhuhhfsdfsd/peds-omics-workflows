#!/usr/bin/env Rscript

# Export a TwoSampleMR harmonised-data RDS file to the deliberately small CSV
# schema accepted by `peds-omics mr`. This script does not perform clumping,
# allele harmonisation, or sensitivity analysis; those responsibilities remain
# with the upstream workflow and its documented settings.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2) {
  stop(
    "Usage: Rscript export_twosamplemr_harmonised.R <harmonised-data.rds> <output.csv>",
    call. = FALSE
  )
}

input_path <- arguments[[1]]
output_path <- arguments[[2]]
if (!file.exists(input_path)) {
  stop(sprintf("Input RDS file does not exist: %s", input_path), call. = FALSE)
}

harmonised <- readRDS(input_path)
if (!is.data.frame(harmonised)) {
  stop("Input RDS must contain a data frame produced by an upstream harmonisation step.", call. = FALSE)
}

required_columns <- c(
  "SNP", "beta.exposure", "se.exposure", "beta.outcome", "se.outcome", "mr_keep"
)
missing_columns <- setdiff(required_columns, names(harmonised))
if (length(missing_columns) > 0) {
  stop(
    sprintf("Missing required harmonised-data columns: %s", paste(missing_columns, collapse = ", ")),
    call. = FALSE
  )
}

keep <- !is.na(harmonised$mr_keep) & harmonised$mr_keep
if (sum(keep) < 2) {
  stop("At least two rows with mr_keep = TRUE are required for the downstream IVW summary.", call. = FALSE)
}

numeric_columns <- c("beta.exposure", "se.exposure", "beta.outcome", "se.outcome")
for (column in numeric_columns) {
  values <- harmonised[[column]][keep]
  if (!is.numeric(values) || any(!is.finite(values))) {
    stop(sprintf("Column %s must contain finite numeric values for retained rows.", column), call. = FALSE)
  }
}

variants <- trimws(as.character(harmonised$SNP[keep]))
if (any(!nzchar(variants))) {
  stop("Retained rows contain an empty SNP identifier.", call. = FALSE)
}
if (anyDuplicated(variants)) {
  stop("Retained rows contain duplicate SNP identifiers.", call. = FALSE)
}

export <- data.frame(
  variant = variants,
  exposure_beta = harmonised$beta.exposure[keep],
  exposure_se = harmonised$se.exposure[keep],
  outcome_beta = harmonised$beta.outcome[keep],
  outcome_se = harmonised$se.outcome[keep],
  aligned = "true",
  check.names = FALSE,
  stringsAsFactors = FALSE
)

output_directory <- dirname(output_path)
if (!dir.exists(output_directory)) {
  dir.create(output_directory, recursive = TRUE)
}
write.csv(export, output_path, row.names = FALSE, quote = TRUE)
