#!/usr/bin/env python3
"""Apply a deterministic dotted-path mutation fixture to a generated JSON document."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def tokens(path: str) -> list[str | int]:
    parsed: list[str | int] = []
    for match in TOKEN_RE.finditer(path):
        name, index = match.groups()
        parsed.append(int(index) if index is not None else name)
    return parsed


def set_path(document: Any, path: str, value: Any, aliases: dict[str, str]) -> None:
    parts = tokens(path)
    current = document
    for position, part in enumerate(parts[:-1]):
        if isinstance(current, dict) and part in aliases:
            part = aliases[str(part)]
        next_part = parts[position + 1]
        current = current[part]
        if isinstance(current, dict) and next_part in aliases:
            parts[position + 1] = aliases[str(next_part)]
    final = parts[-1]
    if isinstance(current, dict) and final in aliases:
        final = aliases[str(final)]
    current[final] = value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    aliases = {
        "RUNTIME_OBSERVATION": document["records"][2]["record_ref"],
        "CONTINUITY": document["records"][5]["record_ref"],
    }
    for path, value in fixture["set"].items():
        set_path(document, path, value, aliases)
    Path(args.output).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output, "mutations": len(fixture["set"]), "expected_verdict": fixture["expected_verdict"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
