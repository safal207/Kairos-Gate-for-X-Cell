from __future__ import annotations

import copy
import json
import unittest
from importlib.resources import files
from pathlib import Path

from kairos_gate.handoff import validate_handoff_record
from kairos_gate.validator import ValidationError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "tip-kairos-handoff.json"
NEGATIVE_FIXTURES = ROOT / "testdata" / "tip-kairos-negative-fixtures.json"


class TipKairosHandoffTests(unittest.TestCase):
    """Regression tests for the narrow research-only interoperability profile."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load canonical and negative fixture descriptors."""
        cls.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        cls.fixtures = json.loads(NEGATIVE_FIXTURES.read_text(encoding="utf-8"))

    def test_canonical_handoff_is_valid(self) -> None:
        validate_handoff_record(copy.deepcopy(self.base))

    def test_negative_fixtures_fail_closed(self) -> None:
        self.assertGreaterEqual(len(self.fixtures["cases"]), 3)
        for case in self.fixtures["cases"]:
            with self.subTest(case=case["id"]):
                record = copy.deepcopy(self.base)
                target = record
                for part in case["path"][:-1]:
                    target = target[part]
                del target[case["path"][-1]]
                with self.assertRaisesRegex(ValidationError, case["expected_error"]):
                    validate_handoff_record(record)

    def test_handoff_cannot_authorize_execution(self) -> None:
        record = copy.deepcopy(self.base)
        record["authority"]["execution_authorized"] = True
        with self.assertRaisesRegex(ValidationError, "False was expected"):
            validate_handoff_record(record)

    def test_packaged_handoff_schema_matches_public_mirror(self) -> None:
        packaged = files("kairos_gate.schemas").joinpath(
            "tip-kairos-handoff.schema.json"
        ).read_text(encoding="utf-8")
        public = (ROOT / "schemas" / "tip-kairos-handoff.schema.json").read_text(
            encoding="utf-8"
        )
        self.assertEqual(json.loads(packaged), json.loads(public))


if __name__ == "__main__":
    unittest.main()
