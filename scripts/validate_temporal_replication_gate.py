#!/usr/bin/env python3
"""Validate temporal-replication records with fail-closed direct-candidate rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED = {
    "schema_version",
    "case_id",
    "frozen_target",
    "sources_searched",
    "candidates",
    "direct_replication_gap",
    "model_discrimination_plan",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}

DIRECT_GATES = (
    "independent_of_target",
    "biological_unit_established",
)
SOURCE_STATUSES = {"searched", "partial", "unavailable"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append a validation error when a required condition is false."""
    if not condition:
        errors.append(message)


def load(path: Path) -> dict[str, Any]:
    """Load one temporal-replication record as a JSON object."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("record root must be an object")
    return value


def non_empty_string_list(value: Any) -> bool:
    """Return whether value is a non-empty list of non-empty strings."""
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def validate(record: dict[str, Any]) -> list[str]:
    """Return all temporal-replication contract violations for one record."""
    errors: list[str] = []
    missing = sorted(REQUIRED - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(
        record.get("overall_verdict")
        in {
            "DIRECT_CANDIDATE_AVAILABLE",
            "PARTIAL_CANDIDATE_AVAILABLE",
            "DIRECT_REPLICATION_GAP",
            "BLOCK",
        },
        "invalid overall_verdict",
        errors,
    )

    target = record.get("frozen_target", {})
    require(isinstance(target, dict), "frozen_target must be an object", errors)
    if isinstance(target, dict):
        for key in (
            "pre_state",
            "transition",
            "later_phenotype",
            "identity_linkage",
            "biological_unit",
        ):
            require(bool(target.get(key)), f"frozen_target.{key} is required", errors)
        require(
            non_empty_string_list(target.get("acceptable_endpoint_substitutions")),
            "frozen_target.acceptable_endpoint_substitutions must be a non-empty string list",
            errors,
        )
        require(
            non_empty_string_list(target.get("forbidden_substitutions")),
            "frozen_target.forbidden_substitutions must be a non-empty string list",
            errors,
        )
        models = target.get("competing_models")
        require(
            isinstance(models, list)
            and len(models) >= 3
            and all(isinstance(item, str) and bool(item.strip()) for item in models),
            "at least three non-empty competing models are required",
            errors,
        )

    sources = record.get("sources_searched")
    require(
        isinstance(sources, list) and len(sources) > 0,
        "sources_searched must be a non-empty array",
        errors,
    )
    if isinstance(sources, list):
        for index, source in enumerate(sources):
            require(
                isinstance(source, dict),
                f"sources_searched[{index}] must be an object",
                errors,
            )
            if not isinstance(source, dict):
                continue
            for key in ("source", "scope", "searched_at"):
                require(
                    isinstance(source.get(key), str) and bool(source[key].strip()),
                    f"sources_searched[{index}].{key} must be non-empty",
                    errors,
                )
            require(
                source.get("status") in SOURCE_STATUSES,
                f"sources_searched[{index}].status is invalid",
                errors,
            )

    candidates = record.get("candidates", [])
    require(
        isinstance(candidates, list) and len(candidates) > 0,
        "candidates must be non-empty",
        errors,
    )
    accepted_direct = 0
    partial = 0
    if isinstance(candidates, list):
        ids: set[str] = set()
        for index, candidate in enumerate(candidates):
            require(
                isinstance(candidate, dict),
                f"candidate {index} must be an object",
                errors,
            )
            if not isinstance(candidate, dict):
                continue
            cid = candidate.get("candidate_id")
            require(bool(cid), f"candidate {index}: candidate_id required", errors)
            if cid:
                require(cid not in ids, f"duplicate candidate_id: {cid}", errors)
                ids.add(cid)

            klass = candidate.get("candidate_class")
            verdict = candidate.get("verdict")
            if verdict == "ACCEPT_DIRECT":
                accepted_direct += 1
                require(
                    klass == "direct_temporal_replication_candidate",
                    f"{cid}: ACCEPT_DIRECT requires direct class",
                    errors,
                )
                for gate in DIRECT_GATES:
                    require(
                        candidate.get(gate) is True,
                        f"{cid}: direct candidate requires {gate}=true",
                        errors,
                    )
                require(
                    candidate.get("pre_state_before_transition") == "established",
                    f"{cid}: pre-state must precede transition",
                    errors,
                )
                require(
                    candidate.get("later_phenotype_after_transition") == "established",
                    f"{cid}: later phenotype must follow transition",
                    errors,
                )
                require(
                    candidate.get("same_cell_or_longitudinal_link") == "established",
                    f"{cid}: same-cell/longitudinal linkage required",
                    errors,
                )
                require(
                    candidate.get("endpoint_compatibility") == "compatible",
                    f"{cid}: endpoint must be compatible",
                    errors,
                )
                require(
                    candidate.get("technical_lineage") in {"complete", "partial"},
                    f"{cid}: technical lineage cannot be unknown",
                    errors,
                )
                require(
                    candidate.get("evidence_level") in {"F3", "F4", "F5"},
                    f"{cid}: direct candidate requires F3+",
                    errors,
                )
            if verdict == "ACCEPT_PARTIAL":
                partial += 1
            if klass == "conceptual_replication":
                require(
                    verdict != "ACCEPT_DIRECT",
                    f"{cid}: conceptual replication cannot be direct",
                    errors,
                )
            if candidate.get("pre_state_before_transition") == "contradicted":
                require(
                    verdict != "ACCEPT_DIRECT",
                    f"{cid}: post-transition molecular measurement cannot be direct",
                    errors,
                )
            if candidate.get("independent_of_target") is False:
                require(
                    verdict != "ACCEPT_DIRECT",
                    f"{cid}: same-study evidence cannot be external direct replication",
                    errors,
                )

    gap = record.get("direct_replication_gap", {})
    require(
        isinstance(gap, dict),
        "direct_replication_gap must be an object",
        errors,
    )
    gap_present = gap.get("present") is True if isinstance(gap, dict) else False
    if isinstance(gap, dict):
        require(
            isinstance(gap.get("present"), bool),
            "direct_replication_gap.present must be boolean",
            errors,
        )
        require(bool(gap.get("search_conclusion")), "search_conclusion required", errors)
        if gap_present:
            require(
                isinstance(gap.get("missing_fields"), list)
                and len(gap["missing_fields"]) > 0,
                "gap requires missing_fields",
                errors,
            )

    plan = record.get("model_discrimination_plan", {})
    require(
        isinstance(plan, dict),
        "model_discrimination_plan must be an object",
        errors,
    )
    if isinstance(plan, dict):
        for key in (
            "candidate_only_model",
            "broader_state_model",
            "technical_confounder_model",
        ):
            require(
                bool(plan.get(key)),
                f"model_discrimination_plan.{key} required",
                errors,
            )
        require(
            plan.get("outcome_inspected_before_freeze") is False,
            "outcome_inspected_before_freeze must be false",
            errors,
        )

    verdict = record.get("overall_verdict")
    if verdict == "DIRECT_CANDIDATE_AVAILABLE":
        require(
            accepted_direct > 0,
            "DIRECT_CANDIDATE_AVAILABLE requires an accepted direct candidate",
            errors,
        )
        require(not gap_present, "direct candidate verdict conflicts with gap present", errors)
    if verdict == "PARTIAL_CANDIDATE_AVAILABLE":
        require(partial > 0, "partial verdict requires ACCEPT_PARTIAL candidate", errors)
        require(
            accepted_direct == 0,
            "partial verdict cannot coexist with accepted direct candidate",
            errors,
        )
    if verdict == "DIRECT_REPLICATION_GAP":
        require(gap_present, "DIRECT_REPLICATION_GAP requires present=true", errors)
        require(
            accepted_direct == 0,
            "gap verdict cannot contain accepted direct candidate",
            errors,
        )

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(
            safety.get("mode") == "computational_only",
            "mode must be computational_only",
            errors,
        )
        require(
            safety.get("physical_biology_authorized") is False,
            "physical_biology_authorized must be false",
            errors,
        )

    require(bool(record.get("next_valid_action")), "next_valid_action required", errors)
    return errors


def main(argv: list[str]) -> int:
    """Validate all supplied temporal records and return a process exit code."""
    if len(argv) < 2:
        print(
            "usage: validate_temporal_replication_gate.py RECORD.json [RECORD.json ...]",
            file=sys.stderr,
        )
        return 2
    failed = False
    for raw in argv[1:]:
        path = Path(raw)
        try:
            errors = validate(load(path))
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
