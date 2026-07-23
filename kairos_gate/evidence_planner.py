"""Deterministic research-only evidence planning from readiness results."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from .dataset_readiness import validate_result_record

PLAN_SCHEMA = "kairos.evidence-request-plan.v0.1"
SCHEMA_PACKAGE = "kairos_gate.schemas"
SCHEMA_NAME = "evidence-request-plan.schema.json"
SUPPORTED_BLOCKER = "BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED"
READY = "READY_FOR_PREREGISTRATION"


class EvidencePlannerError(ValueError):
    """Raised when a readiness result cannot produce a bounded evidence plan."""


def _reject_constant(value: str) -> None:
    raise EvidencePlannerError(f"non-finite JSON constant: {value}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise EvidencePlannerError(f"unable to hash readiness result: {exc}") from exc
    return f"sha256:{digest.hexdigest()}"


def _load_plan_schema() -> Mapping[str, Any]:
    try:
        schema = json.loads(
            files(SCHEMA_PACKAGE).joinpath(SCHEMA_NAME).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError, ModuleNotFoundError) as exc:
        raise EvidencePlannerError(f"unable to load evidence plan schema: {exc}") from exc
    if not isinstance(schema, Mapping):
        raise EvidencePlannerError("evidence plan schema root must be an object")
    return schema


def validate_evidence_plan_record(plan: Mapping[str, Any]) -> None:
    """Validate one evidence plan against the packaged Draft 2020-12 schema."""
    schema = _load_plan_schema()
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(plan), key=lambda error: list(error.absolute_path)
        )
    except SchemaError as exc:
        raise EvidencePlannerError(
            f"invalid bundled evidence plan schema: {exc.message}"
        ) from exc
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise EvidencePlannerError(
            f"evidence plan schema violation at {location}: {error.message}"
        )


def load_readiness_result(path: Path) -> Mapping[str, Any]:
    """Load and validate one machine-readable Dataset Readiness result."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            result = json.load(handle, parse_constant=_reject_constant)
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidencePlannerError(f"unable to load readiness result: {exc}") from exc
    if not isinstance(result, Mapping):
        raise EvidencePlannerError("readiness result root must be an object")
    try:
        validate_result_record(result)
    except ValueError as exc:
        raise EvidencePlannerError(f"invalid readiness result: {exc}") from exc
    return result


def _authority() -> dict[str, Any]:
    return {
        "classification": "RESEARCH_ONLY",
        "readiness_verdict_changed": False,
        "model_fitting_authorized": False,
        "author_contact_authorized": False,
        "experiment_authorization": False,
        "clinical_authorization": False,
        "merge_authorization": False,
    }


def _source_result(result: Mapping[str, Any], digest: str) -> dict[str, Any]:
    dataset = result["dataset"]
    return {
        "schema": result["schema"],
        "dataset_id": dataset["id"],
        "dataset_version": dataset["version"],
        "adapter": dataset["adapter"],
        "status": result["status"],
        "sha256": digest,
    }


