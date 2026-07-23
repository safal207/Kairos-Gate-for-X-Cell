#!/usr/bin/env python3
"""Validate experimental-unit audit records with fail-closed policy checks.

This validator intentionally uses only the Python standard library so the
contract can run in minimal CI environments.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "study_id",
    "audit_scope",
    "source_identity",
    "resolved_experimental_unit",
    "technical_hierarchy",
    "independence_status",
    "unresolved_metadata",
    "pseudoreplication_findings",
    "admissible_analyses",
    "claim_firewall",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}

VERDICTS = {"ACCEPT", "ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}
CLAIM_STATUSES = {
    "supported",
    "supported_with_limits",
    "not_established",
    "blocked",
}
CLAIM_KEYS = {
    "descriptive",
    "association",
    "prediction",
    "generalization",
    "causal",
    "tissue",
    "clinical_therapeutic",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("audit root must be a JSON object")
    return value


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)

    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(record.get("overall_verdict") in VERDICTS, "unknown overall_verdict", errors)

    source = record.get("source_identity", {})
    require(isinstance(source, dict), "source_identity must be an object", errors)
    if isinstance(source, dict):
        require(bool(source.get("accession")), "source_identity.accession is required", errors)
        refs = source.get("evidence_refs")
        require(isinstance(refs, list) and len(refs) > 0, "at least one evidence_ref is required", errors)

    resolved = record.get("resolved_experimental_unit", {})
    require(isinstance(resolved, dict), "resolved_experimental_unit must be an object", errors)
    if isinstance(resolved, dict):
        require(
            resolved.get("status") in {"established", "partially_established", "not_established"},
            "invalid resolved_experimental_unit.status",
            errors,
        )
        require(
            resolved.get("evidence_level") in {"F0", "F1", "F2", "F3", "F4", "F5"},
            "invalid resolved_experimental_unit.evidence_level",
            errors,
        )

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_only", "mode must be computational_only", errors)
        require(
            safety.get("physical_biology_authorized") is False,
            "physical_biology_authorized must be false",
            errors,
        )

    firewall = record.get("claim_firewall", {})
    require(isinstance(firewall, dict), "claim_firewall must be an object", errors)
    if isinstance(firewall, dict):
        missing_claims = sorted(CLAIM_KEYS - firewall.keys())
        require(not missing_claims, f"missing claim firewall entries: {missing_claims}", errors)
        for key in CLAIM_KEYS & firewall.keys():
            item = firewall[key]
            require(isinstance(item, dict), f"claim_firewall.{key} must be an object", errors)
            if isinstance(item, dict):
                require(
                    item.get("status") in CLAIM_STATUSES,
                    f"claim_firewall.{key}.status is invalid",
                    errors,
                )
                require(bool(item.get("reason")), f"claim_firewall.{key}.reason is required", errors)

    independence = record.get("independence_status", {})
    resolved_status = resolved.get("status") if isinstance(resolved, dict) else None
    biological_status = independence.get("biological_independence") if isinstance(independence, dict) else None

    # Fail-closed invariants.
    if resolved_status != "established" or biological_status != "established":
        require(
            record.get("overall_verdict") != "ACCEPT",
            "ACCEPT is forbidden when biological independence is not established",
            errors,
        )
        if isinstance(firewall, dict):
            for key in ("generalization", "causal", "tissue", "clinical_therapeutic"):
                status = firewall.get(key, {}).get("status") if isinstance(firewall.get(key), dict) else None
                require(
                    status in {"not_established", "blocked"},
                    f"{key} claim must be not_established or blocked without biological independence",
                    errors,
                )

    if isinstance(independence, dict) and independence.get("plate_independence") == "contradicted":
        analyses = record.get("admissible_analyses", [])
        require(isinstance(analyses, list), "admissible_analyses must be an array", errors)
        if isinstance(analyses, list):
            for item in analyses:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("analysis", "")).lower()
                status = item.get("status")
                if "pseudobulk" in name and "plate" in name:
                    require(status == "blocked", "plate-based pseudobulk must be blocked", errors)
                if "leave-one-plate-out" in name:
                    require(
                        status in {"allowed_with_warning", "exploratory_only"},
                        "leave-one-plate-out cannot be treated as biological validation",
                        errors,
                    )

    require(bool(record.get("next_valid_action")), "next_valid_action is required", errors)

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_experimental_unit_audit.py AUDIT.json [AUDIT.json ...]", file=sys.stderr)
        return 2

    failed = False
    for raw_path in argv[1:]:
        path = Path(raw_path)
        try:
            record = load_json(path)
            errors = validate(record)
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
