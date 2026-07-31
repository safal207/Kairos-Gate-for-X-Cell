"""Tests for the exact RINSE → Kairos revalidation bridge."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from kairos_gate.rinse_reinterpretation_bridge import (
    EXPECTED_OUTPUT,
    EXPECTED_WORKFLOW,
    MISSING_CAUSAL_INTERMEDIATES,
    RinseReinterpretationError,
    build_rinse_revalidation_graph,
    main,
    revalidate_rinse_candidate,
    validate_pinned_rinse_manifest,
    validate_rinse_loop,
)
from kairos_gate.transition_graph import analyze_transition_network


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifests/rinse-trace-loop-pr23.v0.1.json"
LOOP_PATH = ROOT / "examples/rinse-trace-loop.v0.1.json"


class RinseReinterpretationBridgeTests(unittest.TestCase):
    """Exercise exact pins, dual transition semantics, and tamper resistance."""

    def setUp(self) -> None:
        """Load fresh objects for each test."""

        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.loop = json.loads(LOOP_PATH.read_text(encoding="utf-8"))

    def test_committed_loop_file_matches_workflow_sha256(self) -> None:
        """The checked-in loop must be byte-identical to the successful artifact file."""

        actual = "sha256:" + hashlib.sha256(LOOP_PATH.read_bytes()).hexdigest()
        self.assertEqual(actual, EXPECTED_WORKFLOW["loop_file_sha256"])

    def test_exact_manifest_and_loop_validate(self) -> None:
        """All exact repository, blob, artifact, and semantic pins must pass."""

        validate_pinned_rinse_manifest(self.manifest)
        validate_rinse_loop(self.loop, self.manifest)

    def test_revalidation_is_deterministic_and_input_immutable(self) -> None:
        """Repeated revalidation must not mutate either source object."""

        loop_snapshot = copy.deepcopy(self.loop)
        manifest_snapshot = copy.deepcopy(self.manifest)
        first = revalidate_rinse_candidate(self.loop, self.manifest)
        second = revalidate_rinse_candidate(self.loop, self.manifest)
        self.assertEqual(first, second)
        self.assertEqual(self.loop, loop_snapshot)
        self.assertEqual(self.manifest, manifest_snapshot)
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_kairos_accepts_reinterpretation_but_holds_causality(self) -> None:
        """Meaning revision and scientific causal proof must remain separate paths."""

        result = revalidate_rinse_candidate(self.loop, self.manifest)
        self.assertEqual(result["kairos_analysis"]["verdict"], "ACCEPT_WITH_LIMITS")
        self.assertEqual(
            result["decision"]["reinterpretation_transition"], "ACCEPT_WITH_LIMITS"
        )
        self.assertEqual(
            result["decision"]["adaptive_causality"], "HOLD_MISSING_EVIDENCE"
        )
        self.assertEqual(result["decision"]["execution"], "HOLD")
        self.assertEqual(result["decision"]["merge"], "NOT_AUTHORIZED")
        self.assertEqual(
            result["decision"]["active_interpretation"],
            EXPECTED_OUTPUT["active_reflection_id"],
        )

    def test_exact_four_causal_gaps_are_preserved(self) -> None:
        """The association-to-causality path must retain all missing intermediates."""

        result = revalidate_rinse_candidate(self.loop, self.manifest)
        self.assertEqual(
            result["kairos_analysis"]["causal_gaps"],
            [
                {
                    "transition_id": "association_to_adaptive_causality",
                    "missing_intermediates": sorted(MISSING_CAUSAL_INTERMEDIATES),
                    "status": "CAUSAL_GAP",
                }
            ],
        )
        self.assertEqual(result["kairos_analysis"]["claim_firewall"], [])
        self.assertEqual(result["kairos_analysis"]["temporal_conflicts"], [])

    def test_all_authority_remains_false(self) -> None:
        """No reflection or revalidation result may grant truth or action authority."""

        result = revalidate_rinse_candidate(self.loop, self.manifest)
        for key, value in result["authority"].items():
            if key.endswith("authorized"):
                self.assertIs(value, False)
        self.assertIs(result["candidate"]["execution_allowed"], False)
        self.assertEqual(
            result["kairos_analysis"]["authority"]["classification"],
            "RESEARCH_ONLY",
        )
        self.assertIs(
            result["kairos_analysis"]["authority"]["causal_authorization"], False
        )

    def test_causal_overclaim_would_be_blocked_by_transition_engine(self) -> None:
        """Promoting the missing-evidence transition to causal must trip the firewall."""

        graph = build_rinse_revalidation_graph(self.loop, self.manifest)
        graph["transitions"][1]["claim"]["level"] = "causal"
        analysis = analyze_transition_network(graph)
        self.assertEqual(analysis["verdict"], "BLOCK")
        self.assertEqual(
            analysis["claim_firewall"][0]["transition_id"],
            "association_to_adaptive_causality",
        )

    def test_manifest_tampering_is_rejected(self) -> None:
        """A changed RINSE source, blob, artifact, or authority pin must fail closed."""

        mutations = {
            "commit": lambda value: value.__setitem__("commit", "0" * 40),
            "blob": lambda value: value["files"][0].__setitem__(
                "git_blob_sha", "0" * 40
            ),
            "artifact": lambda value: value["workflow"].__setitem__(
                "artifact_digest", "sha256:" + "0" * 64
            ),
            "output": lambda value: value["expected_output"].__setitem__(
                "loop_digest", "sha256:" + "0" * 64
            ),
            "authority": lambda value: value["authority"].__setitem__(
                "execution_authorized", True
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                tampered = copy.deepcopy(self.manifest)
                mutate(tampered)
                with self.assertRaises(RinseReinterpretationError):
                    validate_pinned_rinse_manifest(tampered)

    def test_loop_tampering_is_rejected(self) -> None:
        """A changed digest, node, edge, handoff, evidence, or authority must fail."""

        mutations = {
            "loop digest": lambda value: value.__setitem__(
                "digest", "sha256:" + "0" * 64
            ),
            "active node": lambda value: value["reflection_graph"]["nodes"][1].__setitem__(
                "effective_status", "SUPPORTED"
            ),
            "edge": lambda value: value["reflection_graph"]["edges"].pop(),
            "handoff": lambda value: value["kairos_handoff"].__setitem__(
                "execution_allowed", True
            ),
            "evidence": lambda value: value["upstream_evidence_digests"].__setitem__(
                "final_event", "sha256:" + "0" * 64
            ),
            "authority": lambda value: value["authority"].__setitem__(
                "scientific_truth_authorized", True
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                tampered = copy.deepcopy(self.loop)
                mutate(tampered)
                with self.assertRaises(RinseReinterpretationError):
                    validate_rinse_loop(tampered, self.manifest)

    def test_cli_tampered_file_returns_two_without_traceback(self) -> None:
        """Byte-level changes must be blocked before semantic revalidation."""

        tampered = copy.deepcopy(self.loop)
        tampered["kairos_handoff"]["execution_allowed"] = True
        with tempfile.TemporaryDirectory() as directory:
            loop_path = Path(directory) / "loop.json"
            loop_path.write_text(json.dumps(tampered), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "--manifest",
                        str(MANIFEST_PATH),
                        "--loop",
                        str(loop_path),
                    ]
                )
        self.assertEqual(exit_code, 2)
        self.assertTrue(output.getvalue().startswith("BLOCK: "))
        self.assertNotIn("Traceback", output.getvalue())


if __name__ == "__main__":
    unittest.main()
