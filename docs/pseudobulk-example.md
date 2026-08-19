# Synthetic immune-cell pseudobulk example

`data/example/pseudobulk_counts.csv` is a synthetic, long-format count table. The `pseudobulk` command sums `count` values by `donor_id`, `cell_type`, and `gene`.

```bash
peds-omics pseudobulk \
  --input data/example/pseudobulk_counts.csv \
  --output results/pseudobulk_counts.csv
```

The example's donor identifiers, cell-type labels, genes, and counts are illustrative only. It is not patient data and it does not establish cell identity, disease association, or clinical relevance.

## Required columns

| Column | Requirement |
| --- | --- |
| `donor_id` | Non-empty study-local donor identifier |
| `cell_type` | Non-empty pre-existing annotation |
| `gene` | Non-empty gene label |
| `count` | Finite, non-negative numeric count |

This command is intentionally limited to deterministic aggregation. It does not perform normalization, batch correction, differential expression, cell-type annotation, quality control, or statistical inference. Select those methods and document their assumptions separately for each study.
