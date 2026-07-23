#!/usr/bin/env python3
"""Validate Model Evidence Passports with exact identity and claim boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SHA256 = re.compile(r"^[a-f0-9]{64}$")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_model_evidence_passport.py PASSPORT.json")
        return 2

    try:
        record = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCK cannot load passport: {exc}")
        return 1

    errors: list[str] = []
    require(record.get("schema_version") == "0.2.0", "schema_version must be 0.2.0", errors)
    require(bool(record.get("passport_id")), "passport_id is required", errors)

    run = record.get("run_identity", {})
    model = record.get("model_identity", {})
    data = record.get("data_identity", {})
    execution = record.get("execution", {})
    uncertainty = record.get("uncertainty", {})
    claims = record.get("claim_boundary", {})
    safety = record.get("safety_status", {})

    for key in ("run_id", "created_at", "code_revision", "execution_mode"):
        require(bool(run.get(key)), f"run_identity.{key} is required", errors)
    for key in ("provider", "registry_id", "model_family", "checkpoint_or_version", "runtime_or_container", "source_url"):
        require(bool(model.get(key)), f"model_identity.{key} is required", errors)
    for key in ("dataset_id", "input_artifact", "output_artifact"):
        require(bool(data.get(key)), f"data_identity.{key} is required", errors)

    require(bool(SHA256.fullmatch(str(data.get("input_sha256", "")))), "input_sha256 must be exact", errors)
    require(bool(SHA256.fullmatch(str(data.get("output_sha256", "")))), "output_sha256 must be exact", errors)
    require(isinstance(execution.get("parameters"), dict), "execution.parameters must be an object", errors)
    require(isinstance(execution.get("random_seeds"), list), "execution.random_seeds must be a list", errors)
    require(isinstance(execution.get("hardware"), dict), "execution.hardware must be an object", errors)
    require(isinstance(execution.get("software"), dict), "execution.software must be an object", errors)
    require(execution.get("status") in {"completed", "failed", "not_executed"}, "execution.status is invalid", errors)

    if run.get("execution_mode") == "metadata_only_no_model_inference":
        require(execution.get("status") == "not_executed",
                "metadata-only passport must state not_executed", errors)
        require(record.get("compatibility_verdict") in {"ACCEPT_WITH_LIMITS", "SPECIES_COMPATIBILITY_HOLD", "QUESTION_NOT_APPLICABLE"},
                "metadata-only demo must preserve a bounded compatibility verdict", errors)

    for transformation in record.get("transformations", []):
        for key in ("name", "version", "parameters", "status"):
            require(key in transformation, f"transformation missing {key}", errors)

    require(uncertainty.get("training_overlap_status") is not None,
            "training_overlap_status is required", errors)
    require(bool(uncertainty.get("limitations")), "at least one limitation is required", errors)
    require(claims.get("causal") == "blocked", "causal claims must remain blocked", errors)
    require(claims.get("clinical_therapeutic") == "blocked",
            "clinical/therapeutic claims must remain blocked", errors)
    require(safety.get("physical_biology_authorized") is False,
            "physical biology cannot be authorized", errors)
    require(safety.get("clinical_use_authorized") is False,
            "clinical use cannot be authorized", errors)

    if errors:
        print("BLOCK Model Evidence Passport")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("ACCEPT Model Evidence Passport")
    print(f"  passport_id={record['passport_id']}")
    print(f"  input_sha256={data['input_sha256']}")
    print(f"  output_sha256={data['output_sha256']}")
    print(f"  compatibility_verdict={record['compatibility_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
