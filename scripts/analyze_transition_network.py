#!/usr/bin/env python3
"""Analyze a Kairos transition-network JSON document fail-closed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from kairos_gate.transition_graph import TransitionGraphError, analyze_transition_network


def _reject_constant(value: str) -> None:
    raise TransitionGraphError(f"input contains non-standard JSON constant: {value}")


def load_graph(path: Path) -> dict[str, Any]:
    try:
        graph = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransitionGraphError(f"unable to load graph: {exc}") from exc
    if not isinstance(graph, dict):
        raise TransitionGraphError("graph root must be an object")
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path)
    parser.add_argument("--enforce", action="store_true", help="return non-zero for BLOCK")
    args = parser.parse_args()

    try:
        report = analyze_transition_network(load_graph(args.graph))
    except TransitionGraphError as exc:
        print(json.dumps({"verdict": "BLOCK", "error": str(exc)}, sort_keys=True))
        return 2

    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    if args.enforce and report["verdict"] == "BLOCK":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
