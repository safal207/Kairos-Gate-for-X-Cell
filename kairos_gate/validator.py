"""Deterministic research-record validation for Kairos Gate v0.1.

This module validates a narrow protocol shape and derives a research-only
classification. It does not validate biological truth or authorize experiments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ALLOWED_DECISIONS = {
    "CANDIDATE_WINDOW",
    "WAIT",
    "EXCLUDE",
    "INSUFFICIENT_EVIDENCE",
}

REQUIRED_TOP_LEVEL = {
    "schema",
    "transition_id",
    "subject",
    "observed_at",
    "current_state",
    "phase_context",
    "perturbation",
    "target_state",
    "forecast",
    "gate_assessment",
    "decision",
    "justification",
    "provenance",
    "limitations",
}

ASSESSMENT_FIELDS = {
    "effectiveness",
    "identity_preservation",
    "toxicity_risk",
    "reversibility",
    "evidence_quality",
    "timing_confidence",
}


class ValidationError(ValueError):
    """Raised when a Kairos transition record violates v0.1 invariants."""


def _score(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} must be a number")
    score = float(value)
    if not 0.0 <= score <= 1.0:
        raise ValidationError(f"{field} must be between 0 and 1")
    return score


def _has_measured_phase(phase_context: Mapping[str, Any]) -> bool:
    for value in phase_context.values():
        if not isinstance(value, Mapping):
            continue
        status = value.get("status")
        confidence = value.get("confidence", 0.0)
        if status in {"observed", "inferred"}:
            try:
                if _score(confidence, "phase confidence") >= 0.60:
                    return True
            except ValidationError:
                return False
    return False


def recommend_decision(record: Mapping[str, Any]) -> str:
    """Derive a conservative research-only decision from a validated record."""

    assessment = record["gate_assessment"]
    effectiveness = _score(assessment["effectiveness"], "effectiveness")
    identity = _score(assessment["identity_preservation"], "identity_preservation")
    toxicity = _score(assessment["toxicity_risk"], "toxicity_risk")
    reversibility = _score(assessment["reversibility"], "reversibility")
    evidence = _score(assessment["evidence_quality"], "evidence_quality")
    timing = _score(assessment["timing_confidence"], "timing_confidence")

    if not _has_measured_phase(record["phase_context"]) or evidence < 0.60:
        return "INSUFFICIENT_EVIDENCE"
    if toxicity > 0.35 or identity < 0.65 or reversibility < 0.40:
        return "EXCLUDE"
    if effectiveness < 0.60 or timing < 0.65:
        return "WAIT"
    return "CANDIDATE_WINDOW"


def validate_record(record: Mapping[str, Any]) -> None:
    """Validate record shape and decision consistency."""

    missing = REQUIRED_TOP_LEVEL - set(record)
    if missing:
        raise ValidationError(f"missing top-level fields: {sorted(missing)}")

    if record["schema"] != "kairos.transition.v0.1":
        raise ValidationError("unsupported schema")

    if not isinstance(record["transition_id"], str) or not record["transition_id"].strip():
        raise ValidationError("transition_id must be a non-empty string")

    if not isinstance(record["phase_context"], Mapping) or not record["phase_context"]:
        raise ValidationError("phase_context must be a non-empty object")

    assessment = record["gate_assessment"]
    if not isinstance(assessment, Mapping):
        raise ValidationError("gate_assessment must be an object")

    missing_scores = ASSESSMENT_FIELDS - set(assessment)
    if missing_scores:
        raise ValidationError(f"missing assessment fields: {sorted(missing_scores)}")

    for field in ASSESSMENT_FIELDS:
        _score(assessment[field], field)

    decision = record["decision"]
    if decision not in ALLOWED_DECISIONS:
        raise ValidationError(f"unsupported decision: {decision}")

    expected = recommend_decision(record)
    if decision != expected:
        raise ValidationError(
            f"decision mismatch: record={decision}, deterministic recommendation={expected}"
        )

    for field in ("justification", "limitations"):
        value = record[field]
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValidationError(f"{field} must be a non-empty list of strings")


def validate_path(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    if not isinstance(record, Mapping):
        raise ValidationError("record root must be an object")
    validate_record(record)
    return record
