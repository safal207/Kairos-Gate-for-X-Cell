#!/usr/bin/env python3
"""Validate non-operational partner-laboratory evidence handoffs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"READY_FOR_PARTNER_SCIENTIFIC_REVIEW", "HOLD", "BLOCK"}
EVIDENCE_LEVELS = {"F0", "F1", "F2", "F3", "F4", "F5"}
TECHNICAL_UNITS = {"cell", "well", "plate", "library", "sequencing_run", "read", "image_frame"}
REQUIRED_MODELS = {"candidate_only", "broader_baseline_state", "technical_confounder", "combined"}
REQUIRED_DECISIONS = {"shared_state", "direct_effect", "marker_only", "technical_confounding", "small_context_effect", "null_or_instability"}
REQUIRED_TOP = {
    "schema_version",
    "handoff_id",
    "status",
    "evidence_question",
    "current_evidence",
    "hypotheses_to_distinguish",
    "experimental_unit_contract",
    "temporal_identity_contract",
    "model_comparison_plan",
    "data_return_contract",
    "decision_matrix",
    "stop_hold_rules",
    "governance_gates",
    "claim_boundary",
    "operational_content",
    "next_action",
    "safety_status",
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("handoff root must be an object")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    require(not (REQUIRED_TOP - record.keys()), f"missing fields: {sorted(REQUIRED_TOP - record.keys())}", errors)
    require(record.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(record.get("status") in VALID_STATUSES, "invalid status", errors)
    require(bool(record.get("handoff_id")), "handoff_id is required", errors)
    require(bool(record.get("next_action")), "next_action is required", errors)

    question = record.get("evidence_question", {})
    require(isinstance(question, dict), "evidence_question must be an object", errors)
    if isinstance(question, dict):
        for key in ("candidate", "phenotype", "temporal_order", "biological_system", "decision_to_inform", "statement"):
            require(bool(question.get(key)), f"evidence_question.{key} is required", errors)

    evidence = record.get("current_evidence", [])
    require(isinstance(evidence, list) and len(evidence) >= 1, "current_evidence must be non-empty", errors)
    if isinstance(evidence, list):
        roles: set[str] = set()
        for index, item in enumerate(evidence):
            require(isinstance(item, dict), f"current_evidence[{index}] must be an object", errors)
            if not isinstance(item, dict):
                continue
            require(bool(item.get("evidence_id")), f"evidence {index}: evidence_id required", errors)
            require(bool(item.get("statement")), f"evidence {index}: statement required", errors)
            require(item.get("evidence_level") in EVIDENCE_LEVELS, f"evidence {index}: invalid evidence_level", errors)
            role = item.get("role")
            require(role in {"supporting", "limiting", "blocking", "negative_result"}, f"evidence {index}: invalid role", errors)
            if isinstance(role, str):
                roles.add(role)
        require("blocking" in roles or "limiting" in roles, "handoff must preserve at least one limiting or blocking item", errors)

    hypotheses = record.get("hypotheses_to_distinguish", [])
    require(isinstance(hypotheses, list) and len(hypotheses) >= 2, "at least two hypotheses are required", errors)
    if isinstance(hypotheses, list):
        ids: set[str] = set()
        for index, item in enumerate(hypotheses):
            require(isinstance(item, dict), f"hypotheses[{index}] must be an object", errors)
            if not isinstance(item, dict):
                continue
            hypothesis_id = item.get("hypothesis_id")
            require(bool(hypothesis_id), f"hypothesis {index}: hypothesis_id required", errors)
            if hypothesis_id:
                require(hypothesis_id not in ids, f"duplicate hypothesis_id: {hypothesis_id}", errors)
                ids.add(hypothesis_id)
            require(bool(item.get("statement")), f"hypothesis {hypothesis_id}: statement required", errors)
            require(bool(item.get("distinguishing_observation")), f"hypothesis {hypothesis_id}: distinguishing observation required", errors)

    units = record.get("experimental_unit_contract", {})
    require(isinstance(units, dict), "experimental_unit_contract must be an object", errors)
    if isinstance(units, dict):
        require(bool(units.get("required_unit")), "required biological unit must be stated", errors)
        require(units.get("assignment_level") == "biological_unit", "assignment_level must be biological_unit", errors)
        require(units.get("lineage_required") is True, "unit lineage must be required", errors)
        require(units.get("precision_justification_required") is True, "precision justification must be required", errors)
        excluded_units = units.get("technical_units_not_replicates", [])
        require(isinstance(excluded_units, list), "technical_units_not_replicates must be an array", errors)
        if isinstance(excluded_units, list):
            excluded = set(excluded_units)
            require(len(excluded) >= 4, "at least four technical unit classes must be excluded from replication", errors)
            require(excluded <= TECHNICAL_UNITS, "unknown technical unit class", errors)
            require("cell" in excluded and "plate" in excluded and "library" in excluded, "cell, plate, and library must not be biological replicates", errors)

    temporal = record.get("temporal_identity_contract", {})
    require(isinstance(temporal, dict), "temporal_identity_contract must be an object", errors)
    if isinstance(temporal, dict):
        for key in ("pre_state_before_transition", "later_phenotype_after_transition", "same_longitudinal_unit_linkage", "machine_auditable_lineage"):
            require(temporal.get(key) is True, f"temporal_identity_contract.{key} must be true", errors)
        chain = temporal.get("required_chain", [])
        require(isinstance(chain, list) and len(chain) >= 6, "required_chain must contain at least six lineage nodes", errors)

    model = record.get("model_comparison_plan", {})
    require(isinstance(model, dict), "model_comparison_plan must be an object", errors)
    if isinstance(model, dict):
        require(model.get("frozen_before_outcome_analysis") is True, "model plan must be frozen before outcome analysis", errors)
        require(model.get("negative_controls_required") is True, "negative controls must be required", errors)
        require(model.get("changes_require_superseding_record") is True, "post-freeze changes require a superseding record", errors)
        families = set(model.get("model_families", [])) if isinstance(model.get("model_families"), list) else set()
        require(REQUIRED_MODELS <= families, "candidate, state, technical, and combined models are required", errors)
        require("null_or_negative_control" in families, "null or negative-control model is required", errors)

    returned = record.get("data_return_contract", {})
    require(isinstance(returned, dict), "data_return_contract must be an object", errors)
    if isinstance(returned, dict):
        for key in ("machine_readable", "deidentified_or_lawful", "lineage", "timing", "missingness", "transform_provenance", "model_diagnostics", "checksums", "deviations"):
            require(returned.get(key) is True, f"data_return_contract.{key} must be true", errors)

    matrix = record.get("decision_matrix", [])
    require(isinstance(matrix, list) and len(matrix) >= 4, "decision_matrix must be non-empty", errors)
    if isinstance(matrix, list):
        classes: set[str] = set()
        for index, item in enumerate(matrix):
            require(isinstance(item, dict), f"decision_matrix[{index}] must be an object", errors)
            if not isinstance(item, dict):
                continue
            outcome = item.get("outcome_class")
            require(outcome in REQUIRED_DECISIONS, f"decision {index}: invalid outcome_class", errors)
            if isinstance(outcome, str):
                classes.add(outcome)
            require(bool(item.get("observation")), f"decision {outcome}: observation required", errors)
            require(bool(item.get("interpretation_limit")), f"decision {outcome}: interpretation limit required", errors)
        require(REQUIRED_DECISIONS <= classes, "decision matrix must cover all six competing outcome classes", errors)

    stop_rules = record.get("stop_hold_rules", [])
    require(isinstance(stop_rules, list) and len(stop_rules) >= 5, "at least five stop/hold rules are required", errors)

    governance = record.get("governance_gates", {})
    require(isinstance(governance, dict), "governance_gates must be an object", errors)
    if isinstance(governance, dict):
        for key in ("institution_determines_required_approvals", "qualified_principal_investigator", "domain_review", "quantitative_review", "biosafety_review_if_applicable", "ethics_review_if_applicable", "data_governance_review"):
            require(governance.get(key) is True, f"governance_gates.{key} must be true", errors)
        require(governance.get("execution_authorized") is False, "scientific handoff must not authorize execution", errors)

    boundary = record.get("claim_boundary", {})
    require(isinstance(boundary, dict), "claim_boundary must be an object", errors)
    if isinstance(boundary, dict):
        require(boundary.get("causal") in {"not_established", "blocked"}, "causal claim must remain not established or blocked", errors)
        require(boundary.get("tissue") == "blocked", "tissue claim must be blocked", errors)
        require(boundary.get("clinical_therapeutic") == "blocked", "clinical/therapeutic claim must be blocked", errors)

    operational = record.get("operational_content", {})
    require(isinstance(operational, dict), "operational_content must be an object", errors)
    if isinstance(operational, dict):
        for key in ("physical_protocol_included", "recipes_or_concentrations_included", "dosing_or_treatment_included", "biological_modification_instructions_included", "human_experimentation_instructions_included"):
            require(operational.get(key) is False, f"operational_content.{key} must be false", errors)

    safety = record.get("safety_status", {})
    require(isinstance(safety, dict), "safety_status must be an object", errors)
    if isinstance(safety, dict):
        require(safety.get("mode") == "computational_documentary_only", "safety mode must be computational_documentary_only", errors)
        require(safety.get("physical_biology_authorized") is False, "physical biology must remain unauthorized", errors)
        require(safety.get("ai_authorizes_execution") is False, "AI must not authorize execution", errors)

    status = record.get("status")
    if status == "READY_FOR_PARTNER_SCIENTIFIC_REVIEW":
        require(isinstance(governance, dict) and governance.get("execution_authorized") is False, "review-ready status cannot authorize execution", errors)
        require(isinstance(safety, dict) and safety.get("physical_biology_authorized") is False, "review-ready status cannot authorize physical biology", errors)
        require(isinstance(safety, dict) and safety.get("ai_authorizes_execution") is False, "review-ready status cannot grant AI authorization", errors)
    if status == "BLOCK":
        require(len(errors) > 0 or bool(record.get("next_action")), "BLOCK records must explain why they are blocked", errors)

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_partner_lab_evidence_handoff.py HANDOFF.json [HANDOFF.json ...]", file=sys.stderr)
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
