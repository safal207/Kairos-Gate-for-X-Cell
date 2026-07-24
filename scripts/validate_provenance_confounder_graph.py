#!/usr/bin/env python3
"""Validate bio provenance/confounder graph records with fail-closed rules."""

from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


REQUIRED = {
    "schema_version",
    "study_id",
    "graph_id",
    "source_freeze",
    "nodes",
    "provenance_edges",
    "confounders",
    "claim_reachability",
    "provenance_completeness",
    "overall_verdict",
    "next_evidence_action",
    "safety_status",
}

VERDICTS = {"ACCEPT", "ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}
LEVELS = {"F0", "F1", "F2", "F3", "F4", "F5"}
EDGE_STATUSES = {"observed", "documented", "executable", "author_confirmed", "inferred", "unknown"}
CONFOUNDER_EDGE_CLASSES = {
    "may_influence",
    "coincides_with",
    "determines_assignment",
    "partially_determines_assignment",
    "unknown_relationship",
}
REVERSIBILITY = {"reversible", "irreversible", "unknown"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append a validation error when a required condition is false."""
    if not condition:
        errors.append(message)


def load(path: Path) -> dict[str, Any]:
    """Load one provenance graph JSON object."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("graph root must be a JSON object")
    return value


def has_cycle(node_ids: set[str], edges: list[dict[str, Any]]) -> bool:
    """Return whether the directed provenance graph contains a cycle."""
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        if source in node_ids and target in node_ids:
            adjacency[source].append(target)
            indegree[target] += 1

    queue = deque(node for node, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in adjacency[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited != len(node_ids)


def validate(record: dict[str, Any]) -> list[str]:
    """Return all contract violations found in one provenance graph."""
    errors: list[str] = []

    missing = sorted(REQUIRED - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(record.get("overall_verdict") in VERDICTS, "invalid overall_verdict", errors)
    require(record.get("provenance_completeness") in {"complete", "partial", "insufficient"}, "invalid provenance_completeness", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_only", "mode must be computational_only", errors)
        require(safety.get("physical_biology_authorized") is False, "physical_biology_authorized must be false", errors)

    nodes = record.get("nodes", [])
    edges = record.get("provenance_edges", [])
    require(isinstance(nodes, list) and len(nodes) > 0, "nodes must be a non-empty array", errors)
    require(isinstance(edges, list), "provenance_edges must be an array", errors)

    node_ids: set[str] = set()
    claim_ids: set[str] = set()
    if isinstance(nodes, list):
        for index, node in enumerate(nodes):
            require(isinstance(node, dict), f"nodes[{index}] must be an object", errors)
            if not isinstance(node, dict):
                continue
            node_id = node.get("node_id")
            require(isinstance(node_id, str) and bool(node_id), f"nodes[{index}].node_id is required", errors)
            if isinstance(node_id, str):
                require(node_id not in node_ids, f"duplicate node_id: {node_id}", errors)
                node_ids.add(node_id)
                if node.get("node_class") == "scientific_claim":
                    claim_ids.add(node_id)
            require(node.get("evidence_level") in LEVELS, f"nodes[{index}] has invalid evidence_level", errors)
            require(node.get("status") in EDGE_STATUSES, f"nodes[{index}] has invalid status", errors)

    edge_ids: set[str] = set()
    incoming: dict[str, int] = defaultdict(int)
    if isinstance(edges, list):
        for index, edge in enumerate(edges):
            require(isinstance(edge, dict), f"provenance_edges[{index}] must be an object", errors)
            if not isinstance(edge, dict):
                continue
            edge_id = edge.get("edge_id")
            require(isinstance(edge_id, str) and bool(edge_id), f"provenance_edges[{index}].edge_id is required", errors)
            if isinstance(edge_id, str):
                require(edge_id not in edge_ids, f"duplicate edge_id: {edge_id}", errors)
                edge_ids.add(edge_id)
            source = edge.get("from")
            target = edge.get("to")
            require(source in node_ids, f"edge {edge_id} references unknown source node {source}", errors)
            require(target in node_ids, f"edge {edge_id} references unknown target node {target}", errors)
            if target in node_ids:
                incoming[str(target)] += 1
            require(edge.get("evidence_level") in LEVELS, f"edge {edge_id} has invalid evidence_level", errors)
            require(edge.get("status") in EDGE_STATUSES, f"edge {edge_id} has invalid status", errors)
            confidence = edge.get("confidence")
            require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, f"edge {edge_id} confidence must be between 0 and 1", errors)
            require(edge.get("transformation_reversibility") in REVERSIBILITY, f"edge {edge_id} has invalid transformation_reversibility", errors)
            require("missing_input_impact" in edge, f"edge {edge_id} must record missing_input_impact", errors)
            impact = edge.get("missing_input_impact")
            require(impact is None or (isinstance(impact, str) and bool(impact.strip())), f"edge {edge_id} missing_input_impact must be null or non-empty text", errors)

    if node_ids and isinstance(edges, list):
        require(not has_cycle(node_ids, [edge for edge in edges if isinstance(edge, dict)]), "provenance graph must be acyclic", errors)

    for claim_id in claim_ids:
        require(incoming.get(claim_id, 0) > 0, f"orphan claim node: {claim_id}", errors)

    confounders = record.get("confounders", [])
    blocking_confounders: set[str] = set()
    if isinstance(confounders, list):
        for index, item in enumerate(confounders):
            require(isinstance(item, dict), f"confounders[{index}] must be an object", errors)
            if not isinstance(item, dict):
                continue
            confounder_id = item.get("confounder_id")
            require(bool(confounder_id), f"confounders[{index}].confounder_id is required", errors)
            require(item.get("edge_class") in CONFOUNDER_EDGE_CLASSES, f"confounder {confounder_id} has invalid edge_class", errors)
            require(item.get("status") in EDGE_STATUSES, f"confounder {confounder_id} has invalid status", errors)
            require(item.get("separability") in {"separable", "partially_separable", "aliased", "unknown"}, f"confounder {confounder_id} has invalid separability", errors)
            require(item.get("risk") in {"low", "medium", "high", "blocking", "unknown"}, f"confounder {confounder_id} has invalid risk", errors)
            if item.get("load_bearing") is True and item.get("risk") in {"high", "blocking", "unknown"}:
                blocking_confounders.add(str(confounder_id))

    reachability = record.get("claim_reachability", [])
    require(isinstance(reachability, list) and len(reachability) > 0, "claim_reachability must be non-empty", errors)
    seen_claims: set[str] = set()
    if isinstance(reachability, list):
        for index, claim in enumerate(reachability):
            require(isinstance(claim, dict), f"claim_reachability[{index}] must be an object", errors)
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("claim_node_id")
            require(claim_id in claim_ids, f"claim reachability references unknown claim {claim_id}", errors)
            if isinstance(claim_id, str):
                seen_claims.add(claim_id)
            require(claim.get("weakest_evidence_level") in LEVELS, f"claim {claim_id} has invalid weakest_evidence_level", errors)
            require(claim.get("verdict") in VERDICTS, f"claim {claim_id} has invalid verdict", errors)
            unknown_count = claim.get("unknown_edge_count")
            inferred_count = claim.get("inferred_edge_count")
            require(isinstance(unknown_count, int) and unknown_count >= 0, f"claim {claim_id} has invalid unknown_edge_count", errors)
            require(isinstance(inferred_count, int) and inferred_count >= 0, f"claim {claim_id} has invalid inferred_edge_count", errors)
            require(isinstance(claim.get("reproducible_from_frozen_inputs"), bool), f"claim {claim_id} must record frozen-input reproducibility", errors)
            high_risk = claim.get("high_risk_confounders")
            require(isinstance(high_risk, list), f"claim {claim_id}.high_risk_confounders must be an array", errors)

            if claim.get("complete_path") is not True:
                require(claim.get("verdict") in {"HOLD", "BLOCK"}, f"incomplete claim path {claim_id} must HOLD or BLOCK", errors)
            if claim.get("independent_validation") != "present" and claim.get("weakest_evidence_level") in {"F0", "F1", "F2"}:
                require(claim.get("verdict") in {"HOLD", "BLOCK"}, f"weak unvalidated claim {claim_id} must HOLD or BLOCK", errors)
            if isinstance(high_risk, list) and blocking_confounders.intersection(map(str, high_risk)):
                require(claim.get("verdict") != "ACCEPT", f"claim {claim_id} cannot ACCEPT with load-bearing high-risk confounders", errors)
            if claim.get("reproducible_from_frozen_inputs") is not True:
                require(claim.get("verdict") != "ACCEPT", f"claim {claim_id} cannot ACCEPT without frozen-input reproducibility", errors)

    missing_claim_rows = sorted(claim_ids - seen_claims)
    require(not missing_claim_rows, f"missing reachability rows for claims: {missing_claim_rows}", errors)

    completeness = record.get("provenance_completeness")
    if completeness != "complete" or blocking_confounders:
        require(record.get("overall_verdict") != "ACCEPT", "overall ACCEPT requires complete provenance and no load-bearing high-risk confounders", errors)

    next_action = record.get("next_evidence_action", {})
    require(isinstance(next_action, dict), "next_evidence_action must be an object", errors)
    if isinstance(next_action, dict):
        require(bool(next_action.get("action")), "next_evidence_action.action is required", errors)
        require(next_action.get("expected_uncertainty_reduction") in {"low", "medium", "high"}, "invalid expected_uncertainty_reduction", errors)

    return errors


def main(argv: list[str]) -> int:
    """Validate all supplied graph records and return a process exit code."""
    if len(argv) < 2:
        print("usage: validate_provenance_confounder_graph.py GRAPH.json [GRAPH.json ...]", file=sys.stderr)
        return 2

    failed = False
    for raw_path in argv[1:]:
        path = Path(raw_path)
        try:
            errors = validate(load(path))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors = [str(exc)]

        if errors:
            failed = True
            print(f"BLOCK {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"ACCEPT {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
