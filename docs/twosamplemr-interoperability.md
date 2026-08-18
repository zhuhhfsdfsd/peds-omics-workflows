# TwoSampleMR interoperability export

This optional R helper exports an already harmonised `TwoSampleMR`-style data frame to the small CSV schema used by `peds-omics mr`.

## Scope and safety

The helper does **not** install or call `TwoSampleMR`. It does not perform instrument selection, LD clumping, allele harmonisation, palindromic-variant handling, pleiotropy testing, or sensitivity analyses. Run and document those upstream steps first. The exported `aligned = true` value only records that the upstream workflow marked the row as eligible with `mr_keep = TRUE`; it is not an independent verification of alignment.

Do not commit harmonised RDS files or exported CSV files if they contain restricted or unpublished summary statistics. Use only data that you are permitted to process locally and share.

## Required upstream object

Save the upstream harmonised data frame as an RDS file. Retained rows must contain these columns:

| Upstream column | Exported project column |
| --- | --- |
| `SNP` | `variant` |
| `beta.exposure` | `exposure_beta` |
| `se.exposure` | `exposure_se` |
| `beta.outcome` | `outcome_beta` |
| `se.outcome` | `outcome_se` |
| `mr_keep` | used to retain eligible rows |

The helper requires at least two retained, unique SNP identifiers and finite numeric effects and standard errors.

## Export and run

```r
# Example after performing and documenting your own TwoSampleMR workflow:
saveRDS(harmonised_data, "local/harmonised_data.rds")
```

```bash
Rscript examples/export_twosamplemr_harmonised.R \
  local/harmonised_data.rds local/mr_instruments.csv

peds-omics mr \
  --input local/mr_instruments.csv \
  --output results/mr_summary.json \
  --manifest results/mr_manifest.json
```

The resulting Python summary remains exploratory. Record the upstream package versions, GWAS sources, clumping and harmonisation settings, and all sensitivity analyses alongside the analysis manifest.
