import tempfile
import unittest
from pathlib import Path

from peds_omics_workflows.pseudobulk import (
    CellGeneCount,
    aggregate_pseudobulk,
    read_long_counts,
)


class PseudobulkTests(unittest.TestCase):
    def test_sums_counts_by_donor_cell_type_and_gene(self) -> None:
        result = aggregate_pseudobulk(
            [
                CellGeneCount("donor-1", "T_cell", "IL7R", 10.0),
                CellGeneCount("donor-1", "T_cell", "IL7R", 3.0),
                CellGeneCount("donor-1", "B_cell", "CD74", 8.0),
            ]
        )
        self.assertEqual(
            result,
            [
                CellGeneCount("donor-1", "B_cell", "CD74", 8.0),
                CellGeneCount("donor-1", "T_cell", "IL7R", 13.0),
            ],
        )

    def test_rejects_blank_identifiers(self) -> None:
        csv_text = "donor_id,cell_type,gene,count\ndonor-1,T_cell,,5\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "counts.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "gene must not be empty"):
                read_long_counts(path)
