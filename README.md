# Peds Omics Workflows

> Reproducible starter workflows for pediatric omics research — designed to be transparent, inspectable, and safe to extend.

中文简介：这是一个面向儿科疾病生物信息学研究的开源起步工具箱。首个版本提供两个零额外依赖、可在本地直接运行的最小工作流：已协调两样本孟德尔随机化（MR）的 IVW 汇总计算，以及单细胞元数据的质量控制（QC）汇总。它的目标是帮助研究者建立可复现的分析骨架，而非替代完整的研究设计、专业统计审查或临床判断。

## Why this project

Pediatric cohorts are often smaller, heterogeneous, and difficult to share. A transparent baseline makes it easier to:

- record data assumptions and QC thresholds explicitly;
- separate reusable code from study-specific, potentially sensitive data;
- test a workflow before adding complex R/Python packages; and
- invite contributors to add well-documented modules for real research needs.

## Scope and safety

- The bundled CSV files are **synthetic examples**, not patient data or real GWAS summary statistics.
- The MR command assumes that instruments are independent and already harmonised. It does **not** perform LD clumping, allele harmonisation, pleiotropy diagnostics, multiple-testing correction, or sensitivity analyses.
- The single-cell command only summarises supplied QC metadata. Thresholds must be chosen for each study, chemistry, tissue, and sequencing design.
- This software is for research and education only; it is **not clinical decision-support software**.

## Quick start

Requires Python 3.10 or later. No third-party runtime packages are required.

```bash
git clone https://github.com/zhuhhfsdfsd/peds-omics-workflows.git
cd peds-omics-workflows
python -m venv .venv
```

Activate the virtual environment, then install the local package:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
```

Run the synthetic examples:

```bash
peds-omics mr --input data/example/mr_instruments.csv --output results/mr_summary.json
peds-omics scrna-qc --input data/example/scrna_cells.csv --output results/scrna_qc_summary.json
peds-omics pseudobulk --input data/example/pseudobulk_counts.csv --output results/pseudobulk_counts.csv
```

The commands create JSON results containing the method, thresholds, summary statistics, and a short interpretation reminder. Add `--manifest results/manifest.json` to create a machine-readable provenance record with the input filename, SHA-256 hash, parameters, and software version. It does not include input rows or full paths. See [data/example](data/example/) for the required CSV columns.

## Input schemas

### `mr_instruments.csv`

| Column | Meaning |
| --- | --- |
| `variant` | Unique, non-empty public variant identifier |
| `exposure_beta`, `exposure_se` | Exposure association and standard error |
| `outcome_beta`, `outcome_se` | Outcome association and standard error |
| `aligned` | Must be `true`; confirms prior allele harmonisation |

### `scrna_cells.csv`

| Column | Meaning |
| --- | --- |
| `cell_id` | Unique, non-empty, non-identifying cell identifier |
| `total_counts` | Per-cell total count |
| `n_genes` | Detected genes per cell |
| `mito_fraction` | Mitochondrial fraction, 0–1 |
| `cell_type` | Existing annotation; blank values are normalised to `unassigned` |

## Commands

| Command | Description |
| --- | --- |
| `peds-omics mr --input INPUT --output OUTPUT` | Calculate an exploratory delta-method IVW MR summary from harmonised instruments. |
| `peds-omics scrna-qc --input INPUT --output OUTPUT` | Summarise cell-level QC using configurable thresholds. |
| `python -m unittest discover -s tests -v` | Run the unit tests. |

## Repository layout

```text
src/peds_omics_workflows/  # Reusable MR, single-cell QC, and CLI modules
data/example/              # Synthetic, non-identifying example inputs
tests/                      # Unit tests
docs/decisions/             # Architecture decision records
.github/workflows/          # GitHub Actions quality checks
```

## Contributing

Contributions are welcome, particularly reproducible templates for pediatric disease omics studies. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request. The issue templates ask for minimal, safe-to-share reproduction details and validation plans. Do not submit identifiable patient data, credentials, or unpublished restricted datasets.

Planned work is listed in [docs/roadmap.md](docs/roadmap.md). Key design rationale is recorded in [ADR-001](docs/decisions/ADR-001-stdlib-first.md).

For an optional export of already harmonised `TwoSampleMR`-style data into this project's narrow MR CSV schema, see [the interoperability guide](docs/twosamplemr-interoperability.md). The helper does not replace upstream harmonisation or sensitivity analyses.

For a synthetic immune-cell count aggregation example, see [the pseudobulk guide](docs/pseudobulk-example.md). It performs aggregation only, not normalization or inference.

## Citation

Until the project has a citable release, please cite the repository URL, commit hash, release tag, and access date. The maintainer should update [CITATION.cff](CITATION.cff) before the first public release.

## License

Released under the [MIT License](LICENSE).
