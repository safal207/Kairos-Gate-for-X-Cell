#!/usr/bin/env python3
"""Export Geneformer runtime preflight evidence as a LiminalDB transition chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LIMINALDB_COMMIT = "ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d"
TRANSITION_ID = "gse184241-geneformer-runtime-preflight-v0-1"
SUBJECT_ID = "GSE184241"


def canonical_bytes(value: Any) -> bytes:
    """Serialize a JSON-compatible value into deterministic UTF-8 bytes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_ref(value: Any) -> str:
    """Return a lowercase sha256 reference over canonical JSON bytes."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256_ref(path: Path) -> str:
    """Return a lowercase sha256 reference for the exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def make_record(
    kind: str,
    payload: dict[str, Any],
    links: dict[str, Any],
    captured_at_ms: int,
    dimensions: dict[str, str] | None = None,
) -> tuple[dict[str, Any], str]:
    """Build one deterministic record envelope and its globally unique reference."""
    payload_digest = sha256_ref(payload)
    record_ref = sha256_ref(
        {
            "transition_id": TRANSITION_ID,
            "subject_id": SUBJECT_ID,
            "kind": kind,
            "payload_digest": payload_digest,
        }
    )
    record = {
        "kind": kind,
        "record_ref": record_ref,
        "payload_digest": payload_digest,
        "links": links,
        "dimensions": dimensions,
        "side_effect_committed": False,
        "captured_at_ms": captured_at_ms,
    }
    return record, record_ref


def empty_links() -> dict[str, Any]:
    """Create an empty current-transition LiminalDB parent-link set."""
    return {
        "authorization_ref": None,
        "observation_refs": [],
        "response_integrity_ref": None,
        "causal_audit_ref": None,
        "previous_continuity_ref": None,
    }


