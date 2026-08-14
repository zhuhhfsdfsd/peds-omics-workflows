import tempfile
import unittest
from pathlib import Path

from peds_omics_workflows.mr import Instrument, ivw_summary, read_instruments


class IvwSummaryTests(unittest.TestCase):
    def test_returns_a_finite_estimate(self) -> None:
        instruments = [
            Instrument("rs1", 0.10, 0.02, 0.04, 0.02),
            Instrument("rs2", 0.12, 0.02, 0.05, 0.02),
        ]
        result = ivw_summary(instruments)
        self.assertEqual(result["instrument_count"], 2)
        self.assertGreater(float(result["standard_error"]), 0)
        self.assertGreaterEqual(float(result["p_value"]), 0)
        self.assertLessEqual(float(result["p_value"]), 1)

    def test_rejects_duplicate_variant_identifiers(self) -> None:
        csv_text = (
            "variant,exposure_beta,exposure_se,outcome_beta,outcome_se,aligned\n"
            "rs1,0.10,0.02,0.04,0.02,true\n"
            "rs1,0.12,0.02,0.05,0.02,true\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "instruments.csv"
            path.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate variant 'rs1'"):
                read_instruments(path)


if __name__ == "__main__":
    unittest.main()
