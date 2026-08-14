import unittest

from peds_omics_workflows.scrna import qc_summary


class QcSummaryTests(unittest.TestCase):
    def test_applies_all_thresholds(self) -> None:
        cells = [
            {"cell_id": "a", "cell_type": "T_cell", "total_counts": 600.0, "n_genes": 220.0, "mito_fraction": 0.1},
            {"cell_id": "b", "cell_type": "B_cell", "total_counts": 600.0, "n_genes": 220.0, "mito_fraction": 0.3},
        ]
        result = qc_summary(cells)
        self.assertEqual(result["passing_cell_count"], 1)
        self.assertEqual(result["passing_cells_by_annotation"], {"T_cell": 1})


if __name__ == "__main__":
    unittest.main()