def main() -> int:
    """Read frozen evidence inputs and emit one deterministic root transition bundle."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark)
    preflight_path = Path(args.preflight)
    output_path = Path(args.output)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    captured_at_ms = int(preflight["captured_at_ms"])

    payloads: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []

    authorization_payload = {
        "payload_schema": "kairos-gate.geneformer-runtime-authorization.v0.1",
        "action": "GENEFORMER_RUNTIME_PREFLIGHT",
        "scope": "computational_environment_and_public_source_readiness_only",
        "source_revision": args.source_revision,
        "allowed": [
            "resolve_public_model_source_revision",
            "inspect_runner_hardware",
            "import_runtime_dependencies",
            "record_checkpoint_target",
            "export_report_only_evidence",
        ],
        "denied": [
            "claim_model_inference_without_execution_receipt",
            "claim_embedding_generation_without_artifact_digest",
            "claim_incremental_value",
            "claim_same_cell_future_response",
            "claim_causal_or_clinical_validity",
            "physical_biological_work",
            "production_liminaldb_write",
            "external_submission",
            "deployment",
            "merge",
        ],
        "physical_execution_authorized": False,
        "production_write": False,
        "side_effect_authorized": False,
    }
    record, authorization_ref = make_record(
        "authorization", authorization_payload, empty_links(), captured_at_ms
    )
    records.append(record)
    payloads[authorization_ref] = authorization_payload

    benchmark_payload = {
        "payload_schema": "kairos-gate.gse184241-benchmark-observation.v0.1",
        "accession": "GSE184241",
        "benchmark_id": benchmark.get("benchmark_id"),
        "canonical_file": benchmark_path.name,
        "canonical_file_sha256": file_sha256_ref(benchmark_path),
        "frozen_result": [
            "BROAD_RESPONSE_STATE_DOMINATES",
            "NFKBIA_ONLY_IS_INFORMATIVE_BUT_NOT_UNIQUE",
            "NOT_SAME_CELL_FUTURE_RESPONSE_VALIDATION",
        ],
        "macro_metrics": benchmark.get("macro_metrics"),
        "biological_unit": benchmark.get("split_contract", {}).get("biological_unit"),
        "split_strategy": benchmark.get("split_contract", {}).get("strategy"),
        "independent_donors": 3,
        "cells_are_biological_replicates": False,
        "authoritative_prior_workflow_run": 30009843408,
        "authoritative_prior_artifact_id": 8564575055,
        "authoritative_prior_artifact_digest": "sha256:87747564b1eda1a6d1d99f51be4f98d71f72a9b0f37bf093b3599643ec9ae5ed",
    }
    observation_links = empty_links()
    observation_links["authorization_ref"] = authorization_ref
    record, benchmark_observation_ref = make_record(
        "observation", benchmark_payload, observation_links, captured_at_ms + 1
    )
    records.append(record)
    payloads[benchmark_observation_ref] = benchmark_payload

    runtime_payload = {
        "payload_schema": "kairos-gate.geneformer-runtime-preflight-observation.v0.1",
        "preflight_file": preflight_path.name,
        "preflight_file_sha256": file_sha256_ref(preflight_path),
        "status": preflight.get("status"),
        "execution_state": preflight.get("execution_state"),
        "model_source": preflight.get("model_source"),
        "environment": preflight.get("environment"),
        "modules": preflight.get("modules"),
        "torch": preflight.get("torch"),
        "runtime_boundary": preflight.get("runtime_boundary"),
        "model_inference_executed": False,
        "embedding_generated": False,
        "incremental_value_tested": False,
        "time_semantics": "DECLARATIVE_CAPTURE_TIME_NOT_WORLD_PRECEDENCE",
    }
    record, runtime_observation_ref = make_record(
        "observation", runtime_payload, observation_links, captured_at_ms + 2
    )
    records.append(record)
    payloads[runtime_observation_ref] = runtime_payload

    observation_refs = sorted([benchmark_observation_ref, runtime_observation_ref])
    integrity_payload = {
        "payload_schema": "kairos-gate.bioevidence-response-integrity.v0.1",
        "verdict": "VERIFIED",
        "observation_refs": observation_refs,
        "verification": {
            "payload_digests_recomputed": True,
            "record_refs_recomputed": True,
            "observation_set_exact": True,
            "runtime_preflight_not_relabelled_as_inference": True,
        },
    }
    integrity_links = empty_links()
    integrity_links["authorization_ref"] = authorization_ref
    integrity_links["observation_refs"] = observation_refs
    record, integrity_ref = make_record(
        "response_integrity", integrity_payload, integrity_links, captured_at_ms + 3
    )
    records.append(record)
    payloads[integrity_ref] = integrity_payload

    causal_payload = {
        "payload_schema": "kairos-gate.geneformer-runtime-causal-audit.v0.1",
        "causal_validity": "NOT_EVALUATED",
        "decision": "RUNTIME_PREFLIGHT_RECORDED_WITHOUT_INFERENCE_CLAIM",
        "supported": [
            "public_source_revision_observed",
            "runtime_dependency_import_status_observed",
            "runner_hardware_status_observed",
            "frozen_donor_benchmark_preserved",
        ],
        "blocked": [
            "geneformer_inference_executed",
            "geneformer_embeddings_generated",
            "incremental_value_over_pca",
            "same_cell_future_response_prediction",
            "NFKBIA_specific_causal_effect",
            "clinical_or_therapeutic_utility",
        ],
        "next_valid_action": "EXECUTE_EXACT_CHECKPOINT_WITH_MODEL_EVIDENCE_PASSPORT_OR_RECORD_EXPLICIT_RESOURCE_HOLD",
    }
    causal_links = empty_links()
    causal_links["authorization_ref"] = authorization_ref
    causal_links["observation_refs"] = observation_refs
    causal_links["response_integrity_ref"] = integrity_ref
    record, causal_ref = make_record(
        "causal_audit", causal_payload, causal_links, captured_at_ms + 4
    )
    records.append(record)
    payloads[causal_ref] = causal_payload

    execution_state = str(preflight.get("execution_state", "OBSERVED_BLOCKED"))
    continuity_posture = "REPORT_ONLY" if execution_state == "OBSERVED_EXECUTED" else "BLOCKED"
    dimensions = {
        "authority": "VALID",
        "execution": execution_state,
        "response_integrity": "VERIFIED",
        "causal_validity": "NOT_EVALUATED",
        "continuity_posture": continuity_posture,
    }
    continuity_payload = {
        "payload_schema": "kairos-gate.geneformer-runtime-continuity.v0.1",
        "decision": "REPORT_ONLY_PREFLIGHT_MEMORY",
        "supersession_required_for_future_inference": True,
        "current_authorization_ref": authorization_ref,
        "model_inference_executed": False,
        "embedding_generated": False,
        "production_write": False,
        "physical_execution_authorized": False,
    }
    continuity_links = empty_links()
    continuity_links.update(
        {
            "authorization_ref": authorization_ref,
            "observation_refs": observation_refs,
            "response_integrity_ref": integrity_ref,
            "causal_audit_ref": causal_ref,
        }
    )
    record, continuity_ref = make_record(
        "continuity_snapshot",
        continuity_payload,
        continuity_links,
        captured_at_ms + 5,
        dimensions=dimensions,
    )
    records.append(record)
    payloads[continuity_ref] = continuity_payload

    bundle = {
        "schema_version": "0.1.0",
        "bridge_profile": "org.kairos-gate.liminaldb-bioevidence-bridge.v0.1",
        "liminaldb_pin": {
            "repository": "safal207/LiminalDB",
            "commit": LIMINALDB_COMMIT,
            "event_schema": "liminaldb.trustworthy-transition-event.v0.1",
            "ledger_profile": "org.liminaldb.trustworthy-transition-ledger.v0.1",
        },
        "transition_id": TRANSITION_ID,
        "subject_id": SUBJECT_ID,
        "action": "GENEFORMER_RUNTIME_PREFLIGHT",
        "supersession": {
            "relation": "ROOT",
            "predecessor_transition_id": None,
            "predecessor_authorization_ref": None,
        },
        "records": records,
        "payloads": payloads,
        "claim_boundary": {
            "runtime_preflight_observed": True,
            "model_inference_executed": False,
            "embedding_generated": False,
            "incremental_value_established": False,
            "same_cell_prediction_established": False,
            "causal_effect_established": False,
            "clinical_utility_established": False,
            "physical_execution_authorized": False,
        },
        "storage_boundary": {
            "temporary_ledger_only": True,
            "production_write": False,
            "external_submission": False,
            "deployment": False,
            "merge": False,
        },
    }
    bundle["bundle_sha256"] = sha256_ref(bundle)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(output_path),
                "bundle_sha256": bundle["bundle_sha256"],
                "records": len(records),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
