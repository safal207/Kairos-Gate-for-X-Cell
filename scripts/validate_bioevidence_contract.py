#!/usr/bin/env python3
"""Canonical schema-first gateway for BioEvidence contract validation.

A record is accepted only when it passes its public Draft 2020-12 JSON Schema
and the corresponding semantic fail-closed validator. Direct semantic
validators remain implementation details; this gateway is the authoritative
acceptance entrypoint for CI and release evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]

CONTRACTS: dict[str, tuple[str, str]] = {
    "experimental-unit": (
        "schemas/experimental-unit-audit.schema.json",
        "scripts/validate_experimental_unit_audit.py",
    ),
    "provenance-confounder": (
        "schemas/bio-provenance-confounder-graph.schema.json",
        "scripts/validate_provenance_confounder_graph.py",
    ),
    "independent-replication": (
        "schemas/independent-replication-search.schema.json",
        "scripts/validate_independent_replication_search.py",
    ),
    "causal-hypothesis": (
        "schemas/causal-hypothesis-ranking.schema.json",
        "scripts/validate_causal_hypothesis_ranking.py",
    ),
    "temporal-replication": (
        "schemas/temporal-replication-gate.schema.json",
        "scripts/validate_temporal_replication_gate.py",
    ),
    "partner-handoff": (
        "schemas/partner-lab-evidence-handoff.schema.json",
        "scripts/validate_partner_lab_evidence_handoff.py",
    ),
}


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_path(parts: Any) -> str:
    """Render a jsonschema error path deterministically."""
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


def load_object(path: Path) -> dict[str, Any]:
    """Load a JSON object without permitting non-object contract roots."""
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("contract root must be a JSON object")
    return value


def validate_schema(record: dict[str, Any], schema_path: Path) -> list[str]:
    """Return deterministic Draft 2020-12 schema and format violations."""
    schema = load_object(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(record),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    return [
        f"schema {json_path(error.absolute_path)}: {error.message}"
        for error in errors
    ]


def validate_semantics(record_path: Path, semantic_path: Path) -> list[str]:
    """Run one semantic validator and normalize its failure output."""
    result = subprocess.run(
        [sys.executable, str(semantic_path), str(record_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if "Traceback" in combined:
        if os.environ.get("BIOEVIDENCE_DEBUG") == "1":
            return ["semantic validator raised an unexpected exception", combined.strip()]
        return ["semantic validator raised an unexpected exception"]

    lines = []
    for raw_line in combined.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("BLOCK "):
            continue
        lines.append(line[2:] if line.startswith("- ") else line)
    return lines or [f"semantic validator exited with status {result.returncode}"]


def validate_one(contract: str, record_path: Path) -> list[str]:
    """Validate one record against schema first, then semantic rules."""
    schema_relative, semantic_relative = CONTRACTS[contract]
    schema_path = ROOT / schema_relative
    semantic_path = ROOT / semantic_relative

    record = load_object(record_path)
    schema_errors = validate_schema(record, schema_path)
    if schema_errors:
        return schema_errors
    return validate_semantics(record_path, semantic_path)


def main(argv: list[str]) -> int:
    """Validate one or more records and emit canonical ACCEPT/BLOCK output."""
    if len(argv) < 3 or argv[1] not in CONTRACTS:
        names = " | ".join(sorted(CONTRACTS))
        print(
            f"usage: validate_bioevidence_contract.py ({names}) RECORD.json [RECORD.json ...]",
            file=sys.stderr,
        )
        return 2

    contract = argv[1]
    schema_relative, semantic_relative = CONTRACTS[contract]
    schema_digest = sha256_file(ROOT / schema_relative)
    failed = False

    for raw_path in argv[2:]:
        record_path = Path(raw_path)
        try:
            errors = validate_one(contract, record_path)
        except (OSError, json.JSONDecodeError, ValueError, SchemaError) as exc:
            errors = [f"validation input error: {exc}"]
        except Exception as exc:  # fail closed without leaking a traceback by default
            if os.environ.get("BIOEVIDENCE_DEBUG") == "1":
                raise
            errors = [f"unexpected validation failure: {type(exc).__name__}"]

        if errors:
            failed = True
            print(f"BLOCK {record_path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"ACCEPT {record_path}")
            print(f"  contract={contract}")
            print(f"  schema={schema_relative}")
            print(f"  schema_sha256={schema_digest}")
            print(f"  semantic_validator={semantic_relative}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
