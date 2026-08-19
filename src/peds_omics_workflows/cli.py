"""Command line interface for the reproducible starter workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import __version__
from .mr import ivw_summary, read_instruments
from .pseudobulk import aggregate_pseudobulk, read_long_counts, write_pseudobulk_csv
from .scrna import qc_summary, read_cell_metadata


def _write_json(path: str | Path, value: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: str | Path) -> str:
    """Return a content hash without loading an entire input file into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(65_536):
            digest.update(chunk)
    return digest.hexdigest()


def _write_manifest(
    path: str | Path,
    *,
    workflow: str,
    input_path: str | Path,
    output_path: str | Path,
    parameters: dict[str, object],
) -> None:
    """Write a shareable, machine-readable record of a local analysis run."""

    source = Path(input_path)
    target = Path(output_path)
    _write_json(
        path,
        {
            "manifest_schema_version": "1.0",
            "workflow": workflow,
            "input": {"filename": source.name, "sha256": _sha256(source)},
            "output": {"filename": target.name},
            "parameters": parameters,
            "software": {"package": "peds-omics-workflows", "version": __version__},
            "data_handling": (
                "Input data remain local. The manifest records filenames, a content hash, "
                "and parameters; it does not include input rows."
            ),
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="peds-omics", description="Reproducible pediatric omics starter workflows."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    mr = commands.add_parser("mr", help="Run an educational IVW MR summary.")
    mr.add_argument("--input", required=True, help="Harmonised instrument CSV.")
    mr.add_argument("--output", required=True, help="Output JSON path.")
    mr.add_argument("--manifest", help="Optional provenance manifest JSON path.")

    qc = commands.add_parser("scrna-qc", help="Summarise single-cell QC metadata.")
    qc.add_argument("--input", required=True, help="Cell metadata CSV.")
    qc.add_argument("--output", required=True, help="Output JSON path.")
    qc.add_argument("--manifest", help="Optional provenance manifest JSON path.")
    qc.add_argument("--min-counts", type=float, default=500)
    qc.add_argument("--min-genes", type=float, default=200)
    qc.add_argument("--max-mito", type=float, default=0.20)

    pseudobulk = commands.add_parser(
        "pseudobulk", help="Aggregate long-format counts by donor, cell type, and gene."
    )
    pseudobulk.add_argument("--input", required=True, help="Long-format count CSV.")
    pseudobulk.add_argument("--output", required=True, help="Aggregated pseudobulk CSV path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a requested workflow and write a provenance-friendly JSON result."""

    args = build_parser().parse_args(argv)
    if args.command == "mr":
        _write_json(args.output, ivw_summary(read_instruments(args.input)))
        if args.manifest:
            _write_manifest(
                args.manifest,
                workflow="mr",
                input_path=args.input,
                output_path=args.output,
                parameters={"method": "ivw_delta_method"},
            )
    elif args.command == "scrna-qc":
        cells = read_cell_metadata(args.input)
        _write_json(
            args.output,
            qc_summary(cells, args.min_counts, args.min_genes, args.max_mito),
        )
        if args.manifest:
            _write_manifest(
                args.manifest,
                workflow="scrna-qc",
                input_path=args.input,
                output_path=args.output,
                parameters={
                    "min_counts": args.min_counts,
                    "min_genes": args.min_genes,
                    "max_mito_fraction": args.max_mito,
                },
            )
    elif args.command == "pseudobulk":
        write_pseudobulk_csv(args.output, aggregate_pseudobulk(read_long_counts(args.input)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
