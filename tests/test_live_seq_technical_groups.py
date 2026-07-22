from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_live_seq_technical_groups.py"
METADATA = ROOT / "tests" / "fixtures" / "live-seq-technical-meta-tiny.csv"


class LiveSeqTechnicalGroupingTests(unittest.TestCase):
    """Keep technical metadata distinct from verified replicate semantics."""

    def test_summary_reports_groups_without_unlocking_confirmation(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(METADATA)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)

        self.assertEqual(result["cohort"]["selected_cells"], 4)
        self.assertFalse(result["cohort"]["selection_uses_response_label"])
        self.assertEqual(
            result["technical_group_candidates"]["plate_like_prefix"],
            {"plate1": 2, "plate2": 2},
        )
        self.assertEqual(
            result["technical_group_candidates"]["sequencing_run"],
            {"NXT0590": 4},
        )
        decision = result["decision"]
        self.assertEqual(
            decision["classification"], "EXPLORATORY_ONLY_TECHNICAL_GROUPING"
        )
        self.assertEqual(
            decision["status"], "BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED"
        )
        self.assertFalse(decision["replicate_semantics_verified"])
        self.assertFalse(decision["confirmatory_preregistration_unlocked"])
        self.assertEqual(result["authority"]["classification"], "RESEARCH_ONLY")


if __name__ == "__main__":
    unittest.main()
