from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "schemas"
PACKAGED = ROOT / "kairos_gate" / "schemas"
EXAMPLE = ROOT / "examples" / "trace-transition-network.v0.1.json"
SCHEMAS = (
    "kairos-state-node.schema.json",
    "kairos-evidence-object.schema.json",
    "kairos-transition-edge.schema.json",
)


class TransitionGraphSchemaTests(unittest.TestCase):
    def test_public_and_packaged_schemas_are_semantically_identical(self) -> None:
        for name in SCHEMAS:
            public = json.loads((PUBLIC / name).read_text(encoding="utf-8"))
            packaged = json.loads((PACKAGED / name).read_text(encoding="utf-8"))
            self.assertEqual(public, packaged, name)

    def test_schemas_are_valid_draft_2020_12(self) -> None:
        for name in SCHEMAS:
            schema = json.loads((PUBLIC / name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)

    def test_trace_objects_validate_against_component_schemas(self) -> None:
        graph = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        state_schema = json.loads(
            (PUBLIC / "kairos-state-node.schema.json").read_text(encoding="utf-8")
        )
        evidence_schema = json.loads(
            (PUBLIC / "kairos-evidence-object.schema.json").read_text(encoding="utf-8")
        )
        transition_schema = json.loads(
            (PUBLIC / "kairos-transition-edge.schema.json").read_text(encoding="utf-8")
        )
        checker = FormatChecker()
        state_validator = Draft202012Validator(state_schema, format_checker=checker)
        evidence_validator = Draft202012Validator(evidence_schema, format_checker=checker)
        transition_validator = Draft202012Validator(
            transition_schema, format_checker=checker
        )
        for state in graph["states"]:
            self.assertEqual(list(state_validator.iter_errors(state)), [])
        for evidence in graph["evidence"]:
            self.assertEqual(list(evidence_validator.iter_errors(evidence)), [])
        for transition in graph["transitions"]:
            self.assertEqual(list(transition_validator.iter_errors(transition)), [])


if __name__ == "__main__":
    unittest.main()
