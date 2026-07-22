"""Validate the narrow TIP-to-Kairos research-only handoff contract."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from .validator import ValidationError

SCHEMA_PACKAGE = "kairos_gate.schemas"
SCHEMA_NAME = "tip-kairos-handoff.schema.json"


def _reject_constant(value: str) -> None:
    """Reject non-standard JSON constants."""
    raise ValidationError(f"handoff contains non-finite JSON constant: {value}")


def _load_schema() -> Mapping[str, Any]:
    """Load the packaged TIP-to-Kairos handoff schema."""
    try:
        schema = json.loads(
            files(SCHEMA_PACKAGE).joinpath(SCHEMA_NAME).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError, ModuleNotFoundError) as exc:
        raise ValidationError(f"unable to load handoff schema: {exc}") from exc
    if not isinstance(schema, Mapping):
        raise ValidationError("handoff schema root must be an object")
    return schema


def validate_handoff_record(record: Mapping[str, Any]) -> None:
    """Validate complete handoff shape, provenance, versions, and authority."""
    schema = _load_schema()
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(record),
            key=lambda error: list(error.absolute_path),
        )
    except SchemaError as exc:
        raise ValidationError(f"invalid bundled handoff schema: {exc.message}") from exc

    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    raise ValidationError(f"handoff schema violation at {location}: {error.message}")


def validate_handoff_path(path: Path) -> Mapping[str, Any]:
    """Load strict JSON from path, validate the handoff, and return it."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            record = json.load(handle, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"handoff is not valid JSON: {exc}") from exc
    if not isinstance(record, Mapping):
        raise ValidationError("handoff root must be an object")
    validate_handoff_record(record)
    return record
