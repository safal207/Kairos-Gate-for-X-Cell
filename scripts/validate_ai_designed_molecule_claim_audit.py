#!/usr/bin/env python3
"""Validate AI-designed molecule claim audits with fail-closed evidence boundaries."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

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


def complete_independence(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value.get("unrelated_laboratory_identity"))
        and value.get("independent_materials") is True
        and bool(value.get("replication_unit"))
    )


def provenance_valid_for_level(
    *,
    level: str,
    provenance: Any,
    publication_urls: set[str],
    context: str,
    errors: list[str],
    external: bool,
) -> None:
    require(isinstance(provenance, dict), f"{context}: provenance required", errors)
    if not isinstance(provenance, dict):
        return

    role = provenance.get("source_role")
    url = provenance.get("source_url")
    locator = provenance.get("source_locator")
    derivation = provenance.get("derivation")
    artifact_kind = provenance.get("artifact_kind")
    confirmation = provenance.get("confirmation_type")
    digest = provenance.get("artifact_sha256")

    require(bool(locator), f"{context}: source_locator required", errors)
    if role in {"primary_publication", "supplementary_material", "structure_record"}:
        require(
            url in publication_urls,
            f"{context}: provenance URL must be listed by source_publication",
            errors,
        )

    if derivation in {"reconstructed", "computed"}:
        require(
            isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None,
            f"{context}: reconstructed/computed evidence requires artifact SHA-256",
            errors,
        )

    if level in {"F0", "F1", "F2"}:
        require(
            role in {"primary_publication", "supplementary_material", "structure_record"},
            f"{context}: F0-F2 must remain publication or repository reporting",
            errors,
        )
        require(
            derivation == "directly_reported",
            f"{context}: F0-F2 must be directly reported",
            errors,
        )

    if level == "F3":
        require(
            role == "derived_artifact"
            and derivation in {"reconstructed", "computed"}
            and artifact_kind in {"executable_analysis", "reproducibility_bundle"}
            and isinstance(digest, str)
            and SHA256_RE.fullmatch(digest) is not None,
            f"{context}: F3 requires a digested executable or reproducibility artifact",
            errors,
        )

    if level == "F4":
        structure_confirmation = (
            role == "structure_record"
            and artifact_kind == "deposited_structure"
            and confirmation == "repository_record"
        )
        laboratory_confirmation = (
            role == "laboratory_confirmation"
            and artifact_kind == "author_confirmation"
            and confirmation == "author_or_laboratory_confirmation"
            and isinstance(digest, str)
            and SHA256_RE.fullmatch(digest) is not None
        )
        require(
            structure_confirmation or laboratory_confirmation,
            f"{context}: F4 requires repository or author/laboratory confirmation",
            errors,
        )

    if level == "F5":
        require(external, f"{context}: F5 is reserved for external evidence objects", errors)
        require(
            role == "laboratory_confirmation"
            and artifact_kind in {"independent_replication_record", "risk_assessment_record"}
            and confirmation == "independent_laboratory_replication"
            and isinstance(digest, str)
            and SHA256_RE.fullmatch(digest) is not None,
            f"{context}: F5 requires a frozen independent-laboratory evidence artifact",
            errors,
        )


def validate(record: dict[str, Any]) -> list[str]:
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
    selected_count = None
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
            require(
                isinstance(generated, int) and not isinstance(generated, bool),
                "exact_count_reported requires generated_count",
                errors,
            )
        else:
            require(generated is None, "non-exact generation scale must not invent generated_count", errors)

        if selection_status == "positive_exact":
            require(
                isinstance(selected_count, int) and not isinstance(selected_count, bool) and selected_count > 0,
                "positive_exact requires selected_count > 0",
                errors,
            )
        elif selection_status == "zero_exact":
            require(selected_count == 0, "zero_exact requires selected_count=0", errors)
        elif selection_status in {"positive_nonexact", "unknown"}:
            require(selected_count is None, f"{selection_status} requires selected_count=null", errors)
        else:
            errors.append("invalid selected_count_status")

        if denominator == "complete":
            require(
                all(isinstance(value, int) and not isinstance(value, bool) for value in exact_fields),
                "complete denominator requires exact generated, excluded, screened, failed, and selected counts",
                errors,
            )
            if all(isinstance(value, int) and not isinstance(value, bool) for value in exact_fields):
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
                require(
                    isinstance(independent_n, int) and not isinstance(independent_n, bool) and independent_n > 0,
                    f"assay {assay_id}: established unit requires positive independent N",
                    errors,
                )
            if unit_status in {"unresolved", "not_applicable"}:
                require(
                    independent_n is None,
                    f"assay {assay_id}: unresolved/non-applicable unit must not invent N",
                    errors,
                )
            endpoints = assay.get("endpoint_types", [])
            require(isinstance(endpoints, list) and bool(endpoints), f"assay {assay_id}: endpoint_types required", errors)
            provenance_valid_for_level(
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
            provenance_valid_for_level(
                level=level,
                provenance=item.get("provenance"),
                publication_urls=publication_urls,
                context=f"external evidence {evidence_id}",
                errors=errors,
                external=True,
            )
            endpoints = item.get("endpoint_types", [])
            require(isinstance(endpoints, list) and bool(endpoints), f"external evidence {evidence_id}: endpoint_types required", errors)
            kind = item.get("evidence_kind")
            if kind in {"independent_replication", "platform_generalization"}:
                require(
                    level == "F5" and complete_independence(item.get("independence")),
                    f"external evidence {evidence_id}: {kind} requires F5 independent-laboratory evidence",
                    errors,
                )
            if kind == "platform_generalization":
                require(isinstance(item.get("coverage"), dict), f"external evidence {evidence_id}: platform coverage required", errors)
            else:
                require(
                    item.get("coverage") is None or isinstance(item.get("coverage"), dict),
                    f"external evidence {evidence_id}: invalid coverage",
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
            require(
                replication_evidence is None,
                "non-established replication requires replication_evidence=null",
                errors,
            )

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

            require(isinstance(refs, list) and bool(refs), f"claim {claim_id}: evidence_refs required", errors)
            ref_set = {str(ref) for ref in refs} if isinstance(refs, list) else set()
            unknown = sorted(ref_set - allowed_refs)
            require(not unknown, f"claim {claim_id}: unknown evidence refs {unknown}", errors)
            claim_assays = [assay_by_id[ref] for ref in ref_set if ref in assay_by_id]
            claim_external = [external_by_id[ref] for ref in ref_set if ref in external_by_id]

            if status == "supported_with_limits":
                supported_claims += 1
                require(
                    claim_type in SUPPORTED_TYPES,
                    f"claim {claim_id}: {claim_type} cannot be supported in this preview",
                    errors,
                )

            if claim_type in PROTECTED_TYPES:
                require(
                    status in {"not_established", "blocked"},
                    f"claim {claim_id}: {claim_type} must be blocked or not established",
                    errors,
                )
            if claim_type in {"universal_superiority", "ai_autonomy", "physical_authorization"}:
                require(status == "blocked", f"claim {claim_id}: {claim_type} must be blocked", errors)

            if claim_type == "molecular_activity" and status == "supported_with_limits":
                selected_candidate_support = True
                active = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and "molecular_activity" in assay.get("endpoint_types", [])
                    and assay.get("result_direction")
                    in {"retained_reference_activity", "exceeded_reference_activity", "mixed"}
                    and evidence_level(assay.get("evidence_level")) >= EVIDENCE_ORDER["F2"]
                ]
                require(
                    publication_peer_reviewed and bool(active),
                    f"claim {claim_id}: peer-reviewed referenced F2+ molecular-activity evidence required",
                    errors,
                )

            if claim_type == "bounded_comparator_superiority" and status == "supported_with_limits":
                selected_candidate_support = True
                require(
                    comparator.get("comparator_class") == "wild_type_same_family"
                    and comparator.get("scope") == "test_context_bounded",
                    f"claim {claim_id}: comparator must be bounded wild-type same-family",
                    errors,
                )
                require(
                    screening.get("selection_bias_status") != "BLOCK" if isinstance(screening, dict) else False,
                    f"claim {claim_id}: blocked selection bias cannot support superiority",
                    errors,
                )
                named = comparator.get("name")
                require(bool(claim_assays), f"claim {claim_id}: referenced assay required", errors)
                require(
                    all(assay.get("comparator") == named for assay in claim_assays),
                    f"claim {claim_id}: every referenced assay must use named comparator",
                    errors,
                )
                exceeded = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") in FUNCTIONAL_SYSTEMS
                    and "bounded_comparator_superiority" in assay.get("endpoint_types", [])
                    and assay.get("result_direction") == "exceeded_reference_activity"
                    and evidence_level(assay.get("evidence_level")) >= EVIDENCE_ORDER["F2"]
                ]
                require(
                    publication_peer_reviewed and bool(exceeded),
                    f"claim {claim_id}: peer-reviewed referenced F2+ superiority evidence required",
                    errors,
                )

            if claim_type == "structural_characterization" and status == "supported_with_limits":
                selected_candidate_support = True
                structural = [
                    assay
                    for assay in claim_assays
                    if assay.get("system") == "cryo_em_structure"
                    and "structural_characterization" in assay.get("endpoint_types", [])
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
                    require(
                        replication_refs.issubset(ref_set),
                        f"claim {claim_id}: independent_replication must cite all replication evidence",
                        errors,
                    )
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
                        require(
                            len(values) >= 2,
                            f"claim {claim_id}: platform generalization requires at least two {dimension}",
                            errors,
                        )
                else:
                    require(
                        status in {"not_established", "blocked"},
                        f"claim {claim_id}: platform generalization is not established",
                        errors,
                    )

        missing_types = sorted(REQUIRED_CLAIM_TYPES - claim_by_type.keys())
        require(not missing_types, f"claim firewall missing types: {missing_types}", errors)

    replication_claim = claim_by_type.get("independent_replication", {})
    if independent_replication == "established":
        require(
            replication_claim.get("status") == "supported_with_limits",
            "established replication requires supported independent_replication claim",
            errors,
        )
        refs = replication_claim.get("evidence_refs", [])
        require(
            isinstance(refs, list) and replication_refs.issubset({str(ref) for ref in refs}),
            "independent_replication claim must cite structured F5 replication evidence",
            errors,
        )
    else:
        require(
            replication_claim.get("status") in {"not_established", "blocked"},
            "non-established replication requires non-supported replication claim",
            errors,
        )

    if selected_candidate_support:
        require(
            selection_status in POSITIVE_SELECTION_STATES,
            "supported selected-candidate claims require positive selected candidates",
            errors,
        )

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
            if item.get("status") == "established":
                matching: list[dict[str, Any]] = []
                matching.extend(
                    assay
                    for ref, assay in assay_by_id.items()
                    if ref in ref_set and name in assay.get("endpoint_types", [])
                )
                matching.extend(
                    evidence
                    for ref, evidence in external_by_id.items()
                    if ref in ref_set and name in evidence.get("endpoint_types", [])
                )
                threshold = EVIDENCE_ORDER[RISK_MIN_LEVEL[name]]
                require(
                    bool(matching)
                    and all(evidence_level(value.get("evidence_level")) >= threshold for value in matching),
                    f"risk {name}: established status requires risk-specific {RISK_MIN_LEVEL[name]}+ evidence",
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


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_ai_designed_molecule_claim_audit.py AUDIT.json [...]", file=sys.stderr)
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
