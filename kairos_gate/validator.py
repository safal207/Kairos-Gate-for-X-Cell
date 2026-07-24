"""Deterministic research-record validation for Kairos Gate v0.1.

This module validates a narrow protocol shape and derives a research-only
classification. It does not validate biological truth or authorize experiments.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ALLOWED_DECISIONS = {
    "CANDIDATE_WINDOW",
    "WAIT",
    "EXCLUDE",
    "INSUFFICIENT_EVIDENCE",
}

SUPPORTED_PHASES = {
    "cell_cycle",
    "calcium",
    "membrane_potential",
    "metabolic",
    "circadian",
}

SCHEMA_PACKAGE = "kairos_gate.schemas"
SCHEMA_NAME = "kairos-transition.schema.json"

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
    """Return a finite protocol score constrained to the inclusive range [0, 1]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} must be a number")
    score = float(value)
    if not math.isfinite(score):
        raise ValidationError(f"{field} must be finite")
    if not 0.0 <= score <= 1.0:
        raise ValidationError(f"{field} must be between 0 and 1")
    return score


def _validate_finite_numbers(value: Any, path: str = "$") -> None:
    """Reject NaN and infinities anywhere in an in-memory record."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            raise ValidationError(f"{path} must be finite")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _validate_finite_numbers(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _validate_finite_numbers(child, f"{path}[{index}]")


def _parse_datetime(value: Any) -> datetime:
    """Parse an RFC 3339 timestamp into a timezone-aware datetime."""
    if not isinstance(value, str):
        raise ValidationError("timestamp must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise ValidationError("timestamp must include a timezone")
    return parsed


def _reject_json_constant(value: str) -> None:
    """Reject non-standard JSON constants such as NaN and Infinity."""
    raise ValidationError(f"record contains non-finite JSON constant: {value}")


def _load_schema() -> Mapping[str, Any]:
    """Load the canonical packaged Draft 2020-12 transition schema."""
    try:
        schema = json.loads(
            files(SCHEMA_PACKAGE).joinpath(SCHEMA_NAME).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError, ModuleNotFoundError) as exc:
        raise ValidationError(f"unable to load transition schema: {exc}") from exc
    if not isinstance(schema, Mapping):
        raise ValidationError("transition schema root must be an object")
    return schema


def _validate_schema(record: Mapping[str, Any]) -> None:
    """Validate a record against the complete schema, including date-time formats."""
    schema = _load_schema()
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(record),
            key=lambda error: list(error.absolute_path),
        )
    except SchemaError as exc:
        raise ValidationError(f"invalid bundled transition schema: {exc.message}") from exc

    if not errors:
        return

    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    raise ValidationError(f"schema violation at {location}: {error.message}")


def _has_measured_phase(
    phase_context: Mapping[str, Any], record_observed_at: Any
) -> bool:
    """Return whether a supported phase has pre-record, confident evidence."""
    try:
        record_time = _parse_datetime(record_observed_at)
    except ValidationError:
        return False

    for phase_name in SUPPORTED_PHASES:
        value = phase_context.get(phase_name)
        if not isinstance(value, Mapping):
            continue
        if value.get("status") not in {"observed", "inferred"}:
            continue
        if not all(
            isinstance(value.get(field), str) and value[field].strip()
            for field in ("label", "method", "observed_at")
        ):
            continue
        try:
            phase_time = _parse_datetime(value["observed_at"])
            confidence = _score(value.get("confidence"), "phase confidence")
        except ValidationError:
            continue
        if phase_time > record_time:
            continue
        if confidence >= 0.60:
            return True
    return False


def recommend_decision(record: Mapping[str, Any]) -> str:
    """Derive a conservative research-only classification from a valid record."""
    assessment = record["gate_assessment"]
    effectiveness = _score(assessment["effectiveness"], "effectiveness")
    identity = _score(assessment["identity_preservation"], "identity_preservation")
    toxicity = _score(assessment["toxicity_risk"], "toxicity_risk")
    reversibility = _score(assessment["reversibility"], "reversibility")
    evidence = _score(assessment["evidence_quality"], "evidence_quality")
    timing = _score(assessment["timing_confidence"], "timing_confidence")

    if toxicity > 0.35 or identity < 0.65 or reversibility < 0.40:
        return "EXCLUDE"
    if (
        not _has_measured_phase(record["phase_context"], record.get("observed_at"))
        or evidence < 0.60
    ):
        return "INSUFFICIENT_EVIDENCE"
    if effectiveness < 0.60 or timing < 0.65:
        return "WAIT"
    return "CANDIDATE_WINDOW"


def validate_record(record: Mapping[str, Any]) -> None:
    """Validate finite values, full schema conformance, and decision consistency."""
    _validate_finite_numbers(record)
    _validate_schema(record)

    assessment = record["gate_assessment"]
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


def validate_path(path: Path) -> Mapping[str, Any]:
    """Load a strict JSON record from path, validate it, and return the mapping."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            record = json.load(handle, parse_constant=_reject_json_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"record is not valid JSON: {exc}") from exc
    if not isinstance(record, Mapping):
        raise ValidationError("record root must be an object")
    validate_record(record)
    return record
