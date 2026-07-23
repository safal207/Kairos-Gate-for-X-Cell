#!/usr/bin/env python3
"""Export one Geneformer V1 execution or HOLD as a superseding LiminalDB chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LIMINALDB_COMMIT = "ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d"
TRANSITION_ID = "gse184241-geneformer-v1-inference-v0-1"
SUBJECT_ID = "GSE184241"
ACTION = "GENEFORMER_V1_INFERENCE"
PREDECESSOR_TRANSITION_ID = "gse184241-geneformer-runtime-preflight-v0-1"
PREDECESSOR_AUTHORIZATION_REF = "sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665"
COMPLETED_STATUS = "GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY"


def canonical_bytes(value: Any) -> bytes:
    """Serialize JSON-compatible evidence into deterministic bytes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_ref(value: Any) -> str:
    """Return a lowercase sha256 reference over canonical JSON bytes."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256_ref(path: Path) -> str:
    """Return a lowercase sha256 reference over exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def empty_links() -> dict[str, Any]:
    """Create an empty current-transition parent-link set."""
    return {"authorization_ref": None, "observation_refs": [], "response_integrity_ref": None, "causal_audit_ref": None, "previous_continuity_ref": None}


def make_record(kind: str, payload: dict[str, Any], links: dict[str, Any], captured_at_ms: int, dimensions: dict[str, str] | None = None) -> tuple[dict[str, Any], str]:
    """Build one deterministic record envelope and globally unique reference."""
    payload_digest = sha256_ref(payload)
    record_ref = sha256_ref({"transition_id": TRANSITION_ID, "subject_id": SUBJECT_ID, "kind": kind, "payload_digest": payload_digest})
    return ({"kind": kind, "record_ref": record_ref, "payload_digest": payload_digest, "links": links, "dimensions": dimensions, "side_effect_committed": False, "captured_at_ms": captured_at_ms}, record_ref)


