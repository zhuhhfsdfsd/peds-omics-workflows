"""Dependency-free pseudobulk aggregation for synthetic or approved count data."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = {"donor_id", "cell_type", "gene", "count"}


@dataclass(frozen=True)
class CellGeneCount:
    """One long-format cell-type count record for a donor and gene."""

    donor_id: str
    cell_type: str
    gene: str
    count: float


def _finite_nonnegative(value: str, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"Row {row_number}: {field} must be finite and non-negative.")
    return number


def read_long_counts(path: str | Path) -> list[CellGeneCount]:
    """Read a validated long-format count table without altering source data."""

    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}.")

        records: list[CellGeneCount] = []
        for row_number, row in enumerate(reader, start=2):
            identifiers = {
                field: (row[field] or "").strip()
                for field in ("donor_id", "cell_type", "gene")
            }
            empty = [field for field, value in identifiers.items() if not value]
            if empty:
                raise ValueError(f"Row {row_number}: {', '.join(empty)} must not be empty.")
            records.append(
                CellGeneCount(
                    donor_id=identifiers["donor_id"],
                    cell_type=identifiers["cell_type"],
                    gene=identifiers["gene"],
                    count=_finite_nonnegative(row["count"], "count", row_number),
                )
            )
    if not records:
        raise ValueError("Long-format count input is empty.")
    return records


def aggregate_pseudobulk(records: list[CellGeneCount]) -> list[CellGeneCount]:
    """Sum counts by donor, cell type, and gene in a deterministic order."""

    totals: dict[tuple[str, str, str], float] = {}
    for record in records:
        key = (record.donor_id, record.cell_type, record.gene)
        totals[key] = totals.get(key, 0.0) + record.count
    return [
        CellGeneCount(donor_id, cell_type, gene, count)
        for (donor_id, cell_type, gene), count in sorted(totals.items())
    ]


def write_pseudobulk_csv(path: str | Path, records: list[CellGeneCount]) -> None:
    """Write aggregated pseudobulk counts as a portable CSV file."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["donor_id", "cell_type", "gene", "count"])
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "donor_id": record.donor_id,
                    "cell_type": record.cell_type,
                    "gene": record.gene,
                    "count": record.count,
                }
            )
