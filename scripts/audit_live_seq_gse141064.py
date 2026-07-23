"""Deprecated compatibility CLI for the GSE141064 readiness audit.

All cohort, linkage, repeated-identity, replicate-semantics, licensing, and
readiness decisions are delegated to the Dataset Readiness Scanner. This module
preserves the historical positional command shape and exit-code contract only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from kairos_gate.dataset_adapters import get_adapter
from kairos_gate.dataset_readiness import (
    DatasetReadinessError,
    READY,
    evaluate_contract,
    validate_manifest_record,
)

AuditError = DatasetReadinessError

MANIFEST_SCHEMA = "kairos.dataset-manifest.v0.1"
DATASET_ID = "GSE141064"
DATASET_VERSION = "pinned-2026-07-v0.1"
ADAPTER_NAME = "live-seq-gse141064"
META_URL = (
    "https://raw.githubusercontent.com/DeplanckeLab/Live-seq/"
    "6633d4d468f56031ea197474e09921088d878512/data/meta.final.csv"
)
COUNT_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/download/"
    "?acc=GSE141064&file=GSE141064_count.final.csv.gz&format=file"
)
DEPRECATION = (
    "DEPRECATED: scripts/audit_live_seq_gse141064.py is a compatibility shim; "
    "use `kairos audit-dataset` with the pinned GSE141064 manifest."
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DatasetReadinessError(f"unable to hash input {path}: {exc}") from exc
    return f"sha256:{digest.hexdigest()}"


def _compatibility_manifest(
    metadata_path: Path,
    count_matrix_path: Path,
    *,
    data_reuse_status: str,
) -> dict[str, Any]:
    """Build the bounded manifest required by the canonical scanner engine."""
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "adapter": {"name": ADAPTER_NAME},
        "sources": [
            {
                "role": "metadata",
                "url": META_URL,
                "version": "Live-seq@6633d4d468f56031ea197474e09921088d878512",
                "sha256": _sha256(metadata_path),
            },
            {
                "role": "matrix",
                "url": COUNT_URL,
                "version": "GEO:GSE141064-count-final",
                "sha256": _sha256(count_matrix_path),
            },
        ],
        "reuse_status": data_reuse_status,
        "minimum_independent_units": 2,
    }
    validate_manifest_record(manifest)
    return manifest


def audit(
    metadata_path: Path,
    count_matrix_path: Path,
    *,
    data_reuse_status: str,
) -> dict[str, Any]:
    """Delegate the historical audit call to the canonical readiness engine."""
    manifest = _compatibility_manifest(
        metadata_path,
        count_matrix_path,
        data_reuse_status=data_reuse_status,
    )
    adapter = get_adapter(manifest["adapter"])
    contract = adapter.build_contract(metadata_path, count_matrix_path)
    return evaluate_contract(
        contract,
        manifest,
        input_digests={
            "metadata": manifest["sources"][0]["sha256"],
            "matrix": manifest["sources"][1]["sha256"],
        },
    )


def _error_record(exc: Exception) -> dict[str, Any]:
    return {
        "schema": "kairos.dataset-readiness-compatibility-error.v0.1",
        "dataset": {
            "id": DATASET_ID,
            "version": DATASET_VERSION,
            "adapter": ADAPTER_NAME,
        },
        "status": "BLOCKED_DATA_INTEGRITY",
        "authority": {
            "classification": "RESEARCH_ONLY",
            "preregistration_gate_passed": False,
            "model_fitting_authorized": False,
            "experiment_authorization": False,
            "clinical_authorization": False,
            "merge_authorization": False,
        },
        "deprecated_entrypoint": True,
        "error": str(exc),
    }


def main(argv: list[str] | None = None) -> int:
    """Preserve the legacy command shape while emitting scanner result records."""
    parser = argparse.ArgumentParser(
        description="Deprecated GSE141064 compatibility wrapper for kairos audit-dataset"
    )
    parser.add_argument("metadata", type=Path)
    parser.add_argument("count_matrix", type=Path)
    parser.add_argument(
        "--data-reuse-status",
        choices=("clear", "unclear"),
        default="unclear",
    )
    args = parser.parse_args(argv)

    print(DEPRECATION, file=sys.stderr)
    try:
        result = audit(
            args.metadata,
            args.count_matrix,
            data_reuse_status=args.data_reuse_status,
        )
    except (OSError, ValueError, DatasetReadinessError) as exc:
        print(json.dumps(_error_record(exc), indent=2, sort_keys=True, allow_nan=False))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
