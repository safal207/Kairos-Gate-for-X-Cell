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
    "platform_generalization",
    "independent_replication",
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
CLAIM_SEMANTICS: dict[str, tuple[str, str]] = {
    "molecular_activity": (
        "designed_molecule",
        "has_bounded_molecular_activity",
    ),
    "bounded_comparator_superiority": (
        "selected_variants",
        "exceeds_named_comparator_in_test_context",
    ),
    "structural_characterization": (
        "selected_variant_structure",
        "has_selected_variant_structural_contacts",
    ),
    "platform_generalization": (
        "design_platform",
        "generalizes_across_targets_labs_delivery_populations",
    ),
    "universal_superiority": (
        "designed_molecule",
        "outperforms_cas9_cas12_or_all_natural_editors",
    ),
    "clinical_safety": ("designed_molecule", "is_clinically_safe"),
    "therapeutic_efficacy": (
        "designed_molecule",
        "has_therapeutic_efficacy",
    ),
    "agricultural_readiness": (
        "designed_molecule",
        "is_ready_for_agricultural_deployment",
    ),
    "independent_replication": (
        "study_findings",
        "has_unrelated_laboratory_replication",
    ),
    "ai_autonomy": (
        "ai_system",
        "was_created_and_validated_autonomously_by_ai",
    ),
    "physical_authorization": (
        "audit_record",
        "authorizes_physical_biology",
    ),
}
SUPPORTED_STATEMENT_PROHIBITED_MARKERS = {
    "cas9",
    "cas12",
    "all natural",
    "all editors",
    "universal",
    "clinically",
    "clinical",
    "therapeutic",
    "treatment",
    "patient",
    "safe for",
    "proven safe",
    "agricultur",
    "field-ready",
    "field ready",
    "deployment-ready",
    "deployment ready",
    "autonomous",
    "without human",
    "authorizes",
    "authorized",
    "best editor",
}
FUNCTIONAL_SYSTEMS = {"bacterial_cells", "plant_cells", "human_cells", "other"}
POSITIVE_SELECTION_STATES = {"positive_exact", "positive_nonexact"}


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


def replication_evidence_complete(value: Any) -> bool:
    """Return whether structured unrelated-laboratory evidence is complete."""
    if not isinstance(value, dict):
        return False
    refs = value.get("evidence_refs")
    return (
        bool(value.get("unrelated_laboratory_identity"))
        and value.get("independent_materials") is True
        and bool(value.get("replication_unit"))
        and isinstance(refs, list)
        and bool(refs)
        and value.get("evidence_level") in {"F3", "F4", "F5"}
    )


