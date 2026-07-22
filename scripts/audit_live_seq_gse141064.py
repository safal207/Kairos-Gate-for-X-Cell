"""Audit local GSE141064 metadata and count-matrix linkage without modelling.

The auditor is research-only. It never downloads data, never mutates source files,
and never treats a technically valid linkage as biological or experimental approval.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, TextIO

RESULT_SCHEMA = "kairos.live-seq-feasibility-result.v0.1"
RESPONSE_FIELD = "mCherry.log.slope"
REQUIRED_COLUMNS = {
    "sample_ID",
    "sample_name",
    "original_sample_name",
    "Batch",
    "Cell_type",
    "sampling_type",
    "treatment",
    "Probe",
    "Date",
    "nFeature_RNA",
    "percent.mt",
    "percent.rRNA",
    "input.reads",
    "uniquely.mapped",
    "nCount_RNA",
    "mCherry.log.intercept",
    RESPONSE_FIELD,
    "mCherry.AUC",
    "double_extraction",
    "double_extraction_order",
}


class AuditError(ValueError):
    """Raised when source files violate the preregistered audit contract."""


@contextmanager
def _open_text(path: Path) -> Iterator[TextIO]:
    """Open plain or gzip-compressed text with deterministic UTF-8 decoding."""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            yield handle
    else:
        with path.open("r", encoding="utf-8", newline="") as handle:
            yield handle


def _sha256(path: Path) -> str:
    """Return a byte-level SHA-256 digest for an immutable local input record."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _finite_number(value: Any) -> float | None:
    """Parse one optional finite numeric field; blanks and NA are unavailable."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NA", "N/A", "NAN", "NULL"}:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def _load_metadata(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Load metadata and enforce fields required by the preregistered cohort."""
    try:
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
            if missing:
                raise AuditError(f"metadata missing required columns: {missing}")
            rows = [dict(row) for row in reader]
    except (OSError, csv.Error, UnicodeError) as exc:
        raise AuditError(f"unable to read metadata: {exc}") from exc

    if not rows:
        raise AuditError("metadata contains no rows")
    return fieldnames, rows


def _load_count_columns(path: Path) -> list[str]:
    """Read only the count-matrix header; genes remain untouched on disk."""
    try:
        with _open_text(path) as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
    except (OSError, csv.Error, UnicodeError) as exc:
        raise AuditError(f"unable to read count matrix header: {exc}") from exc

    if not header or len(header) < 2:
        raise AuditError("count matrix header must contain a feature column and samples")
    sample_ids = [value.strip() for value in header[1:]]
    if any(not value for value in sample_ids):
        raise AuditError("count matrix contains an empty sample identifier")
    if len(sample_ids) != len(set(sample_ids)):
        raise AuditError("count matrix contains duplicate sample identifiers")
    return sample_ids


