"""Dependency-free single-cell QC summaries for CSV cell metadata."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


REQUIRED_COLUMNS = {"cell_id", "total_counts", "n_genes", "mito_fraction", "cell_type"}


def _number(value: str, field: str, row_number: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(result):
        raise ValueError(f"Row {row_number}: {field} must be finite.")
    return result


def read_cell_metadata(path: str | Path) -> list[dict[str, str | float]]:
    """Read non-identifying cell-level summary metadata from a CSV file."""

    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}.")
        rows: list[dict[str, str | float]] = []
        seen_cell_ids: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            counts = _number(row["total_counts"], "total_counts", row_number)
            genes = _number(row["n_genes"], "n_genes", row_number)
            mito = _number(row["mito_fraction"], "mito_fraction", row_number)
            if counts < 0 or genes < 0 or not 0 <= mito <= 1:
                raise ValueError(f"Row {row_number}: QC values are out of range.")
            cell_id = (row["cell_id"] or "").strip()
            if not cell_id:
                raise ValueError(f"Row {row_number}: cell_id must not be empty.")
            if cell_id in seen_cell_ids:
                raise ValueError(f"Row {row_number}: duplicate cell_id {cell_id!r}.")
            seen_cell_ids.add(cell_id)
            cell_type = (row["cell_type"] or "").strip() or "unassigned"
            rows.append(
                {
                    "cell_id": cell_id,
                    "cell_type": cell_type,
                    "total_counts": counts,
                    "n_genes": genes,
                    "mito_fraction": mito,
                }
            )
    if not rows:
        raise ValueError("Cell metadata input is empty.")
    return rows


def qc_summary(
    cells: list[dict[str, str | float]],
    min_counts: float = 500,
    min_genes: float = 200,
    max_mito_fraction: float = 0.20,
) -> dict[str, object]:
    """Summarise transparent QC thresholds without modifying the source data."""

    if min_counts < 0 or min_genes < 0 or not 0 <= max_mito_fraction <= 1:
        raise ValueError("QC thresholds are out of range.")

    passing = [
        cell
        for cell in cells
        if float(cell["total_counts"]) >= min_counts
        and float(cell["n_genes"]) >= min_genes
        and float(cell["mito_fraction"]) <= max_mito_fraction
    ]
    by_cell_type: dict[str, int] = {}
    for cell in passing:
        cell_type = str(cell["cell_type"])
        by_cell_type[cell_type] = by_cell_type.get(cell_type, 0) + 1

    counts = [float(cell["total_counts"]) for cell in cells]
    genes = [float(cell["n_genes"]) for cell in cells]
    mito = [float(cell["mito_fraction"]) for cell in cells]
    return {
        "cell_count": len(cells),
        "passing_cell_count": len(passing),
        "passing_fraction": len(passing) / len(cells),
        "thresholds": {
            "min_counts": min_counts,
            "min_genes": min_genes,
            "max_mito_fraction": max_mito_fraction,
        },
        "median_total_counts": statistics.median(counts),
        "median_n_genes": statistics.median(genes),
        "median_mito_fraction": statistics.median(mito),
        "passing_cells_by_annotation": dict(sorted(by_cell_type.items())),
        "interpretation": "QC summary only; choose study-specific thresholds before downstream analysis.",
    }
