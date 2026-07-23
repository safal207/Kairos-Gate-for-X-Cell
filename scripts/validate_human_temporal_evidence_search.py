#!/usr/bin/env python3
"""Fail-closed validator for human macrophage temporal-evidence searches."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DIRECT_GATES = (
    "human",
    "pre_state_before_transition",
    "later_phenotype",
    "same_cell_or_defensible_longitudinal_identity",
    "independent_biological_units_explicit",
    "technical_lineage_sufficient",
    "public_analysis_data",
)

ALLOWED_CLASSES = {
    "DIRECT_TEMPORAL_CANDIDATE",
    "DONOR_LEVEL_TEMPORAL_SUPPORT",
    "SINGLE_CELL_POST_RESPONSE_SUPPORT",
    "HUMAN_DOMAIN_REFERENCE",
    "METHOD_TRANSFER_ONLY",
    "CROSS_SECTIONAL_SUPPORT",
    "EXCLUDE",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(record: Any) -> list[str]:
    errors: list[str] = []
    require(isinstance(record, dict), "record must be an object", errors)
    if not isinstance(record, dict):
        return errors

    require(record.get("schema_version") == "0.2.0", "schema_version must be 0.2.0", errors)
    require(record.get("global_verdict") in {"HUMAN_DIRECT_REPLICATION_FOUND", "HUMAN_DIRECT_REPLICATION_GAP"}, "unknown global_verdict", errors)

    target = record.get("frozen_target", {})
    require(target.get("organism") == "Homo sapiens", "frozen target must remain Homo sapiens", errors)
    require(target.get("identity_requirement") == "same_cell", "frozen target identity must remain same_cell", errors)

    repositories = record.get("repositories")
    require(isinstance(repositories, list) and len(repositories) >= 2, "at least two repositories are required", errors)
    queries = record.get("queries")
    require(isinstance(queries, list) and len(queries) >= 4, "at least four frozen queries are required", errors)

    candidates = record.get("candidates")
    require(isinstance(candidates, list) and len(candidates) > 0, "at least one candidate is required", errors)
    if not isinstance(candidates, list):
        candidates = []

    ids: set[str] = set()
    eligible_count = 0
    for index, candidate in enumerate(candidates):
        prefix = f"candidate[{index}]"
        require(isinstance(candidate, dict), f"{prefix} must be an object", errors)
        if not isinstance(candidate, dict):
            continue
        candidate_id = candidate.get("candidate_id")
        require(isinstance(candidate_id, str) and candidate_id, f"{prefix} missing candidate_id", errors)
        if isinstance(candidate_id, str):
            require(candidate_id not in ids, f"duplicate candidate_id: {candidate_id}", errors)
            ids.add(candidate_id)

        classification = candidate.get("classification")
        require(classification in ALLOWED_CLASSES, f"{prefix} has unknown classification", errors)
        gates = candidate.get("gates")
        require(isinstance(gates, dict), f"{prefix} missing gates", errors)
        if not isinstance(gates, dict):
            gates = {}
        for gate in DIRECT_GATES:
            require(isinstance(gates.get(gate), bool), f"{prefix}.{gate} must be boolean", errors)

        urls = candidate.get("source_urls")
        require(isinstance(urls, list) and len(urls) > 0, f"{prefix} needs source_urls", errors)
        if isinstance(urls, list):
            for url in urls:
                require(isinstance(url, str) and url.startswith("https://"), f"{prefix} source URL must use https", errors)

        eligible = candidate.get("direct_replication_eligible") is True
        all_gates = all(gates.get(gate) is True for gate in DIRECT_GATES)
        if eligible:
            eligible_count += 1
            require(classification == "DIRECT_TEMPORAL_CANDIDATE", f"{prefix} eligible candidate must be classified DIRECT_TEMPORAL_CANDIDATE", errors)
            require(all_gates, f"{prefix} direct candidate does not pass every required gate", errors)
        if classification == "DIRECT_TEMPORAL_CANDIDATE":
            require(eligible, f"{prefix} direct classification requires direct_replication_eligible=true", errors)
            require(all_gates, f"{prefix} direct classification lacks required gate evidence", errors)

        if candidate_id == "GSE184241":
            require(not eligible, "GSE184241 cannot be direct without same-cell pre-state linkage", errors)
            require(gates.get("same_cell_or_defensible_longitudinal_identity") is False, "GSE184241 same-cell linkage must remain false", errors)

        if classification == "SINGLE_CELL_POST_RESPONSE_SUPPORT":
            require(gates.get("pre_state_before_transition") is False, f"{prefix} post-response support cannot claim baseline timing", errors)

    verdict = record.get("global_verdict")
    if verdict == "HUMAN_DIRECT_REPLICATION_FOUND":
        require(eligible_count > 0, "FOUND verdict requires at least one eligible direct candidate", errors)
    if verdict == "HUMAN_DIRECT_REPLICATION_GAP":
        require(eligible_count == 0, "GAP verdict cannot contain an eligible direct candidate", errors)

    prefix_resolution = record.get("gse94383_prefix_resolution", {})
    require(prefix_resolution.get("status") == "TECHNICAL_OR_CONDITION_PREFIX", "GSE94383 prefix status must remain technical/condition", errors)
    require(prefix_resolution.get("biological_replicate") is False, "GSE94383 prefixes cannot be biological replicates", errors)
    require(prefix_resolution.get("allowed_use") == "technical_or_condition_sensitivity_only", "GSE94383 prefixes may only support sensitivity analysis", errors)

    partner = record.get("partner_lab_requirement", {})
    require(partner.get("required") is True, "partner-laboratory evidence remains required while the direct gap is open", errors)
    require(partner.get("physical_execution_authorized") is False, "search record cannot authorize physical execution", errors)

    claims = record.get("claim_boundary", {})
    require(claims.get("direct_prediction") == "not_established", "direct prediction must remain not_established", errors)
    require(claims.get("causal") == "blocked", "causal claims must remain blocked", errors)
    require(claims.get("clinical_therapeutic") == "blocked", "clinical/therapeutic claims must remain blocked", errors)

    safety = record.get("safety_status", {})
    require(safety.get("computational_only") is True, "record must be computational_only", errors)
    require(safety.get("physical_biology_authorized") is False, "physical biology cannot be authorized", errors)
    require(safety.get("clinical_use_authorized") is False, "clinical use cannot be authorized", errors)

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} RECORD.json")
        return 2
    path = Path(sys.argv[1])
    try:
        record = load(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCK human temporal evidence search: {exc}")
        return 1

    errors = validate(record)
    if errors:
        print("BLOCK human temporal evidence search")
        for error in errors:
            print(f"  - {error}")
        return 1

    candidates = record["candidates"]
    class_counts: dict[str, int] = {}
    for candidate in candidates:
        cls = candidate["classification"]
        class_counts[cls] = class_counts.get(cls, 0) + 1
    print("ACCEPT human temporal evidence search")
    print(f"  verdict={record['global_verdict']}")
    print(f"  candidates={len(candidates)}")
    print(f"  classes={json.dumps(class_counts, sort_keys=True)}")
    print("  direct_candidates=0")
    print("  gse94383_prefixes=technical_or_condition_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
