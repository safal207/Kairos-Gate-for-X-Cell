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


CASES: list[tuple[str, Mutation, tuple[str, ...]]] = [
    (
        "protected-supported",
        mutate_protected_supported,
        ("universal_superiority", "must be blocked or not established"),
    ),
    (
        "comparator-mismatch",
        mutate_comparator_mismatch,
        ("every referenced assay must use named comparator",),
    ),
    (
        "structured-predicate-mismatch",
        mutate_structured_predicate,
        ("claim_predicate", "was expected"),
    ),
    (
        "publication-mislabeled-f3",
        mutate_publication_as_f3,
        ("F3 requires a digested executable or reproducibility artifact",),
    ),
    (
        "replication-below-f5",
        mutate_replication_not_f5,
        ("independent_replication requires F5 independent-laboratory evidence",),
    ),
    (
        "invented-replication-reference",
        mutate_invented_replication_ref,
        ("must resolve to external evidence objects",),
    ),
    (
        "platform-insufficient-coverage",
        mutate_platform_insufficient_coverage,
        ("at least two target_classes",),
    ),
    (
        "unreconciled-denominator",
        mutate_unreconciled_denominator,
        ("generated = excluded_before_screen + screened",),
    ),
    (
        "risk-wrong-endpoint",
        mutate_risk_wrong_endpoint,
        ("risk delivery: established status requires risk-specific F4+ evidence",),
    ),
    (
        "zero-selected-candidates",
        mutate_zero_selected,
        ("require positive selected candidates",),
    ),
    (
        "structural-assay-relabelled-as-delivery",
        mutate_structural_assay_relabelled_as_delivery,
        ("structural assay endpoints must be exactly structural_characterization",),
    ),
    (
        "partial-impossible-counts",
        mutate_partial_impossible_counts,
        ("screened_count cannot exceed generated_count", "selected_count cannot exceed screened_count"),
    ),
    (
        "f5-artifact-kind-mismatch",
        mutate_f5_artifact_kind_mismatch,
        ("platform_generalization requires matching F5 replication artifact",),
    ),
]


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    results: list[dict[str, Any]] = []

    for name, mutate, markers in CASES:
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
        block_marker = f"BLOCK {fixture}"
        block_index = completed.stdout.find(block_marker)
        relevant_output = completed.stdout[block_index:] if block_index >= 0 else completed.stdout
        ok = (
            completed.returncode != 0
            and block_index >= 0
            and "Traceback" not in relevant_output
            and all(marker in relevant_output for marker in markers)
        )
        results.append(
            {
                "case": name,
                "blocked": completed.returncode != 0,
                "markers": list(markers),
                "passed": ok,
            }
        )
        print(f"{'PASS' if ok else 'FAIL'} {name}")
        if not ok:
            print(completed.stdout)

    result_path = OUT / "results.json"
    result_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
