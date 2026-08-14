"""Transparent, educational two-sample MR summary calculations.

This module intentionally implements only an inverse-variance weighted (IVW)
summary estimate for already harmonised, independent instruments. It is a
reproducible baseline, not a substitute for a full Mendelian-randomisation
pipeline or expert causal inference review.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = {
    "variant",
    "exposure_beta",
    "exposure_se",
    "outcome_beta",
    "outcome_se",
    "aligned",
}


@dataclass(frozen=True)
class Instrument:
    """A harmonised summary-statistics instrument used by the IVW estimator."""

    variant: str
    exposure_beta: float
    exposure_se: float
    outcome_beta: float
    outcome_se: float


def _as_finite_float(value: str, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Row {row_number}: {field} must be numeric.") from error
    if not math.isfinite(number):
        raise ValueError(f"Row {row_number}: {field} must be finite.")
    return number


def read_instruments(path: str | Path) -> list[Instrument]:
    """Read public, pre-harmonised instruments from a CSV file.

    Rows with ``aligned`` other than ``true`` are rejected rather than silently
    analysed. This makes a potentially unsafe data decision visible to users.
    """

    source = Path(path)
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}.")

        instruments: list[Instrument] = []
        for row_number, row in enumerate(reader, start=2):
            if (row.get("aligned") or "").strip().lower() != "true":
                raise ValueError(
                    f"Row {row_number}: aligned must be true before IVW analysis."
                )
            exposure_beta = _as_finite_float(row["exposure_beta"], "exposure_beta", row_number)
            exposure_se = _as_finite_float(row["exposure_se"], "exposure_se", row_number)
            outcome_beta = _as_finite_float(row["outcome_beta"], "outcome_beta", row_number)
            outcome_se = _as_finite_float(row["outcome_se"], "outcome_se", row_number)
            if exposure_beta == 0:
                raise ValueError(f"Row {row_number}: exposure_beta cannot be zero.")
            if exposure_se <= 0 or outcome_se <= 0:
                raise ValueError(f"Row {row_number}: standard errors must be positive.")
            instruments.append(
                Instrument(
                    variant=(row["variant"] or "").strip(),
                    exposure_beta=exposure_beta,
                    exposure_se=exposure_se,
                    outcome_beta=outcome_beta,
                    outcome_se=outcome_se,
                )
            )

    if len(instruments) < 2:
        raise ValueError("At least two independent instruments are required for IVW.")
    return instruments


def ivw_summary(instruments: list[Instrument]) -> dict[str, float | int | str]:
    """Calculate a delta-method IVW estimate and diagnostic heterogeneity value."""

    if len(instruments) < 2:
        raise ValueError("At least two instruments are required for IVW.")

    ratios: list[float] = []
    weights: list[float] = []
    for instrument in instruments:
        ratio = instrument.outcome_beta / instrument.exposure_beta
        # Delta-method variance for the ratio of two estimated associations.
        variance = (instrument.outcome_se / instrument.exposure_beta) ** 2 + (
            instrument.outcome_beta * instrument.exposure_se / instrument.exposure_beta**2
        ) ** 2
        if variance <= 0 or not math.isfinite(variance):
            raise ValueError(f"Invalid ratio variance for {instrument.variant!r}.")
        ratios.append(ratio)
        weights.append(1 / variance)

    total_weight = sum(weights)
    estimate = sum(weight * ratio for weight, ratio in zip(weights, ratios)) / total_weight
    standard_error = math.sqrt(1 / total_weight)
    z_score = estimate / standard_error
    p_value = math.erfc(abs(z_score) / math.sqrt(2))
    q_statistic = sum(weight * (ratio - estimate) ** 2 for weight, ratio in zip(weights, ratios))

    return {
        "method": "ivw_delta_method",
        "instrument_count": len(instruments),
        "estimate": estimate,
        "standard_error": standard_error,
        "z_score": z_score,
        "p_value": p_value,
        "heterogeneity_q": q_statistic,
        "heterogeneity_df": len(instruments) - 1,
        "interpretation": "Exploratory IVW estimate; assess instrument validity, LD independence, and pleiotropy separately.",
    }
