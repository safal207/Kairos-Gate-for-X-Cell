from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "testdata" / "phase-window-tiny.json"
SCRIPT = ROOT / "scripts" / "run_phase_benchmark.py"


class SyntheticPhaseBenchmarkTests(unittest.TestCase):
    """Verify the preregistered synthetic benchmark and negative control."""

    def test_phase_conditioning_beats_baseline_and_shuffle_does_not(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(DATASET)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
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


if __name__ == "__main__":
    unittest.main()