def validate(record: dict[str, Any]) -> list[str]:
    """Return all semantic contract violations for one audit record."""
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(
        record.get("schema_version") == "0.2.0-preview.2",
        "schema_version must be 0.2.0-preview.2",
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
    selected_count = None
    if isinstance(screening, dict):
        generation_scale = screening.get("generation_scale")
        generated = screening.get("generated_count")
        screened = screening.get("screened_count")
        selected_count = screening.get("selected_count")
        selection_status = screening.get("selected_count_status")
        denominator = screening.get("denominator_completeness")
        prespecified = screening.get("winner_selection_prespecified")
        failed_reporting = screening.get("failed_candidate_reporting")
        selection_bias = screening.get("selection_bias_status")

        if generation_scale == "exact_count_reported":
            require(
                isinstance(generated, int) and not isinstance(generated, bool),
                "exact_count_reported requires generated_count",
                errors,
            )
        if generation_scale in {"reported_as_thousands", "reported_as_many", "unknown"}:
            require(
                generated is None,
                "non-exact generation scale must not invent generated_count",
                errors,
            )
        if isinstance(generated, int) and isinstance(screened, int):
            require(screened <= generated, "screened_count cannot exceed generated_count", errors)
        if isinstance(screened, int) and isinstance(selected_count, int):
            require(selected_count <= screened, "selected_count cannot exceed screened_count", errors)

        if selection_status == "positive_exact":
            require(
                isinstance(selected_count, int)
                and not isinstance(selected_count, bool)
                and selected_count > 0,
                "positive_exact requires a positive selected_count",
                errors,
            )
        elif selection_status == "zero_exact":
            require(selected_count == 0, "zero_exact requires selected_count=0", errors)
        elif selection_status in {"positive_nonexact", "unknown"}:
            require(selected_count is None, f"{selection_status} requires selected_count=null", errors)
        else:
            errors.append("invalid selected_count_status")

        if denominator == "complete":
            require(isinstance(generated, int), "complete denominator requires generated_count", errors)
            require(isinstance(screened, int), "complete denominator requires screened_count", errors)
            require(
                selection_status in {"positive_exact", "zero_exact"},
                "complete denominator requires an exact selected-count status",
                errors,
            )
            require(
                failed_reporting == "complete",
                "complete denominator requires complete failed-candidate reporting",
                errors,
            )
        if selection_bias == "LOW":
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
                    isinstance(independent_n, int)
                    and not isinstance(independent_n, bool)
                    and independent_n > 0,
                    f"assay {assay_id}: established biological unit requires positive independent N",
                    errors,
                )
            if unit_status in {"unresolved", "not_applicable"}:
                require(
                    independent_n is None,
                    f"assay {assay_id}: unresolved or non-applicable unit must not invent independent N",
                    errors,
                )

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
    replication_evidence: Any = None
    replication_refs: set[str] = set()
    if isinstance(replication, dict):
        independent_replication = replication.get("independent_replication")
        same_collaboration_only = replication.get("same_collaboration_only")
        replication_evidence = replication.get("replication_evidence")
        if independent_replication == "established":
            require(
                same_collaboration_only is False,
                "independent replication cannot be same-collaboration only",
                errors,
            )
            require(
                replication_evidence_complete(replication_evidence),
                "established independent replication requires complete structured evidence",
                errors,
            )
            if isinstance(replication_evidence, dict):
                raw_refs = replication_evidence.get("evidence_refs", [])
                if isinstance(raw_refs, list):
                    replication_refs = {str(ref) for ref in raw_refs}
        else:
            require(
                replication_evidence is None,
                "non-established replication status requires replication_evidence=null",
                errors,
            )

    claims = record.get("claim_audit", [])
    require(isinstance(claims, list) and bool(claims), "claim_audit must be a non-empty array", errors)
    supported_claims = 0
    selected_candidate_support = False
    observed_claim_types: set[str] = set()
    if isinstance(claims, list):
        seen_claims: set[str] = set()
        for index, claim in enumerate(claims):
            require(isinstance(claim, dict), f"claim_audit[{index}] must be an object", errors)
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("claim_id")
            claim_type = claim.get("claim_type")
            claim_subject = claim.get("claim_subject")
            claim_predicate = claim.get("claim_predicate")
            status = claim.get("status")
            scope = claim.get("comparator_scope")
            statement = claim.get("statement")
            refs = claim.get("evidence_refs", [])

            require(bool(claim_id), f"claim_audit[{index}].claim_id is required", errors)
            if claim_id:
                require(claim_id not in seen_claims, f"duplicate claim_id: {claim_id}", errors)
                seen_claims.add(str(claim_id))
            if isinstance(claim_type, str):
                observed_claim_types.add(claim_type)

            expected_semantics = CLAIM_SEMANTICS.get(str(claim_type))
            require(
                expected_semantics is not None,
                f"claim {claim_id}: unknown structured claim type",
                errors,
            )
            if expected_semantics is not None:
                require(
                    (claim_subject, claim_predicate) == expected_semantics,
                    f"claim {claim_id}: structured subject/predicate do not match {claim_type}",
                    errors,
                )

            require(isinstance(refs, list) and bool(refs), f"claim {claim_id}: evidence_refs must be non-empty", errors)
            claim_assays: list[dict[str, Any]] = []
            if isinstance(refs, list):
                for ref in refs:
                    require(
                        ref == "publication" or ref in assay_by_id or ref in replication_refs,
                        f"claim {claim_id}: unknown evidence ref {ref}",
                        errors,
                    )
                    if ref in assay_by_id:
                        claim_assays.append(assay_by_id[ref])

            if status == "supported_with_limits":
                supported_claims += 1
                require(
                    claim_type in SUPPORTED_TYPES,
                    f"claim {claim_id}: {claim_type} cannot be supported by this preview contract",
                    errors,
                )
                lowered_statement = statement.lower() if isinstance(statement, str) else ""
                found_markers = sorted(
                    marker
                    for marker in SUPPORTED_STATEMENT_PROHIBITED_MARKERS
                    if marker in lowered_statement
                )
                require(
                    not found_markers,
                    f"claim {claim_id}: supported statement contains prohibited escalation markers: {found_markers}",
                    errors,
                )

            if claim_type in PROHIBITED_SUPPORTED_TYPES:
                require(
                    status in {"not_established", "blocked"},
                    f"claim {claim_id}: {claim_type} must be blocked or not established",
                    errors,
                )

            if claim_type == "universal_superiority":
                require(status == "blocked", f"claim {claim_id}: universal superiority must be blocked", errors)
                require(
                    scope in {"cas9_or_cas12", "all_natural_editors"},
                    f"claim {claim_id}: universal-superiority scope must name the broader comparator",
                    errors,
                )

            if claim_type in {"ai_autonomy", "physical_authorization"}:
                require(status == "blocked", f"claim {claim_id}: {claim_type} must be blocked", errors)

            if claim_type == "bounded_comparator_superiority" and status == "supported_with_limits":
                selected_candidate_support = True
                require(
                    scope in {"wild_type_same_family", "specific_test_context"},
                    f"claim {claim_id}: superiority must remain comparator-bounded",
                    errors,
                )
                require(
                    comparator.get("comparator_class") == "wild_type_same_family",
                    f"claim {claim_id}: supported superiority requires a wild-type same-family comparator",
                    errors,
                )
                require(
                    comparator.get("scope") == "test_context_bounded",
                    f"claim {claim_id}: supported superiority requires test-context-bounded scope",
                    errors,
                )
                require(
                    screening.get("selection_bias_status") != "BLOCK" if isinstance(screening, dict) else False,
                    f"claim {claim_id}: blocked selection-bias status cannot support superiority",
                    errors,
                )
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
                require(
                    bool(exceeded),
                    f"claim {claim_id}: no referenced F3+ functional assay exceeds the named reference",
                    errors,
                )

            if claim_type == "molecular_activity" and status == "supported_with_limits":
                selected_candidate_support = True
                active = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and assay.get("result_direction")
                    in {"retained_reference_activity", "exceeded_reference_activity", "mixed"}
                    and EVIDENCE_ORDER.get(assay.get("evidence_level"), -1) >= EVIDENCE_ORDER["F3"]
                ]
                require(
                    bool(active),
                    f"claim {claim_id}: molecular activity support requires a referenced F3+ functional assay",
                    errors,
                )

            if claim_type == "structural_characterization" and status == "supported_with_limits":
                selected_candidate_support = True
                structural_assays = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") == "cryo_em_structure"
                    and assay.get("result_direction") == "structural_observation"
                    and EVIDENCE_ORDER.get(assay.get("evidence_level"), -1) >= EVIDENCE_ORDER["F3"]
                ]
                require(
                    bool(structural_assays),
                    f"claim {claim_id}: structural support requires a referenced F3+ cryo-EM assay",
                    errors,
                )
                require(
                    isinstance(mechanism, dict) and mechanism.get("cryo_em_characterized") is True,
                    f"claim {claim_id}: structural support requires cryo-EM characterization",
                    errors,
                )
                require(
                    isinstance(mechanism, dict) and mechanism.get("status") == "structural_contacts_observed",
                    f"claim {claim_id}: structural claim exceeds recorded mechanism evidence",
                    errors,
                )

            if claim_type in {"independent_replication", "platform_generalization"}:
                if status == "supported_with_limits":
                    require(
                        independent_replication == "established"
                        and same_collaboration_only is False
                        and replication_evidence_complete(replication_evidence),
                        f"claim {claim_id}: supported {claim_type} requires structured unrelated-laboratory replication evidence",
                        errors,
                    )
                    require(
                        replication_refs.issubset({str(ref) for ref in refs}),
                        f"claim {claim_id}: supported {claim_type} must reference the replication evidence",
                        errors,
                    )
                elif independent_replication != "established":
                    require(
                        status in {"not_established", "blocked"},
                        f"claim {claim_id}: {claim_type} is not established",
                        errors,
                    )

        missing_claim_types = sorted(REQUIRED_CLAIM_TYPES - observed_claim_types)
        require(
            not missing_claim_types,
            f"claim firewall missing required claim types: {missing_claim_types}",
            errors,
        )

    if selected_candidate_support:
        require(
            selection_status in POSITIVE_SELECTION_STATES,
            "supported activity, superiority, or selected-structure claims require positive selected candidates",
            errors,
        )
        if selection_status == "positive_exact":
            require(
                isinstance(selected_count, int) and selected_count > 0,
                "positive_exact supported claims require selected_count > 0",
                errors,
            )

    overall = record.get("overall_verdict")
    require(overall in {"ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}, "invalid overall_verdict", errors)
    if overall == "ACCEPT_WITH_LIMITS":
        require(
            supported_claims > 0,
            "ACCEPT_WITH_LIMITS requires at least one bounded supported claim",
            errors,
        )

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(
            safety.get("mode") == "computational_documentary_only",
            "safety mode must be computational_documentary_only",
            errors,
        )
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
