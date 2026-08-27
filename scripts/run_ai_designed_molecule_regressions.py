#!/usr/bin/env python3
"""Run deterministic fail-closed regressions for the AI-designed molecule audit."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "syntnpb-2026.ai-designed-molecule-claim-audit.json"
OUT = ROOT / "ai-designed-molecule-regressions"
GATEWAY = ROOT / "scripts" / "validate_bioevidence_contract.py"

Mutation = Callable[[dict[str, Any]], None]


def claim(record: dict[str, Any], claim_type: str) -> dict[str, Any]:
    return next(item for item in record["claim_audit"] if item["claim_type"] == claim_type)


def external_item(
    *,
    evidence_id: str,
    kind: str,
    endpoints: list[str],
    level: str = "F5",
    coverage: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "evidence_kind": kind,
        "evidence_level": level,
        "endpoint_types": endpoints,
        "provenance": {
            "source_role": "laboratory_confirmation",
            "source_url": f"https://evidence.example/{evidence_id}",
            "source_locator": f"frozen evidence record {evidence_id}",
            "derivation": "directly_reported",
            "artifact_kind": (
                "risk_assessment_record" if kind == "risk_assessment"
                else "independent_replication_record"
            ),
            "confirmation_type": "independent_laboratory_replication",
            "artifact_sha256": "a" * 64,
        },
        "independence": {
            "unrelated_laboratory_identity": "external-lab-a",
            "independent_materials": True,
            "replication_unit": "independent biological preparation",
        },
        "coverage": coverage,
        "limitations": ["Synthetic regression evidence object."],
    }


def risk_external_item(*, evidence_id: str, endpoint: str, level: str) -> dict[str, Any]:
    if level == "F3":
        provenance = {
            "source_role": "derived_artifact",
            "source_url": f"https://evidence.example/{evidence_id}",
            "source_locator": f"computed risk artifact {evidence_id}",
            "derivation": "computed",
            "artifact_kind": "risk_assessment_record",
            "confirmation_type": None,
            "artifact_sha256": "b" * 64,
        }
    elif level == "F4":
        provenance = {
            "source_role": "laboratory_confirmation",
            "source_url": f"https://evidence.example/{evidence_id}",
            "source_locator": f"laboratory-confirmed risk artifact {evidence_id}",
            "derivation": "directly_reported",
            "artifact_kind": "risk_assessment_record",
            "confirmation_type": "author_or_laboratory_confirmation",
            "artifact_sha256": "c" * 64,
        }
    else:
        raise ValueError(f"unsupported positive risk level: {level}")

    return {
        "evidence_id": evidence_id,
        "evidence_kind": "risk_assessment",
        "evidence_level": level,
        "endpoint_types": [endpoint],
        "provenance": provenance,
        "independence": None,
        "coverage": None,
        "limitations": ["Synthetic positive compatibility evidence object."],
    }


def set_established_replication(
    record: dict[str, Any],
    evidence_ref: str,
    *,
    level: str = "F5",
) -> None:
    record["replication_status"] = {
        "same_collaboration_only": False,
        "independent_replication": "established",
        "replication_evidence": {
            "unrelated_laboratory_identity": "external-lab-a",
            "independent_materials": True,
            "replication_unit": "independent biological preparation",
            "evidence_refs": [evidence_ref],
            "evidence_level": level,
        },
    }
    replication_claim = claim(record, "independent_replication")
    replication_claim["status"] = "supported_with_limits"
    replication_claim["evidence_refs"] = ["publication", evidence_ref]


def mutate_protected_supported(record: dict[str, Any]) -> None:
    claim(record, "universal_superiority")["status"] = "supported_with_limits"


def mutate_comparator_mismatch(record: dict[str, Any]) -> None:
    record["assays"][1]["comparator"] = "Cas9"


def mutate_comparator_scope_mismatch(record: dict[str, Any]) -> None:
    claim(record, "bounded_comparator_superiority")["comparator_scope"] = "all_natural_editors"


def mutate_comparator_only_activity(record: dict[str, Any]) -> None:
    for assay in record["assays"]:
        if "molecular_activity" in assay["endpoint_types"]:
            assay["tested_subject"] = "reference_comparator_only"


def mutate_structured_predicate(record: dict[str, Any]) -> None:
    claim(record, "molecular_activity")["claim_predicate"] = "is_clinically_safe"


def mutate_publication_as_f3(record: dict[str, Any]) -> None:
    record["assays"][0]["evidence_level"] = "F3"


def mutate_replication_not_f5(record: dict[str, Any]) -> None:
    evidence = external_item(
        evidence_id="replication-f4",
        kind="independent_replication",
        endpoints=["independent_replication"],
        level="F4",
    )
    evidence["provenance"]["artifact_kind"] = "author_confirmation"
    evidence["provenance"]["confirmation_type"] = "author_or_laboratory_confirmation"
    record["external_evidence"] = [evidence]
    set_established_replication(record, "replication-f4")


def mutate_invented_replication_ref(record: dict[str, Any]) -> None:
    set_established_replication(record, "replication-invented")


def mutate_platform_insufficient_coverage(record: dict[str, Any]) -> None:
    coverage = {
        "target_classes": ["target-a"],
        "laboratories": ["lab-a"],
        "delivery_systems": ["delivery-a"],
        "organisms": ["organism-a"],
        "populations": ["population-a"],
    }
    evidence = external_item(
        evidence_id="platform-one-context",
        kind="platform_generalization",
        endpoints=["platform_generalization"],
        coverage=coverage,
    )
    record["external_evidence"] = [evidence]
    platform = claim(record, "platform_generalization")
    platform["status"] = "supported_with_limits"
    platform["evidence_refs"] = ["publication", "platform-one-context"]


def mutate_unreconciled_denominator(record: dict[str, Any]) -> None:
    record["screening_context"].update(
        {
            "generation_scale": "exact_count_reported",
            "generated_count": 100,
            "excluded_before_screen_count": 0,
            "screened_count": 1,
            "failed_screen_count": 0,
            "selected_count": 1,
            "selected_count_status": "positive_exact",
            "denominator_completeness": "complete",
            "winner_selection_prespecified": True,
            "failed_candidate_reporting": "complete",
            "selection_bias_status": "LOW",
        }
    )


def mutate_risk_wrong_endpoint(record: dict[str, Any]) -> None:
    record["risk_assessment"]["delivery"] = {
        "status": "established",
        "evidence_refs": ["cryo-em-selected-variant"],
        "limitations": ["Synthetic invalid risk promotion."],
    }


def mutate_f5_risk_without_independence(record: dict[str, Any]) -> None:
    evidence = external_item(
        evidence_id="ecological-f5-without-independence",
        kind="risk_assessment",
        endpoints=["ecological_safety"],
    )
    evidence["independence"]["unrelated_laboratory_identity"] = "   "
    evidence["independence"]["replication_unit"] = "\t"
    record["external_evidence"] = [evidence]
    record["risk_assessment"]["ecological_safety"] = {
        "status": "established",
        "evidence_refs": [evidence["evidence_id"]],
        "limitations": ["Synthetic missing-independence attack."],
    }


def mutate_risks_not_applicable(record: dict[str, Any]) -> None:
    for item in record["risk_assessment"].values():
        item["status"] = "not_applicable"


def mutate_observed_mechanism_without_structure(record: dict[str, Any]) -> None:
    record["assays"] = [
        assay for assay in record["assays"] if assay["system"] != "cryo_em_structure"
    ]
    structural_claim = claim(record, "structural_characterization")
    structural_claim["status"] = "not_established"
    structural_claim["evidence_refs"] = ["publication"]


def mutate_supported_structure_without_observed_mechanism(
    record: dict[str, Any],
) -> None:
    record["mechanism_evidence"]["cryo_em_characterized"] = False
    record["mechanism_evidence"]["status"] = "not_established"


def mutate_zero_selected(record: dict[str, Any]) -> None:
    record["screening_context"]["selected_count"] = 0
    record["screening_context"]["selected_count_status"] = "zero_exact"


def mutate_structural_assay_relabelled_as_delivery(record: dict[str, Any]) -> None:
    structural = next(assay for assay in record["assays"] if assay["system"] == "cryo_em_structure")
    structural["endpoint_types"] = ["structural_characterization", "delivery"]
    record["risk_assessment"]["delivery"] = {
        "status": "established",
        "evidence_refs": [structural["assay_id"]],
        "limitations": ["Synthetic endpoint-relabel attack."],
    }


def mutate_partial_impossible_counts(record: dict[str, Any]) -> None:
    record["screening_context"].update(
        {
            "generation_scale": "exact_count_reported",
            "generated_count": 1,
            "excluded_before_screen_count": None,
            "screened_count": 100,
            "failed_screen_count": None,
            "selected_count": 101,
            "selected_count_status": "positive_exact",
            "denominator_completeness": "partial",
            "winner_selection_prespecified": None,
            "failed_candidate_reporting": "partial",
            "selection_bias_status": "HOLD",
        }
    )


def mutate_f5_artifact_kind_mismatch(record: dict[str, Any]) -> None:
    coverage = {
        "target_classes": ["target-a", "target-b"],
        "laboratories": ["lab-a", "lab-b"],
        "delivery_systems": ["delivery-a", "delivery-b"],
        "organisms": ["organism-a", "organism-b"],
        "populations": ["population-a", "population-b"],
    }
    evidence = external_item(
        evidence_id="platform-wrong-artifact-kind",
        kind="platform_generalization",
        endpoints=["platform_generalization"],
        coverage=coverage,
    )
    evidence["provenance"]["artifact_kind"] = "risk_assessment_record"
    record["external_evidence"] = [evidence]
    platform = claim(record, "platform_generalization")
    platform["status"] = "supported_with_limits"
    platform["evidence_refs"] = ["publication", evidence["evidence_id"]]


def mutate_positive_nonexact_after_zero_upstream(record: dict[str, Any]) -> None:
    record["screening_context"].update(
        {
            "generation_scale": "exact_count_reported",
            "generated_count": 0,
            "excluded_before_screen_count": None,
            "screened_count": 0,
            "failed_screen_count": None,
            "selected_count": None,
            "selected_count_status": "positive_nonexact",
            "denominator_completeness": "partial",
            "winner_selection_prespecified": None,
            "failed_candidate_reporting": "partial",
            "selection_bias_status": "HOLD",
        }
    )


def mutate_retained_activity_with_superiority_endpoint(record: dict[str, Any]) -> None:
    assay = record["assays"][1]
    assay["result_direction"] = "retained_reference_activity"
    assay["endpoint_types"] = ["molecular_activity", "bounded_comparator_superiority"]


def mutate_f3_specificity_risk_accepted(record: dict[str, Any]) -> None:
    evidence = risk_external_item(
        evidence_id="specificity-f3-risk-artifact",
        endpoint="specificity_off_target",
        level="F3",
    )
    record["external_evidence"] = [evidence]
    record["risk_assessment"]["specificity_off_target"] = {
        "status": "established",
        "evidence_refs": [evidence["evidence_id"]],
        "limitations": ["Synthetic F3 specificity compatibility case."],
    }


def mutate_f4_delivery_risk_accepted(record: dict[str, Any]) -> None:
    evidence = risk_external_item(
        evidence_id="delivery-f4-risk-artifact",
        endpoint="delivery",
        level="F4",
    )
    record["external_evidence"] = [evidence]
    record["risk_assessment"]["delivery"] = {
        "status": "established",
        "evidence_refs": [evidence["evidence_id"]],
        "limitations": ["Synthetic F4 delivery compatibility case."],
    }


def mutate_f4_computed_confirmation(record: dict[str, Any]) -> None:
    mutate_f4_delivery_risk_accepted(record)
    record["external_evidence"][0]["provenance"]["derivation"] = "computed"


CASES: list[tuple[str, Mutation, str, tuple[str, ...]]] = [
    (
        "protected-supported",
        mutate_protected_supported,
        "BLOCK",
        ("universal_superiority", "must be blocked or not established"),
    ),
    (
        "comparator-mismatch",
        mutate_comparator_mismatch,
        "BLOCK",
        ("every referenced assay must use named comparator",),
    ),
    (
        "comparator-scope-mismatch",
        mutate_comparator_scope_mismatch,
        "BLOCK",
        ("comparator_scope", "wild_type_same_family", "was expected"),
    ),
    (
        "comparator-only-activity",
        mutate_comparator_only_activity,
        "BLOCK",
        ("peer-reviewed referenced F2+ molecular-activity evidence required",),
    ),
    (
        "structured-predicate-mismatch",
        mutate_structured_predicate,
        "BLOCK",
        ("claim_predicate", "was expected"),
    ),
    (
        "publication-mislabeled-f3",
        mutate_publication_as_f3,
        "BLOCK",
        ("F3 requires a digested executable",),
    ),
    (
        "replication-below-f5",
        mutate_replication_not_f5,
        "BLOCK",
        ("independent_replication requires matching F5 replication artifact",),
    ),
    (
        "invented-replication-reference",
        mutate_invented_replication_ref,
        "BLOCK",
        ("must resolve to external evidence objects",),
    ),
    (
        "platform-insufficient-coverage",
        mutate_platform_insufficient_coverage,
        "BLOCK",
        ("target_classes", "is too short"),
    ),
    (
        "unreconciled-denominator",
        mutate_unreconciled_denominator,
        "BLOCK",
        ("generated = excluded_before_screen + screened",),
    ),
    (
        "risk-wrong-endpoint",
        mutate_risk_wrong_endpoint,
        "BLOCK",
        ("risk delivery: established status requires risk-specific F4+ evidence",),
    ),
    (
        "f5-risk-without-independence",
        mutate_f5_risk_without_independence,
        "BLOCK",
        ("external_evidence[0].independence", "not valid under any"),
    ),
    (
        "mandatory-risks-not-applicable",
        mutate_risks_not_applicable,
        "BLOCK",
        ("mandatory dimension cannot be not_applicable",),
    ),
    (
        "observed-mechanism-without-structure",
        mutate_observed_mechanism_without_structure,
        "BLOCK",
        ("observed structure requires a supported structural_characterization claim",),
    ),
    (
        "supported-structure-without-observed-mechanism",
        mutate_supported_structure_without_observed_mechanism,
        "BLOCK",
        ("supported structural_characterization requires observed cryo-EM mechanism state",),
    ),
    (
        "zero-selected-candidates",
        mutate_zero_selected,
        "BLOCK",
        ("require positive selected candidates",),
    ),
    (
        "structural-assay-relabelled-as-delivery",
        mutate_structural_assay_relabelled_as_delivery,
        "BLOCK",
        ("structural assay endpoints must be exactly structural_characterization",),
    ),
    (
        "partial-impossible-counts",
        mutate_partial_impossible_counts,
        "BLOCK",
        ("screened_count cannot exceed generated_count", "selected_count cannot exceed screened_count"),
    ),
    (
        "f5-artifact-kind-mismatch",
        mutate_f5_artifact_kind_mismatch,
        "BLOCK",
        ("platform_generalization requires matching F5 replication artifact",),
    ),
    (
        "positive-nonexact-after-zero-upstream",
        mutate_positive_nonexact_after_zero_upstream,
        "BLOCK",
        ("positive_nonexact selection cannot follow known zero generated_count",),
    ),
    (
        "retained-activity-with-superiority-endpoint",
        mutate_retained_activity_with_superiority_endpoint,
        "BLOCK",
        ("retained_reference_activity cannot assert comparator superiority",),
    ),
    (
        "f4-computed-confirmation",
        mutate_f4_computed_confirmation,
        "BLOCK",
        ("F4 requires repository, laboratory, or risk-assessment confirmation",),
    ),
    (
        "f3-specificity-risk-evidence-accepted",
        mutate_f3_specificity_risk_accepted,
        "ACCEPT",
        ("contract=ai-designed-molecule",),
    ),
    (
        "f4-delivery-risk-evidence-accepted",
        mutate_f4_delivery_risk_accepted,
        "ACCEPT",
        ("contract=ai-designed-molecule",),
    ),
]

EXPECTED_CASE_NAMES = (
    "protected-supported",
    "comparator-mismatch",
    "comparator-scope-mismatch",
    "comparator-only-activity",
    "structured-predicate-mismatch",
    "publication-mislabeled-f3",
    "replication-below-f5",
    "invented-replication-reference",
    "platform-insufficient-coverage",
    "unreconciled-denominator",
    "risk-wrong-endpoint",
    "f5-risk-without-independence",
    "mandatory-risks-not-applicable",
    "observed-mechanism-without-structure",
    "supported-structure-without-observed-mechanism",
    "zero-selected-candidates",
    "structural-assay-relabelled-as-delivery",
    "partial-impossible-counts",
    "f5-artifact-kind-mismatch",
    "positive-nonexact-after-zero-upstream",
    "retained-activity-with-superiority-endpoint",
    "f4-computed-confirmation",
    "f3-specificity-risk-evidence-accepted",
    "f4-delivery-risk-evidence-accepted",
)


def main() -> int:
    actual_names = tuple(name for name, _mutate, _expected, _markers in CASES)
    if actual_names != EXPECTED_CASE_NAMES or len(set(actual_names)) != len(actual_names):
        raise RuntimeError("regression case manifest drift")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    results: list[dict[str, Any]] = []

    for name, mutate, expected, markers in CASES:
        record = copy.deepcopy(source)
        mutate(record)
        fixture = OUT / f"{name}.json"
        log = OUT / f"{name}.txt"
        fixture.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(GATEWAY), "ai-designed-molecule", str(fixture)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log.write_text(completed.stdout, encoding="utf-8")

        if expected == "BLOCK":
            verdict_marker = f"BLOCK {fixture}"
            verdict_index = completed.stdout.find(verdict_marker)
            relevant_output = completed.stdout[verdict_index:] if verdict_index >= 0 else completed.stdout
            ok = (
                completed.returncode != 0
                and verdict_index >= 0
                and "Traceback" not in relevant_output
                and all(marker in relevant_output for marker in markers)
            )
        elif expected == "ACCEPT":
            verdict_marker = f"ACCEPT {fixture}"
            verdict_index = completed.stdout.find(verdict_marker)
            relevant_output = completed.stdout[verdict_index:] if verdict_index >= 0 else completed.stdout
            ok = (
                completed.returncode == 0
                and verdict_index >= 0
                and "Traceback" not in relevant_output
                and all(marker in relevant_output for marker in markers)
            )
        else:
            raise RuntimeError(f"unknown expected verdict: {expected}")

        if f"BLOCK {fixture}" in completed.stdout:
            observed = "BLOCK"
        elif f"ACCEPT {fixture}" in completed.stdout:
            observed = "ACCEPT"
        else:
            observed = "NO_VERDICT"

        results.append(
            {
                "case": name,
                "expected": expected,
                "verdict_observed": observed,
                "markers": list(markers),
                "passed": ok,
            }
        )
        print(f"{'PASS' if ok else 'FAIL'} {name} expected={expected}")
        if not ok:
            print(completed.stdout)

    result_path = OUT / "results.json"
    result_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
