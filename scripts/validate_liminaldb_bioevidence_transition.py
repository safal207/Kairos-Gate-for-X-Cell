#!/usr/bin/env python3
"""Fail-closed validator for Kairos Gate -> LiminalDB transition bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SHA_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_PIN = "ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d"
EXPECTED_KINDS = [
    "authorization",
    "observation",
    "observation",
    "response_integrity",
    "causal_audit",
    "continuity_snapshot",
]


def canonical_bytes(value: Any) -> bytes:
    """Serialize a JSON-compatible value into deterministic UTF-8 bytes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_ref(value: Any) -> str:
    """Return a lowercase sha256 reference over canonical JSON bytes."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def block(errors: list[str], message: str) -> None:
    """Append one stable fail-closed validation error."""
    errors.append(message)


def main() -> int:
    """Validate one preflight root bundle and return zero only for ACCEPT."""
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    args = parser.parse_args()

    path = Path(args.bundle)
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - parse failure is evidence
        print(
            json.dumps(
                {"verdict": "BLOCK", "errors": [f"invalid JSON: {type(exc).__name__}: {exc}"]},
                indent=2,
            )
        )
        return 1

    if data.get("schema_version") != "0.1.0":
        block(errors, "schema_version must be 0.1.0")
    if data.get("bridge_profile") != "org.kairos-gate.liminaldb-bioevidence-bridge.v0.1":
        block(errors, "bridge_profile mismatch")

    pin = data.get("liminaldb_pin", {})
    if pin.get("repository") != "safal207/LiminalDB":
        block(errors, "LiminalDB repository pin mismatch")
    if pin.get("commit") != EXPECTED_PIN:
        block(errors, "LiminalDB commit pin mismatch")
    if pin.get("event_schema") != "liminaldb.trustworthy-transition-event.v0.1":
        block(errors, "LiminalDB event schema mismatch")
    if pin.get("ledger_profile") != "org.liminaldb.trustworthy-transition-ledger.v0.1":
        block(errors, "LiminalDB ledger profile mismatch")

    if data.get("subject_id") != "GSE184241":
        block(errors, "subject_id must remain GSE184241")
    if data.get("action") != "GENEFORMER_RUNTIME_PREFLIGHT":
        block(errors, "action must remain runtime preflight")

    supersession = data.get("supersession")
    expected_root = {
        "relation": "ROOT",
        "predecessor_transition_id": None,
        "predecessor_authorization_ref": None,
    }
    if supersession != expected_root:
        block(errors, "runtime preflight must be a ROOT transition with null predecessor fields")
    predecessor_authorization_ref = (
        supersession.get("predecessor_authorization_ref") if isinstance(supersession, dict) else None
    )

    bundle_hash = data.get("bundle_sha256")
    without_hash = dict(data)
    without_hash.pop("bundle_sha256", None)
    if bundle_hash != sha256_ref(without_hash):
        block(errors, "bundle_sha256 mismatch")

    records = data.get("records")
    payloads = data.get("payloads")
    actual_kinds = [record.get("kind") for record in records if isinstance(record, dict)] if isinstance(records, list) else []
    if not isinstance(records, list) or actual_kinds != EXPECTED_KINDS:
        block(
            errors,
            "record chain must be authorization -> observation -> observation -> response_integrity -> causal_audit -> continuity_snapshot",
        )
        records = records if isinstance(records, list) else []
    if not isinstance(payloads, dict):
        block(errors, "payloads must be an object")
        payloads = {}

    refs: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            block(errors, f"record {index} is not an object")
            continue
        record_ref = record.get("record_ref")
        payload_digest = record.get("payload_digest")
        if not isinstance(record_ref, str) or not SHA_REF.fullmatch(record_ref):
            block(errors, f"record {index} has invalid record_ref")
            continue
        refs.append(record_ref)
        if not isinstance(payload_digest, str) or not SHA_REF.fullmatch(payload_digest):
            block(errors, f"record {index} has invalid payload_digest")
        payload = payloads.get(record_ref)
        if not isinstance(payload, dict):
            block(errors, f"record {index} has no matching payload")
            continue
        if payload_digest != sha256_ref(payload):
            block(errors, f"record {index} payload_digest mismatch")
        expected_ref = sha256_ref(
            {
                "transition_id": data.get("transition_id"),
                "subject_id": data.get("subject_id"),
                "kind": record.get("kind"),
                "payload_digest": payload_digest,
            }
        )
        if record_ref != expected_ref:
            block(errors, f"record {index} record_ref mismatch")
        if record.get("side_effect_committed") is not False:
            block(errors, f"record {index} must not commit a side effect")
        if not isinstance(record.get("captured_at_ms"), int) or record.get("captured_at_ms", -1) < 0:
            block(errors, f"record {index} has invalid captured_at_ms")
        links = record.get("links")
        if not isinstance(links, dict):
            block(errors, f"record {index} links missing")
        elif predecessor_authorization_ref is not None and links.get("authorization_ref") == predecessor_authorization_ref:
            block(errors, f"record {index} must not use predecessor authorization as current authority")

    if len(refs) != len(set(refs)):
        block(errors, "record references must be globally unique")
    if set(payloads) != set(refs):
        block(errors, "payload key set must exactly equal record references")

    if len(records) == 6 and all(isinstance(record, dict) for record in records):
        auth, obs_a, obs_b, integrity, causal, continuity = records
        auth_ref = auth.get("record_ref")
        obs_refs = sorted([obs_a.get("record_ref"), obs_b.get("record_ref")])
        if auth.get("links") != {
            "authorization_ref": None,
            "observation_refs": [],
            "response_integrity_ref": None,
            "causal_audit_ref": None,
            "previous_continuity_ref": None,
        }:
            block(errors, "authorization links must be empty")
        for name, observation in [("benchmark observation", obs_a), ("runtime observation", obs_b)]:
            links = observation.get("links", {})
            if links.get("authorization_ref") != auth_ref or links.get("observation_refs") != []:
                block(errors, f"{name} must reference only current authorization")
        integrity_links = integrity.get("links", {})
        if integrity_links.get("authorization_ref") != auth_ref:
            block(errors, "response_integrity authorization link mismatch")
        if integrity_links.get("observation_refs") != obs_refs:
            block(errors, "response_integrity must bind exact sorted observation set")
        integrity_payload = payloads.get(integrity.get("record_ref"), {})
        if integrity_payload.get("verdict") != "VERIFIED" or integrity_payload.get("observation_refs") != obs_refs:
            block(errors, "response integrity payload must verify exact observation set")
        causal_links = causal.get("links", {})
        if causal_links.get("authorization_ref") != auth_ref:
            block(errors, "causal_audit authorization link mismatch")
        if causal_links.get("observation_refs") != obs_refs:
            block(errors, "causal_audit observation set mismatch")
        if causal_links.get("response_integrity_ref") != integrity.get("record_ref"):
            block(errors, "causal_audit response_integrity link mismatch")
        continuity_links = continuity.get("links", {})
        if continuity_links.get("authorization_ref") != auth_ref:
            block(errors, "continuity authorization link mismatch")
        if continuity_links.get("observation_refs") != obs_refs:
            block(errors, "continuity observation set mismatch")
        if continuity_links.get("response_integrity_ref") != integrity.get("record_ref"):
            block(errors, "continuity response_integrity link mismatch")
        if continuity_links.get("causal_audit_ref") != causal.get("record_ref"):
            block(errors, "continuity causal_audit link mismatch")

        dimensions = continuity.get("dimensions")
        if not isinstance(dimensions, dict):
            block(errors, "continuity snapshot must carry all independent dimensions")
        else:
            required_dimensions = {
                "authority",
                "execution",
                "response_integrity",
                "causal_validity",
                "continuity_posture",
            }
            if set(dimensions) != required_dimensions:
                block(errors, "continuity dimension set mismatch")
            if dimensions.get("authority") != "VALID":
                block(errors, "preflight authority must be VALID")
            if dimensions.get("execution") not in {
                "OBSERVED_EXECUTED",
                "OBSERVED_BLOCKED",
                "OBSERVED_ERRORED",
            }:
                block(errors, "preflight execution state is invalid")
            if dimensions.get("response_integrity") != "VERIFIED":
                block(errors, "response integrity must be VERIFIED")
            if dimensions.get("causal_validity") != "NOT_EVALUATED":
                block(errors, "runtime preflight cannot establish causal validity")
            expected_posture = (
                "REPORT_ONLY" if dimensions.get("execution") == "OBSERVED_EXECUTED" else "BLOCKED"
            )
            if dimensions.get("continuity_posture") != expected_posture:
                block(errors, "continuity posture does not match preflight execution")

        authorization_payload = payloads.get(auth_ref, {})
        if authorization_payload.get("physical_execution_authorized") is not False:
            block(errors, "authorization must deny physical execution")
        if authorization_payload.get("production_write") is not False:
            block(errors, "authorization must deny production write")
        if authorization_payload.get("side_effect_authorized") is not False:
            block(errors, "authorization must deny side effects")

        runtime_payload = payloads.get(obs_b.get("record_ref"), {})
        runtime_boundary = runtime_payload.get("runtime_boundary", {})
        if runtime_payload.get("model_inference_executed") is not False:
            block(errors, "runtime preflight must not claim model inference")
        if runtime_payload.get("embedding_generated") is not False:
            block(errors, "runtime preflight must not claim embeddings")
        if runtime_payload.get("incremental_value_tested") is not False:
            block(errors, "runtime preflight must not claim incremental-value testing")
        for key in ["model_inference_executed", "embedding_generated", "incremental_value_tested"]:
            if runtime_boundary.get(key) is not False:
                block(errors, f"runtime boundary {key} must be false")

        causal_payload = payloads.get(causal.get("record_ref"), {})
        if causal_payload.get("causal_validity") != "NOT_EVALUATED":
            block(errors, "causal audit must remain NOT_EVALUATED")

        continuity_payload = payloads.get(continuity.get("record_ref"), {})
        for key in [
            "model_inference_executed",
            "embedding_generated",
            "production_write",
            "physical_execution_authorized",
        ]:
            if continuity_payload.get(key) is not False:
                block(errors, f"continuity payload {key} must be false")
        if continuity_payload.get("supersession_required_for_future_inference") is not True:
            block(errors, "future inference must require explicit supersession")
        if continuity_payload.get("current_authorization_ref") != auth_ref:
            block(errors, "continuity payload must identify the current authorization")

    claim_boundary = data.get("claim_boundary", {})
    for key in [
        "model_inference_executed",
        "embedding_generated",
        "incremental_value_established",
        "same_cell_prediction_established",
        "causal_effect_established",
        "clinical_utility_established",
        "physical_execution_authorized",
    ]:
        if claim_boundary.get(key) is not False:
            block(errors, f"claim boundary {key} must be false")

    storage = data.get("storage_boundary", {})
    if storage.get("temporary_ledger_only") is not True:
        block(errors, "ledger must remain temporary")
    for key in ["production_write", "external_submission", "deployment", "merge"]:
        if storage.get(key) is not False:
            block(errors, f"storage boundary {key} must be false")

    verdict = "ACCEPT" if not errors else "BLOCK"
    print(
        json.dumps(
            {"verdict": verdict, "bundle": str(path), "errors": errors},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
