"""Dataset-agnostic readiness checks for research-only modelling gates."""

from __future__ import annotations

import hashlib
import json
import math
import re
from importlib.resources import files
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

MANIFEST_SCHEMA = "kairos.dataset-manifest.v0.1"
RESULT_SCHEMA = "kairos.dataset-readiness-result.v0.1"
SCHEMA_PACKAGE = "kairos_gate.schemas"
SCHEMA_NAME = "dataset-manifest.schema.json"

READY = "READY_FOR_PREREGISTRATION"
EXPLORATORY = "EXPLORATORY_ONLY"
BLOCKED_DATA_INTEGRITY = "BLOCKED_DATA_INTEGRITY"
BLOCKED_MISSING_CELL_LINKAGE = "BLOCKED_MISSING_CELL_LINKAGE"
BLOCKED_MISSING_RESPONSE_LABELS = "BLOCKED_MISSING_RESPONSE_LABELS"
BLOCKED_REPEATED_CELL_GROUP_LEAKAGE = "BLOCKED_REPEATED_CELL_GROUP_LEAKAGE"
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED = "BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED"
BLOCKED_EFFECTIVE_SAMPLE_SIZE = "BLOCKED_EFFECTIVE_SAMPLE_SIZE"
BLOCKED_LICENSE_UNCLEAR = "BLOCKED_LICENSE_UNCLEAR"


class DatasetReadinessError(ValueError):
    """Raised when a dataset manifest or canonical contract is invalid."""


def _reject_constant(value: str) -> None:
    raise DatasetReadinessError(f"non-finite JSON constant: {value}")


