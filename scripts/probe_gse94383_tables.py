#!/usr/bin/env python3
"""Probe public GSE94383 supplementary tables before freezing analysis code.

The probe is deliberately descriptive. It does not choose outcome features or
run hypothesis tests. Its purpose is to expose table orientation, identifiers,
and whether Nfkbia is present before the conceptual-replication endpoint is
implemented.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def probe(path: Path) -> None:
    frame = pd.read_csv(path)
    print(f"\n=== {path.name} ===")
    print(f"shape={frame.shape}")
    print("columns:")
    for column in frame.columns[:30]:
        print(f"  - {column!r}")
    if len(frame.columns) > 30:
        print(f"  ... {len(frame.columns) - 30} more")

    print("dtypes:")
    for column, dtype in frame.dtypes.head(20).items():
        print(f"  - {column!r}: {dtype}")

    print("head:")
    print(frame.head(5).to_string(max_cols=12, max_colwidth=40))

    nfkbia_column_hits = [column for column in frame.columns if "nfkbia" in str(column).lower()]
    print(f"Nfkbia column hits: {nfkbia_column_hits}")

    object_columns = list(frame.select_dtypes(include=["object"]).columns)
    row_hits: list[tuple[int, str, str]] = []
    for column in object_columns:
        series = frame[column].astype(str)
        mask = series.str.contains("nfkbia", case=False, na=False)
        for index, value in series[mask].head(10).items():
            row_hits.append((int(index) if isinstance(index, int) else -1, str(column), value))
    print(f"Nfkbia row hits: {row_hits[:20]}")

    for column in object_columns[:10]:
        values = frame[column].dropna().astype(str).unique()[:15]
        print(f"sample values {column!r}: {values.tolist()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tables", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.tables:
        probe(path)


if __name__ == "__main__":
    main()
