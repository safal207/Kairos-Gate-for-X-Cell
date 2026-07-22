"""Summarize technical grouping candidates for the pinned Live-seq cohort.

This script does not infer biological replicate semantics. It reports only fields
present in public metadata and keeps confirmatory modelling blocked until an
independent experimental unit is documented.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

RESULT_SCHEMA = "kairos.live-seq-technical-group-summary.v0.1"
REQUIRED_COLUMNS = {
    "sample_ID",
    "sample_name",
    "original_sample_name",
    "Batch",
    "Cell_type",
    "sampling_type",
    "treatment",
    "mCherry.log.intercept",
    "Sequencing_run",
    "i5_index",
    "i7_index",
    "Date",
    "Probe",
}


class SummaryError(ValueError):
    """Raised when metadata cannot support a deterministic technical summary."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _finite_number(value: Any) -> float | None:
    text = "" if value is None else str(value).strip()
    if not text or text.upper() in {"NA", "N/A", "NAN", "NULL"}:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def _prefix(value: str) -> str:
    text = value.strip()
    return text.split("_", 1)[0] if text else "<missing>"


def _load(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or [])
            missing = sorted(REQUIRED_COLUMNS - fields)
            if missing:
                raise SummaryError(f"metadata missing required columns: {missing}")
            rows = [dict(row) for row in reader]
    except (OSError, csv.Error, UnicodeError) as exc:
        raise SummaryError(f"unable to read metadata: {exc}") from exc
    if not rows:
        raise SummaryError("metadata contains no rows")
    return rows


def _select(rows: list[dict[str, str]]) -> list[dict[str, str]]:
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
    if not selected:
        raise SummaryError("no rows satisfy the response-independent cohort rule")
    return selected


def _counts(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def summarize(metadata_path: Path) -> dict[str, Any]:
    """Return a technical map without assigning biological replicate meaning."""
    rows = _load(metadata_path)
    selected = _select(rows)

    ids = [str(row["sample_ID"]).strip() for row in selected]
    if any(not value for value in ids):
        raise SummaryError("selected cohort contains an empty sample_ID")
    if len(ids) != len(set(ids)):
        raise SummaryError("selected cohort contains duplicate sample_ID values")

    records = []
    for row in selected:
        i5 = str(row.get("i5_index", "")).strip() or "<missing>"
        i7 = str(row.get("i7_index", "")).strip() or "<missing>"
        records.append(
            {
                "sample_ID": str(row["sample_ID"]).strip(),
                "sample_name": str(row.get("sample_name", "")).strip(),
                "original_sample_name": str(
                    row.get("original_sample_name", "")
                ).strip(),
                "plate_like_prefix": _prefix(str(row.get("sample_name", ""))),
                "original_name_prefix": _prefix(
                    str(row.get("original_sample_name", ""))
                ),
                "sequencing_run": str(row.get("Sequencing_run", "")).strip()
                or "<missing>",
                "i5_index": i5,
                "i7_index": i7,
                "index_pair": f"{i5}|{i7}",
                "date": str(row.get("Date", "")).strip() or "<missing>",
                "probe": str(row.get("Probe", "")).strip() or "<missing>",
            }
        )

    dimensions = {
        "plate_like_prefix": _counts(
            [record["plate_like_prefix"] for record in records]
        ),
        "original_name_prefix": _counts(
            [record["original_name_prefix"] for record in records]
        ),
        "sequencing_run": _counts([record["sequencing_run"] for record in records]),
        "i5_index": _counts([record["i5_index"] for record in records]),
        "i7_index": _counts([record["i7_index"] for record in records]),
        "index_pair": _counts([record["index_pair"] for record in records]),
        "date": _counts([record["date"] for record in records]),
        "probe": _counts([record["probe"] for record in records]),
    }

    return {
        "schema": RESULT_SCHEMA,
        "dataset_id": "GSE141064",
        "metadata": {
            "path": str(metadata_path),
            "sha256": _sha256(metadata_path),
            "rows": len(rows),
        },
        "cohort": {
            "selection_uses_response_label": False,
            "selected_cells": len(records),
            "sample_ids": ids,
        },
        "technical_group_candidates": dimensions,
        "selected_records": records,
        "decision": {
            "classification": "EXPLORATORY_ONLY_TECHNICAL_GROUPING",
            "replicate_semantics_verified": False,
            "confirmatory_preregistration_unlocked": False,
            "status": "BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED",
            "reason": (
                "Public metadata expose technical group candidates, but no reviewed "
                "source yet establishes them as independent biological or experimental "
                "replicates."
            ),
        },
        "authority": {
            "classification": "RESEARCH_ONLY",
            "experiment_authorization": False,
            "clinical_authorization": False,
            "merge_authorization": False,
        },
        "limitations": [
            "Plate, well, sequencing-run, and index fields are technical metadata.",
            "Distinct technical labels do not prove independent cultures or experiments.",
            "No model split or performance estimate is authorized by this summary.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.metadata)
    except SummaryError as exc:
        print(
            json.dumps(
                {
                    "schema": RESULT_SCHEMA,
                    "dataset_id": "GSE141064",
                    "status": "BLOCKED_DATA_INTEGRITY",
                    "error": str(exc),
                    "authority": {"classification": "RESEARCH_ONLY"},
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
