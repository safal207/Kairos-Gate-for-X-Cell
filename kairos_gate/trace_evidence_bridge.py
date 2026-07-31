"""Pinned TRACE evidence-package bridge for Kairos ecosystem projections.

This module consumes a bounded evidence package, derives a transition graph, and
emits documentary projections for CML, ProofPath, and LiminalDB. It does not
establish scientific truth, execute biological work, or grant action authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

from .transition_graph import TransitionGraphError, analyze_transition_network


class TraceEvidenceBridgeError(ValueError):
    """Raised when the pinned TRACE package or a derived receipt is invalid."""


EXPECTED_CASE_ID = "trace-archaic-introgression-2026"
EXPECTED_PRIMARY_STATUS = "KAIROS_PARTIAL_COMPUTATIONAL_INFERENCE"
EXPECTED_PHASE_STATUS = "KAIROS_EXTERNAL_METHOD_CASE_NO_CELLULAR_PHASE"
EXPECTED_ROLES = {
    "claim_map",
    "causal_transition_map",
    "disposition",
    "source_manifest",
    "reproducibility_contract",
    "phase_compatibility",
}
EXPECTED_CLAIM_STATUSES = {
    "C1": "SUPPORTED_METHOD_DESCRIPTION",
    "C2": "SUPPORTED_BY_AUTHOR_VALIDATION",
    "C3": "SUPPORTED_MODEL_BASED_INFERENCE",
    "C4": "SUPPORTED_AS_AUTHOR_REPORTED_ESTIMATE",
    "C5": "SUPPORTED_MODEL_DEPENDENT_TIME_ESTIMATE",
    "C6": "SUPPORTED_MODEL_BASED_INFERENCE",
    "C7": "REJECTED_DIRECT_OBSERVATION_CLAIM",
    "C8": "UNRESOLVED_TAXONOMIC_IDENTITY",
    "C9": "REJECTED_UNIVERSAL_SEGMENT_CLAIM",
    "C10": "REJECTED_CAUSAL_ADAPTATION_OVERCLAIM",
    "C11": "NOT_ESTABLISHED",
    "C12": "NOT_ESTABLISHED_UNIQUE_IDENTIFICATION",
}
REQUIRED_SECONDARY_STATUSES = {
    "NO_DIRECT_ARCHAIC_GENOME",
    "NO_DIRECT_FOSSIL_ASSIGNMENT",
    "TAXONOMIC_IDENTITY_UNRESOLVED",
    "FUNCTIONAL_ADAPTATION_UNRESOLVED",
    "REPRODUCTION_PENDING",
    "PROCESSED_DATA_PENDING",
    "OUTSIDE_CELLULAR_PHASE_DOMAIN",
}
REQUIRED_CAUSAL_NODES = {"N1", "N3", "N5", "N9", "N10", "N11", "N12", "N13"}
REQUIRED_REPRO_BLOCKERS = {"B1", "B2", "B3", "B4", "B5", "B6", "B7"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TraceEvidenceBridgeError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TraceEvidenceBridgeError(f"{label} must be an array")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TraceEvidenceBridgeError(f"{label} must be a non-empty string")
    return value


def _unique_index(items: Sequence[Any], label: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for position, raw in enumerate(items):
        item = _mapping(raw, f"{label}[{position}]")
        item_id = _text(item.get("id"), f"{label}[{position}].id")
        if item_id in result:
            raise TraceEvidenceBridgeError(f"duplicate {label} id: {item_id}")
        result[item_id] = item
    return result


def _assert_no_authority_escalation(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "classification" and child != "RESEARCH_ONLY":
                raise TraceEvidenceBridgeError(
                    f"{child_path} must remain RESEARCH_ONLY"
                )
            if (
                isinstance(child, bool)
                and child is True
                and any(
                    token in key
                    for token in (
                        "authoriz",
                        "allowed",
                        "unlocked",
                        "established",
                        "reproduced",
                    )
                )
            ):
                raise TraceEvidenceBridgeError(
                    f"authority escalation is forbidden at {child_path}"
                )
            _assert_no_authority_escalation(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _assert_no_authority_escalation(child, f"{path}[{index}]")


def validate_pinned_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate the immutable source-package declaration."""
    if manifest.get("schema") != "kairos.pinned-evidence-package.v0.1":
        raise TraceEvidenceBridgeError("unsupported pinned package schema")
    if manifest.get("case_id") != EXPECTED_CASE_ID:
        raise TraceEvidenceBridgeError("pinned package case_id mismatch")
    _text(manifest.get("repository"), "repository")
    commit = _text(manifest.get("commit"), "commit")
    if not HEX40.fullmatch(commit):
        raise TraceEvidenceBridgeError("commit must be a lowercase 40-character SHA")
    files = _array(manifest.get("files"), "files")
    roles: set[str] = set()
    paths: set[str] = set()
    for position, raw in enumerate(files):
        item = _mapping(raw, f"files[{position}]")
        role = _text(item.get("role"), f"files[{position}].role")
        path = _text(item.get("path"), f"files[{position}].path")
        blob = _text(item.get("git_blob_sha"), f"files[{position}].git_blob_sha")
        _text(item.get("expected_schema"), f"files[{position}].expected_schema")
        if not HEX40.fullmatch(blob):
            raise TraceEvidenceBridgeError(f"invalid Git blob SHA for role {role}")
        if role in roles:
            raise TraceEvidenceBridgeError(f"duplicate pinned role: {role}")
        if path in paths:
            raise TraceEvidenceBridgeError(f"duplicate pinned path: {path}")
        roles.add(role)
        paths.add(path)
    if roles != EXPECTED_ROLES:
        raise TraceEvidenceBridgeError(
            f"pinned roles mismatch: {sorted(roles)} != {sorted(EXPECTED_ROLES)}"
        )
    _assert_no_authority_escalation(manifest.get("authority", {}), "$.authority")


