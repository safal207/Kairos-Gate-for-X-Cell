from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "testdata" / "phase-window-tiny.json"
SCRIPT = ROOT / "scripts" / "run_phase_benchmark.py"


class SyntheticPhaseBenchmarkTests(unittest.TestCase):
    """Verify the preregistered synthetic benchmark and negative controls."""

    def _run(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_phase_conditioning_beats_baseline_and_shuffle_does_not(self) -> None:
        completed = self._run(DATASET)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        metrics = result["metrics"]

        self.assertEqual(result["interpretation"], "SUPPORTED_SYNTHETIC_ONLY")
        self.assertEqual(result["authority"], "RESEARCH_ONLY")
        self.assertFalse(result["experiment_authorization"])
        self.assertAlmostEqual(metrics["baseline_mse"], 0.05625)
        self.assertAlmostEqual(metrics["phase_conditioned_mse"], 0.0)
        self.assertAlmostEqual(metrics["phase_ablation_mse"], metrics["baseline_mse"])
        self.assertAlmostEqual(metrics["phase_shuffle_mse"], 0.225)
        self.assertGreater(metrics["phase_shuffle_mse"], metrics["baseline_mse"])

    def test_missing_dataset_id_fails_closed(self) -> None:
        dataset = json.loads(DATASET.read_text(encoding="utf-8"))
        del dataset["dataset_id"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-dataset-id.json"
            path.write_text(json.dumps(dataset), encoding="utf-8")
            completed = self._run(path)

        self.assertEqual(completed.returncode, 1)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("dataset_id must be a non-empty string", result["error"])
        self.assertNotIn("Traceback", completed.stderr)

    def test_missing_version_fails_closed(self) -> None:
        dataset = json.loads(DATASET.read_text(encoding="utf-8"))
        del dataset["version"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-version.json"
            path.write_text(json.dumps(dataset), encoding="utf-8")
            completed = self._run(path)

        self.assertEqual(completed.returncode, 1)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("version must be a non-empty string", result["error"])
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
