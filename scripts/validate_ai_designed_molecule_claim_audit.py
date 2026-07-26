#!/usr/bin/env python3
"""Validate AI-designed molecule claim audits with fail-closed boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "case_id",
    "source_publication",
    "designed_system",
    "screening_context",
    "assays",
    "claim_audit",
    "mechanism_evidence",
    "replication_status",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}

EVIDENCE_ORDER = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}
SUPPORTED_TYPES = {
    "molecular_activity",
    "bounded_comparator_superiority",
    "structural_characterization",
}
REQUIRED_CLAIM_TYPES = {
    "molecular_activity",
    "bounded_comparator_superiority",
    "structural_characterization",
    "platform_generalization",
    "universal_superiority",
    "clinical_safety",
    "therapeutic_efficacy",
    "agricultural_readiness",
    "independent_replication",
    "ai_autonomy",
    "physical_authorization",
}
PROHIBITED_SUPPORTED_TYPES = {
    "universal_superiority",
    "clinical_safety",
    "therapeutic_efficacy",
    "agricultural_readiness",
    "ai_autonomy",
    "physical_authorization",
}
FUNCTIONAL_SYSTEMS = {"bacterial_cells", "plant_cells", "human_cells", "other"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append a validation error when a required condition is false."""
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    """Load one audit record as a JSON object."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("AI-designed molecule audit root must be a JSON object")
    return value


def validate(record: dict[str, Any]) -> list[str]:
    """Return all semantic contract violations for one audit record."""
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(
        record.get("schema_version") == "0.2.0-preview.1",
        "schema_version must be 0.2.0-preview.1",
        errors,
    )
    require(bool(record.get("case_id")), "case_id is required", errors)
    require(bool(record.get("next_valid_action")), "next_valid_action is required", errors)

    publication = record.get("source_publication", {})
    require(isinstance(publication, dict), "source_publication must be an object", errors)
    if isinstance(publication, dict):
        require(bool(publication.get("title")), "source publication title is required", errors)
        require(bool(publication.get("doi")), "source publication DOI is required", errors)
        require(
            publication.get("publication_status") in {"peer_reviewed", "preprint", "other"},
            "invalid publication_status",
            errors,
        )

    designed = record.get("designed_system", {})
    require(isinstance(designed, dict), "designed_system must be an object", errors)
    comparator: dict[str, Any] = {}
    if isinstance(designed, dict):
        require(
            designed.get("generated_entity") == "protein_amino_acid_sequence",
            "AI output must be represented as a proposed protein amino-acid sequence",
            errors,
        )
        require(
            designed.get("physical_entity_created_by_laboratory") is True,
            "physical molecules must be attributed to laboratory creation and testing",
            errors,
        )
        comparator_value = designed.get("reference_comparator", {})
        require(isinstance(comparator_value, dict), "reference_comparator must be an object", errors)
        if isinstance(comparator_value, dict):
            comparator = comparator_value

    screening = record.get("screening_context", {})
    require(isinstance(screening, dict), "screening_context must be an object", errors)
    selection_status = None
    if isinstance(screening, dict):
        generation_scale = screening.get("generation_scale")
        generated = screening.get("generated_count")
        screened = screening.get("screened_count")
        selected = screening.get("selected_count")
        denominator = screening.get("denominator_completeness")
        prespecified = screening.get("winner_selection_prespecified")
        failed_reporting = screening.get("failed_candidate_reporting")
        selection_status = screening.get("selection_bias_status")

        if generation_scale == "exact_count_reported":
            require(isinstance(generated, int), "exact_count_reported requires generated_count", errors)
        if generation_scale in {"reported_as_thousands", "reported_as_many", "unknown"}:
            require(generated is None, "non-exact generation scale must not invent generated_count", errors)
        if isinstance(generated, int) and isinstance(screened, int):
            require(screened <= generated, "screened_count cannot exceed generated_count", errors)
        if isinstance(screened, int) and isinstance(selected, int):
            require(selected <= screened, "selected_count cannot exceed screened_count", errors)
        if denominator == "complete":
            require(isinstance(generated, int), "complete denominator requires generated_count", errors)
            require(isinstance(screened, int), "complete denominator requires screened_count", errors)
            require(failed_reporting == "complete", "complete denominator requires complete failed-candidate reporting", errors)
        if selection_status == "LOW":
            require(denominator == "complete", "LOW selection bias requires a complete denominator", errors)
            require(prespecified is True, "LOW selection bias requires prespecified winner selection", errors)

    assays = record.get("assays", [])
    require(isinstance(assays, list) and bool(assays), "assays must be a non-empty array", errors)
    assay_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(assays, list):
        for index, assay in enumerate(assays):
            require(isinstance(assay, dict), f"assays[{index}] must be an object", errors)
            if not isinstance(assay, dict):
                continue
            assay_id = assay.get("assay_id")
            require(bool(assay_id), f"assays[{index}].assay_id is required", errors)
            if assay_id:
                require(assay_id not in assay_by_id, f"duplicate assay_id: {assay_id}", errors)
                assay_by_id[str(assay_id)] = assay
            evidence = assay.get("evidence_level")
            require(evidence in EVIDENCE_ORDER, f"assay {assay_id}: invalid evidence_level", errors)
            unit_status = assay.get("biological_unit_status")
            independent_n = assay.get("independent_biological_n")
            if unit_status == "established":
                require(
                    isinstance(independent_n, int) and not isinstance(independent_n, bool) and independent_n > 0,
                    f"assay {assay_id}: established biological unit requires positive independent N",
                    errors,
                )
            if unit_status in {"unresolved", "not_applicable"}:
                require(independent_n is None, f"assay {assay_id}: unresolved or non-applicable unit must not invent independent N", errors)

    mechanism = record.get("mechanism_evidence", {})
    require(isinstance(mechanism, dict), "mechanism_evidence must be an object", errors)
    if isinstance(mechanism, dict):
        require(
            mechanism.get("functional_causality_identified") is False,
            "structural characterization must not claim identified functional causality",
            errors,
        )

    replication = record.get("replication_status", {})
    require(isinstance(replication, dict), "replication_status must be an object", errors)
    independent_replication = None
    same_collaboration_only = None
    if isinstance(replication, dict):
        independent_replication = replication.get("independent_replication")
        same_collaboration_only = replication.get("same_collaboration_only")
        if independent_replication == "established":
            require(same_collaboration_only is False, "independent replication cannot be same-collaboration only", errors)

    claims = record.get("claim_audit", [])
    require(isinstance(claims, list) and bool(claims), "claim_audit must be a non-empty array", errors)
    supported_claims = 0
    observed_claim_types: set[str] = set()
    if isinstance(claims, list):
        seen_claims: set[str] = set()
        for index, claim in enumerate(claims):
            require(isinstance(claim, dict), f"claim_audit[{index}] must be an object", errors)
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("claim_id")
            claim_type = claim.get("claim_type")
            status = claim.get("status")
            scope = claim.get("comparator_scope")
            refs = claim.get("evidence_refs", [])

            require(bool(claim_id), f"claim_audit[{index}].claim_id is required", errors)
            if claim_id:
                require(claim_id not in seen_claims, f"duplicate claim_id: {claim_id}", errors)
                seen_claims.add(str(claim_id))
            if isinstance(claim_type, str):
                observed_claim_types.add(claim_type)
            require(isinstance(refs, list) and bool(refs), f"claim {claim_id}: evidence_refs must be non-empty", errors)
            claim_assays: list[dict[str, Any]] = []
            if isinstance(refs, list):
                for ref in refs:
                    require(ref == "publication" or ref in assay_by_id, f"claim {claim_id}: unknown evidence ref {ref}", errors)
                    if ref in assay_by_id:
                        claim_assays.append(assay_by_id[ref])

            if status == "supported_with_limits":
                supported_claims += 1
                require(claim_type in SUPPORTED_TYPES, f"claim {claim_id}: {claim_type} cannot be supported by this preview contract", errors)

            if claim_type in PROHIBITED_SUPPORTED_TYPES:
                require(status in {"not_established", "blocked"}, f"claim {claim_id}: {claim_type} must be blocked or not established", errors)

            if claim_type == "universal_superiority":
                require(status == "blocked", f"claim {claim_id}: universal superiority must be blocked", errors)
                require(scope in {"cas9_or_cas12", "all_natural_editors"}, f"claim {claim_id}: universal-superiority scope must name the broader comparator", errors)

            if claim_type in {"ai_autonomy", "physical_authorization"}:
                require(status == "blocked", f"claim {claim_id}: {claim_type} must be blocked", errors)

            if claim_type == "bounded_comparator_superiority" and status == "supported_with_limits":
                require(scope in {"wild_type_same_family", "specific_test_context"}, f"claim {claim_id}: superiority must remain comparator-bounded", errors)
                require(comparator.get("comparator_class") == "wild_type_same_family", f"claim {claim_id}: supported superiority requires a wild-type same-family comparator", errors)
                require(comparator.get("scope") == "test_context_bounded", f"claim {claim_id}: supported superiority requires test-context-bounded scope", errors)
                require(selection_status != "BLOCK", f"claim {claim_id}: blocked selection-bias status cannot support superiority", errors)
                require(bool(claim_assays), f"claim {claim_id}: supported superiority must reference a functional assay", errors)
                comparator_name = comparator.get("name")
                require(
                    all(assay.get("comparator") == comparator_name for assay in claim_assays),
                    f"claim {claim_id}: every referenced assay must use the named comparator",
                    errors,
                )
                exceeded = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and assay.get("result_direction") == "exceeded_reference_activity"
                    and EVIDENCE_ORDER.get(assay.get("evidence_level"), -1) >= EVIDENCE_ORDER["F3"]
                ]
                require(bool(exceeded), f"claim {claim_id}: no referenced F3+ functional assay exceeds the named reference", errors)

            if claim_type == "molecular_activity" and status == "supported_with_limits":
                active = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and assay.get("result_direction") in {"retained_reference_activity", "exceeded_reference_activity", "mixed"}
                    and EVIDENCE_ORDER.get(assay.get("evidence_level"), -1) >= EVIDENCE_ORDER["F3"]
                ]
                require(bool(active), f"claim {claim_id}: molecular activity support requires a referenced F3+ functional assay", errors)

            if claim_type == "structural_characterization" and status == "supported_with_limits":
                structural_assays = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") == "cryo_em_structure"
                    and assay.get("result_direction") == "structural_observation"
                    and EVIDENCE_ORDER.get(assay.get("evidence_level"), -1) >= EVIDENCE_ORDER["F3"]
                ]
                require(bool(structural_assays), f"claim {claim_id}: structural support requires a referenced F3+ cryo-EM assay", errors)
                require(isinstance(mechanism, dict) and mechanism.get("cryo_em_characterized") is True, f"claim {claim_id}: structural support requires cryo-EM characterization", errors)
                require(isinstance(mechanism, dict) and mechanism.get("status") == "structural_contacts_observed", f"claim {claim_id}: structural claim exceeds recorded mechanism evidence", errors)

            if claim_type == "independent_replication":
                if independent_replication != "established" or same_collaboration_only is not False:
                    require(status in {"not_established", "blocked"}, f"claim {claim_id}: independent replication is not established", errors)

            if claim_type == "platform_generalization":
                require(status in {"not_established", "blocked"}, f"claim {claim_id}: platform generalization is outside the supported preview scope", errors)

        missing_claim_types = sorted(REQUIRED_CLAIM_TYPES - observed_claim_types)
        require(
            not missing_claim_types,
            f"claim firewall missing required claim types: {missing_claim_types}",
            errors,
        )

    overall = record.get("overall_verdict")
    require(overall in {"ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}, "invalid overall_verdict", errors)
    if overall == "ACCEPT_WITH_LIMITS":
        require(supported_claims > 0, "ACCEPT_WITH_LIMITS requires at least one bounded supported claim", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_documentary_only", "safety mode must be computational_documentary_only", errors)
        require(safety.get("physical_biology_authorized") is False, "physical biology must remain unauthorized", errors)
        require(safety.get("physical_protocol_included") is False, "physical protocols must not be included", errors)
        require(safety.get("sequence_instructions_included") is False, "sequence instructions must not be included", errors)
        require(safety.get("clinical_or_field_use_authorized") is False, "clinical or field use must remain unauthorized", errors)

    return errors


def main(argv: list[str]) -> int:
    """Validate each path from argv and return a fail-closed process code."""
    if len(argv) < 2:
        print(
            "usage: validate_ai_designed_molecule_claim_audit.py AUDIT.json [AUDIT.json ...]",
            file=sys.stderr,
        )
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
