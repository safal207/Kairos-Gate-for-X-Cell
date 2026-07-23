#!/usr/bin/env python3
"""Compare exact GSE184241 count-matrix and barcode-workbook cell identities."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from run_gse184241_donor_baselines_v2 import clean_identifier, load_counts, sha256_file


def digest_identifiers(values: set[str]) -> str:
    """Hash one sorted identifier set using newline-delimited UTF-8 text."""
    return hashlib.sha256("\n".join(sorted(values)).encode("utf-8")).hexdigest()


def main() -> int:
    """Write exact identity diagnostics without changing or filtering inputs."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", required=True)
    parser.add_argument("--barcodes", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    counts_path = Path(args.counts)
    barcodes_path = Path(args.barcodes)
    counts = load_counts(counts_path)
    workbook = pd.read_excel(barcodes_path, sheet_name=0)
    if "Sample_ID" not in workbook.columns:
        raise ValueError("barcode workbook lacks Sample_ID")

    count_ids = {clean_identifier(value) for value in counts.columns}
    shared_clean_ids = {clean_identifier(value) for value in workbook["Sample_ID"].dropna()}
    inline_clean_ids = {
        str(value).strip().strip('"').strip("'")
        for value in workbook["Sample_ID"].dropna()
    }
    result = {
        "schema_version": "0.1.0",
        "artifact_type": "gse184241_cell_identity_diagnostic",
        "files": {
            "counts_sha256": sha256_file(counts_path),
            "barcodes_sha256": sha256_file(barcodes_path),
        },
        "counts": {
            "matrix_shape": [int(counts.shape[0]), int(counts.shape[1])],
            "identifier_count": len(count_ids),
            "identifier_sha256": digest_identifiers(count_ids),
            "first_10": sorted(count_ids)[:10],
            "last_10": sorted(count_ids)[-10:],
        },
        "workbook_shared_clean": {
            "identifier_count": len(shared_clean_ids),
            "identifier_sha256": digest_identifiers(shared_clean_ids),
            "first_10": sorted(shared_clean_ids)[:10],
            "last_10": sorted(shared_clean_ids)[-10:],
        },
        "workbook_inline_clean": {
            "identifier_count": len(inline_clean_ids),
            "identifier_sha256": digest_identifiers(inline_clean_ids),
            "first_10": sorted(inline_clean_ids)[:10],
            "last_10": sorted(inline_clean_ids)[-10:],
        },
        "comparison": {
            "shared_clean_equal": count_ids == shared_clean_ids,
            "inline_clean_equal": count_ids == inline_clean_ids,
            "shared_vs_inline_equal": shared_clean_ids == inline_clean_ids,
            "missing_in_workbook_shared": sorted(count_ids - shared_clean_ids)[:50],
            "missing_in_counts_shared": sorted(shared_clean_ids - count_ids)[:50],
            "missing_in_workbook_inline": sorted(count_ids - inline_clean_ids)[:50],
            "missing_in_counts_inline": sorted(inline_clean_ids - count_ids)[:50],
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["comparison"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
