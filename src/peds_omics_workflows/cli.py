"""Command line interface for the reproducible starter workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mr import ivw_summary, read_instruments
from .scrna import qc_summary, read_cell_metadata


def _write_json(path: str | Path, value: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="peds-omics", description="Reproducible pediatric omics starter workflows."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    mr = commands.add_parser("mr", help="Run an educational IVW MR summary.")
    mr.add_argument("--input", required=True, help="Harmonised instrument CSV.")
    mr.add_argument("--output", required=True, help="Output JSON path.")

    qc = commands.add_parser("scrna-qc", help="Summarise single-cell QC metadata.")
    qc.add_argument("--input", required=True, help="Cell metadata CSV.")
    qc.add_argument("--output", required=True, help="Output JSON path.")
    qc.add_argument("--min-counts", type=float, default=500)
    qc.add_argument("--min-genes", type=float, default=200)
    qc.add_argument("--max-mito", type=float, default=0.20)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a requested workflow and write a provenance-friendly JSON result."""

    args = build_parser().parse_args(argv)
    if args.command == "mr":
        _write_json(args.output, ivw_summary(read_instruments(args.input)))
    elif args.command == "scrna-qc":
        cells = read_cell_metadata(args.input)
        _write_json(
            args.output,
            qc_summary(cells, args.min_counts, args.min_genes, args.max_mito),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
