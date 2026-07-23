#!/usr/bin/env python3
"""Probe the Live-seq Supplementary Table 4 workbook without interpreting it as replication."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: probe_live_seq_supplementary_table4.py INPUT.xlsx OUTPUT.json", file=sys.stderr)
        return 2

    source = Path(argv[1])
    output = Path(argv[2])
    raw = source.read_bytes()
    workbook = load_workbook(source, read_only=True, data_only=False)

    report: dict[str, Any] = {
        "source_file": source.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "sheet_count": len(workbook.sheetnames),
        "sheets": [],
        "nfkbia_hits": [],
        "interpretation_boundary": {
            "artifact_role": "original-study model-ranking supplement",
            "external_replication": False,
            "causal_identification": False,
            "notes": "This probe preserves workbook structure and locates Nfkbia. It does not establish biological independence, direct replication, or causality."
        }
    }

    for sheet_name in workbook.sheetnames:
        ws = workbook[sheet_name]
        rows: list[list[str]] = []
        nonempty = 0
        max_seen_columns = 0
        for row_index, row in enumerate(ws.iter_rows(values_only=True), start=1):
            values = [text(value) for value in row]
            while values and values[-1] == "":
                values.pop()
            if values:
                nonempty += 1
                max_seen_columns = max(max_seen_columns, len(values))
                if len(rows) < 8:
                    rows.append(values[:20])
                for column_index, value in enumerate(values, start=1):
                    if value.lower() == "nfkbia" or "nfkbia" in value.lower():
                        report["nfkbia_hits"].append({
                            "sheet": sheet_name,
                            "row": row_index,
                            "column": column_index,
                            "value": value,
                            "row_preview": values[:20]
                        })

        report["sheets"].append({
            "name": sheet_name,
            "max_row_declared": ws.max_row,
            "max_column_declared": ws.max_column,
            "nonempty_rows": nonempty,
            "max_seen_columns": max_seen_columns,
            "first_nonempty_rows": rows
        })

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "sha256": report["sha256"],
        "size_bytes": report["size_bytes"],
        "sheet_count": report["sheet_count"],
        "nfkbia_hit_count": len(report["nfkbia_hits"]),
        "output": str(output)
    }, indent=2))

    if report["sheet_count"] < 1:
        print("workbook contains no sheets", file=sys.stderr)
        return 1
    if len(report["nfkbia_hits"]) < 1:
        print("Nfkbia was not found in Supplementary Table 4", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
