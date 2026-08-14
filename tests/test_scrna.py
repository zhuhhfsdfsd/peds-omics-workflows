import tempfile
import unittest
from pathlib import Path

from peds_omics_workflows.scrna import qc_summary, read_cell_metadata


class QcSummaryTests(unittest.TestCase):
    def test_applies_all_thresholds(self) -> None:
        cells = [
            {"cell_id": "a", "cell_type": "T_cell", "total_counts": 600.0, "n_genes": 220.0, "mito_fraction": 0.1},
            {"cell_id": "b", "cell_type": "B_cell", "total_counts": 600.0, "n_genes": 220.0, "mito_fraction": 0.3},
        ]
        result = qc_summary(cells)
        self.assertEqual(result["passing_cell_count"], 1)
        self.assertEqual(result["passing_cells_by_annotation"], {"T_cell": 1})

    def test_rejects_duplicate_cell_identifiers(self) -> None:
        csv_text = (
            "cell_id,total_counts,n_genes,mito_fraction,cell_type\n"
            "cell-1,600,220,0.10,T_cell\n"
            "cell-1,700,250,0.08,\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cells.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate cell_id 'cell-1'"):
                read_cell_metadata(path)

    def test_blank_cell_type_is_normalised(self) -> None:
        csv_text = (
            "cell_id,total_counts,n_genes,mito_fraction,cell_type\n"
            "cell-1,600,220,0.10,   \n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cells.csv"
            path.write_text(csv_text, encoding="utf-8")
            rows = read_cell_metadata(path)
        self.assertEqual(rows[0]["cell_type"], "unassigned")


if __name__ == "__main__":
    unittest.main()