def _validate_finite_numbers(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DatasetReadinessError(f"{path} must be finite")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            _validate_finite_numbers(child, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_finite_numbers(child, f"{path}[{index}]")


def _load_schema() -> Mapping[str, Any]:
    try:
        schema = json.loads(
            files(SCHEMA_PACKAGE).joinpath(SCHEMA_NAME).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError, ModuleNotFoundError) as exc:
        raise DatasetReadinessError(
            f"unable to load dataset manifest schema: {exc}"
        ) from exc
    if not isinstance(schema, Mapping):
        raise DatasetReadinessError("dataset manifest schema root must be an object")
    return schema


def _is_immutable_source(source: Mapping[str, Any]) -> bool:
    digest = source.get("sha256")
    if not isinstance(digest, str) or re.fullmatch(
        r"sha256:[0-9a-f]{64}", digest
    ) is None:
        return False
    url = source.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        return False
    lowered = url.lower()
    if "/latest" in lowered or "/releases/latest" in lowered:
        return False
    if "github.com/" in lowered and "/blob/" in lowered:
        return re.search(r"/blob/[0-9a-f]{40}/", lowered) is not None
    if "raw.githubusercontent.com/" in lowered:
        return re.search(
            r"raw\.githubusercontent\.com/[^/]+/[^/]+/[0-9a-f]{40}/", lowered
        ) is not None
    return True


def validate_manifest_record(manifest: Mapping[str, Any]) -> None:
    """Validate schema, finite values, and immutable provenance."""
    _validate_finite_numbers(manifest)
    schema = _load_schema()
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(
            validator.iter_errors(manifest),
            key=lambda error: list(error.absolute_path),
        )
    except SchemaError as exc:
        raise DatasetReadinessError(
            f"invalid bundled dataset manifest schema: {exc.message}"
        ) from exc
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise DatasetReadinessError(
            f"dataset manifest schema violation at {location}: {error.message}"
        )
    for index, source in enumerate(manifest["sources"]):
        if not _is_immutable_source(source):
            raise DatasetReadinessError(
                f"sources[{index}] must use an immutable or digest-bound HTTPS reference"
            )


def load_manifest(path: Path) -> Mapping[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle, parse_constant=_reject_constant)
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetReadinessError(f"unable to load dataset manifest: {exc}") from exc
    if not isinstance(manifest, Mapping):
        raise DatasetReadinessError("dataset manifest root must be an object")
    validate_manifest_record(manifest)
    return manifest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DatasetReadinessError(f"unable to hash input {path}: {exc}") from exc
    return f"sha256:{digest.hexdigest()}"


def _source_by_role(manifest: Mapping[str, Any], role: str) -> Mapping[str, Any]:
    matches = [source for source in manifest["sources"] if source.get("role") == role]
    if len(matches) != 1:
        raise DatasetReadinessError(
            f"manifest must contain exactly one {role!r} source"
        )
    return matches[0]


def _verify_input(path: Path, source: Mapping[str, Any], role: str) -> str:
    actual = _sha256(path)
    expected = source["sha256"]
    if actual != expected:
        raise DatasetReadinessError(
            f"{role} digest mismatch: expected {expected}, got {actual}"
        )
    return actual


def _duplicates(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def evaluate_contract(
    contract: Mapping[str, Any],
    manifest: Mapping[str, Any],
    *,
    input_digests: Mapping[str, str],
) -> dict[str, Any]:
    """Apply invariant readiness checks to one canonical adapter contract."""
    _validate_finite_numbers(contract)
    metadata_ids = [str(value).strip() for value in contract.get("metadata_ids", [])]
    matrix_ids = [str(value).strip() for value in contract.get("matrix_ids", [])]
    records = contract.get("records", [])
    if not isinstance(records, list):
        raise DatasetReadinessError("canonical contract records must be an array")
    if any(not isinstance(record, Mapping) for record in records):
        raise DatasetReadinessError("canonical contract records must be objects")

    integrity_errors: list[str] = []
    if not metadata_ids or any(not value for value in metadata_ids):
        integrity_errors.append("metadata identifiers must be non-empty")
    if not matrix_ids or any(not value for value in matrix_ids):
        integrity_errors.append("matrix identifiers must be non-empty")
    metadata_duplicates = _duplicates(metadata_ids)
    matrix_duplicates = _duplicates(matrix_ids)
    if metadata_duplicates:
        integrity_errors.append(
            f"duplicate metadata identifiers: {metadata_duplicates}"
        )
    if matrix_duplicates:
        integrity_errors.append(f"duplicate matrix identifiers: {matrix_duplicates}")

    selected = [record for record in records if record.get("selected") is True]
    if not selected:
        integrity_errors.append("no records satisfy the declared cohort selection")
    selected_ids = [str(record.get("sample_id", "")).strip() for record in selected]
    if any(not value for value in selected_ids):
        integrity_errors.append("selected records must have non-empty sample_id values")
    selected_duplicates = _duplicates(selected_ids)
    if selected_duplicates:
        integrity_errors.append(
            f"duplicate selected identifiers: {selected_duplicates}"
        )

    metadata_set = set(metadata_ids)
    matrix_set = set(matrix_ids)
    missing_selected = sorted(set(selected_ids) - matrix_set)
    selected_missing_from_metadata = sorted(set(selected_ids) - metadata_set)
    if selected_missing_from_metadata:
        integrity_errors.append(
            f"selected identifiers absent from metadata: {selected_missing_from_metadata}"
        )
    full_id_sets_match = metadata_set == matrix_set
    if not full_id_sets_match:
        integrity_errors.append(
            "full metadata identifier set does not exactly match matrix sample identifiers"
        )

    missing_response_ids = sorted(
        str(record["sample_id"])
        for record in selected
        if record.get("response_available") is not True
    )

    groups_by_identity: dict[str, set[str]] = {}
    for record in selected:
        identity = record.get("repeated_identity")
        if identity in (None, ""):
            continue
        group = record.get("independent_unit") or "<missing>"
        groups_by_identity.setdefault(str(identity), set()).add(str(group))
    cross_group_repeated_ids = sorted(
        identity for identity, groups in groups_by_identity.items() if len(groups) > 1
    )

    semantics = contract.get("replicate_semantics")
    independent_units = sorted(
        {
            str(record["independent_unit"])
            for record in selected
            if record.get("independent_unit") not in (None, "")
        }
    )
    minimum_units = int(manifest["minimum_independent_units"])

    if integrity_errors and not selected:
        status = BLOCKED_DATA_INTEGRITY
    elif missing_selected:
        status = BLOCKED_MISSING_CELL_LINKAGE
    elif integrity_errors:
        status = BLOCKED_DATA_INTEGRITY
    elif missing_response_ids:
        status = BLOCKED_MISSING_RESPONSE_LABELS
    elif cross_group_repeated_ids:
        status = BLOCKED_REPEATED_CELL_GROUP_LEAKAGE
    elif semantics == "unresolved":
        status = BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
    elif semantics == "verified" and len(independent_units) < minimum_units:
        status = BLOCKED_EFFECTIVE_SAMPLE_SIZE
    elif manifest["reuse_status"] != "clear":
        status = BLOCKED_LICENSE_UNCLEAR
    elif semantics == "technical_only":
        status = EXPLORATORY
    elif semantics == "verified":
        status = READY
    else:
        raise DatasetReadinessError(
            f"unsupported replicate semantics: {semantics!r}"
        )

    return {
        "schema": RESULT_SCHEMA,
        "dataset": {
            "id": manifest["dataset_id"],
            "version": manifest["dataset_version"],
            "adapter": manifest["adapter"]["name"],
        },
        "status": status,
        "authority": {
            "classification": "RESEARCH_ONLY",
            "preregistration_gate_passed": status == READY,
            "model_fitting_authorized": False,
            "experiment_authorization": False,
            "clinical_authorization": False,
            "merge_authorization": False,
        },
        "inputs": {
            "metadata": {
                "path": str(contract.get("metadata_path", "")),
                "sha256": input_digests["metadata"],
                "identifiers": len(metadata_ids),
            },
            "matrix": {
                "path": str(contract.get("matrix_path", "")),
                "sha256": input_digests["matrix"],
                "sample_identifiers": len(matrix_ids),
            },
            "reuse_status": manifest["reuse_status"],
        },
        "cohort": {
            "selection_uses_response_label": False,
            "selected_records": len(selected),
            "response_complete_records": len(selected) - len(missing_response_ids),
            "selected_sample_ids": selected_ids,
            "missing_response_sample_ids": missing_response_ids,
            "missing_selected_sample_ids": missing_selected,
        },
        "replicates": {
            "semantics": semantics,
            "minimum_independent_units": minimum_units,
            "independent_units": independent_units,
            "effective_independent_units": len(independent_units),
            "repeated_identity_groups": {
                identity: sorted(groups)
                for identity, groups in sorted(groups_by_identity.items())
            },
            "cross_group_repeated_identity_ids": cross_group_repeated_ids,
        },
        "integrity": {
            "metadata_ids_unique": not metadata_duplicates,
            "matrix_ids_unique": not matrix_duplicates,
            "selected_ids_unique": not selected_duplicates,
            "full_id_sets_match": full_id_sets_match,
            "errors": integrity_errors,
        },
        "next_action": {
            READY: "Freeze the modelling protocol before fitting any model.",
            EXPLORATORY: "Use technical grouping only for labelled sensitivity analysis; do not claim confirmatory generalization.",
            BLOCKED_DATA_INTEGRITY: "Resolve identifier, schema, or canonical-contract integrity failures.",
            BLOCKED_MISSING_CELL_LINKAGE: "Resolve selected metadata identifiers absent from the matrix.",
            BLOCKED_MISSING_RESPONSE_LABELS: "Resolve or explicitly disposition missing downstream labels without changing cohort membership.",
            BLOCKED_REPEATED_CELL_GROUP_LEAKAGE: "Keep each repeated identity within one split group or exclude it before preregistration.",
            BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED: "Obtain source-backed experimental-unit semantics before preregistration.",
            BLOCKED_EFFECTIVE_SAMPLE_SIZE: "Increase or recover the number of independent experimental units.",
            BLOCKED_LICENSE_UNCLEAR: "Document data reuse and redistribution terms.",
        }[status],
        "limitations": [
            "Readiness checks validate data and evidence contracts, not biological truth.",
            "No model is fitted and no biological effect is estimated.",
            "No causal, safety, therapeutic, clinical, or experiment-authorization claim is produced.",
        ],
    }


def audit_dataset_paths(
    manifest_path: Path,
    metadata_path: Path,
    matrix_path: Path,
) -> dict[str, Any]:
    """Load a manifest, invoke its adapter, and evaluate the canonical contract."""
    manifest = load_manifest(manifest_path)
    metadata_digest = _verify_input(
        metadata_path, _source_by_role(manifest, "metadata"), "metadata"
    )
    matrix_digest = _verify_input(
        matrix_path, _source_by_role(manifest, "matrix"), "matrix"
    )
    from .dataset_adapters import get_adapter

    adapter = get_adapter(manifest["adapter"])
    contract = adapter.build_contract(metadata_path, matrix_path)
    return evaluate_contract(
        contract,
        manifest,
        input_digests={"metadata": metadata_digest, "matrix": matrix_digest},
    )
