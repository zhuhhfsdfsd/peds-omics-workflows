import json
import tempfile
import unittest
from pathlib import Path

from peds_omics_workflows.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliManifestTests(unittest.TestCase):
    def test_writes_a_non_identifying_mr_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary.json"
            manifest = Path(directory) / "manifest.json"
            main(
                [
                    "mr",
                    "--input",
                    str(PROJECT_ROOT / "data/example/mr_instruments.csv"),
                    "--output",
                    str(output),
                    "--manifest",
                    str(manifest),
                ]
            )
            result = json.loads(manifest.read_text(encoding="utf-8"))

        self.assertEqual(result["manifest_schema_version"], "1.0")
        self.assertEqual(result["workflow"], "mr")
        self.assertEqual(result["input"]["filename"], "mr_instruments.csv")
        self.assertEqual(len(result["input"]["sha256"]), 64)
        self.assertEqual(result["parameters"], {"method": "ivw_delta_method"})
        self.assertNotIn("path", result["input"])
