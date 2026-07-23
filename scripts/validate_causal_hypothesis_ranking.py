#!/usr/bin/env python3
"""Validate causal-hypothesis rankings with fail-closed identification rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "case_id",
    "target_claim",
    "inherited_constraints",
    "hypotheses",
    "pairwise_discriminators",
    "causal_identification",
    "claim_boundary",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}

EVIDENCE_ORDER = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}
VALID_VERDICTS = {"RANKED_NOT_IDENTIFIED", "IDENTIFIED_WITH_LIMITS", "BLOCK"}
VALID_STATUSES = {
    "causally_identified_with_limits",
    "supported_explanation",
    "plausible",
    "weakened",
    "not_identified",
    "blocked",
}
IDENTIFICATION_FLAGS = {
    "temporal_order_matched",
    "experimental_unit_established",
    "identifying_design_present",
    "major_confounders_separable",
    "independent_validation_present",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("causal ranking root must be a JSON object")
    return value


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(record.get("overall_verdict") in VALID_VERDICTS, "invalid overall_verdict", errors)
    require(bool(record.get("case_id")), "case_id is required", errors)
    require(bool(record.get("next_valid_action")), "next_valid_action is required", errors)

    target = record.get("target_claim", {})
    require(isinstance(target, dict), "target_claim must be an object", errors)
    if isinstance(target, dict):
        for key in ("candidate", "phenotype", "temporal_order", "biological_system", "claim_level", "statement"):
            require(bool(target.get(key)), f"target_claim.{key} is required", errors)

    constraints = record.get("inherited_constraints", [])
    require(isinstance(constraints, list) and len(constraints) > 0, "inherited_constraints must be non-empty", errors)
    if isinstance(constraints, list):
        for index, item in enumerate(constraints):
            require(isinstance(item, dict), f"inherited_constraints[{index}] must be an object", errors)
            if isinstance(item, dict):
                require(item.get("evidence_level") in EVIDENCE_ORDER, f"constraint {index}: invalid evidence_level", errors)
                require(item.get("impact") in {"informational", "limiting", "blocking"}, f"constraint {index}: invalid impact", errors)

    hypotheses = record.get("hypotheses", [])
    require(isinstance(hypotheses, list) and len(hypotheses) >= 3, "at least three competing hypotheses are required", errors)

    hypothesis_ids: set[str] = set()
    ranks: list[int] = []
    ordered_scores: list[tuple[int, float]] = []
    identified_hypotheses = 0

    if isinstance(hypotheses, list):
        for index, hypothesis in enumerate(hypotheses):
            require(isinstance(hypothesis, dict), f"hypotheses[{index}] must be an object", errors)
            if not isinstance(hypothesis, dict):
                continue

            hypothesis_id = hypothesis.get("hypothesis_id")
            require(bool(hypothesis_id), f"hypotheses[{index}].hypothesis_id is required", errors)
            if hypothesis_id:
                require(hypothesis_id not in hypothesis_ids, f"duplicate hypothesis_id: {hypothesis_id}", errors)
                hypothesis_ids.add(hypothesis_id)

            rank = hypothesis.get("rank")
            score = hypothesis.get("priority_score")
            require(isinstance(rank, int) and rank >= 1, f"hypothesis {hypothesis_id}: invalid rank", errors)
            require(isinstance(score, (int, float)) and 0 <= score <= 100, f"hypothesis {hypothesis_id}: invalid priority_score", errors)
            if isinstance(rank, int):
                ranks.append(rank)
            if isinstance(rank, int) and isinstance(score, (int, float)):
                ordered_scores.append((rank, float(score)))

            status = hypothesis.get("status")
            evidence = hypothesis.get("evidence_level")
            require(status in VALID_STATUSES, f"hypothesis {hypothesis_id}: invalid status", errors)
            require(evidence in EVIDENCE_ORDER, f"hypothesis {hypothesis_id}: invalid evidence_level", errors)

            predictions = hypothesis.get("predicted_observations")
            falsifiers = hypothesis.get("falsifiers")
            require(isinstance(predictions, list) and len(predictions) > 0, f"hypothesis {hypothesis_id}: predicted_observations required", errors)
            require(isinstance(falsifiers, list) and len(falsifiers) > 0, f"hypothesis {hypothesis_id}: at least one falsifier required", errors)

            discriminator = hypothesis.get("discriminating_test", {})
            require(isinstance(discriminator, dict), f"hypothesis {hypothesis_id}: discriminating_test must be an object", errors)
            if isinstance(discriminator, dict):
                require(bool(discriminator.get("question")), f"hypothesis {hypothesis_id}: discriminator question required", errors)
                require(bool(discriminator.get("required_evidence")), f"hypothesis {hypothesis_id}: discriminator evidence required", errors)
                require(discriminator.get("operational_protocol_included") is False, f"hypothesis {hypothesis_id}: operational protocol must be false", errors)

            scores = hypothesis.get("scores", {})
            require(isinstance(scores, dict), f"hypothesis {hypothesis_id}: scores must be an object", errors)
            if isinstance(scores, dict):
                for key in (
                    "temporal_fit",
                    "experimental_unit_fit",
                    "cross_dataset_support",
                    "confounder_resilience",
                    "mechanistic_coherence",
                    "intervention_support",
                    "falsifiability",
                    "effect_relevance",
                    "uncertainty_penalty",
                ):
                    value = scores.get(key)
                    require(isinstance(value, int) and 0 <= value <= 4, f"hypothesis {hypothesis_id}: invalid score {key}", errors)

            if status == "causally_identified_with_limits":
                identified_hypotheses += 1
                require(EVIDENCE_ORDER.get(evidence, -1) >= EVIDENCE_ORDER["F4"], f"hypothesis {hypothesis_id}: causal identification requires F4 or F5", errors)
                if isinstance(scores, dict):
                    require(scores.get("intervention_support", 0) > 0, f"hypothesis {hypothesis_id}: causal identification requires intervention support", errors)

        if ranks:
            require(sorted(ranks) == list(range(1, len(ranks) + 1)), "hypothesis ranks must be unique and contiguous from 1", errors)
        if ordered_scores:
            by_rank = [score for _, score in sorted(ordered_scores)]
            require(all(left >= right for left, right in zip(by_rank, by_rank[1:])), "priority_score must be non-increasing by rank", errors)

    discriminators = record.get("pairwise_discriminators", [])
    require(isinstance(discriminators, list) and len(discriminators) > 0, "pairwise_discriminators must be non-empty", errors)
    if isinstance(discriminators, list):
        for index, item in enumerate(discriminators):
            require(isinstance(item, dict), f"pairwise_discriminators[{index}] must be an object", errors)
            if isinstance(item, dict):
                a = item.get("hypothesis_a")
                b = item.get("hypothesis_b")
                require(a in hypothesis_ids, f"pairwise discriminator {index}: unknown hypothesis_a", errors)
                require(b in hypothesis_ids, f"pairwise discriminator {index}: unknown hypothesis_b", errors)
                require(a != b, f"pairwise discriminator {index}: hypotheses must differ", errors)
                require(bool(item.get("distinguishing_observation")), f"pairwise discriminator {index}: observation required", errors)

    identification = record.get("causal_identification", {})
    require(isinstance(identification, dict), "causal_identification must be an object", errors)
    identified = False
    all_identification_flags = False
    if isinstance(identification, dict):
        identified = identification.get("identified") is True
        for flag in IDENTIFICATION_FLAGS:
            require(isinstance(identification.get(flag), bool), f"causal_identification.{flag} must be boolean", errors)
        all_identification_flags = all(identification.get(flag) is True for flag in IDENTIFICATION_FLAGS)
        require(bool(identification.get("reason")), "causal_identification.reason is required", errors)
        if identified:
            require(all_identification_flags, "identified=true requires every identification gate", errors)
            require(identified_hypotheses > 0, "identified=true requires a causally identified hypothesis", errors)
        else:
            require(identified_hypotheses == 0, "no hypothesis may be causally identified when identified=false", errors)

    boundary = record.get("claim_boundary", {})
    require(isinstance(boundary, dict), "claim_boundary must be an object", errors)
    overall = record.get("overall_verdict")
    if isinstance(boundary, dict):
        for key in ("association", "prediction", "causal", "tissue", "clinical_therapeutic"):
            require(boundary.get(key) in {"supported", "supported_with_limits", "not_established", "blocked"}, f"claim_boundary.{key} is invalid", errors)

        if not identified:
            require(boundary.get("causal") in {"not_established", "blocked"}, "causal claim must remain not_established or blocked without identification", errors)
            require(boundary.get("tissue") == "blocked", "tissue claim must be blocked without identification", errors)
            require(boundary.get("clinical_therapeutic") == "blocked", "clinical/therapeutic claim must be blocked without identification", errors)

    if overall == "RANKED_NOT_IDENTIFIED":
        require(not identified, "RANKED_NOT_IDENTIFIED requires identified=false", errors)
    if overall == "IDENTIFIED_WITH_LIMITS":
        require(identified and all_identification_flags, "IDENTIFIED_WITH_LIMITS requires all identification gates", errors)
        require(identified_hypotheses > 0, "IDENTIFIED_WITH_LIMITS requires an identified hypothesis", errors)
    if not identified:
        require(overall != "IDENTIFIED_WITH_LIMITS", "overall verdict cannot identify causality when identification=false", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_only", "mode must be computational_only", errors)
        require(safety.get("physical_biology_authorized") is False, "physical_biology_authorized must be false", errors)

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_causal_hypothesis_ranking.py RANKING.json [RANKING.json ...]", file=sys.stderr)
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