def _replicate_semantics_plan(
    result: Mapping[str, Any], source_digest: str
) -> dict[str, Any]:
    source_classes = [
        "PUBLIC_AUTHOR_CLARIFICATION",
        "IMMUTABLE_SUPPLEMENTARY_METHODS",
        "PINNED_PROTOCOL",
        "MACHINE_READABLE_METADATA_WITH_SEMANTICS",
        "VERSIONED_LAB_DOCUMENTATION",
    ]
    plan = {
        "schema": PLAN_SCHEMA,
        "plan_status": "OPEN_EVIDENCE_REQUEST",
        "source_result": _source_result(result, source_digest),
        "blocker": {
            "code": SUPPORTED_BLOCKER,
            "summary": (
                "Independent experimental-unit semantics are not established by "
                "the reviewed evidence."
            ),
        },
        "required_evidence": [
            {
                "id": "independent_unit_definition",
                "question": "What is the independent experimental unit for this cohort?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "physical and experimental definition of one unit",
                    "statement of whether units reflect cultures, days, imaging sessions, or another design level",
                ],
                "blocking_if_missing": True,
            },
            {
                "id": "sample_to_unit_mapping",
                "question": "How does every selected sample map to an independent unit?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "complete mapping for every selected sample ID",
                    "stable unit identifiers with no inferred gaps",
                ],
                "blocking_if_missing": True,
            },
            {
                "id": "dependency_disclosure",
                "question": "Which samples share cultures, days, imaging sessions, extractions, or repeated measurements?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "all known shared dependencies",
                    "rules for keeping dependent observations in one split group",
                ],
                "blocking_if_missing": True,
            },
            {
                "id": "technical_label_semantics",
                "question": "What do plate, well, index, sequencing-run, Date, Probe, and sample-name labels represent?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "explicit semantics for each proposed grouping label",
                    "clear separation of technical labels from biological replication",
                ],
                "blocking_if_missing": True,
            },
            {
                "id": "effective_unit_count",
                "question": "How many independent units remain after all dependencies are grouped?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "effective independent-unit count",
                    "derivation from the complete sample-to-unit mapping",
                ],
                "blocking_if_missing": True,
            },
            {
                "id": "held_out_split_recommendation",
                "question": "Which held-out split is scientifically defensible for this cohort?",
                "acceptable_sources": source_classes,
                "minimum_content": [
                    "split unit defined before model fitting",
                    "statement on whether leave-one-plate-out is confirmatory or only exploratory",
                ],
                "blocking_if_missing": True,
            },
        ],
        "forbidden_substitutions": [
            "plate, well, index pair, sequencing run, Date, or Probe diversity without source-backed semantics",
            "individual cells counted as independent replicates without evidence",
            "random cell split presented as generalization evidence",
            "grouping selected after viewing response values or model performance",
            "sample-name patterns treated as experimental-unit evidence by themselves",
            "synthetic or foundation-model output treated as replicate evidence",
        ],
        "decision_mapping": [
            {
                "condition": "complete source-backed semantics and sufficient independent units",
                "outcome": "REPLICATE_GROUPING_VERIFIED",
            },
            {
                "condition": "source-backed semantics but too few independent units",
                "outcome": "BLOCKED_EFFECTIVE_SAMPLE_SIZE",
            },
            {
                "condition": "technical grouping is documented but biological independence is not",
                "outcome": "EXPLORATORY_ONLY_TECHNICAL_GROUPING",
            },
            {
                "condition": "semantics remain missing, incomplete, or contradictory",
                "outcome": SUPPORTED_BLOCKER,
            },
        ],
        "authority": _authority(),
        "next_action": (
            "Collect immutable source-backed answers for every required evidence item; "
            "do not change the readiness verdict until they are reviewed."
        ),
        "limitations": [
            "The planner identifies missing evidence but does not infer biological facts.",
            "The planner does not contact authors or accept evidence automatically.",
            "Generating a plan does not change the source readiness verdict.",
            "No model fitting, experiment, clinical action, or merge is authorized.",
        ],
    }
    validate_evidence_plan_record(plan)
    return plan


def _ready_plan(result: Mapping[str, Any], source_digest: str) -> dict[str, Any]:
    plan = {
        "schema": PLAN_SCHEMA,
        "plan_status": "NO_BLOCKING_EVIDENCE_REQUEST",
        "source_result": _source_result(result, source_digest),
        "blocker": {
            "code": "NONE",
            "summary": "The supplied readiness result has no blocking evidence request.",
        },
        "required_evidence": [],
        "forbidden_substitutions": [],
        "decision_mapping": [
            {
                "condition": "the reviewed readiness result remains unchanged",
                "outcome": READY,
            }
        ],
        "authority": _authority(),
        "next_action": "Freeze the preregistered protocol before any separate authorization decision.",
        "limitations": [
            "A passed readiness gate is not model-fitting or experiment authorization.",
            "The planner does not establish biological validity or causality.",
        ],
    }
    validate_evidence_plan_record(plan)
    return plan


def build_evidence_plan(
    result: Mapping[str, Any], *, source_result_sha256: str
) -> dict[str, Any]:
    """Build one deterministic evidence request plan from a validated result."""
    validate_result_record(result)
    status = result["status"]
    if status == SUPPORTED_BLOCKER:
        return _replicate_semantics_plan(result, source_result_sha256)
    if status == READY:
        return _ready_plan(result, source_result_sha256)
    raise EvidencePlannerError(
        f"readiness status {status!r} is not supported by evidence planner v0.1"
    )


def plan_evidence_path(path: Path) -> dict[str, Any]:
    """Load a readiness result, bind its digest, and produce a validated plan."""
    result = load_readiness_result(path)
    return build_evidence_plan(result, source_result_sha256=_sha256(path))