def _selected_recorded_cells(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Apply the upstream cohort rule without consulting the response label."""
    selected: list[dict[str, str]] = []
    for row in rows:
        intercept = _finite_number(row.get("mCherry.log.intercept"))
        if (
            row.get("sampling_type") == "Live_seq"
            and row.get("Cell_type") == "Raw264.7_G9"
            and row.get("treatment") == "not_treated"
            and row.get("Batch") == "8_8"
            and intercept is not None
            and intercept > 0
        ):
            selected.append(row)
    return selected


def audit(
    metadata_path: Path,
    count_matrix_path: Path,
    *,
    data_reuse_status: str,
) -> dict[str, Any]:
    """Return a machine-readable, fail-closed feasibility result."""
    _, rows = _load_metadata(metadata_path)
    count_columns = _load_count_columns(count_matrix_path)

    metadata_ids = [str(row.get("sample_ID", "")).strip() for row in rows]
    if any(not sample_id for sample_id in metadata_ids):
        raise AuditError("metadata contains an empty sample_ID")
    if len(metadata_ids) != len(set(metadata_ids)):
        raise AuditError("metadata contains duplicate sample_ID values")

    selected = _selected_recorded_cells(rows)
    selected_ids = [row["sample_ID"] for row in selected]
    response_complete = [
        row for row in selected if _finite_number(row.get(RESPONSE_FIELD)) is not None
    ]
    missing_response_ids = [
        row["sample_ID"]
        for row in selected
        if _finite_number(row.get(RESPONSE_FIELD)) is None
    ]

    count_set = set(count_columns)
    missing_selected = sorted(set(selected_ids) - count_set)

    replicate_groups = sorted(
        {
            f"{str(row.get('Date', '')).strip()}|{str(row.get('Probe', '')).strip()}"
            for row in selected
            if str(row.get("Date", "")).strip() or str(row.get("Probe", "")).strip()
        }
    )
    repeated_measurement_rows = sum(
        1
        for row in selected
        if str(row.get("double_extraction", "")).strip().upper()
        not in {"", "NA", "N/A"}
    )

    integrity_errors: list[str] = []
    if not selected:
        integrity_errors.append("no rows satisfy the preregistered recorded-cell cohort rule")
    if set(metadata_ids) != count_set:
        integrity_errors.append(
            "full metadata sample_ID set does not exactly match count-matrix sample columns"
        )

    if not selected:
        status = "BLOCKED_DATA_INTEGRITY"
    elif missing_selected:
        status = "BLOCKED_MISSING_CELL_LINKAGE"
    elif integrity_errors:
        status = "BLOCKED_DATA_INTEGRITY"
    elif missing_response_ids:
        status = "BLOCKED_MISSING_RESPONSE_LABELS"
    elif len(replicate_groups) < 2:
        status = "BLOCKED_INSUFFICIENT_REPLICATES"
    elif data_reuse_status != "clear":
        status = "BLOCKED_LICENSE_UNCLEAR"
    else:
        status = "READY_FOR_PREREGISTRATION"

    return {
        "schema": RESULT_SCHEMA,
        "protocol_id": "kairos.live-seq-gse141064.feasibility.v0.1",
        "dataset_id": "GSE141064",
        "status": status,
        "authority": {
            "classification": "RESEARCH_ONLY",
            "experiment_authorization": False,
            "clinical_authorization": False,
        },
        "inputs": {
            "metadata": {
                "path": str(metadata_path),
                "sha256": _sha256(metadata_path),
                "rows": len(rows),
            },
            "count_matrix": {
                "path": str(count_matrix_path),
                "sha256": _sha256(count_matrix_path),
                "sample_columns": len(count_columns),
            },
            "data_reuse_status": data_reuse_status,
        },
        "cohort": {
            "selection_uses_response_label": False,
            "response_field": RESPONSE_FIELD,
            "selected_recorded_cells": len(selected),
            "response_complete_cells": len(response_complete),
            "selected_sample_ids": selected_ids,
            "missing_response_sample_ids": missing_response_ids,
            "missing_selected_sample_ids": missing_selected,
            "replicate_groups": replicate_groups,
            "repeated_measurement_rows": repeated_measurement_rows,
        },
        "integrity": {
            "metadata_ids_unique": len(metadata_ids) == len(set(metadata_ids)),
            "count_ids_unique": len(count_columns) == len(set(count_columns)),
            "full_id_sets_match": set(metadata_ids) == count_set,
            "errors": integrity_errors,
        },
        "next_action": {
            "READY_FOR_PREREGISTRATION": "Freeze the real-data model protocol before fitting any model.",
            "BLOCKED_MISSING_CELL_LINKAGE": "Resolve selected metadata IDs absent from the count matrix.",
            "BLOCKED_MISSING_RESPONSE_LABELS": "Resolve or explicitly exclude missing downstream labels before defining the modelling cohort.",
            "BLOCKED_INSUFFICIENT_REPLICATES": "Define or recover an auditable replicate-aware split.",
            "BLOCKED_LICENSE_UNCLEAR": "Document dataset reuse terms before redistributing derived inputs.",
            "BLOCKED_DATA_INTEGRITY": "Resolve metadata/count-matrix integrity failures before modelling.",
        }[status],
        "limitations": [
            "A successful audit validates data linkage only, not predictive performance.",
            "Cell-cycle state is expected to be inferred from pre-intervention transcriptomes.",
            "No causal, safety, therapeutic, X-Cell, or experimental authorization claim is made.",
        ],
    }


def main() -> int:
    """Run the local audit and emit JSON on both success and blocked outcomes."""
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    parser.add_argument("count_matrix", type=Path)
    parser.add_argument(
        "--data-reuse-status",
        choices=("clear", "unclear"),
        default="unclear",
    )
    args = parser.parse_args()

    try:
        result = audit(
            args.metadata,
            args.count_matrix,
            data_reuse_status=args.data_reuse_status,
        )
    except AuditError as exc:
        result = {
            "schema": RESULT_SCHEMA,
            "dataset_id": "GSE141064",
            "status": "BLOCKED_DATA_INTEGRITY",
            "authority": {
                "classification": "RESEARCH_ONLY",
                "experiment_authorization": False,
                "clinical_authorization": False,
            },
            "error": str(exc),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "READY_FOR_PREREGISTRATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
