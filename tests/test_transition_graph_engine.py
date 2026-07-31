from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from kairos_gate.transition_graph import (
    TransitionGraphError,
    analyze_transition_network,
    causal_gaps,
    claim_firewall,
    rank_transitions,
    temporal_conflicts,
    validate_graph,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "trace-transition-network.v0.1.json"


class TransitionGraphEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_trace_example_accepts_with_explicit_limits(self) -> None:
        result = analyze_transition_network(self.graph)
        self.assertEqual(result["verdict"], "ACCEPT_WITH_LIMITS")
        self.assertEqual(result["temporal_conflicts"], [])
        self.assertEqual(result["claim_firewall"], [])
        self.assertFalse(result["authority"]["experiment_authorization"])
        self.assertFalse(result["authority"]["truth_probability"])

    def test_trace_example_preserves_causal_gaps(self) -> None:
        gaps = {item["transition_id"]: item for item in causal_gaps(self.graph)}
        self.assertIn("modern_to_functional_signal", gaps)
        self.assertEqual(
            gaps["modern_to_functional_signal"]["missing_intermediates"],
            ["cellular_effect", "expression_change", "fitness_advantage", "organism_phenotype"],
        )
        self.assertIn("ghost_to_sapiens", gaps)

    def test_missing_evidence_reference_fails_closed(self) -> None:
        broken = copy.deepcopy(self.graph)
        broken["transitions"][0]["evidence_refs"].append("invented_source")
        with self.assertRaisesRegex(TransitionGraphError, "missing evidence"):
            validate_graph(broken)

    def test_temporally_impossible_transition_is_reported_and_blocks(self) -> None:
        broken = copy.deepcopy(self.graph)
        broken["transitions"][0]["time_window"] = {
            "start": -10000,
            "end": -5000,
            "unit": "years_relative_to_present",
        }
        conflicts = temporal_conflicts(broken)
        self.assertEqual(conflicts[0]["transition_id"], "superarchaic_to_denisovan")
        self.assertIn("NO_SOURCE_STATE_OVERLAP", conflicts[0]["reasons"])
        self.assertEqual(analyze_transition_network(broken)["verdict"], "BLOCK")

    def test_adaptive_causality_claim_is_blocked_without_causal_design(self) -> None:
        broken = copy.deepcopy(self.graph)
        functional = next(
            item
            for item in broken["transitions"]
            if item["id"] == "modern_to_functional_signal"
        )
        functional["claim"] = {
            "text": "Archaic segments caused an adaptive fitness advantage",
            "level": "causal",
        }
        violations = claim_firewall(broken)
        self.assertEqual(violations[0]["transition_id"], "modern_to_functional_signal")
        self.assertEqual(violations[0]["allowed_level"], "association")
        self.assertEqual(analyze_transition_network(broken)["verdict"], "BLOCK")

    def test_authorization_claim_is_always_blocked(self) -> None:
        broken = copy.deepcopy(self.graph)
        broken["transitions"][0]["claim"]["level"] = "authorization"
        violations = claim_firewall(broken)
        self.assertEqual(violations[0]["status"], "OVERCLAIM_BLOCKED")

    def test_independent_replication_ranks_above_computational_inference(self) -> None:
        graph = copy.deepcopy(self.graph)
        first = graph["transitions"][0]
        second = graph["transitions"][1]
        graph["evidence"][0]["status"] = "independently_replicated"
        graph["evidence"][0]["independent"] = True
        first["status"] = "independently_replicated"
        first["confidence"] = 0.85
        second["confidence"] = 0.85
        ranked = rank_transitions(graph)
        positions = {item.transition_id: index for index, item in enumerate(ranked)}
        self.assertLess(
            positions["superarchaic_to_denisovan"],
            positions["ghost_to_sapiens"],
        )

    def test_duplicate_ids_fail_closed(self) -> None:
        broken = copy.deepcopy(self.graph)
        duplicate = copy.deepcopy(broken["states"][0])
        broken["states"].append(duplicate)
        with self.assertRaisesRegex(TransitionGraphError, "duplicate states id"):
            validate_graph(broken)

    def test_self_transition_fails_closed(self) -> None:
        broken = copy.deepcopy(self.graph)
        broken["transitions"][0]["to_state"] = broken["transitions"][0]["from_state"]
        with self.assertRaisesRegex(TransitionGraphError, "self-transition"):
            validate_graph(broken)


if __name__ == "__main__":
    unittest.main()
