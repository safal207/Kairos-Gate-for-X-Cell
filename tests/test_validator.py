from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from kairos_gate.validator import ValidationError, recommend_decision, validate_record

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "phase-conditioned-transition.json"


class KairosValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_canonical_example_is_candidate_window(self) -> None:
        record = copy.deepcopy(self.base)
        self.assertEqual(recommend_decision(record), "CANDIDATE_WINDOW")
        validate_record(record)

    def test_missing_phase_becomes_insufficient_evidence(self) -> None:
        record = copy.deepcopy(self.base)
        for phase in record["phase_context"].values():
            phase["status"] = "unobserved"
            phase.pop("confidence", None)
        record["decision"] = "INSUFFICIENT_EVIDENCE"
        self.assertEqual(recommend_decision(record), "INSUFFICIENT_EVIDENCE")
        validate_record(record)

    def test_high_toxicity_is_excluded(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["toxicity_risk"] = 0.70
        record["decision"] = "EXCLUDE"
        self.assertEqual(recommend_decision(record), "EXCLUDE")
        validate_record(record)

    def test_low_timing_confidence_waits(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["timing_confidence"] = 0.50
        record["decision"] = "WAIT"
        self.assertEqual(recommend_decision(record), "WAIT")
        validate_record(record)

    def test_claimed_decision_must_match_deterministic_result(self) -> None:
        record = copy.deepcopy(self.base)
        record["decision"] = "EXCLUDE"
        with self.assertRaisesRegex(ValidationError, "decision mismatch"):
            validate_record(record)

    def test_scores_are_bounded(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["effectiveness"] = 1.5
        with self.assertRaisesRegex(ValidationError, "between 0 and 1"):
            validate_record(record)


if __name__ == "__main__":
    unittest.main()
