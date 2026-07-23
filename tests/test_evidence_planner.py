from __future__ import annotations

import contextlib
import hashlib
import io
import json
import unittest
from pathlib import Path

from kairos_gate.__main__ import main
from kairos_gate.dataset_readiness import audit_dataset_paths
from kairos_gate.evidence_planner import (
    EvidencePlannerError,
    build_evidence_plan,
    plan_evidence_path,
    validate_evidence_plan_record,
)

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_RESULT = ROOT / "examples" / "live-seq-gse141064.readiness-result.v0.1.json"
PLAN_EXAMPLE = (
    ROOT / "examples" / "live-seq-gse141064.evidence-request-plan.v0.1.json"
)
PACKAGED_SCHEMA = (
    ROOT / "kairos_gate" / "schemas" / "evidence-request-plan.schema.json"
)
PUBLIC_SCHEMA = ROOT / "schemas" / "evidence-request-plan.schema.json"
SYN_MANIFEST = ROOT / "tests" / "fixtures" / "dataset-readiness-synthetic.manifest.json"
SYN_META = ROOT / "tests" / "fixtures" / "dataset-readiness-synthetic-meta.csv"
SYN_COUNTS = ROOT / "tests" / "fixtures" / "dataset-readiness-synthetic-counts.csv"


class EvidencePlannerTests(unittest.TestCase):
    def test_packaged_schema_matches_public_mirror(self) -> None:
        self.assertEqual(PACKAGED_SCHEMA.read_bytes(), PUBLIC_SCHEMA.read_bytes())

    def test_committed_live_seq_plan_matches_deterministic_output(self) -> None:
        generated = plan_evidence_path(BLOCKED_RESULT)
        committed = json.loads(PLAN_EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(generated, committed)
        validate_evidence_plan_record(committed)

        expected_digest = "sha256:" + hashlib.sha256(
            BLOCKED_RESULT.read_bytes()
        ).hexdigest()
        self.assertEqual(committed["source_result"]["sha256"], expected_digest)
        self.assertEqual(committed["plan_status"], "OPEN_EVIDENCE_REQUEST")
        self.assertEqual(len(committed["required_evidence"]), 6)
        self.assertIn(
            "random cell split presented as generalization evidence",
            committed["forbidden_substitutions"],
        )

    def test_planner_never_changes_verdict_or_authorizes_actions(self) -> None:
        plan = plan_evidence_path(BLOCKED_RESULT)
        authority = plan["authority"]
        self.assertFalse(authority["readiness_verdict_changed"])
        self.assertFalse(authority["model_fitting_authorized"])
        self.assertFalse(authority["author_contact_authorized"])
        self.assertFalse(authority["experiment_authorization"])
        self.assertFalse(authority["clinical_authorization"])
        self.assertFalse(authority["merge_authorization"])

    def test_ready_result_has_no_blocking_evidence_request(self) -> None:
        ready = audit_dataset_paths(SYN_MANIFEST, SYN_META, SYN_COUNTS)
        plan = build_evidence_plan(
            ready,
            source_result_sha256="sha256:" + "0" * 64,
        )
        self.assertEqual(plan["plan_status"], "NO_BLOCKING_EVIDENCE_REQUEST")
        self.assertEqual(plan["blocker"]["code"], "NONE")
        self.assertEqual(plan["required_evidence"], [])
        self.assertFalse(plan["authority"]["model_fitting_authorized"])

    def test_unsupported_status_fails_closed(self) -> None:
        result = json.loads(BLOCKED_RESULT.read_text(encoding="utf-8"))
        result["status"] = "BLOCKED_LICENSE_UNCLEAR"
        with self.assertRaises(EvidencePlannerError):
            build_evidence_plan(
                result,
                source_result_sha256="sha256:" + "1" * 64,
            )

    def test_cli_emits_machine_readable_plan(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(
                [
                    "plan-next-evidence",
                    "--result",
                    str(BLOCKED_RESULT),
                ]
            )

        self.assertEqual(code, 0)
        emitted = json.loads(stream.getvalue())
        self.assertEqual(emitted["schema"], "kairos.evidence-request-plan.v0.1")
        self.assertEqual(
            emitted["blocker"]["code"],
            "BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED",
        )


if __name__ == "__main__":
    unittest.main()