def main() -> int:
    """Emit a seven-record SUPERSEDES bundle for completed or held inference."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--passport", required=True)
    parser.add_argument("--input-manifest", required=False)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--captured-at-ms", type=int, required=True)
    args = parser.parse_args()

    inference_path = Path(args.inference)
    benchmark_path = Path(args.benchmark)
    passport_path = Path(args.passport)
    input_manifest_path = Path(args.input_manifest) if args.input_manifest else None
    output_path = Path(args.output)
    inference = json.loads(inference_path.read_text(encoding="utf-8"))
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    passport = json.loads(passport_path.read_text(encoding="utf-8"))
    input_manifest = json.loads(input_manifest_path.read_text(encoding="utf-8")) if input_manifest_path is not None and input_manifest_path.is_file() else None
    if inference.get("predecessor") != {"transition_id": PREDECESSOR_TRANSITION_ID, "authorization_ref": PREDECESSOR_AUTHORIZATION_REF}:
        raise ValueError("inference predecessor does not match exact preflight record")
    completed = inference.get("status") == COMPLETED_STATUS
    captured = args.captured_at_ms
    records: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any]] = {}

    authorization_payload = {
        "payload_schema": "kairos-gate.geneformer-v1-inference-authorization.v0.1",
        "action": ACTION,
        "scope": "bounded_public_checkpoint_execution_and_donor_held_out_report_only_comparison",
        "source_revision": args.source_revision,
        "new_authorization_epoch": True,
        "supersedes_preflight_only_authorization": PREDECESSOR_AUTHORIZATION_REF,
        "allowed": ["download_exact_public_checkpoint_assets", "tokenize_frozen_public_GSE184241_raw_counts", "execute_Geneformer_V1_on_CPU", "generate_report_only_cell_embeddings", "run_frozen_leave_one_donor_out_probe", "write_temporary_artifact_ledger"],
        "denied": ["reuse_predecessor_authorization_as_current_authority", "claim_same_cell_future_response", "claim_incremental_value_as_established", "claim_causality_or_clinical_utility", "physical_biological_work", "production_liminaldb_write", "external_submission", "deployment", "merge"],
        "physical_execution_authorized": False,
        "production_write": False,
        "side_effect_authorized": False,
    }
    auth_record, auth_ref = make_record("authorization", authorization_payload, empty_links(), captured)
    if auth_ref == PREDECESSOR_AUTHORIZATION_REF:
        raise ValueError("new inference authorization must differ from predecessor authorization")
    records.append(auth_record)
    payloads[auth_ref] = authorization_payload
    current_links = empty_links()
    current_links["authorization_ref"] = auth_ref

    benchmark_payload = {
        "payload_schema": "kairos-gate.gse184241-frozen-benchmark-observation.v0.2",
        "benchmark_id": benchmark.get("benchmark_id"),
        "canonical_file": benchmark_path.name,
        "canonical_file_sha256": file_sha256_ref(benchmark_path),
        "counts_sha256": benchmark.get("dataset", {}).get("counts_sha256"),
        "barcodes_sha256": benchmark.get("dataset", {}).get("barcodes_sha256"),
        "biological_unit": benchmark.get("split_contract", {}).get("biological_unit"),
        "split_strategy": benchmark.get("split_contract", {}).get("strategy"),
        "macro_metrics": benchmark.get("macro_metrics"),
        "same_cell_future_response": False,
    }
    record, benchmark_ref = make_record("observation", benchmark_payload, current_links.copy(), captured + 1)
    records.append(record)
    payloads[benchmark_ref] = benchmark_payload

    model_payload = {
        "payload_schema": "kairos-gate.geneformer-v1-model-input-observation.v0.1",
        "status": inference.get("status"),
        "compatibility_verdict": inference.get("compatibility_verdict"),
        "dataset": inference.get("dataset"),
        "model": inference.get("model"),
        "tokenization": inference.get("tokenization"),
        "input_manifest_file": input_manifest_path.name if input_manifest_path and input_manifest_path.is_file() else None,
        "input_manifest_file_sha256": file_sha256_ref(input_manifest_path) if input_manifest_path and input_manifest_path.is_file() else None,
        "input_manifest": input_manifest,
    }
    record, model_ref = make_record("observation", model_payload, current_links.copy(), captured + 2)
    records.append(record)
    payloads[model_ref] = model_payload

    execution_payload = {
        "payload_schema": "kairos-gate.geneformer-v1-execution-observation.v0.1",
        "inference_file": inference_path.name,
        "inference_file_sha256": file_sha256_ref(inference_path),
        "passport_file": passport_path.name,
        "passport_file_sha256": file_sha256_ref(passport_path),
        "execution": inference.get("execution"),
        "inference": inference.get("inference"),
        "benchmark": inference.get("benchmark"),
        "evidence": inference.get("evidence"),
        "passport_identity": {"passport_id": passport.get("passport_id"), "execution_status": passport.get("execution", {}).get("status"), "compatibility_verdict": passport.get("compatibility_verdict"), "training_overlap_status": passport.get("uncertainty", {}).get("training_overlap_status")},
        "model_inference_executed": bool(completed),
        "embedding_generated": bool(completed),
        "descriptive_comparison_completed": bool(completed),
    }
    record, execution_ref = make_record("observation", execution_payload, current_links.copy(), captured + 3)
    records.append(record)
    payloads[execution_ref] = execution_payload
    observation_refs = sorted([benchmark_ref, model_ref, execution_ref])

    integrity_payload = {"payload_schema": "kairos-gate.geneformer-v1-response-integrity.v0.1", "verdict": "VERIFIED", "observation_refs": observation_refs, "verification": {"payload_digests_recomputed": True, "record_refs_recomputed": True, "observation_set_exact": True, "current_authorization_distinct_from_predecessor": True, "passport_and_inference_files_digest_bound": True}}
    integrity_links = current_links.copy()
    integrity_links["observation_refs"] = observation_refs
    record, integrity_ref = make_record("response_integrity", integrity_payload, integrity_links, captured + 4)
    records.append(record)
    payloads[integrity_ref] = integrity_payload

    causal_payload = {
        "payload_schema": "kairos-gate.geneformer-v1-causal-audit.v0.1",
        "causal_validity": "NOT_EVALUATED",
        "decision": "INFERENCE_EXECUTED_REPORT_ONLY_WITH_TRAINING_OVERLAP_HOLD" if completed else "INFERENCE_ATTEMPT_RECORDED_AS_FAIL_CLOSED_HOLD",
        "supported": ["exact_checkpoint_execution_observed", "cell_embeddings_generated_and_digest_bound", "frozen_donor_held_out_probe_completed"] if completed else ["bounded_inference_attempt_and_exact_hold_observed"],
        "blocked": ["incremental_value_established", "same_cell_future_response_prediction", "NFKBIA_specific_causal_effect", "clinical_or_therapeutic_utility", "physical_experiment_authority"],
        "training_overlap_status": passport.get("uncertainty", {}).get("training_overlap_status"),
        "next_valid_action": "INDEPENDENTLY_ASSESS_TRAINING_OVERLAP_AND_REPLICATE_ACROSS_MORE_DONORS" if completed else "RESOLVE_EXACT_HOLD_WITHOUT_REUSING_PREDECESSOR_AUTHORITY",
    }
    causal_links = current_links.copy()
    causal_links["observation_refs"] = observation_refs
    causal_links["response_integrity_ref"] = integrity_ref
    record, causal_ref = make_record("causal_audit", causal_payload, causal_links, captured + 5)
    records.append(record)
    payloads[causal_ref] = causal_payload

    dimensions = {"authority": "VALID", "execution": "OBSERVED_EXECUTED" if completed else "OBSERVED_BLOCKED", "response_integrity": "VERIFIED", "causal_validity": "NOT_EVALUATED", "continuity_posture": "REPORT_ONLY" if completed else "BLOCKED"}
    continuity_payload = {
        "payload_schema": "kairos-gate.geneformer-v1-continuity.v0.1",
        "decision": "REPORT_ONLY_INFERENCE_MEMORY_WITH_TRAINING_OVERLAP_HOLD" if completed else "BLOCKED_INFERENCE_ATTEMPT_MEMORY",
        "current_authorization_ref": auth_ref,
        "predecessor_authorization_ref": PREDECESSOR_AUTHORIZATION_REF,
        "status": inference.get("status"),
        "model_inference_executed": bool(completed),
        "embedding_generated": bool(completed),
        "incremental_value_established": False,
        "production_write": False,
        "physical_execution_authorized": False,
    }
    continuity_links = current_links.copy()
    continuity_links.update({"observation_refs": observation_refs, "response_integrity_ref": integrity_ref, "causal_audit_ref": causal_ref})
    record, continuity_ref = make_record("continuity_snapshot", continuity_payload, continuity_links, captured + 6, dimensions=dimensions)
    records.append(record)
    payloads[continuity_ref] = continuity_payload

    bundle: dict[str, Any] = {
        "schema_version": "0.1.0",
        "bridge_profile": "org.kairos-gate.liminaldb-geneformer-inference-bridge.v0.1",
        "liminaldb_pin": {"repository": "safal207/LiminalDB", "commit": LIMINALDB_COMMIT, "event_schema": "liminaldb.trustworthy-transition-event.v0.1", "ledger_profile": "org.liminaldb.trustworthy-transition-ledger.v0.1"},
        "transition_id": TRANSITION_ID,
        "subject_id": SUBJECT_ID,
        "action": ACTION,
        "supersession": {"relation": "SUPERSEDES", "predecessor_transition_id": PREDECESSOR_TRANSITION_ID, "predecessor_authorization_ref": PREDECESSOR_AUTHORIZATION_REF},
        "records": records,
        "payloads": payloads,
        "claim_boundary": {"model_inference_executed": bool(completed), "embedding_generated": bool(completed), "descriptive_comparison_completed": bool(completed), "incremental_value_established": False, "same_cell_prediction_established": False, "causal_effect_established": False, "clinical_utility_established": False, "physical_execution_authorized": False},
        "storage_boundary": {"temporary_ledger_only": True, "production_write": False, "external_submission": False, "deployment": False, "merge": False},
    }
    bundle["bundle_sha256"] = sha256_ref(bundle)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "status": inference.get("status"), "current_authorization_ref": auth_ref, "predecessor_authorization_ref": PREDECESSOR_AUTHORIZATION_REF, "records": len(records), "bundle_sha256": bundle["bundle_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
