#!/usr/bin/env python3
"""Validate AI-designed molecule claim audits with fail-closed evidence boundaries."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = "0.2.0-preview.4"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "case_id",
    "source_publication",
    "designed_system",
    "screening_context",
    "assays",
    "external_evidence",
    "claim_audit",
    "risk_assessment",
    "mechanism_evidence",
    "replication_status",
    "overall_verdict",
    "next_valid_action",
    "safety_status",
}
EVIDENCE_ORDER = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}
FUNCTIONAL_SYSTEMS = {"bacterial_cells", "plant_cells", "human_cells", "other"}
FUNCTIONAL_ENDPOINTS = {"molecular_activity", "bounded_comparator_superiority"}
DESIGNED_TEST_SUBJECTS = {"designed_candidates", "selected_variants"}
POSITIVE_SELECTION_STATES = {"positive_exact", "positive_nonexact"}
SUPPORTED_TYPES = {
    "molecular_activity",
    "bounded_comparator_superiority",
    "structural_characterization",
    "platform_generalization",
    "independent_replication",
}
PROTECTED_TYPES = {
    "universal_superiority",
    "clinical_safety",
    "therapeutic_efficacy",
    "agricultural_readiness",
    "ai_autonomy",
    "physical_authorization",
}
CLAIM_SEMANTICS: dict[str, tuple[str, str]] = {
    "molecular_activity": ("designed_molecule", "has_bounded_molecular_activity"),
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
    "therapeutic_efficacy": ("designed_molecule", "has_therapeutic_efficacy"),
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
    "physical_authorization": ("audit_record", "authorizes_physical_biology"),
}
CLAIM_COMPARATOR_SCOPES: dict[str, set[str]] = {
    "molecular_activity": {"specific_test_context"},
    "bounded_comparator_superiority": {"wild_type_same_family"},
    "structural_characterization": {"specific_test_context"},
    "platform_generalization": {"not_applicable"},
    "universal_superiority": {"cas9_or_cas12", "all_natural_editors"},
    "clinical_safety": {"not_applicable"},
    "therapeutic_efficacy": {"not_applicable"},
    "agricultural_readiness": {"not_applicable"},
    "independent_replication": {"not_applicable"},
    "ai_autonomy": {"not_applicable"},
    "physical_authorization": {"not_applicable"},
}
REQUIRED_CLAIM_TYPES = set(CLAIM_SEMANTICS)
RISK_DIMENSIONS = {
    "specificity_off_target",
    "delivery",
    "immunogenicity",
    "toxicity",
    "durability",
    "ecological_safety",
}
RISK_MIN_LEVEL = {
    "specificity_off_target": "F3",
    "delivery": "F4",
    "immunogenicity": "F4",
    "toxicity": "F4",
    "durability": "F4",
    "ecological_safety": "F5",
}
COVERAGE_DIMENSIONS = (
    "target_classes",
    "laboratories",
    "delivery_systems",
    "organisms",
    "populations",
)
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("AI-designed molecule audit root must be a JSON object")
    return value


def evidence_level(value: Any) -> int:
    return EVIDENCE_ORDER.get(str(value), -1)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def complete_independence(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value.get("unrelated_laboratory_identity"))
        and value.get("independent_materials") is True
        and bool(value.get("replication_unit"))
    )


def validate(
    record: dict[str, Any],
    *,
    provenance_rule: Callable[..., None],
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - record.keys())
    require(not missing, f"missing required fields: {missing}", errors)
    require(record.get("schema_version") == SCHEMA_VERSION, f"schema_version must be {SCHEMA_VERSION}", errors)
    require(bool(record.get("case_id")), "case_id is required", errors)
    require(bool(record.get("next_valid_action")), "next_valid_action is required", errors)

    publication = record.get("source_publication", {})
    require(isinstance(publication, dict), "source_publication must be an object", errors)
    publication_urls: set[str] = set()
    publication_peer_reviewed = False
    if isinstance(publication, dict):
        require(bool(publication.get("title")), "source publication title is required", errors)
        require(bool(publication.get("doi")), "source publication DOI is required", errors)
        publication_peer_reviewed = publication.get("publication_status") == "peer_reviewed"
        urls = publication.get("source_urls", [])
        require(isinstance(urls, list) and bool(urls), "source_urls must be non-empty", errors)
        if isinstance(urls, list):
            publication_urls = {str(url) for url in urls}

    designed = record.get("designed_system", {})
    require(isinstance(designed, dict), "designed_system must be an object", errors)
    comparator: dict[str, Any] = {}
    if isinstance(designed, dict):
        require(
            designed.get("generated_entity") == "protein_amino_acid_sequence",
            "AI output must be a proposed protein amino-acid sequence",
            errors,
        )
        require(
            designed.get("physical_entity_created_by_laboratory") is True,
            "physical molecules must be attributed to laboratory creation and testing",
            errors,
        )
        value = designed.get("reference_comparator", {})
        require(isinstance(value, dict), "reference_comparator must be an object", errors)
        if isinstance(value, dict):
            comparator = value

    screening = record.get("screening_context", {})
    require(isinstance(screening, dict), "screening_context must be an object", errors)
    selection_status = None
    if isinstance(screening, dict):
        generation_scale = screening.get("generation_scale")
        generated = screening.get("generated_count")
        excluded = screening.get("excluded_before_screen_count")
        screened = screening.get("screened_count")
        failed = screening.get("failed_screen_count")
        selected_count = screening.get("selected_count")
        selection_status = screening.get("selected_count_status")
        denominator = screening.get("denominator_completeness")
        prespecified = screening.get("winner_selection_prespecified")
        failed_reporting = screening.get("failed_candidate_reporting")
        selection_bias = screening.get("selection_bias_status")

        exact_fields = [generated, excluded, screened, failed, selected_count]
        if generation_scale == "exact_count_reported":
            require(is_int(generated), "exact_count_reported requires generated_count", errors)
        else:
            require(generated is None, "non-exact generation scale must not invent generated_count", errors)

        if selection_status == "positive_exact":
            require(is_int(selected_count) and selected_count > 0, "positive_exact requires selected_count > 0", errors)
        elif selection_status == "zero_exact":
            require(selected_count == 0, "zero_exact requires selected_count=0", errors)
        elif selection_status in {"positive_nonexact", "unknown"}:
            require(selected_count is None, f"{selection_status} requires selected_count=null", errors)
        else:
            errors.append("invalid selected_count_status")

        # Known counts must remain physically possible even when the denominator is partial.
        if is_int(generated) and is_int(screened):
            require(screened <= generated, "screened_count cannot exceed generated_count", errors)
        if is_int(screened) and is_int(selected_count):
            require(selected_count <= screened, "selected_count cannot exceed screened_count", errors)
        if is_int(generated) and is_int(selected_count):
            require(selected_count <= generated, "selected_count cannot exceed generated_count", errors)
        if is_int(excluded) and is_int(generated):
            require(excluded <= generated, "excluded_before_screen_count cannot exceed generated_count", errors)
        if is_int(failed) and is_int(screened):
            require(failed <= screened, "failed_screen_count cannot exceed screened_count", errors)
        if is_int(generated) and is_int(excluded) and is_int(screened):
            require(
                generated == excluded + screened,
                "known counts must reconcile generated = excluded_before_screen + screened",
                errors,
            )
        if is_int(screened) and is_int(failed) and is_int(selected_count):
            require(
                screened == failed + selected_count,
                "known counts must reconcile screened = failed_screen + selected",
                errors,
            )

        if denominator == "complete":
            require(
                all(is_int(value) for value in exact_fields),
                "complete denominator requires exact generated, excluded, screened, failed, and selected counts",
                errors,
            )
            if all(is_int(value) for value in exact_fields):
                require(
                    generated == excluded + screened,
                    "complete denominator must reconcile generated = excluded_before_screen + screened",
                    errors,
                )
                require(
                    screened == failed + selected_count,
                    "complete denominator must reconcile screened = failed_screen + selected",
                    errors,
                )
            require(
                selection_status in {"positive_exact", "zero_exact"},
                "complete denominator requires exact selected_count_status",
                errors,
            )
            require(
                failed_reporting == "complete",
                "complete denominator requires complete failed-candidate reporting",
                errors,
            )
        else:
            require(
                excluded is None and failed is None,
                "partial/unknown denominator must not invent reconciliation counts",
                errors,
            )

        if selection_bias == "LOW":
            require(denominator == "complete", "LOW selection bias requires complete denominator", errors)
            require(prespecified is True, "LOW selection bias requires prespecified selection", errors)

    assays = record.get("assays", [])
    require(isinstance(assays, list) and bool(assays), "assays must be non-empty", errors)
    assay_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(assays, list):
        for index, assay in enumerate(assays):
            require(isinstance(assay, dict), f"assays[{index}] must be an object", errors)
            if not isinstance(assay, dict):
                continue
            assay_id = str(assay.get("assay_id") or "")
            require(bool(assay_id), f"assays[{index}].assay_id is required", errors)
            require(assay_id not in assay_by_id, f"duplicate assay_id: {assay_id}", errors)
            if assay_id:
                assay_by_id[assay_id] = assay

            level = str(assay.get("evidence_level") or "")
            require(level in {"F0", "F1", "F2", "F3", "F4"}, f"assay {assay_id}: invalid evidence_level", errors)
            unit_status = assay.get("biological_unit_status")
            independent_n = assay.get("independent_biological_n")
            if unit_status == "established":
                require(is_int(independent_n) and independent_n > 0, f"assay {assay_id}: established unit requires positive independent N", errors)
            if unit_status in {"unresolved", "not_applicable"}:
                require(independent_n is None, f"assay {assay_id}: unresolved/non-applicable unit must not invent N", errors)

            endpoints = assay.get("endpoint_types", [])
            require(isinstance(endpoints, list) and bool(endpoints), f"assay {assay_id}: endpoint_types required", errors)
            endpoint_set = {str(endpoint) for endpoint in endpoints} if isinstance(endpoints, list) else set()
            system = assay.get("system")
            direction = assay.get("result_direction")
            tested_subject = assay.get("tested_subject")
            if system == "cryo_em_structure" or direction == "structural_observation":
                require(
                    system == "cryo_em_structure"
                    and direction == "structural_observation"
                    and endpoint_set == {"structural_characterization"},
                    f"assay {assay_id}: structural assay endpoints must be exactly structural_characterization",
                    errors,
                )
                require(
                    tested_subject == "selected_variant_structure",
                    f"assay {assay_id}: structural evidence must bind the selected variant structure",
                    errors,
                )
            else:
                require(system in FUNCTIONAL_SYSTEMS, f"assay {assay_id}: unsupported functional assay system", errors)
                require(
                    tested_subject in DESIGNED_TEST_SUBJECTS | {"reference_comparator_only"},
                    f"assay {assay_id}: functional evidence requires a controlled tested_subject",
                    errors,
                )
                require(
                    endpoint_set.issubset(FUNCTIONAL_ENDPOINTS),
                    f"assay {assay_id}: cellular activity assays cannot assert risk or structural endpoints",
                    errors,
                )
                require(
                    direction in {"retained_reference_activity", "exceeded_reference_activity", "mixed"},
                    f"assay {assay_id}: functional assay requires an activity result direction",
                    errors,
                )

            provenance_rule(
                level=level,
                provenance=assay.get("provenance"),
                publication_urls=publication_urls,
                context=f"assay {assay_id}",
                errors=errors,
                external=False,
            )

    external = record.get("external_evidence", [])
    require(isinstance(external, list), "external_evidence must be an array", errors)
    external_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(external, list):
        for index, item in enumerate(external):
            require(isinstance(item, dict), f"external_evidence[{index}] must be an object", errors)
            if not isinstance(item, dict):
                continue
            evidence_id = str(item.get("evidence_id") or "")
            require(bool(evidence_id), f"external_evidence[{index}].evidence_id required", errors)
            require(evidence_id not in external_by_id, f"duplicate external evidence_id: {evidence_id}", errors)
            if evidence_id:
                external_by_id[evidence_id] = item
            level = str(item.get("evidence_level") or "")
            require(level in {"F3", "F4", "F5"}, f"external evidence {evidence_id}: invalid evidence_level", errors)
            provenance_rule(
                level=level,
                provenance=item.get("provenance"),
                publication_urls=publication_urls,
                context=f"external evidence {evidence_id}",
                errors=errors,
                external=True,
            )
            endpoints = item.get("endpoint_types", [])
            require(isinstance(endpoints, list) and bool(endpoints), f"external evidence {evidence_id}: endpoint_types required", errors)
            endpoint_set = {str(endpoint) for endpoint in endpoints} if isinstance(endpoints, list) else set()
            kind = item.get("evidence_kind")
            provenance = item.get("provenance", {})
            artifact_kind = provenance.get("artifact_kind") if isinstance(provenance, dict) else None

            if kind == "independent_replication":
                require(
                    level == "F5"
                    and complete_independence(item.get("independence"))
                    and endpoint_set == {"independent_replication"}
                    and artifact_kind == "independent_replication_record",
                    f"external evidence {evidence_id}: independent_replication requires matching F5 replication artifact",
                    errors,
                )
                require(item.get("coverage") is None, f"external evidence {evidence_id}: replication evidence must not claim platform coverage", errors)
            elif kind == "platform_generalization":
                require(
                    level == "F5"
                    and complete_independence(item.get("independence"))
                    and endpoint_set == {"platform_generalization"}
                    and artifact_kind == "independent_replication_record",
                    f"external evidence {evidence_id}: platform_generalization requires matching F5 replication artifact",
                    errors,
                )
                require(isinstance(item.get("coverage"), dict), f"external evidence {evidence_id}: platform coverage required", errors)
            elif kind == "risk_assessment":
                require(
                    bool(endpoint_set) and endpoint_set.issubset(RISK_DIMENSIONS),
                    f"external evidence {evidence_id}: risk_assessment endpoints must be risk dimensions",
                    errors,
                )
                require(
                    artifact_kind == "risk_assessment_record",
                    f"external evidence {evidence_id}: risk_assessment requires risk_assessment_record",
                    errors,
                )
                if level == "F5":
                    require(
                        complete_independence(item.get("independence")),
                        f"external evidence {evidence_id}: F5 risk_assessment requires complete independence metadata",
                        errors,
                    )
                require(item.get("coverage") is None, f"external evidence {evidence_id}: risk evidence must not claim platform coverage", errors)
            elif kind == "reproducibility_artifact":
                require(
                    level in {"F3", "F4"},
                    f"external evidence {evidence_id}: reproducibility_artifact cannot mint F5",
                    errors,
                )
                require(
                    artifact_kind in {"executable_analysis", "reproducibility_bundle", "author_confirmation", "deposited_structure"},
                    f"external evidence {evidence_id}: reproducibility artifact kind mismatch",
                    errors,
                )
            else:
                errors.append(f"external evidence {evidence_id}: unknown evidence_kind")

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
            require(same_collaboration_only is False, "established replication cannot be same-collaboration", errors)
            require(isinstance(replication_evidence, dict), "established replication requires structured evidence", errors)
            if isinstance(replication_evidence, dict):
                require(replication_evidence.get("evidence_level") == "F5", "established replication requires F5", errors)
                refs = replication_evidence.get("evidence_refs", [])
                require(isinstance(refs, list) and bool(refs), "established replication requires evidence_refs", errors)
                if isinstance(refs, list):
                    replication_refs = {str(ref) for ref in refs}
                resolved = [external_by_id[ref] for ref in replication_refs if ref in external_by_id]
                require(
                    len(resolved) == len(replication_refs),
                    "established replication evidence refs must resolve to external evidence objects",
                    errors,
                )
                require(
                    bool(resolved)
                    and all(
                        item.get("evidence_kind") == "independent_replication"
                        and item.get("evidence_level") == "F5"
                        and complete_independence(item.get("independence"))
                        for item in resolved
                    ),
                    "established replication requires F5 independent_replication external evidence",
                    errors,
                )
                if resolved:
                    identity = replication_evidence.get("unrelated_laboratory_identity")
                    unit = replication_evidence.get("replication_unit")
                    require(
                        all(item.get("independence", {}).get("unrelated_laboratory_identity") == identity for item in resolved),
                        "replication laboratory identity must match external evidence",
                        errors,
                    )
                    require(
                        all(item.get("independence", {}).get("replication_unit") == unit for item in resolved),
                        "replication unit must match external evidence",
                        errors,
                    )
        else:
            require(replication_evidence is None, "non-established replication requires replication_evidence=null", errors)

    allowed_refs = {"publication", *assay_by_id, *external_by_id}
    claims = record.get("claim_audit", [])
    require(isinstance(claims, list) and bool(claims), "claim_audit must be non-empty", errors)
    claim_by_type: dict[str, dict[str, Any]] = {}
    supported_claims = 0
    selected_candidate_support = False
    if isinstance(claims, list):
        seen_ids: set[str] = set()
        for index, claim in enumerate(claims):
            require(isinstance(claim, dict), f"claim_audit[{index}] must be an object", errors)
            if not isinstance(claim, dict):
                continue
            claim_id = str(claim.get("claim_id") or "")
            claim_type = str(claim.get("claim_type") or "")
            status = claim.get("status")
            refs = claim.get("evidence_refs", [])
            require(bool(claim_id), f"claim_audit[{index}].claim_id required", errors)
            require(claim_id not in seen_ids, f"duplicate claim_id: {claim_id}", errors)
            seen_ids.add(claim_id)
            require(claim_type not in claim_by_type, f"duplicate claim_type: {claim_type}", errors)
            if claim_type:
                claim_by_type[claim_type] = claim

            expected = CLAIM_SEMANTICS.get(claim_type)
            require(expected is not None, f"claim {claim_id}: unknown claim_type", errors)
            if expected is not None:
                require(
                    (claim.get("claim_subject"), claim.get("claim_predicate")) == expected,
                    f"claim {claim_id}: structured subject/predicate mismatch",
                    errors,
                )
            expected_scopes = CLAIM_COMPARATOR_SCOPES.get(claim_type)
            if expected_scopes is not None:
                require(
                    claim.get("comparator_scope") in expected_scopes,
                    f"claim {claim_id}: comparator_scope is incompatible with {claim_type}",
                    errors,
                )

            require(isinstance(refs, list) and bool(refs), f"claim {claim_id}: evidence_refs required", errors)
            ref_set = {str(ref) for ref in refs} if isinstance(refs, list) else set()
            unknown = sorted(ref_set - allowed_refs)
            require(not unknown, f"claim {claim_id}: unknown evidence refs {unknown}", errors)
            claim_assays = [assay_by_id[ref] for ref in ref_set if ref in assay_by_id]
            claim_external = [external_by_id[ref] for ref in ref_set if ref in external_by_id]

            if status == "supported_with_limits":
                supported_claims += 1
                require(claim_type in SUPPORTED_TYPES, f"claim {claim_id}: {claim_type} cannot be supported in this preview", errors)

            if claim_type in PROTECTED_TYPES:
                require(status in {"not_established", "blocked"}, f"claim {claim_id}: {claim_type} must be blocked or not established", errors)
            if claim_type in {"universal_superiority", "ai_autonomy", "physical_authorization"}:
                require(status == "blocked", f"claim {claim_id}: {claim_type} must be blocked", errors)

            if claim_type == "molecular_activity" and status == "supported_with_limits":
                selected_candidate_support = True
                active = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and assay.get("tested_subject") in DESIGNED_TEST_SUBJECTS
                    and "molecular_activity" in assay.get("endpoint_types", [])
                    and assay.get("result_direction") in {"retained_reference_activity", "exceeded_reference_activity", "mixed"}
                    and evidence_level(assay.get("evidence_level")) >= EVIDENCE_ORDER["F2"]
                ]
                require(publication_peer_reviewed and bool(active), f"claim {claim_id}: peer-reviewed referenced F2+ molecular-activity evidence required", errors)

            if claim_type == "bounded_comparator_superiority" and status == "supported_with_limits":
                selected_candidate_support = True
                require(
                    comparator.get("comparator_class") == "wild_type_same_family"
                    and comparator.get("scope") == "test_context_bounded",
                    f"claim {claim_id}: comparator must be bounded wild-type same-family",
                    errors,
                )
                require(
                    claim.get("comparator_scope") == comparator.get("comparator_class"),
                    f"claim {claim_id}: comparator_scope must match the named comparator class",
                    errors,
                )
                require(
                    screening.get("selection_bias_status") != "BLOCK" if isinstance(screening, dict) else False,
                    f"claim {claim_id}: blocked selection bias cannot support superiority",
                    errors,
                )
                named = comparator.get("name")
                require(bool(claim_assays), f"claim {claim_id}: referenced assay required", errors)
                require(all(assay.get("comparator") == named for assay in claim_assays), f"claim {claim_id}: every referenced assay must use named comparator", errors)
                exceeded = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and assay.get("tested_subject") in DESIGNED_TEST_SUBJECTS
                    and "bounded_comparator_superiority" in assay.get("endpoint_types", [])
                    and assay.get("result_direction") == "exceeded_reference_activity"
                    and evidence_level(assay.get("evidence_level")) >= EVIDENCE_ORDER["F2"]
                ]
                require(publication_peer_reviewed and bool(exceeded), f"claim {claim_id}: peer-reviewed referenced F2+ superiority evidence required", errors)

            if claim_type == "structural_characterization" and status == "supported_with_limits":
                selected_candidate_support = True
                structural = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") == "cryo_em_structure"
                    and assay.get("endpoint_types") == ["structural_characterization"]
                    and assay.get("result_direction") == "structural_observation"
                    and assay.get("evidence_level") == "F4"
                ]
                require(bool(structural), f"claim {claim_id}: referenced F4 structure record required", errors)

            if claim_type == "independent_replication":
                if status == "supported_with_limits":
                    require(
                        independent_replication == "established"
                        and same_collaboration_only is False
                        and bool(replication_refs),
                        f"claim {claim_id}: supported independent_replication requires F5 external evidence",
                        errors,
                    )
                    require(replication_refs.issubset(ref_set), f"claim {claim_id}: independent_replication must cite all replication evidence", errors)
                else:
                    require(
                        independent_replication != "established"
                        and status in {"not_established", "blocked"},
                        f"claim {claim_id}: independent replication is not established",
                        errors,
                    )

            if claim_type == "platform_generalization":
                if status == "supported_with_limits":
                    platform_items = [
                        item
                        for item in claim_external
                        if item.get("evidence_kind") == "platform_generalization"
                        and item.get("evidence_level") == "F5"
                        and complete_independence(item.get("independence"))
                    ]
                    require(bool(platform_items), f"claim {claim_id}: F5 platform-generalization evidence required", errors)
                    coverage_union = {dimension: set() for dimension in COVERAGE_DIMENSIONS}
                    for item in platform_items:
                        coverage = item.get("coverage", {})
                        if isinstance(coverage, dict):
                            for dimension in COVERAGE_DIMENSIONS:
                                values = coverage.get(dimension, [])
                                if isinstance(values, list):
                                    coverage_union[dimension].update(str(value) for value in values)
                    for dimension, values in coverage_union.items():
                        require(len(values) >= 2, f"claim {claim_id}: platform generalization requires at least two {dimension}", errors)
                else:
                    require(status in {"not_established", "blocked"}, f"claim {claim_id}: platform generalization is not established", errors)

        missing_types = sorted(REQUIRED_CLAIM_TYPES - claim_by_type.keys())
        require(not missing_types, f"claim firewall missing types: {missing_types}", errors)

    replication_claim = claim_by_type.get("independent_replication", {})
    if independent_replication == "established":
        require(replication_claim.get("status") == "supported_with_limits", "established replication requires supported independent_replication claim", errors)
        refs = replication_claim.get("evidence_refs", [])
        require(
            isinstance(refs, list) and replication_refs.issubset({str(ref) for ref in refs}),
            "independent_replication claim must cite structured F5 replication evidence",
            errors,
        )
    else:
        require(replication_claim.get("status") in {"not_established", "blocked"}, "non-established replication requires non-supported replication claim", errors)

    if selected_candidate_support:
        require(selection_status in POSITIVE_SELECTION_STATES, "supported selected-candidate claims require positive selected candidates", errors)

    risk = record.get("risk_assessment", {})
    require(isinstance(risk, dict), "risk_assessment must be an object", errors)
    if isinstance(risk, dict):
        missing_risks = sorted(RISK_DIMENSIONS - risk.keys())
        extra_risks = sorted(risk.keys() - RISK_DIMENSIONS)
        require(not missing_risks, f"risk matrix missing dimensions: {missing_risks}", errors)
        require(not extra_risks, f"risk matrix has unknown dimensions: {extra_risks}", errors)
        for name in sorted(RISK_DIMENSIONS & risk.keys()):
            item = risk.get(name, {})
            require(isinstance(item, dict), f"risk {name}: object required", errors)
            if not isinstance(item, dict):
                continue
            refs = item.get("evidence_refs", [])
            require(isinstance(refs, list) and bool(refs), f"risk {name}: evidence_refs required", errors)
            ref_set = {str(ref) for ref in refs} if isinstance(refs, list) else set()
            unknown = sorted(ref_set - allowed_refs)
            require(not unknown, f"risk {name}: unknown evidence refs {unknown}", errors)
            require(
                item.get("status") != "not_applicable",
                f"risk {name}: mandatory dimension cannot be not_applicable",
                errors,
            )
            if item.get("status") == "established":
                matching = [
                    evidence
                    for ref, evidence in external_by_id.items()
                    if ref in ref_set
                    and evidence.get("evidence_kind") == "risk_assessment"
                    and name in evidence.get("endpoint_types", [])
                ]
                threshold = EVIDENCE_ORDER[RISK_MIN_LEVEL[name]]
                require(
                    bool(matching)
                    and all(evidence_level(value.get("evidence_level")) >= threshold for value in matching),
                    f"risk {name}: established status requires risk-specific {RISK_MIN_LEVEL[name]}+ evidence",
                    errors,
                )

    mechanism = record.get("mechanism_evidence", {})
    require(isinstance(mechanism, dict), "mechanism_evidence must be an object", errors)
    if isinstance(mechanism, dict):
        structural_claim = claim_by_type.get("structural_characterization", {})
        structural_refs = structural_claim.get("evidence_refs", [])
        structural_ref_set = (
            {str(ref) for ref in structural_refs}
            if isinstance(structural_refs, list)
            else set()
        )
        referenced_structures = [
            assay_by_id[ref]
            for ref in structural_ref_set
            if ref in assay_by_id
            and assay_by_id[ref].get("system") == "cryo_em_structure"
            and assay_by_id[ref].get("tested_subject") == "selected_variant_structure"
            and assay_by_id[ref].get("endpoint_types") == ["structural_characterization"]
            and assay_by_id[ref].get("result_direction") == "structural_observation"
            and assay_by_id[ref].get("evidence_level") == "F4"
        ]
        mechanism_observed = mechanism.get("status") == "structural_contacts_observed"
        cryo_em_characterized = mechanism.get("cryo_em_characterized") is True
        require(
            mechanism_observed == cryo_em_characterized,
            "mechanism_evidence: cryo_em_characterized and structural_contacts_observed must agree",
            errors,
        )
        if mechanism_observed or cryo_em_characterized:
            require(
                structural_claim.get("status") == "supported_with_limits"
                and bool(referenced_structures),
                "mechanism_evidence: observed structure requires a supported structural_characterization claim with referenced F4 structural evidence",
                errors,
            )

    overall = record.get("overall_verdict")
    require(overall in {"ACCEPT_WITH_LIMITS", "HOLD", "BLOCK"}, "invalid overall_verdict", errors)
    if overall == "ACCEPT_WITH_LIMITS":
        require(supported_claims > 0, "ACCEPT_WITH_LIMITS requires bounded supported claim", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_documentary_only", "invalid safety mode", errors)
        require(safety.get("physical_biology_authorized") is False, "physical biology must remain unauthorized", errors)
        require(safety.get("physical_protocol_included") is False, "physical protocols must not be included", errors)
        require(safety.get("sequence_instructions_included") is False, "sequence instructions must not be included", errors)
        require(safety.get("clinical_or_field_use_authorized") is False, "clinical/field use must remain unauthorized", errors)

    return errors
