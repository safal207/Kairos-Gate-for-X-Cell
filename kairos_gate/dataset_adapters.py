"""Dataset-specific adapters that emit the canonical readiness contract."""

from __future__ import annotations

import csv
import gzip
import math
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping, Protocol, TextIO

from .dataset_readiness import DatasetReadinessError

MISSING_MARKERS = {"", "NA", "N/A", "NAN", "NULL"}


class SourceAdapter(Protocol):
    """Adapter contract for translating source files into canonical records."""

    def build_contract(self, metadata_path: Path, matrix_path: Path) -> Mapping[str, Any]:
        """Build a canonical dataset contract without fitting a model."""


@contextmanager
def _open_text(path: Path) -> Iterator[TextIO]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            yield handle
    else:
        with path.open("r", encoding="utf-8", newline="") as handle:
            yield handle


def _load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
    except (OSError, csv.Error, UnicodeError) as exc:
        raise DatasetReadinessError(f"unable to read metadata: {exc}") from exc
    if not fieldnames:
        raise DatasetReadinessError("metadata header is missing")
    if not rows:
        raise DatasetReadinessError("metadata contains no rows")
    return fieldnames, rows


def _load_matrix_ids(path: Path) -> list[str]:
    try:
        with _open_text(path) as handle:
            header = next(csv.reader(handle), None)
    except (OSError, csv.Error, UnicodeError) as exc:
        raise DatasetReadinessError(f"unable to read matrix header: {exc}") from exc
    if not header or len(header) < 2:
        raise DatasetReadinessError(
            "matrix header must contain one feature column and at least one sample"
        )
    return [str(value).strip() for value in header[1:]]


def _finite_number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.upper() in MISSING_MARKERS:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


class LiveSeqGSE141064Adapter:
    """Translate the reviewed Live-seq metadata contract into canonical records."""

    REQUIRED_COLUMNS = {
        "sample_ID",
        "Batch",
        "Cell_type",
        "sampling_type",
        "treatment",
        "Probe",
        "Date",
        "mCherry.log.intercept",
        "mCherry.log.slope",
        "double_extraction",
    }

    def build_contract(self, metadata_path: Path, matrix_path: Path) -> Mapping[str, Any]:
        fieldnames, rows = _load_rows(metadata_path)
        missing = sorted(self.REQUIRED_COLUMNS - set(fieldnames))
        if missing:
            raise DatasetReadinessError(
                f"Live-seq metadata missing required columns: {missing}"
            )

        records: list[dict[str, Any]] = []
        for row in rows:
            intercept = _finite_number(row.get("mCherry.log.intercept"))
            selected = (
                row.get("sampling_type") == "Live_seq"
                and row.get("Cell_type") == "Raw264.7_G9"
                and row.get("treatment") == "not_treated"
                and row.get("Batch") == "8_8"
                and intercept is not None
                and intercept > 0
            )
            date = str(row.get("Date", "")).strip()
            probe = str(row.get("Probe", "")).strip()
            independent_unit = f"{date}|{probe}" if date or probe else None
            repeated = str(row.get("double_extraction", "")).strip()
            records.append(
                {
                    "sample_id": str(row.get("sample_ID", "")).strip(),
                    "selected": selected,
                    "response_available": (
                        _finite_number(row.get("mCherry.log.slope")) is not None
                    ),
                    "independent_unit": independent_unit,
                    "repeated_identity": (
                        None if repeated.upper() in MISSING_MARKERS else repeated
                    ),
                }
            )

        return {
            "metadata_path": str(metadata_path),
            "matrix_path": str(matrix_path),
            "metadata_ids": [
                str(row.get("sample_ID", "")).strip() for row in rows
            ],
            "matrix_ids": _load_matrix_ids(matrix_path),
            "records": records,
            "replicate_semantics": "unresolved",
        }


class TabularAdapter:
    """Generic CSV adapter configured entirely by manifest field mappings."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        semantics = self.config.get("replicate_semantics")
        if semantics not in {"verified", "technical_only", "unresolved"}:
            raise DatasetReadinessError(
                f"unsupported tabular replicate semantics: {semantics!r}"
            )

    def _selected(self, row: Mapping[str, str]) -> bool:
        for rule in self.config.get("selection", []):
            field = rule["field"]
            if "equals" in rule and row.get(field) != str(rule["equals"]):
                return False
            if "numeric_gt" in rule:
                value = _finite_number(row.get(field))
                if value is None or value <= float(rule["numeric_gt"]):
                    return False
        return True

    def build_contract(self, metadata_path: Path, matrix_path: Path) -> Mapping[str, Any]:
        fieldnames, rows = _load_rows(metadata_path)
        id_field = self.config["id_field"]
        response_field = self.config["response_field"]
        unit_fields = list(self.config.get("independent_unit_fields", []))
        repeated_field = self.config.get("repeated_identity_field")

        required = {id_field, response_field}
        required.update(rule["field"] for rule in self.config.get("selection", []))
        required.update(unit_fields)
        if repeated_field:
            required.add(repeated_field)
        missing = sorted(required - set(fieldnames))
        if missing:
            raise DatasetReadinessError(
                f"tabular metadata missing configured columns: {missing}"
            )

        records: list[dict[str, Any]] = []
        for row in rows:
            unit_values = [str(row.get(field, "")).strip() for field in unit_fields]
            independent_unit = "|".join(unit_values) if any(unit_values) else None
            repeated = str(row.get(repeated_field, "")).strip() if repeated_field else ""
            records.append(
                {
                    "sample_id": str(row.get(id_field, "")).strip(),
                    "selected": self._selected(row),
                    "response_available": _finite_number(row.get(response_field))
                    is not None,
                    "independent_unit": independent_unit,
                    "repeated_identity": (
                        None if repeated.upper() in MISSING_MARKERS else repeated
                    ),
                }
            )

        return {
            "metadata_path": str(metadata_path),
            "matrix_path": str(matrix_path),
            "metadata_ids": [str(row.get(id_field, "")).strip() for row in rows],
            "matrix_ids": _load_matrix_ids(matrix_path),
            "records": records,
            "replicate_semantics": self.config["replicate_semantics"],
        }


def get_adapter(adapter_record: Mapping[str, Any]) -> SourceAdapter:
    """Resolve one declared adapter without dynamic imports or source execution."""
    name = adapter_record.get("name")
    if name == "live-seq-gse141064":
        return LiveSeqGSE141064Adapter()
    if name == "tabular-v0.1":
        config = adapter_record.get("config")
        if not isinstance(config, Mapping):
            raise DatasetReadinessError("tabular-v0.1 adapter requires config")
        return TabularAdapter(config)
    raise DatasetReadinessError(f"unsupported dataset adapter: {name!r}")