def validate_trace_package(
    pinned_manifest: Mapping[str, Any], package: Mapping[str, Any]
) -> None:
    """Validate the semantic boundaries of the six-file TRACE package."""
    validate_pinned_manifest(pinned_manifest)
    if set(package) != EXPECTED_ROLES:
        raise TraceEvidenceBridgeError("loaded package roles do not match manifest")

    declared = {
        item["role"]: item for item in _array(pinned_manifest["files"], "files")
    }
    generated_times: set[str] = set()
    for role in sorted(EXPECTED_ROLES):
        document = _mapping(package[role], role)
        if document.get("schema") != declared[role]["expected_schema"]:
            raise TraceEvidenceBridgeError(f"{role} schema mismatch")
        if document.get("case_id") != EXPECTED_CASE_ID:
            raise TraceEvidenceBridgeError(f"{role} case_id mismatch")
        generated_times.add(_text(document.get("generated_at"), f"{role}.generated_at"))
        _assert_no_authority_escalation(document.get("authority", {}), f"$.{role}.authority")
    if len(generated_times) != 1:
        raise TraceEvidenceBridgeError("package generated_at values are inconsistent")

    source_manifest = _mapping(package["source_manifest"], "source_manifest")
    sources = _unique_index(_array(source_manifest.get("sources"), "sources"), "sources")
    if source_manifest.get("availability_boundary", {}).get(
        "full_independent_reproduction"
    ) != "PENDING":
        raise TraceEvidenceBridgeError("independent reproduction must remain pending")
    if source_manifest.get("availability_boundary", {}).get(
        "direct_unknown_archaic_genome"
    ) is not False:
        raise TraceEvidenceBridgeError("direct unknown-source genome must remain false")
    code_pins = _mapping(source_manifest.get("code_pins"), "code_pins")
    for name in ("trace_repository", "trace_paper_repository"):
        commit = _text(code_pins[name].get("audited_commit"), f"code_pins.{name}")
        if not HEX40.fullmatch(commit):
            raise TraceEvidenceBridgeError(f"invalid audited commit for {name}")

    claim_map = _mapping(package["claim_map"], "claim_map")
    claims = _unique_index(_array(claim_map.get("claims"), "claims"), "claims")
    if set(claims) != set(EXPECTED_CLAIM_STATUSES):
        raise TraceEvidenceBridgeError("TRACE claim IDs must remain exactly C1-C12")
    for claim_id, expected_status in EXPECTED_CLAIM_STATUSES.items():
        claim = claims[claim_id]
        if claim.get("status") != expected_status:
            raise TraceEvidenceBridgeError(
                f"{claim_id} status changed: {claim.get('status')!r}"
            )
        _text(claim.get("claim"), f"claims.{claim_id}.claim")
        for source_id in _array(claim.get("source_basis"), f"claims.{claim_id}.source_basis"):
            if source_id not in sources:
                raise TraceEvidenceBridgeError(
                    f"{claim_id} references unknown source: {source_id}"
                )

    causal_map = _mapping(package["causal_transition_map"], "causal_transition_map")
    if causal_map.get("map_type") != (
        "COMPUTATIONAL_INFERENCE_GRAPH_NOT_BIOLOGICAL_CAUSAL_PROOF"
    ):
        raise TraceEvidenceBridgeError("causal map type exceeded evidence boundary")
    nodes = _unique_index(_array(causal_map.get("nodes"), "nodes"), "nodes")
    if not REQUIRED_CAUSAL_NODES.issubset(nodes):
        raise TraceEvidenceBridgeError("required TRACE causal nodes are missing")
    for position, raw in enumerate(_array(causal_map.get("edges"), "edges")):
        edge = _mapping(raw, f"edges[{position}]")
        if edge.get("from") not in nodes or edge.get("to") not in nodes:
            raise TraceEvidenceBridgeError("causal map edge references missing node")
    shortcuts = "\n".join(
        str(value).lower()
        for value in _array(
            causal_map.get("forbidden_causal_shortcuts"),
            "forbidden_causal_shortcuts",
        )
    )
    for required in (
        "directly observed ancient individual",
        "named species",
        "adaptive benefit",
        "unique identification",
        "identical ancestry",
    ):
        if required not in shortcuts:
            raise TraceEvidenceBridgeError(
                f"missing forbidden causal shortcut boundary: {required}"
            )

    disposition = _mapping(package["disposition"], "disposition")
    if disposition.get("primary_status") != EXPECTED_PRIMARY_STATUS:
        raise TraceEvidenceBridgeError("TRACE primary disposition changed")
    secondary = set(_array(disposition.get("secondary_statuses"), "secondary_statuses"))
    if not REQUIRED_SECONDARY_STATUSES.issubset(secondary):
        raise TraceEvidenceBridgeError("TRACE negative boundary statuses are incomplete")
    if not disposition.get("forbidden_language"):
        raise TraceEvidenceBridgeError("forbidden-language firewall must not be empty")

    reproducibility = _mapping(
        package["reproducibility_contract"], "reproducibility_contract"
    )
    if reproducibility.get("status") != "REPRODUCTION_PENDING":
        raise TraceEvidenceBridgeError("reproduction status must remain pending")
    blockers = _unique_index(
        _array(reproducibility.get("blocking_components"), "blocking_components"),
        "blocking_components",
    )
    if set(blockers) != REQUIRED_REPRO_BLOCKERS:
        raise TraceEvidenceBridgeError("reproduction blockers B1-B7 must remain explicit")
    if any(item.get("status") in {"RESOLVED", "PASS"} for item in blockers.values()):
        raise TraceEvidenceBridgeError("unverified reproduction blocker was promoted")

    phase = _mapping(package["phase_compatibility"], "phase_compatibility")
    assessment = _mapping(phase.get("assessment"), "phase_compatibility.assessment")
    if assessment.get("status") != EXPECTED_PHASE_STATUS:
        raise TraceEvidenceBridgeError("TRACE phase-domain boundary changed")
    if assessment.get("candidate_window_unlocked") is not False:
        raise TraceEvidenceBridgeError("TRACE must not unlock a cellular candidate window")


