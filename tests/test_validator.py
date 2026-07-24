from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from kairos_gate.validator import ValidationError, recommend_decision, validate_path, validate_record

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "phase-conditioned-transition.json"


class KairosValidatorTests(unittest.TestCase):
    """Regression tests for schema, safety precedence, and decision consistency."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load the canonical synthetic record once for isolated mutations."""
        cls.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_canonical_example_is_candidate_window(self) -> None:
        record = copy.deepcopy(self.base)
        self.assertEqual(recommend_decision(record), "CANDIDATE_WINDOW")
        validate_record(record)

    def test_missing_phase_becomes_insufficient_evidence(self) -> None:
        record = copy.deepcopy(self.base)
        for phase in record["phase_context"].values():
            phase.clear()
            phase["status"] = "unobserved"
        record["decision"] = "INSUFFICIENT_EVIDENCE"
        self.assertEqual(recommend_decision(record), "INSUFFICIENT_EVIDENCE")
        validate_record(record)

    def test_future_phase_evidence_is_insufficient(self) -> None:
        record = copy.deepcopy(self.base)
        record["phase_context"]["cell_cycle"]["observed_at"] = "2026-07-21T11:00:00Z"
        record["decision"] = "INSUFFICIENT_EVIDENCE"
        self.assertEqual(recommend_decision(record), "INSUFFICIENT_EVIDENCE")
        validate_record(record)

    def test_high_toxicity_is_excluded(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["toxicity_risk"] = 0.70
        record["decision"] = "EXCLUDE"
        self.assertEqual(recommend_decision(record), "EXCLUDE")
        validate_record(record)

    def test_low_identity_is_excluded(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["identity_preservation"] = 0.50
        record["decision"] = "EXCLUDE"
        self.assertEqual(recommend_decision(record), "EXCLUDE")
        validate_record(record)

    def test_low_reversibility_is_excluded(self) -> None:
        record = copy.deepcopy(self.base)
        record["gate_assessment"]["reversibility"] = 0.20
        record["decision"] = "EXCLUDE"
        self.assertEqual(recommend_decision(record), "EXCLUDE")
        validate_record(record)

    def test_hard_exclusion_precedes_missing_phase(self) -> None:
        record = copy.deepcopy(self.base)
        for phase in record["phase_context"].values():
            phase.clear()
            phase["status"] = "unobserved"
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
        with self.assertRaisesRegex(ValidationError, "schema violation"):
            validate_record(record)

    def test_validate_record_rejects_nan_outside_gate_assessment(self) -> None:
        record = copy.deepcopy(self.base)
        record["current_state"]["quality"] = float("nan")
        with self.assertRaisesRegex(ValidationError, "current_state.quality must be finite"):
            validate_record(record)

    def test_validate_record_rejects_infinity(self) -> None:
        record = copy.deepcopy(self.base)
        record["forecast"]["horizon_hours"] = float("inf")
        with self.assertRaisesRegex(ValidationError, "forecast.horizon_hours must be finite"):
            validate_record(record)

    def test_extra_root_property_is_rejected(self) -> None:
        record = copy.deepcopy(self.base)
        record["approval"] = True
        with self.assertRaisesRegex(ValidationError, "Additional properties"):
            validate_record(record)

    def test_invalid_record_timestamp_is_rejected(self) -> None:
        record = copy.deepcopy(self.base)
        record["observed_at"] = "not-a-timestamp"
        with self.assertRaisesRegex(ValidationError, "not a 'date-time'"):
            validate_record(record)

    def test_missing_provenance_member_is_rejected(self) -> None:
        record = copy.deepcopy(self.base)
        del record["provenance"]["data_digest"]
        with self.assertRaisesRegex(ValidationError, "required property"):
            validate_record(record)

    def test_unsupported_phase_key_is_rejected(self) -> None:
        record = copy.deepcopy(self.base)
        record["phase_context"]["inner_light"] = record["phase_context"].pop("cell_cycle")
        with self.assertRaisesRegex(ValidationError, "Additional properties"):
            validate_record(record)

    def test_qualifying_phase_requires_method_and_timestamp(self) -> None:
        record = copy.deepcopy(self.base)
        del record["phase_context"]["cell_cycle"]["method"]
        with self.assertRaisesRegex(ValidationError, "not valid under any"):
            validate_record(record)

    def test_packaged_schema_matches_repository_schema(self) -> None:
        from importlib.resources import files

        packaged = files("kairos_gate.schemas").joinpath(
            "kairos-transition.schema.json"
        ).read_text(encoding="utf-8")
        repository = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "kairos-transition.schema.json"
        ).read_text(encoding="utf-8")
        self.assertEqual(json.loads(packaged), json.loads(repository))

    def test_validate_path_runs_full_schema_validation(self) -> None:
        record = copy.deepcopy(self.base)
        record["forecast"] = {"horizon_hours": 24}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "schema violation"):
                validate_path(path)

    def test_validate_path_rejects_nan(self) -> None:
        record = copy.deepcopy(self.base)
        record["current_state"]["quality"] = float("nan")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(record, allow_nan=True), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "non-finite JSON constant"):
                validate_path(path)


if __name__ == "__main__":
    unittest.main()
