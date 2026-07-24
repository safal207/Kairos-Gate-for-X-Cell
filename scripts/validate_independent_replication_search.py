#!/usr/bin/env python3
"""Validate independent-replication search records with fail-closed rules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "target_study",
    "target_claim",
    "search_fingerprint",
    "sources_searched",
    "candidates",
    "independence_leakage_findings",
    "prespecified_test",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}

NON_INDEPENDENT_CLASSES = {
    "same_study_new_accession",
    "shared_biological_source",
    "technical_remeasurement",
    "derived_or_reprocessed_data",
}

VALID_INDEPENDENT_ACCEPT_CLASS = "independent_biological_experiment"
EVIDENCE_ORDER = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
OUTCOME_MARKERS = ("completed on ", "rho ", "95% ci", "permutation p 0", "observed result")


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append a validation error when a required condition is false."""
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    """Load one replication-search record as a JSON object."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("replication search root must be a JSON object")
    return value


def validate(record: dict[str, Any]) -> list[str]:
    """Return all contract violations found in one replication-search record."""
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(record.get("overall_verdict") in {"ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}, "invalid overall_verdict", errors)
    require(bool(record.get("target_study")), "target_study is required", errors)
    require(bool(record.get("next_valid_action")), "next_valid_action is required", errors)

    target_claim = record.get("target_claim", {})
    require(isinstance(target_claim, dict), "target_claim must be an object", errors)
    if isinstance(target_claim, dict):
        require(bool(target_claim.get("statement")), "target_claim.statement is required", errors)
        require(
            target_claim.get("claim_level") in {
                "descriptive",
                "association",
                "prediction",
                "generalization",
                "causal",
                "tissue",
                "clinical_therapeutic",
            },
            "invalid target_claim.claim_level",
            errors,
        )

    fingerprint = record.get("search_fingerprint", {})
    require(isinstance(fingerprint, dict), "search_fingerprint must be an object", errors)
    if isinstance(fingerprint, dict):
        excluded = fingerprint.get("excluded_relationships")
        require(isinstance(excluded, list) and len(excluded) > 0, "excluded_relationships must be non-empty", errors)
        require("required_biological_unit" in fingerprint, "required_biological_unit must be explicit", errors)

    sources = record.get("sources_searched", [])
    require(isinstance(sources, list) and len(sources) > 0, "sources_searched must be non-empty", errors)
    if isinstance(sources, list):
        for index, source in enumerate(sources):
            require(isinstance(source, dict), f"sources_searched[{index}] must be an object", errors)
            if not isinstance(source, dict):
                continue
            require(bool(source.get("source")), f"sources_searched[{index}].source is required", errors)
            status = source.get("status")
            require(status in {"planned", "searched", "unavailable"}, f"sources_searched[{index}].status is invalid", errors)
            if status == "searched":
                require(bool(source.get("searched_at")), f"sources_searched[{index}] searched_at is required when searched", errors)

    candidates = record.get("candidates", [])
    require(isinstance(candidates, list), "candidates must be an array", errors)
    accepted_candidates = 0

    if isinstance(candidates, list):
        seen_ids: set[str] = set()
        for index, candidate in enumerate(candidates):
            require(isinstance(candidate, dict), f"candidates[{index}] must be an object", errors)
            if not isinstance(candidate, dict):
                continue

            candidate_id = candidate.get("candidate_id")
            require(bool(candidate_id), f"candidates[{index}].candidate_id is required", errors)
            if candidate_id:
                require(candidate_id not in seen_ids, f"duplicate candidate_id: {candidate_id}", errors)
                seen_ids.add(candidate_id)

            evidence = candidate.get("evidence_level")
            require(evidence in EVIDENCE_ORDER, f"candidate {candidate_id}: invalid evidence_level", errors)

            independence_class = candidate.get("independence_class")
            replication_type = candidate.get("replication_type")
            verdict = candidate.get("candidate_verdict")
            shared_ids = candidate.get("shared_target_identifiers", [])
            compatibility = candidate.get("compatibility", {})

            require(isinstance(shared_ids, list), f"candidate {candidate_id}: shared_target_identifiers must be an array", errors)
            require(isinstance(compatibility, dict), f"candidate {candidate_id}: compatibility must be an object", errors)

            if independence_class in NON_INDEPENDENT_CLASSES:
                require(
                    verdict in {"BLOCK", "EXCLUDE"},
                    f"candidate {candidate_id}: non-independent class cannot be accepted or held as independent replication",
                    errors,
                )
                require(
                    replication_type == "not_a_replication",
                    f"candidate {candidate_id}: non-independent class must be not_a_replication",
                    errors,
                )

            if verdict == "ACCEPT_WITH_LIMITS":
                accepted_candidates += 1
                require(
                    independence_class == VALID_INDEPENDENT_ACCEPT_CLASS,
                    f"candidate {candidate_id}: accepted candidate must be an independent biological experiment",
                    errors,
                )
                require(not shared_ids, f"candidate {candidate_id}: accepted candidate cannot share target identifiers", errors)
                require(
                    EVIDENCE_ORDER.get(evidence, -1) >= EVIDENCE_ORDER["F3"],
                    f"candidate {candidate_id}: accepted candidate requires at least F3 evidence",
                    errors,
                )
                if isinstance(compatibility, dict):
                    require(
                        compatibility.get("biological_source_independence") == "compatible",
                        f"candidate {candidate_id}: biological-source independence must be compatible",
                        errors,
                    )
                    require(
                        compatibility.get("experimental_unit") == "compatible",
                        f"candidate {candidate_id}: experimental unit must be compatible",
                        errors,
                    )
                    require(
                        compatibility.get("provenance") in {"complete", "partial"},
                        f"candidate {candidate_id}: provenance is insufficient",
                        errors,
                    )
                require(
                    replication_type in {"direct_replication", "conceptual_replication", "external_validation"},
                    f"candidate {candidate_id}: accepted candidate must have a replication-capable type",
                    errors,
                )

            if evidence == "F5":
                test = record.get("prespecified_test", {})
                status = test.get("status") if isinstance(test, dict) else None
                require(status == "completed", f"candidate {candidate_id}: F5 requires completed prespecified test", errors)

    test = record.get("prespecified_test", {})
    require(isinstance(test, dict), "prespecified_test must be an object", errors)
    if isinstance(test, dict):
        status = test.get("status")
        require(status in {"not_defined", "defined_not_run", "run_incomplete", "completed"}, "invalid prespecified_test.status", errors)
        freeze_verification = test.get("freeze_verification")
        require(
            freeze_verification in {"commit_bound", "not_commit_bound", "not_applicable"},
            "invalid prespecified_test.freeze_verification",
            errors,
        )
        if status != "not_defined":
            require(bool(test.get("primary_endpoint")), "primary_endpoint is required once test is defined", errors)
            require(bool(test.get("biological_grouping_key")), "biological_grouping_key is required once test is defined", errors)
            require(bool(test.get("success_criteria")), "success_criteria is required once test is defined", errors)
            require(freeze_verification != "not_applicable", "defined tests require a freeze-verification status", errors)
        if freeze_verification == "commit_bound":
            frozen_commit = test.get("criteria_frozen_at_commit")
            require(isinstance(frozen_commit, str) and SHA_RE.fullmatch(frozen_commit) is not None, "commit-bound criteria require a 40-character commit SHA", errors)
        if freeze_verification == "not_commit_bound":
            require(test.get("criteria_frozen_at_commit") is None, "not-commit-bound criteria must not claim a commit SHA", errors)
        if status == "completed":
            observed = test.get("observed_result")
            require(isinstance(observed, str) and bool(observed.strip()), "completed tests require observed_result", errors)
            success = test.get("success_criteria")
            require(success != observed, "success_criteria and observed_result must be separate", errors)
            if isinstance(success, str):
                lowered = success.lower()
                require(not any(marker in lowered for marker in OUTCOME_MARKERS), "success_criteria appears to contain observed statistics", errors)

    overall = record.get("overall_verdict")
    if accepted_candidates == 0:
        require(overall != "ACCEPT_WITH_LIMITS", "overall ACCEPT_WITH_LIMITS requires at least one accepted candidate", errors)
    if overall == "ACCEPT_WITH_LIMITS":
        require(accepted_candidates > 0, "accepted overall verdict requires an accepted candidate", errors)
        if isinstance(test, dict):
            require(test.get("status") in {"defined_not_run", "run_incomplete", "completed"}, "accepted overall verdict requires a defined test", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_only", "mode must be computational_only", errors)
        require(safety.get("physical_biology_authorized") is False, "physical_biology_authorized must be false", errors)

    return errors


def main(argv: list[str]) -> int:
    """Validate each path from argv and return a process exit code."""
    if len(argv) < 2:
        print("usage: validate_independent_replication_search.py SEARCH.json [SEARCH.json ...]", file=sys.stderr)
        return 2

    failed = False
    for raw_path in argv[1:]:
        path = Path(raw_path)
        try:
            errors = validate(load_json(path))
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
