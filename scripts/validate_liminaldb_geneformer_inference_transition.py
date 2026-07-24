#!/usr/bin/env python3
"""Fail-closed validator for superseding Geneformer inference LiminalDB bundles."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_PIN = "ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d"
EXPECTED_PREDECESSOR = "gse184241-geneformer-runtime-preflight-v0-1"
EXPECTED_PREDECESSOR_AUTH = (
    "sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665"
)
EXPECTED_KINDS = [
    "authorization",
    "observation",
    "observation",
    "observation",
    "response_integrity",
    "causal_audit",
    "continuity_snapshot",
]


def canonical_bytes(value: Any) -> bytes:
    """Serialize JSON-compatible evidence into deterministic bytes."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_ref(value: Any) -> str:
    """Return a lowercase sha256 reference over canonical JSON bytes."""
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def block(errors: list[str], message: str) -> None:
    """Append one stable fail-closed validation error."""
    errors.append(message)


def main() -> int:
    """Validate one completed or held inference transition bundle."""
    if len(sys.argv) != 2:
        print("usage: validate_liminaldb_geneformer_inference_transition.py BUNDLE.json")
        return 2

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"verdict": "BLOCK", "errors": [f"cannot load bundle: {exc}"]},
                indent=2,
            )
        )
        return 1

    errors: list[str] = []
    if data.get("schema_version") != "0.1.0":
        block(errors, "schema_version must be 0.1.0")
    if data.get("bridge_profile") != (
        "org.kairos-gate.liminaldb-geneformer-inference-bridge.v0.1"
    ):
        block(errors, "bridge profile mismatch")
    if data.get("transition_id") != "gse184241-geneformer-v1-inference-v0-1":
        block(errors, "transition_id mismatch")
    if data.get("subject_id") != "GSE184241":
        block(errors, "subject_id mismatch")
    if data.get("action") != "GENEFORMER_V1_INFERENCE":
        block(errors, "action mismatch")

    expected_pin = {
        "repository": "safal207/LiminalDB",
        "commit": EXPECTED_PIN,
        "event_schema": "liminaldb.trustworthy-transition-event.v0.1",
        "ledger_profile": "org.liminaldb.trustworthy-transition-ledger.v0.1",
    }
    if data.get("liminaldb_pin", {}) != expected_pin:
        block(errors, "exact LiminalDB compatibility pin mismatch")

    expected_supersession = {
        "relation": "SUPERSEDES",
        "predecessor_transition_id": EXPECTED_PREDECESSOR,
        "predecessor_authorization_ref": EXPECTED_PREDECESSOR_AUTH,
    }
    if data.get("supersession", {}) != expected_supersession:
        block(errors, "exact supersession ancestry mismatch")

    bundle_hash = data.get("bundle_sha256")
    unhashed = dict(data)
    unhashed.pop("bundle_sha256", None)
    if bundle_hash != sha256_ref(unhashed):
        block(errors, "bundle_sha256 mismatch")

    records = data.get("records") if isinstance(data.get("records"), list) else []
    payloads = data.get("payloads") if isinstance(data.get("payloads"), dict) else {}
    record_kinds = [
        record.get("kind") for record in records if isinstance(record, dict)
    ]
    if record_kinds != EXPECTED_KINDS:
        block(
            errors,
            "record chain must contain authorization, three observations, "
            "integrity, causal audit and continuity",
        )

    refs: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            block(errors, f"record {index} is not an object")
            continue

        record_ref = record.get("record_ref")
        digest = record.get("payload_digest")
        if not isinstance(record_ref, str) or not SHA_REF.fullmatch(record_ref):
            block(errors, f"record {index} has invalid record_ref")
            continue

        refs.append(record_ref)
        if not isinstance(digest, str) or not SHA_REF.fullmatch(digest):
            block(errors, f"record {index} has invalid payload_digest")

        payload = payloads.get(record_ref)
        if not isinstance(payload, dict):
            block(errors, f"record {index} has no matching payload")
            continue
        if digest != sha256_ref(payload):
            block(errors, f"record {index} payload digest mismatch")

        expected_ref = sha256_ref(
            {
                "transition_id": data.get("transition_id"),
                "subject_id": data.get("subject_id"),
                "kind": record.get("kind"),
                "payload_digest": digest,
            }
        )
        if record_ref != expected_ref:
            block(errors, f"record {index} record_ref mismatch")
        if record.get("side_effect_committed") is not False:
            block(errors, f"record {index} must not commit a side effect")
        captured_at_ms = record.get("captured_at_ms")
        if not isinstance(captured_at_ms, int) or captured_at_ms < 0:
            block(errors, f"record {index} captured_at_ms is invalid")

    if len(refs) != len(set(refs)):
        block(errors, "record refs must be globally unique")
    if set(payloads) != set(refs):
        block(errors, "payload key set must equal record refs exactly")

    if len(records) == 7 and all(isinstance(record, dict) for record in records):
        auth, obs_a, obs_b, obs_c, integrity, causal, continuity = records
        auth_ref = auth.get("record_ref")
        if auth_ref == EXPECTED_PREDECESSOR_AUTH:
            block(
                errors,
                "current inference authorization must differ from predecessor authorization",
            )

        expected_empty_links = {
            "authorization_ref": None,
            "observation_refs": [],
            "response_integrity_ref": None,
            "causal_audit_ref": None,
            "previous_continuity_ref": None,
        }
        if auth.get("links") != expected_empty_links:
            block(errors, "authorization record links must be empty")

        observation_refs = sorted(
            [obs_a.get("record_ref"), obs_b.get("record_ref"), obs_c.get("record_ref")]
        )
        for index, observation in enumerate([obs_a, obs_b, obs_c], start=1):
            links = observation.get("links", {})
            if links.get("authorization_ref") != auth_ref:
                block(errors, f"observation {index} must reference current authorization")
            if links.get("authorization_ref") == EXPECTED_PREDECESSOR_AUTH:
                block(errors, f"observation {index} illegally uses predecessor authorization")
            if links.get("observation_refs") != []:
                block(errors, f"observation {index} observation_refs must be empty")

        integrity_links = integrity.get("links", {})
        if integrity_links.get("authorization_ref") != auth_ref:
            block(errors, "response integrity must reference current authorization")
        if integrity_links.get("observation_refs") != observation_refs:
            block(errors, "response integrity must bind exact sorted observation set")

        integrity_payload = payloads.get(integrity.get("record_ref"), {})
        if (
            integrity_payload.get("verdict") != "VERIFIED"
            or integrity_payload.get("observation_refs") != observation_refs
        ):
            block(errors, "response integrity payload mismatch")

        causal_links = causal.get("links", {})
        if causal_links.get("authorization_ref") != auth_ref:
            block(errors, "causal audit must reference current authorization")
        if causal_links.get("observation_refs") != observation_refs:
            block(errors, "causal audit observation set mismatch")
        if causal_links.get("response_integrity_ref") != integrity.get("record_ref"):
            block(errors, "causal audit response integrity reference mismatch")
        causal_payload = payloads.get(causal.get("record_ref"), {})
        if causal_payload.get("causal_validity") != "NOT_EVALUATED":
            block(errors, "causal validity must remain NOT_EVALUATED")

        continuity_links = continuity.get("links", {})
        if continuity_links.get("authorization_ref") != auth_ref:
            block(errors, "continuity must reference current authorization")
        if continuity_links.get("observation_refs") != observation_refs:
            block(errors, "continuity observation set mismatch")
        if continuity_links.get("response_integrity_ref") != integrity.get("record_ref"):
            block(errors, "continuity response integrity reference mismatch")
        if continuity_links.get("causal_audit_ref") != causal.get("record_ref"):
            block(errors, "continuity causal audit reference mismatch")

        dimensions = (
            continuity.get("dimensions")
            if isinstance(continuity.get("dimensions"), dict)
            else {}
        )
        expected_dimension_keys = {
            "authority",
            "execution",
            "response_integrity",
            "causal_validity",
            "continuity_posture",
        }
        if set(dimensions) != expected_dimension_keys:
            block(errors, "continuity dimension set mismatch")
        if dimensions.get("authority") != "VALID":
            block(errors, "current inference authority must be VALID")
        if dimensions.get("response_integrity") != "VERIFIED":
            block(errors, "response integrity dimension must be VERIFIED")
        if dimensions.get("causal_validity") != "NOT_EVALUATED":
            block(errors, "causal validity dimension must be NOT_EVALUATED")

        auth_payload = payloads.get(auth_ref, {})
        if auth_payload.get("new_authorization_epoch") is not True:
            block(errors, "inference must create a new authorization epoch")
        if (
            auth_payload.get("supersedes_preflight_only_authorization")
            != EXPECTED_PREDECESSOR_AUTH
        ):
            block(errors, "authorization payload predecessor mismatch")
        for key in [
            "physical_execution_authorized",
            "production_write",
            "side_effect_authorized",
        ]:
            if auth_payload.get(key) is not False:
                block(errors, f"authorization payload {key} must be false")

        execution_payload = payloads.get(obs_c.get("record_ref"), {})
        completed = execution_payload.get("model_inference_executed") is True
        if execution_payload.get("embedding_generated") is not completed:
            block(errors, "embedding generation must match inference execution")
        if execution_payload.get("descriptive_comparison_completed") is not completed:
            block(errors, "descriptive comparison must match inference execution")
        expected_execution = "OBSERVED_EXECUTED" if completed else "OBSERVED_BLOCKED"
        if dimensions.get("execution") != expected_execution:
            block(errors, "execution dimension does not match evidence")
        expected_posture = "REPORT_ONLY" if completed else "BLOCKED"
        if dimensions.get("continuity_posture") != expected_posture:
            block(errors, "continuity posture does not match evidence")

        continuity_payload = payloads.get(continuity.get("record_ref"), {})
        if continuity_payload.get("current_authorization_ref") != auth_ref:
            block(errors, "continuity payload current authorization mismatch")
        if (
            continuity_payload.get("predecessor_authorization_ref")
            != EXPECTED_PREDECESSOR_AUTH
        ):
            block(errors, "continuity payload predecessor authorization mismatch")
        if continuity_payload.get("incremental_value_established") is not False:
            block(errors, "continuity cannot establish incremental value")
        for key in ["production_write", "physical_execution_authorized"]:
            if continuity_payload.get(key) is not False:
                block(errors, f"continuity payload {key} must be false")

        claims = data.get("claim_boundary", {})
        for key in [
            "model_inference_executed",
            "embedding_generated",
            "descriptive_comparison_completed",
        ]:
            if claims.get(key) is not completed:
                block(errors, f"claim boundary {key} must match execution evidence")

    claims = data.get("claim_boundary", {})
    for key in [
        "incremental_value_established",
        "same_cell_prediction_established",
        "causal_effect_established",
        "clinical_utility_established",
        "physical_execution_authorized",
    ]:
        if claims.get(key) is not False:
            block(errors, f"claim boundary {key} must remain false")

    storage = data.get("storage_boundary", {})
    if storage.get("temporary_ledger_only") is not True:
        block(errors, "ledger storage must remain temporary")
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
