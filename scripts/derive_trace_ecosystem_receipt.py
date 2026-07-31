#!/usr/bin/env python3
"""Derive a Kairos/CML/ProofPath/LiminalDB receipt from a pinned TRACE package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from kairos_gate.trace_evidence_bridge import (
    TraceEvidenceBridgeError,
    build_trace_ecosystem_receipt,
    validate_pinned_manifest,
)


def _reject_constant(value: str) -> None:
    raise TraceEvidenceBridgeError(f"non-standard JSON constant: {value}")


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle, parse_constant=_reject_constant)
    except (OSError, json.JSONDecodeError) as exc:
        raise TraceEvidenceBridgeError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise TraceEvidenceBridgeError(f"{path} root must be an object")
    return value


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_package(
    manifest: Mapping[str, Any], source_dir: Path
) -> tuple[dict[str, Mapping[str, Any]], list[dict[str, Any]]]:
    package: dict[str, Mapping[str, Any]] = {}
    receipts: list[dict[str, Any]] = []
    for item in manifest["files"]:
        role = item["role"]
        relative_path = Path(item["path"])
        path = source_dir / relative_path.name
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise TraceEvidenceBridgeError(f"cannot read package role {role}: {exc}") from exc
        actual_blob = _git_blob_sha(data)
        if actual_blob != item["git_blob_sha"]:
            raise TraceEvidenceBridgeError(
                f"Git blob mismatch for {role}: {actual_blob} != {item['git_blob_sha']}"
            )
        try:
            document = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TraceEvidenceBridgeError(f"invalid JSON for package role {role}: {exc}") from exc
        if not isinstance(document, Mapping):
            raise TraceEvidenceBridgeError(f"package role {role} root must be an object")
        package[role] = document
        receipts.append(
            {
                "id": role,
                "path": item["path"],
                "git_blob_sha": actual_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        )
    return package, receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    try:
        manifest = _load_json(args.manifest)
        validate_pinned_manifest(manifest)
        package, receipts = _load_package(manifest, args.source_dir)
        result = build_trace_ecosystem_receipt(manifest, package, receipts)
    except TraceEvidenceBridgeError as exc:
        print(f"BLOCK {exc}")
        return 2

    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.enforce:
        analysis = result["kairos_analysis"]
        if analysis["verdict"] != "ACCEPT_WITH_LIMITS":
            print("BLOCK unexpected Kairos verdict")
            return 2
        if analysis["temporal_conflicts"]:
            print("BLOCK temporal conflicts present")
            return 2
        if analysis["claim_firewall"]:
            print("BLOCK claim firewall violation present")
            return 2
        if result["proofpath_projection"]["decision"] != "HOLD":
            print("BLOCK ProofPath must remain HOLD")
            return 2
        if result["liminaldb_projection"]["projection"]["adds_scientific_verdict"] is not False:
            print("BLOCK LiminalDB added a verdict")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