def _file_receipt_index(file_receipts: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    index = _unique_index(file_receipts, "file_receipts")
    if set(index) != EXPECTED_ROLES:
        raise TraceEvidenceBridgeError("file receipt roles are incomplete")
    for role, receipt in index.items():
        if not HEX40.fullmatch(_text(receipt.get("git_blob_sha"), f"{role}.git_blob_sha")):
            raise TraceEvidenceBridgeError(f"invalid Git blob SHA in receipt {role}")
        sha256 = _text(receipt.get("sha256"), f"{role}.sha256")
        if not HEX64.fullmatch(sha256):
            raise TraceEvidenceBridgeError(f"invalid SHA-256 in receipt {role}")
        if not isinstance(receipt.get("bytes"), int) or receipt["bytes"] <= 0:
            raise TraceEvidenceBridgeError(f"invalid byte count in receipt {role}")
    return index


def derive_trace_transition_graph(
    package: Mapping[str, Any], file_receipts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Derive a bounded graph from validated TRACE package semantics."""
    receipts = _file_receipt_index(file_receipts)
    claims = _unique_index(package["claim_map"]["claims"], "claims")
    causal = package["causal_transition_map"]
    alternatives = list(causal["alternative_explanations_and_sensitivities"])
    source_manifest = package["source_manifest"]
    doi = source_manifest["primary_citation"]["doi"]
    retrieved_at = source_manifest["retrieval"]["retrieved_at"]

    def provenance(role: str, locator: str) -> dict[str, Any]:
        return {
            "locator": locator,
            "content_digest": f"sha256:{receipts[role]['sha256']}",
            "retrieved_at": retrieved_at,
            "reproducible": False,
        }

    evidence = [
        {
            "id": "trace_inference",
            "kind": "arg_hmm_computational_analysis",
            "status": "computational_inference",
            "source": f"TRACE Science 2026 DOI {doi}",
            "strength": 0.78,
            "independent": False,
            "causal_design": False,
            "claim_scope": "latent-source ancestry and introgression-path inference",
            "supports": ["superarchaic_to_denisovan", "ghost_to_sapiens"],
            "contradicts": [],
            "provenance": provenance("claim_map", f"PR55:{claims['C3']['id']},{claims['C6']['id']}"),
        },
        {
            "id": "known_archaic_controls",
            "kind": "positive_control",
            "status": "author_reported",
            "source": "TRACE recovery of known Neanderthal and Denisovan signals",
            "strength": 0.72,
            "independent": False,
            "causal_design": False,
            "claim_scope": "method behavior under author-tested settings",
            "supports": ["denisovan_to_sapiens"],
            "contradicts": [],
            "provenance": provenance("claim_map", "PR55:C2"),
        },
        {
            "id": "modern_genome_observation",
            "kind": "modern_genome_input_observation",
            "status": "direct_observation",
            "source": "Present-day phased genome inputs described by TRACE",
            "strength": 0.84,
            "independent": False,
            "causal_design": False,
            "claim_scope": "modern genome observations, not direct unknown-source DNA",
            "supports": ["sapiens_to_modern"],
            "contradicts": [],
            "provenance": provenance("causal_transition_map", "PR55:N1"),
        },
        {
            "id": "functional_enrichment_report",
            "kind": "functional_annotation_enrichment",
            "status": "author_reported",
            "source": "TRACE reported immune and metabolic annotation enrichment",
            "strength": 0.55,
            "independent": False,
            "causal_design": False,
            "claim_scope": "annotation association only",
            "supports": ["modern_to_functional_signal"],
            "contradicts": [],
            "provenance": provenance("claim_map", "PR55:C10"),
        },
        {
            "id": "reproduction_gap",
            "kind": "reproducibility_boundary",
            "status": "missing_evidence",
            "source": "PR55 reproducibility blockers B1-B7",
            "strength": 0.0,
            "independent": False,
            "causal_design": False,
            "claim_scope": "independent reproduction is not established",
            "supports": [],
            "contradicts": ["independent_reproduction_claim"],
            "provenance": provenance("reproducibility_contract", "PR55:B1-B7"),
        },
    ]

    states = [
        {
            "id": "superarchaic_population",
            "type": "population",
            "label": "Unresolved super-archaic source population",
            "time_window": {"start": -2000000, "end": -200000, "unit": "years_relative_to_present"},
            "uncertainty": 0.8,
            "evidence_refs": ["trace_inference"],
            "properties": {"taxonomic_identity": "unresolved", "direct_genome": False},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "ghost_population",
            "type": "population",
            "label": "Unresolved ghost source population",
            "time_window": {"start": -1200000, "end": -200000, "unit": "years_relative_to_present"},
            "uncertainty": 0.75,
            "evidence_refs": ["trace_inference"],
            "properties": {"taxonomic_identity": "unresolved", "direct_genome": False},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "denisovan_population",
            "type": "population",
            "label": "Denisovan population",
            "time_window": {"start": -500000, "end": -40000, "unit": "years_relative_to_present"},
            "uncertainty": 0.3,
            "evidence_refs": ["known_archaic_controls"],
            "properties": {"ancient_genome_available": True},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "sapiens_ancestors",
            "type": "population",
            "label": "Ancestors of sampled modern Homo sapiens",
            "time_window": {"start": -800000, "end": 0, "unit": "years_relative_to_present"},
            "uncertainty": 0.45,
            "evidence_refs": ["modern_genome_observation"],
            "properties": {"population_structure": "heterogeneous"},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "modern_human_genomes",
            "type": "genomic_observation",
            "label": "Observed present-day human genome panel",
            "time_window": {"start": -100, "end": 0, "unit": "years_relative_to_present"},
            "uncertainty": 0.15,
            "evidence_refs": ["modern_genome_observation"],
            "properties": {"direct_unknown_source_genome": False},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "functional_enrichment_signal",
            "type": "annotation_result",
            "label": "Reported immune and metabolic annotation enrichment",
            "time_window": {"start": -100, "end": 0, "unit": "years_relative_to_present"},
            "uncertainty": 0.6,
            "evidence_refs": ["functional_enrichment_report"],
            "properties": {"adaptive_advantage_established": False},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
    ]

    def competing(values: Sequence[str]) -> list[dict[str, str]]:
        return [
            {
                "id": f"alternative_{index + 1}",
                "description": value,
                "status": "untested",
            }
            for index, value in enumerate(values)
        ]

    transitions = [
        {
            "id": "superarchaic_to_denisovan",
            "from_state": "superarchaic_population",
            "to_state": "denisovan_population",
            "mechanism": "introgression",
            "time_window": {"start": -400000, "end": -200000, "unit": "years_relative_to_present"},
            "status": "computational_inference",
            "confidence": 0.64,
            "evidence_refs": ["trace_inference"],
            "required_intermediates": ["population_contact", "gene_flow", "segment_persistence"],
            "observed_intermediates": ["segment_persistence"],
            "competing_explanations": competing(alternatives[5:8]),
            "claim": {"text": claims["C6"]["claim"], "level": "association"},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "ghost_to_sapiens",
            "from_state": "ghost_population",
            "to_state": "sapiens_ancestors",
            "mechanism": "introgression",
            "time_window": {"start": -700000, "end": -300000, "unit": "years_relative_to_present"},
            "status": "computational_inference",
            "confidence": 0.68,
            "evidence_refs": ["trace_inference"],
            "required_intermediates": ["population_contact", "gene_flow", "segment_persistence"],
            "observed_intermediates": ["segment_persistence"],
            "competing_explanations": competing(alternatives[5:8]),
            "claim": {"text": claims["C3"]["claim"], "level": "association"},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "denisovan_to_sapiens",
            "from_state": "denisovan_population",
            "to_state": "sapiens_ancestors",
            "mechanism": "introgression",
            "time_window": {"start": -100000, "end": -40000, "unit": "years_relative_to_present"},
            "status": "author_reported",
            "confidence": 0.76,
            "evidence_refs": ["known_archaic_controls"],
            "required_intermediates": ["population_contact", "gene_flow", "segment_persistence"],
            "observed_intermediates": ["gene_flow", "segment_persistence"],
            "competing_explanations": [],
            "claim": {"text": "Known Denisovan ancestry provides a bounded control path", "level": "association"},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "sapiens_to_modern",
            "from_state": "sapiens_ancestors",
            "to_state": "modern_human_genomes",
            "mechanism": "inheritance_and_observation",
            "time_window": {"start": -100, "end": 0, "unit": "years_relative_to_present"},
            "status": "direct_observation",
            "confidence": 0.84,
            "evidence_refs": ["modern_genome_observation"],
            "required_intermediates": ["segment_inheritance", "modern_sampling"],
            "observed_intermediates": ["segment_inheritance", "modern_sampling"],
            "competing_explanations": [],
            "claim": {"text": "Modern sequence variation is directly observed", "level": "mechanism"},
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
        {
            "id": "modern_to_functional_signal",
            "from_state": "modern_human_genomes",
            "to_state": "functional_enrichment_signal",
            "mechanism": "functional_annotation_enrichment",
            "time_window": {"start": -100, "end": 0, "unit": "years_relative_to_present"},
            "status": "author_reported",
            "confidence": 0.53,
            "evidence_refs": ["functional_enrichment_report"],
            "required_intermediates": ["expression_change", "cellular_effect", "organism_phenotype", "fitness_advantage"],
            "observed_intermediates": [],
            "competing_explanations": competing(alternatives[7:10]),
            "claim": {
                "text": package["disposition"]["permitted_language"][-1],
                "level": "association",
            },
            "authority": {"classification": "RESEARCH_ONLY", "action_authorized": False},
        },
    ]

    graph = {
        "schema_version": "kairos.transition-network.v0.1",
        "graph_id": "trace-pr55-derived-transition-network-v0.1",
        "domain": "human-evolutionary-genomics",
        "states": states,
        "evidence": evidence,
        "transitions": transitions,
        "policy": {
            "classification": "RESEARCH_ONLY",
            "source_package_case_id": EXPECTED_CASE_ID,
            "direct_unknown_source_genome_claim": False,
            "taxonomic_assignment": False,
            "adaptive_causality_claim": False,
            "independent_reproduction_claim": False,
            "cellular_candidate_window": False,
            "experiment_authorization": False,
            "clinical_authorization": False,
            "deployment_authorization": False,
            "merge_authorization": False,
        },
    }
    try:
        analyze_transition_network(graph)
    except TransitionGraphError as exc:
        raise TraceEvidenceBridgeError(f"derived graph is invalid: {exc}") from exc
    return graph


def _hash_chain(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    previous = "0" * 64
    chained: list[dict[str, Any]] = []
    for sequence, raw in enumerate(records, start=1):
        record = dict(raw)
        record["sequence"] = sequence
        record["previous_hash"] = previous
        record_hash = _digest(record)
        record["record_hash"] = record_hash
        chained.append(record)
        previous = record_hash
    return chained


def _claim_decision(status: str) -> str:
    if status.startswith("SUPPORTED_"):
        return "ACCEPT_WITH_LIMITS"
    if status.startswith("REJECTED_"):
        return "BLOCK"
    return "HOLD"


def _build_cml_projection(
    package: Mapping[str, Any], file_receipts: Sequence[Mapping[str, Any]], analysis: Mapping[str, Any]
) -> dict[str, Any]:
    evidence = [
        {
            "id": f"e-{item['id']}",
            "kind": "artifact",
            "digest": item["sha256"],
            "locator": item["path"],
            "description": f"Pinned TRACE package file role={item['id']}",
        }
        for item in sorted(file_receipts, key=lambda value: value["id"])
    ]
    evidence_ids = [item["id"] for item in evidence]
    body = {
        "schema_version": "cml-memory-pack-v1",
        "manifest": {
            "project": "TRACE archaic-introgression causal memory",
            "source_repository": "https://github.com/safal207/Kairos-Gate-for-X-Cell",
            "source_commit": package["source_manifest"]["code_pins"]["trace_repository"]["audited_commit"],
            "created_at": package["claim_map"]["generated_at"],
            "visibility": "public",
            "license": "MIT",
            "contains_private_data": False,
            "merge_authority": False,
            "execution_authority": False,
            "description": "Preserves model-based ancestry inference, causal gaps, rejected shortcuts, and reproduction blockers without promoting them to biological truth.",
        },
        "graph": {
            "nodes": [
                {
                    "id": "situation-trace-package-observed",
                    "kind": "situation",
                    "label": "Pinned TRACE evidence package was observed and graph-derived",
                    "status": "observed",
                    "confidence": 100,
                    "attributes": {"kairos_verdict": analysis["verdict"]},
                },
                {
                    "id": "constraint-computational-inference",
                    "kind": "constraint",
                    "label": "Unknown source populations remain computational inferences without direct genomes or taxonomic identity",
                    "status": "verified",
                    "confidence": 100,
                    "attributes": {"direct_source_genome": False, "taxonomy_authorized": False},
                },
                {
                    "id": "constraint-adaptive-causal-gap",
                    "kind": "constraint",
                    "label": "Functional enrichment does not establish adaptive causality",
                    "status": "verified",
                    "confidence": 100,
                    "attributes": {"causal_gap_count": len(analysis["causal_gaps"])},
                },
                {
                    "id": "action-independent-reproduction",
                    "kind": "action",
                    "label": "Resolve B1-B7 and independently reproduce controls and segment summaries",
                    "status": "proposed",
                    "confidence": 100,
                    "attributes": {"execution_authority": False},
                },
                {
                    "id": "lesson-preserve-bounded-inference",
                    "kind": "lesson",
                    "label": "Preserve the partial computational inference together with its rejected and unresolved claims",
                    "status": "verified",
                    "confidence": 100,
                    "attributes": {"scientific_truth_claim": False},
                },
            ],
            "edges": [
                {
                    "id": "edge-situation-inference-constraint",
                    "source": "situation-trace-package-observed",
                    "target": "constraint-computational-inference",
                    "relation": "supports",
                    "strength": 100,
                    "evidence_ids": evidence_ids,
                },
                {
                    "id": "edge-inference-adaptive-constraint",
                    "source": "constraint-computational-inference",
                    "target": "constraint-adaptive-causal-gap",
                    "relation": "requires",
                    "strength": 100,
                    "evidence_ids": evidence_ids,
                },
                {
                    "id": "edge-constraints-next-action",
                    "source": "constraint-adaptive-causal-gap",
                    "target": "action-independent-reproduction",
                    "relation": "requires",
                    "strength": 100,
                    "evidence_ids": evidence_ids,
                },
                {
                    "id": "edge-action-lesson",
                    "source": "action-independent-reproduction",
                    "target": "lesson-preserve-bounded-inference",
                    "relation": "leads_to",
                    "strength": 100,
                    "evidence_ids": evidence_ids,
                },
            ],
            "selected_path": [
                "situation-trace-package-observed",
                "constraint-computational-inference",
                "constraint-adaptive-causal-gap",
                "action-independent-reproduction",
                "lesson-preserve-bounded-inference",
            ],
        },
        "evidence": evidence,
        "redactions": [],
    }
    result = dict(body)
    result["pack_id"] = _digest(body)
    return result


def _build_proofpath_projection(
    package: Mapping[str, Any], file_receipts: Sequence[Mapping[str, Any]], analysis: Mapping[str, Any]
) -> dict[str, Any]:
    claims = sorted(package["claim_map"]["claims"], key=lambda item: item["id"])
    proof_paths = []
    for claim in claims:
        proof_paths.append(
            {
                "claim_id": claim["id"],
                "claim_status": claim["status"],
                "decision": _claim_decision(claim["status"]),
                "execution_allowed": False,
                "path": [
                    {"kind": "package_file", "role": "claim_map"},
                    *[
                        {"kind": "source_reference", "source_id": source_id}
                        for source_id in claim["source_basis"]
                    ],
                ],
                "verification_level": claim["verification_level"],
            }
        )
    audit_records = _hash_chain(
        [
            {
                "record_type": "authorization",
                "decision": "RESEARCH_ONLY",
                "execution_allowed": False,
            },
            {
                "record_type": "package_observation",
                "file_count": len(file_receipts),
                "package_digest": _digest(sorted(file_receipts, key=lambda item: item["id"])),
            },
            {
                "record_type": "graph_derivation",
                "kairos_verdict": analysis["verdict"],
                "graph_digest": _digest(analysis),
            },
            {
                "record_type": "claim_boundary",
                "blocked_claims": [item["claim_id"] for item in proof_paths if item["decision"] == "BLOCK"],
                "held_claims": [item["claim_id"] for item in proof_paths if item["decision"] == "HOLD"],
            },
            {
                "record_type": "decision",
                "decision": "HOLD",
                "reason": "REPRODUCTION_TAXONOMY_AND_ADAPTIVE_CAUSALITY_UNRESOLVED",
                "execution_allowed": False,
            },
        ]
    )
    body = {
        "schema_version": "proofpath-portable-evidence-projection-v0.1",
        "decision": "HOLD",
        "execution_allowed": False,
        "proof_paths": proof_paths,
        "audit_chain": audit_records,
        "policy": {
            "model_output_is_proposal_not_authorization": True,
            "scientific_execution_authorized": False,
            "experiment_authorized": False,
            "clinical_authorized": False,
            "ancestry_identity_authorized": False,
            "deployment_authorized": False,
            "merge_authorized": False,
        },
    }
    result = dict(body)
    result["bundle_id"] = _digest(body)
    return result


def _build_liminaldb_projection(analysis: Mapping[str, Any]) -> dict[str, Any]:
    raw_records = [
        {
            "record_ref": "trace-bridge-authorization-v0-1",
            "record_type": "authorization",
            "parent_ref": None,
            "payload": {
                "classification": "RESEARCH_ONLY",
                "analysis_authorized": True,
                "side_effect_authorized": False,
            },
        },
        {
            "record_ref": "trace-package-observation-v0-1",
            "record_type": "observation",
            "parent_ref": "trace-bridge-authorization-v0-1",
            "payload": {"package_observed": True, "biological_event_observed": False},
        },
        {
            "record_ref": "trace-response-integrity-v0-1",
            "record_type": "response_integrity",
            "parent_ref": "trace-package-observation-v0-1",
            "payload": {"kairos_verdict": analysis["verdict"], "report_matches_analysis": True},
        },
        {
            "record_ref": "trace-causal-audit-v0-1",
            "record_type": "causal_audit",
            "parent_ref": "trace-response-integrity-v0-1",
            "payload": {
                "causal_gap_count": len(analysis["causal_gaps"]),
                "causal_validity": "RANKED_NOT_IDENTIFIED",
            },
        },
        {
            "record_ref": "trace-continuity-snapshot-v0-1",
            "record_type": "continuity_snapshot",
            "parent_ref": "trace-causal-audit-v0-1",
            "payload": {
                "continuity_posture": "REPORT_ONLY",
                "side_effect_committed": False,
                "source_verdict": analysis["verdict"],
                "adds_scientific_verdict": False,
            },
        },
    ]
    records = []
    previous_hash = "0" * 64
    for sequence, raw in enumerate(raw_records, start=1):
        record = dict(raw)
        record["sequence"] = sequence
        record["payload_digest"] = _digest(record["payload"])
        record["previous_event_hash"] = previous_hash
        record["event_hash"] = _digest(record)
        previous_hash = record["event_hash"]
        records.append(record)
    projection = {
        "authority": "VALID_RESEARCH_ONLY",
        "execution": "OBSERVED_EXECUTED",
        "response_integrity": "VERIFIED",
        "causal_validity": "RANKED_NOT_IDENTIFIED",
        "continuity_posture": "REPORT_ONLY",
        "side_effect_committed": False,
        "source_verdict": analysis["verdict"],
        "adds_scientific_verdict": False,
    }
    return {
        "profile": "org.liminaldb.trustworthy-transition-ledger.v0.1",
        "conformance": "DOCUMENTARY_PROJECTION_NOT_RUST_REPLAY",
        "transition_id": "trace-pr55-kairos-analysis-v0-1",
        "supersession_relation": "ROOT",
        "records": records,
        "projection": projection,
        "local_projection_replay_equal": True,
        "replay_digest": _digest({"records": records, "projection": projection}),
    }


def build_trace_ecosystem_receipt(
    pinned_manifest: Mapping[str, Any],
    package: Mapping[str, Any],
    file_receipts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build and validate the deterministic TRACE ecosystem receipt."""
    validate_trace_package(pinned_manifest, package)
    receipts = _file_receipt_index(file_receipts)
    declared = {item["role"]: item for item in pinned_manifest["files"]}
    for role, receipt in receipts.items():
        if receipt["git_blob_sha"] != declared[role]["git_blob_sha"]:
            raise TraceEvidenceBridgeError(f"Git blob mismatch for {role}")
        if receipt["path"] != declared[role]["path"]:
            raise TraceEvidenceBridgeError(f"path mismatch for {role}")

    ordered_receipts = [receipts[role] for role in sorted(receipts)]
    graph = derive_trace_transition_graph(package, ordered_receipts)
    analysis = analyze_transition_network(graph)
    if analysis["verdict"] != "ACCEPT_WITH_LIMITS":
        raise TraceEvidenceBridgeError("bounded TRACE graph must be ACCEPT_WITH_LIMITS")
    gap_ids = {item["transition_id"] for item in analysis["causal_gaps"]}
    if "modern_to_functional_signal" not in gap_ids:
        raise TraceEvidenceBridgeError("adaptive causal gap disappeared")

    body = {
        "schema": "kairos.trace-ecosystem-receipt.v0.1",
        "source_package": {
            "package_id": pinned_manifest["package_id"],
            "case_id": EXPECTED_CASE_ID,
            "repository": pinned_manifest["repository"],
            "pull_request": pinned_manifest["pull_request"],
            "commit": pinned_manifest["commit"],
            "files": ordered_receipts,
            "package_digest": _digest(ordered_receipts),
        },
        "transition_graph": graph,
        "kairos_analysis": analysis,
        "cml_projection": _build_cml_projection(package, ordered_receipts, analysis),
        "proofpath_projection": _build_proofpath_projection(package, ordered_receipts, analysis),
        "liminaldb_projection": _build_liminaldb_projection(analysis),
        "authority": {
            "classification": "RESEARCH_ONLY",
            "scientific_truth_authorized": False,
            "causal_authorization": False,
            "experiment_authorization": False,
            "clinical_authorization": False,
            "ancestry_identity_authorization": False,
            "deployment_authorization": False,
            "merge_authorization": False,
        },
    }
    result = dict(body)
    result["receipt_id"] = _digest(body)
    validate_ecosystem_receipt(result)
    return result


def validate_ecosystem_receipt(receipt: Mapping[str, Any]) -> None:
    """Validate receipt identity, chain integrity, and authority boundaries."""
    if receipt.get("schema") != "kairos.trace-ecosystem-receipt.v0.1":
        raise TraceEvidenceBridgeError("unsupported ecosystem receipt schema")
    expected_receipt_id = _digest({key: value for key, value in receipt.items() if key != "receipt_id"})
    if receipt.get("receipt_id") != expected_receipt_id:
        raise TraceEvidenceBridgeError("ecosystem receipt digest mismatch")
    _assert_no_authority_escalation(receipt.get("authority", {}), "$.authority")

    graph = _mapping(receipt.get("transition_graph"), "transition_graph")
    expected_analysis = analyze_transition_network(graph)
    if receipt.get("kairos_analysis") != expected_analysis:
        raise TraceEvidenceBridgeError("Kairos analysis does not match graph")

    cml = _mapping(receipt.get("cml_projection"), "cml_projection")
    cml_body = {key: value for key, value in cml.items() if key != "pack_id"}
    if cml.get("pack_id") != _digest(cml_body):
        raise TraceEvidenceBridgeError("CML pack digest mismatch")
    selected = cml.get("graph", {}).get("selected_path", [])
    node_ids = {item["id"] for item in cml.get("graph", {}).get("nodes", [])}
    if not selected or any(node not in node_ids for node in selected):
        raise TraceEvidenceBridgeError("CML selected path is invalid")

    proof = _mapping(receipt.get("proofpath_projection"), "proofpath_projection")
    proof_body = {key: value for key, value in proof.items() if key != "bundle_id"}
    if proof.get("bundle_id") != _digest(proof_body):
        raise TraceEvidenceBridgeError("ProofPath bundle digest mismatch")
    if proof.get("execution_allowed") is not False:
        raise TraceEvidenceBridgeError("ProofPath must not authorize execution")
    previous = "0" * 64
    for expected_sequence, raw in enumerate(proof.get("audit_chain", []), start=1):
        record = dict(raw)
        record_hash = record.pop("record_hash", None)
        if record.get("sequence") != expected_sequence or record.get("previous_hash") != previous:
            raise TraceEvidenceBridgeError("ProofPath audit chain order mismatch")
        if record_hash != _digest(record):
            raise TraceEvidenceBridgeError("ProofPath audit chain hash mismatch")
        previous = record_hash

    liminal = _mapping(receipt.get("liminaldb_projection"), "liminaldb_projection")
    if liminal.get("projection", {}).get("adds_scientific_verdict") is not False:
        raise TraceEvidenceBridgeError("LiminalDB projection must not add a verdict")
    if liminal.get("projection", {}).get("side_effect_committed") is not False:
        raise TraceEvidenceBridgeError("LiminalDB projection must remain report-only")
    previous_event = "0" * 64
    parent_ref = None
    for expected_sequence, raw in enumerate(liminal.get("records", []), start=1):
        record = dict(raw)
        event_hash = record.pop("event_hash", None)
        if record.get("sequence") != expected_sequence:
            raise TraceEvidenceBridgeError("LiminalDB sequence mismatch")
        if record.get("previous_event_hash") != previous_event:
            raise TraceEvidenceBridgeError("LiminalDB event chain mismatch")
        if record.get("payload_digest") != _digest(record.get("payload")):
            raise TraceEvidenceBridgeError("LiminalDB payload digest mismatch")
        if expected_sequence == 1:
            if record.get("parent_ref") is not None:
                raise TraceEvidenceBridgeError("LiminalDB root parent must be null")
        elif record.get("parent_ref") != parent_ref:
            raise TraceEvidenceBridgeError("LiminalDB parent lineage mismatch")
        if event_hash != _digest(record):
            raise TraceEvidenceBridgeError("LiminalDB event hash mismatch")
        previous_event = event_hash
        parent_ref = record.get("record_ref")

    if receipt["source_package"]["case_id"] != EXPECTED_CASE_ID:
        raise TraceEvidenceBridgeError("receipt source case mismatch")
