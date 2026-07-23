#!/usr/bin/env python3
"""Compare generated and canonical benchmark evidence.

All structural and string fields must match exactly. Finite numeric values may
vary by at most 1e-8 to accommodate BLAS-level floating-point jitter.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ABS_TOL = 1e-8
REL_TOL = 1e-9


def compare(left: Any, right: Any, path: str, errors: list[str]) -> None:
    if isinstance(left, bool) or isinstance(right, bool):
        if left is not right:
            errors.append(f"{path}: {left!r} != {right!r}")
        return
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if not (math.isfinite(float(left)) and math.isfinite(float(right))):
            if left != right:
                errors.append(f"{path}: non-finite mismatch")
        elif not math.isclose(float(left), float(right), rel_tol=REL_TOL, abs_tol=ABS_TOL):
            errors.append(f"{path}: {left!r} != {right!r}")
        return
    if type(left) is not type(right):
        errors.append(f"{path}: type {type(left).__name__} != {type(right).__name__}")
        return
    if isinstance(left, dict):
        if set(left) != set(right):
            errors.append(f"{path}: keys differ: {sorted(set(left) ^ set(right))}")
            return
        for key in sorted(left):
            compare(left[key], right[key], f"{path}.{key}", errors)
        return
    if isinstance(left, list):
        if len(left) != len(right):
            errors.append(f"{path}: length {len(left)} != {len(right)}")
            return
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            compare(left_item, right_item, f"{path}[{index}]", errors)
        return
    if left != right:
        errors.append(f"{path}: {left!r} != {right!r}")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: compare_gse184241_benchmark_evidence.py <generated.json> <canonical.json>", file=sys.stderr)
        return 2
    generated = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    canonical = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    generated.pop("source_revision", None)
    canonical.pop("source_revision", None)
    errors: list[str] = []
    compare(generated, canonical, "$", errors)
    if errors:
        print("DRIFT")
        for error in errors[:50]:
            print(f"- {error}")
        return 1
    print(f"MATCH_WITH_NUMERIC_TOLERANCE abs={ABS_TOL} rel={REL_TOL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
