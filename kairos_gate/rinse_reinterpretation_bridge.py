"""Revalidate an exact RINSE reinterpretation candidate through Kairos Gate.

The bridge accepts only the pinned TRACE loop emitted by RINSE PR #23. It may
accept a transition between interpretations while keeping the separate path from
association to adaptive causality explicitly blocked by missing intermediates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from .transition_graph import TransitionGraphError, analyze_transition_network


MANIFEST_SCHEMA = "kairos.pinned-rinse-loop.v0.1"
LOOP_SCHEMA = "rinse.kairos-reflection-loop.v0.1"
OUTPUT_SCHEMA = "kairos.rinse-revalidation-receipt.v0.1"
CASE_ID = "trace-archaic-introgression-2026"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256_REF = re.compile(r"^sha256:[0-9a-f]{64}$")

EXPECTED_REPOSITORY = "safal207/rinse"
EXPECTED_PULL_REQUEST = 23
EXPECTED_COMMIT = "1ecdf2d704f120d15b8ee458573043bbef4e717b"
EXPECTED_FILES = {
    "adapter": (
        "rinse/adapters/kairos_liminal_receipt.py",
        "8a139e4dc076df3fa4f868ed41aa25b07fd19259",
    ),
    "reflection_graph": (
        "rinse/reflection_graph.py",
        "2c3ce00e83e7a9b849fc2780d5c26ac74d6ff312",
    ),
    "source_receipt": (
        "examples/rinse/trace_kairos_liminal_receipt.v0.1.json",
        "40226ea7279eb17954560cb53dbe9f3b17581ad2",
    ),
    "package": (
        "pyproject.toml",
        "fab0f8543d44b33c53e4fd90efe0533ffa48440c",
    ),
}
EXPECTED_WORKFLOW = {
    "run_id": 30627776819,
    "artifact_id": 8792066011,
    "artifact_digest": "sha256:a63027f98c79bbd8ddefc56eb0408a3fd69c3ecfa5a5ae692a7352d293c29b03",
    "loop_file_sha256": "sha256:b67b1f5977132e925b6c3404a362df04e9206a7fffcb3c40ddd5e297bcf60cc9",
    "upstream_verification_sha256": "sha256:bfa2ffee1046f3ed39226a5e723e1683db46ceb5993807228cb013a279270b37",
}
EXPECTED_OUTPUT = {
    "loop_digest": "sha256:6b0b8050a62275eafd8f2260cf6099fd1b65567101894b955ee5928d55eca6ad",
    "source_receipt_digest": "sha256:d3650aa3061514c41433cff930eed02fa9350d0c888114d23c414656d0ed0fd6",
    "reflection_graph_digest": "sha256:6cde4e6e08e7fb802b7ad3361af899f885512642f634fd0151f3c40d5ff7b776",
    "prior_reflection_id": "rinse-reflection-72915faaef896862",
    "prior_reflection_digest": "sha256:810088173690cb16c5580ed936f4424fe16a366352ce600306760182fee3d37a",
    "active_reflection_id": "rinse-reflection-dce0089f56d6f7cc",
    "active_reflection_digest": "sha256:bf34bbae3c6476a7d52ab573ef3fe9e6165394e403d6cd7aaacda21704d6e883",
    "target_state": "trace-functional-association-with-unresolved-adaptive-causality",
    "verdict": "ACCEPT_WITH_LIMITS",
}
EXPECTED_UPSTREAM = {
    "kairos_commit": "03dbc036513be236cd30e7542145a35b27d41fe7",
    "kairos_pull_request": 60,
    "kairos_repository": "safal207/Kairos-Gate-for-X-Cell",
    "liminaldb_commit": "b8cf0528187c6d3fac3b28dbb9e90f1a2fb740e7",
    "liminaldb_repository": "safal207/LiminalDB",
    "trace_package_commit": "31959a573724d0fd7ef1ac620a47d46355797b2f",
}
EXPECTED_EVIDENCE_DIGESTS = {
    "final_event": "sha256:e0b7a48ebd49d1b232b8ce0030b66f495f5cedfd5edea1c8100ff65f7d49a8a5",
    "rust_replay_receipt": "sha256:412b378cabc62b08978bd38ff9b1b7a674f6eb3a6842ae076c358db4c0070a16",
    "semantic_snapshot": "sha256:c73d9594c1553c4b85040ba8ba87e5afba937a2040d89ea151864b318e7b80aa",
    "snapshot_file": "sha256:39cf07f1b18151a75573a43d72fab4ab3ad2b2d2bbc83fc66b2418ca71376a9b",
    "source_ecosystem_receipt": "sha256:24fda69778ce488180e28ece2e6a893400092fbf872b0cc7850a87378dd98386",
    "wal": "sha256:74167e0af526925859587cd6cb9cdb34b76f959d11935ecb0c57ba788318d6ed",
    "workflow_artifact": "sha256:96b48012c754df81b28134e15e3049740576a36536608d1a1e658acc217f80b3",
}
EXPECTED_MANIFEST_AUTHORITY = {
    "classification": "RESEARCH_ONLY",
    "truth_authorized": False,
    "causal_authorization": False,
    "execution_authorized": False,
    "deployment_authorized": False,
    "merge_authorized": False,
}
EXPECTED_LOOP_AUTHORITY = {
    "causal_authorization": False,
    "classification": "REFLECTION_ONLY",
    "deployment_authorized": False,
    "execution_authorized": False,
    "merge_authorized": False,
    "scientific_truth_authorized": False,
    "source_mutation_authorized": False,
}
EXPECTED_GRAPH_AUTHORITY = {
    "classification": "REFLECTION_ONLY",
    "evidence_mutation_authorized": False,
    "execution_authorized": False,
    "source_trace_mutation_authorized": False,
    "truth_authorized": False,
}
MISSING_CAUSAL_INTERMEDIATES = (
    "cellular effect",
    "expression change",
    "fitness advantage",
    "organism phenotype",
)


class RinseReinterpretationError(ValueError):
    """Raised when the RINSE candidate or its pinned provenance changes."""


def _canonical(value: Any) -> bytes:
    """Serialize a value into deterministic JSON bytes."""

    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RinseReinterpretationError(f"non-canonical value: {exc}") from exc


def _digest(value: Any) -> str:
    """Return a prefixed SHA-256 digest of canonical JSON."""

    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    """Require an object value."""

    if not isinstance(value, Mapping):
        raise RinseReinterpretationError(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    """Require a non-string array value."""

    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise RinseReinterpretationError(f"{label} must be an array")
    return value


def _unique_index(values: Any, *, key: str, label: str) -> dict[str, Mapping[str, Any]]:
    """Index an array of objects by a unique string field."""

    result: dict[str, Mapping[str, Any]] = {}
    for position, raw in enumerate(_sequence(values, label)):
        item = _mapping(raw, f"{label}[{position}]")
        identity = item.get(key)
        if not isinstance(identity, str) or not identity:
            raise RinseReinterpretationError(f"{label}[{position}].{key} is invalid")
        if identity in result:
            raise RinseReinterpretationError(f"duplicate {label} identity: {identity}")
        result[identity] = item
    return result


def validate_pinned_rinse_manifest(value: Any) -> None:
    """Validate the exact RINSE source and workflow declaration."""

    manifest = _mapping(value, "manifest")
    expected_fields = {
        "schema",
        "case_id",
        "repository",
        "pull_request",
        "commit",
        "files",
        "workflow",
        "expected_output",
        "authority",
    }
    if set(manifest) != expected_fields:
        raise RinseReinterpretationError("manifest fields changed")
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("case_id") != CASE_ID:
        raise RinseReinterpretationError("manifest identity changed")
    if manifest.get("repository") != EXPECTED_REPOSITORY:
        raise RinseReinterpretationError("RINSE repository pin changed")
    if manifest.get("pull_request") != EXPECTED_PULL_REQUEST:
        raise RinseReinterpretationError("RINSE pull request pin changed")
    if manifest.get("commit") != EXPECTED_COMMIT or not HEX40.fullmatch(EXPECTED_COMMIT):
        raise RinseReinterpretationError("RINSE commit pin changed")

    files = _unique_index(manifest.get("files"), key="role", label="files")
    if set(files) != set(EXPECTED_FILES):
        raise RinseReinterpretationError("RINSE pinned file roles changed")
    for role, (expected_path, expected_blob) in EXPECTED_FILES.items():
        item = files[role]
        if set(item) != {"role", "path", "git_blob_sha"}:
            raise RinseReinterpretationError(f"unexpected RINSE file fields: {role}")
        if item.get("path") != expected_path or item.get("git_blob_sha") != expected_blob:
            raise RinseReinterpretationError(f"RINSE file pin mismatch: {role}")
        if not HEX40.fullmatch(expected_blob):
            raise RinseReinterpretationError(f"invalid internal Git blob pin: {role}")

    workflow = dict(_mapping(manifest.get("workflow"), "workflow"))
    if workflow != EXPECTED_WORKFLOW:
        raise RinseReinterpretationError("RINSE workflow evidence changed")
    if any(
        not SHA256_REF.fullmatch(value)
        for key, value in workflow.items()
        if key.endswith("digest") or key.endswith("sha256")
    ):
        raise RinseReinterpretationError("invalid workflow SHA-256 reference")
    if dict(_mapping(manifest.get("expected_output"), "expected_output")) != EXPECTED_OUTPUT:
        raise RinseReinterpretationError("expected RINSE semantic output changed")
    if dict(_mapping(manifest.get("authority"), "authority")) != EXPECTED_MANIFEST_AUTHORITY:
        raise RinseReinterpretationError("manifest authority boundary escalated")


def _validate_loop_digest(loop: Mapping[str, Any]) -> None:
    """Recompute the RINSE loop and graph semantic digests."""

    loop_body = {key: deepcopy(value) for key, value in loop.items() if key != "digest"}
    if loop.get("digest") != _digest(loop_body):
        raise RinseReinterpretationError("RINSE loop digest mismatch")
    graph = _mapping(loop.get("reflection_graph"), "reflection_graph")
    graph_body = {key: deepcopy(value) for key, value in graph.items() if key != "digest"}
    if graph.get("digest") != _digest(graph_body):
        raise RinseReinterpretationError("RINSE reflection graph digest mismatch")


def validate_rinse_loop(loop_value: Any, manifest_value: Any) -> None:
    """Validate exact RINSE semantics before creating a Kairos graph."""

    validate_pinned_rinse_manifest(manifest_value)
    loop = _mapping(loop_value, "loop")
    expected_fields = {
        "schema",
        "case_id",
        "source_receipt_digest",
        "upstream",
        "upstream_evidence_digests",
        "reflection_graph",
        "active_reflection_id",
        "kairos_handoff",
        "authority",
        "digest",
    }
    if set(loop) != expected_fields:
        raise RinseReinterpretationError("RINSE loop fields changed")
    if loop.get("schema") != LOOP_SCHEMA or loop.get("case_id") != CASE_ID:
        raise RinseReinterpretationError("RINSE loop identity changed")
    if loop.get("digest") != EXPECTED_OUTPUT["loop_digest"]:
        raise RinseReinterpretationError("RINSE loop digest pin changed")
    if loop.get("source_receipt_digest") != EXPECTED_OUTPUT["source_receipt_digest"]:
        raise RinseReinterpretationError("source receipt digest pin changed")
    if dict(_mapping(loop.get("upstream"), "upstream")) != EXPECTED_UPSTREAM:
        raise RinseReinterpretationError("RINSE upstream provenance changed")
    if dict(_mapping(loop.get("upstream_evidence_digests"), "upstream_evidence_digests")) != EXPECTED_EVIDENCE_DIGESTS:
        raise RinseReinterpretationError("RINSE evidence digests changed")
    if dict(_mapping(loop.get("authority"), "authority")) != EXPECTED_LOOP_AUTHORITY:
        raise RinseReinterpretationError("RINSE loop authority escalated")

    graph = _mapping(loop.get("reflection_graph"), "reflection_graph")
    if graph.get("schema") != "rinse.reflection-graph.v0.2":
        raise RinseReinterpretationError("unsupported RINSE graph schema")
    if graph.get("digest") != EXPECTED_OUTPUT["reflection_graph_digest"]:
        raise RinseReinterpretationError("RINSE graph digest pin changed")
    if graph.get("verdict") != EXPECTED_OUTPUT["verdict"]:
        raise RinseReinterpretationError("RINSE graph verdict changed")
    if dict(_mapping(graph.get("authority"), "reflection_graph.authority")) != EXPECTED_GRAPH_AUTHORITY:
        raise RinseReinterpretationError("RINSE graph authority escalated")
    if graph.get("forked_predecessor_ids") != []:
        raise RinseReinterpretationError("RINSE supersession fork detected")
    if graph.get("active_interpretation_ids") != [EXPECTED_OUTPUT["active_reflection_id"]]:
        raise RinseReinterpretationError("RINSE active reflection changed")
    if loop.get("active_reflection_id") != EXPECTED_OUTPUT["active_reflection_id"]:
        raise RinseReinterpretationError("loop active reflection changed")

    nodes = _unique_index(graph.get("nodes"), key="id", label="reflection_graph.nodes")
    if set(nodes) != {
        EXPECTED_OUTPUT["prior_reflection_id"],
        EXPECTED_OUTPUT["active_reflection_id"],
    }:
        raise RinseReinterpretationError("RINSE reflection node set changed")
    prior = nodes[EXPECTED_OUTPUT["prior_reflection_id"]]
    active = nodes[EXPECTED_OUTPUT["active_reflection_id"]]
    if prior.get("digest") != EXPECTED_OUTPUT["prior_reflection_digest"]:
        raise RinseReinterpretationError("prior interpretation digest changed")
    if prior.get("effective_status") != "SUPERSEDED" or prior.get("declared_status") != "CONTESTED":
        raise RinseReinterpretationError("prior interpretation status changed")
    if prior.get("superseded_by") != [EXPECTED_OUTPUT["active_reflection_id"]]:
        raise RinseReinterpretationError("supersession lineage changed")
    if active.get("digest") != EXPECTED_OUTPUT["active_reflection_digest"]:
        raise RinseReinterpretationError("active interpretation digest changed")
    if active.get("effective_status") != "SUPPORTED_WITH_LIMITS":
        raise RinseReinterpretationError("active interpretation status changed")
    if active.get("statement") != (
        "Functional enrichment is an association; adaptive causality remains unresolved."
    ):
        raise RinseReinterpretationError("active interpretation statement changed")

    handoff = _mapping(loop.get("kairos_handoff"), "kairos_handoff")
    expected_handoff = {
        "execution_allowed": False,
        "kind": "REINTERPRETATION_CANDIDATE",
        "reflection_id": EXPECTED_OUTPUT["active_reflection_id"],
        "status": "CANDIDATE",
        "target_state": EXPECTED_OUTPUT["target_state"],
    }
    if dict(handoff) != expected_handoff:
        raise RinseReinterpretationError("RINSE Kairos handoff changed")
    if graph.get("candidate_handoffs") != [expected_handoff]:
        raise RinseReinterpretationError("RINSE candidate set changed")

    expected_edges = {
        (EXPECTED_OUTPUT["prior_reflection_id"], "kairos:claim:C10", "CONTRADICTED_BY"),
        (EXPECTED_OUTPUT["active_reflection_id"], EXPECTED_OUTPUT["prior_reflection_id"], "SUPERSEDES"),
        (EXPECTED_OUTPUT["active_reflection_id"], "kairos:trace-ecosystem-receipt", "SUPPORTED_BY"),
        (EXPECTED_OUTPUT["active_reflection_id"], "liminaldb:final-event", "SUPPORTED_BY"),
        (EXPECTED_OUTPUT["active_reflection_id"], "liminaldb:rust-replay-receipt", "SUPPORTED_BY"),
        (EXPECTED_OUTPUT["active_reflection_id"], "liminaldb:semantic-snapshot", "SUPPORTED_BY"),
    }
    actual_edges = {
        (edge.get("from"), edge.get("to"), edge.get("type"))
        for edge in _sequence(graph.get("edges"), "reflection_graph.edges")
        if isinstance(edge, Mapping)
    }
    if actual_edges != expected_edges:
        raise RinseReinterpretationError("RINSE evidence or supersession edges changed")
    _validate_loop_digest(loop)


def build_rinse_revalidation_graph(loop_value: Any, manifest_value: Any) -> dict[str, Any]:
    """Project the RINSE candidate and unresolved causal path into Kairos states."""

    validate_rinse_loop(loop_value, manifest_value)
    loop = _mapping(loop_value, "loop")
    active_id = EXPECTED_OUTPUT["active_reflection_id"]
    prior_id = EXPECTED_OUTPUT["prior_reflection_id"]
    evidence_digests = loop["upstream_evidence_digests"]
    return {
        "graph_id": "trace-rinse-reinterpretation-revalidation-v0-1",
        "schema_version": "0.1.0",
        "domain": "research-interpretation-revalidation",
        "states": [
            {
                "id": "prior_overclaim",
                "type": "interpretation",
                "label": "Adaptive-benefit overclaim",
                "time_window": {"start": 0, "end": 1, "unit": "review_order"},
                "uncertainty": 0.65,
                "evidence_refs": ["rinse_prior_contested"],
            },
            {
                "id": "bounded_association",
                "type": "interpretation",
                "label": "Association with unresolved adaptive causality",
                "time_window": {"start": 1, "end": 2, "unit": "review_order"},
                "uncertainty": 0.22,
                "evidence_refs": [
                    "rinse_active_supported",
                    "kairos_ecosystem_receipt",
                    "liminaldb_replay",
                ],
            },
            {
                "id": "adaptive_causality_established",
                "type": "scientific_claim_state",
                "label": "Adaptive causality established",
                "time_window": {"start": 2, "end": 3, "unit": "review_order"},
                "uncertainty": 1.0,
                "evidence_refs": [
                    "missing_expression_change",
                    "missing_cellular_effect",
                    "missing_organism_phenotype",
                    "missing_fitness_advantage",
                ],
            },
        ],
        "evidence": [
            {
                "id": "rinse_prior_contested",
                "kind": "versioned_interpretation",
                "status": "contradicted",
                "source": f"RINSE {prior_id}",
                "strength": 0.35,
                "independent": False,
                "causal_design": False,
                "digest": EXPECTED_OUTPUT["prior_reflection_digest"],
            },
            {
                "id": "rinse_active_supported",
                "kind": "versioned_interpretation",
                "status": "computational_inference",
                "source": f"RINSE {active_id}",
                "strength": 0.78,
                "independent": False,
                "causal_design": False,
                "digest": EXPECTED_OUTPUT["active_reflection_digest"],
            },
            {
                "id": "kairos_ecosystem_receipt",
                "kind": "bounded_transition_analysis",
                "status": "computational_inference",
                "source": "Kairos TRACE ecosystem receipt",
                "strength": 0.78,
                "independent": False,
                "causal_design": False,
                "digest": evidence_digests["source_ecosystem_receipt"],
            },
            {
                "id": "liminaldb_replay",
                "kind": "durability_replay_observation",
                "status": "direct_observation",
                "source": "LiminalDB WAL snapshot reopen replay",
                "strength": 0.90,
                "independent": False,
                "causal_design": False,
                "digest": evidence_digests["rust_replay_receipt"],
            },
            *[
                {
                    "id": f"missing_{name.replace(' ', '_')}",
                    "kind": "missing_causal_intermediate",
                    "status": "missing_evidence",
                    "source": "RINSE explicit unresolved causal boundary",
                    "strength": 0.0,
                    "independent": False,
                    "causal_design": False,
                }
                for name in MISSING_CAUSAL_INTERMEDIATES
            ],
        ],
        "transitions": [
            {
                "id": "rinse_supersession",
                "from_state": "prior_overclaim",
                "to_state": "bounded_association",
                "mechanism": "evidence-bound versioned reinterpretation",
                "time_window": {"start": 0, "end": 2, "unit": "review_order"},
                "confidence": 0.78,
                "status": "computational_inference",
                "evidence_refs": [
                    "rinse_prior_contested",
                    "rinse_active_supported",
                    "kairos_ecosystem_receipt",
                    "liminaldb_replay",
                ],
                "required_intermediates": [
                    "immutable predecessor retained",
                    "supersession relation verified",
                    "non-executable handoff verified",
                ],
                "observed_intermediates": [
                    "immutable predecessor retained",
                    "supersession relation verified",
                    "non-executable handoff verified",
                ],
                "claim": {
                    "text": (
                        "The bounded association-level interpretation supersedes "
                        "the adaptive-benefit overclaim."
                    ),
                    "level": "association",
                },
            },
            {
                "id": "association_to_adaptive_causality",
                "from_state": "bounded_association",
                "to_state": "adaptive_causality_established",
                "mechanism": "unresolved biological causal chain",
                "time_window": {"start": 1, "end": 3, "unit": "review_order"},
                "confidence": 0.0,
                "status": "missing_evidence",
                "evidence_refs": [
                    "missing_expression_change",
                    "missing_cellular_effect",
                    "missing_organism_phenotype",
                    "missing_fitness_advantage",
                ],
                "required_intermediates": list(MISSING_CAUSAL_INTERMEDIATES),
                "observed_intermediates": [],
                "claim": {
                    "text": (
                        "Adaptive causality remains a hypothesis until every "
                        "declared biological intermediate is supported."
                    ),
                    "level": "hypothesis",
                },
            },
        ],
    }


def revalidate_rinse_candidate(loop_value: Any, manifest_value: Any) -> dict[str, Any]:
    """Run the Kairos engine and emit a deterministic bounded receipt."""

    loop_snapshot = deepcopy(loop_value)
    manifest_snapshot = deepcopy(manifest_value)
    graph = build_rinse_revalidation_graph(loop_snapshot, manifest_snapshot)
    analysis = analyze_transition_network(graph)
    if analysis["verdict"] != "ACCEPT_WITH_LIMITS":
        raise RinseReinterpretationError("Kairos rejected the bounded revalidation graph")
    if analysis["temporal_conflicts"] or analysis["claim_firewall"]:
        raise RinseReinterpretationError("Kairos found a temporal conflict or overclaim")
    expected_gap = {
        "transition_id": "association_to_adaptive_causality",
        "missing_intermediates": sorted(MISSING_CAUSAL_INTERMEDIATES),
        "status": "CAUSAL_GAP",
    }
    if analysis["causal_gaps"] != [expected_gap]:
        raise RinseReinterpretationError("adaptive-causality gap changed")

    body = {
        "schema": OUTPUT_SCHEMA,
        "case_id": CASE_ID,
        "source": {
            "rinse_repository": EXPECTED_REPOSITORY,
            "rinse_pull_request": EXPECTED_PULL_REQUEST,
            "rinse_commit": EXPECTED_COMMIT,
            "rinse_loop_digest": EXPECTED_OUTPUT["loop_digest"],
            "rinse_loop_file_sha256": EXPECTED_WORKFLOW["loop_file_sha256"],
            "rinse_artifact_digest": EXPECTED_WORKFLOW["artifact_digest"],
        },
        "candidate": deepcopy(loop_snapshot["kairos_handoff"]),
        "transition_graph": graph,
        "kairos_analysis": analysis,
        "decision": {
            "reinterpretation_transition": "ACCEPT_WITH_LIMITS",
            "active_interpretation": EXPECTED_OUTPUT["active_reflection_id"],
            "adaptive_causality": "HOLD_MISSING_EVIDENCE",
            "execution": "HOLD",
            "deployment": "NOT_AUTHORIZED",
            "merge": "NOT_AUTHORIZED",
        },
        "authority": {
            "classification": "RESEARCH_ONLY",
            "scientific_truth_authorized": False,
            "causal_authorization": False,
            "execution_authorized": False,
            "deployment_authorized": False,
            "merge_authorized": False,
        },
    }
    return {**body, "digest": _digest(body)}


def _load_json(path: Path, label: str) -> Mapping[str, Any]:
    """Load a UTF-8 JSON object through a bounded error path."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RinseReinterpretationError(f"cannot read {label}: {exc}") from exc
    return _mapping(value, label)


def main(argv: list[str] | None = None) -> int:
    """Validate an exact RINSE file and emit a Kairos revalidation receipt."""

    parser = argparse.ArgumentParser(description="Revalidate a pinned RINSE candidate")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--loop", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = _load_json(args.manifest, "manifest")
        loop_bytes = args.loop.read_bytes()
        file_digest = "sha256:" + hashlib.sha256(loop_bytes).hexdigest()
        if file_digest != EXPECTED_WORKFLOW["loop_file_sha256"]:
            raise RinseReinterpretationError("RINSE loop file SHA-256 mismatch")
        try:
            loop = json.loads(loop_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RinseReinterpretationError(f"cannot parse RINSE loop: {exc}") from exc
        result = revalidate_rinse_candidate(loop, manifest)
    except (OSError, RinseReinterpretationError, TransitionGraphError) as exc:
        print(f"BLOCK: {exc}")
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except OSError as exc:
        print(f"BLOCK: cannot write receipt: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
