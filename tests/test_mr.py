import unittest

from peds_omics_workflows.mr import Instrument, ivw_summary


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


if __name__ == "__main__":
    unittest.main()
