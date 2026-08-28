#!/usr/bin/env python3
"""Canonical AI-designed molecule validator with preview.4 semantic hardening.

The large baseline implementation is kept in the adjacent private core module.
This public entrypoint supplies the single level-aware provenance policy and
adds cross-field invariants discovered during exact-head adversarial review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import _validate_ai_designed_molecule_claim_audit_core as core

SCHEMA_VERSION = core.SCHEMA_VERSION


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and core.SHA256_RE.fullmatch(value) is not None


def provenance_valid_for_level(
    *,
    level: str,
    provenance: Any,
    publication_urls: set[str],
    context: str,
    errors: list[str],
    external: bool,
) -> None:
    """Apply evidence-level rules, including F3/F4 risk-assessment artifacts."""

    core.require(isinstance(provenance, dict), f"{context}: provenance required", errors)
    if not isinstance(provenance, dict):
        return

    role = provenance.get("source_role")
    url = provenance.get("source_url")
    locator = provenance.get("source_locator")
    derivation = provenance.get("derivation")
    artifact_kind = provenance.get("artifact_kind")
    confirmation = provenance.get("confirmation_type")
    digest = provenance.get("artifact_sha256")

    core.require(
        isinstance(locator, str) and bool(locator.strip()),
        f"{context}: source_locator must contain non-whitespace characters",
        errors,
    )
    if role in {"primary_publication", "supplementary_material", "structure_record"}:
        core.require(
            url in publication_urls,
            f"{context}: provenance URL must be listed by source_publication",
            errors,
        )

    if derivation in {"reconstructed", "computed"}:
        core.require(
            _valid_digest(digest),
            f"{context}: reconstructed/computed evidence requires artifact SHA-256",
            errors,
        )

    if level in {"F0", "F1", "F2"}:
        core.require(
            role in {"primary_publication", "supplementary_material", "structure_record"},
            f"{context}: F0-F2 must remain publication or repository reporting",
            errors,
        )
        core.require(
            derivation == "directly_reported",
            f"{context}: F0-F2 must be directly reported",
            errors,
        )

    if level == "F3":
        standard_f3 = (
            role == "derived_artifact"
            and derivation in {"reconstructed", "computed"}
            and artifact_kind in {"executable_analysis", "reproducibility_bundle"}
            and _valid_digest(digest)
        )
        risk_f3 = (
            external
            and role == "derived_artifact"
            and derivation in {"reconstructed", "computed"}
            and artifact_kind == "risk_assessment_record"
            and _valid_digest(digest)
        )
        core.require(
            standard_f3 or risk_f3,
            f"{context}: F3 requires a digested executable, reproducibility, or risk-assessment artifact",
            errors,
        )

    if level == "F4":
        structure_confirmation = (
            role == "structure_record"
            and derivation == "directly_reported"
            and artifact_kind == "deposited_structure"
            and confirmation == "repository_record"
        )
        laboratory_confirmation = (
            role == "laboratory_confirmation"
            and derivation == "directly_reported"
            and artifact_kind == "author_confirmation"
            and confirmation == "author_or_laboratory_confirmation"
            and _valid_digest(digest)
        )
        risk_confirmation = (
            external
            and role == "laboratory_confirmation"
            and derivation == "directly_reported"
            and artifact_kind == "risk_assessment_record"
            and confirmation == "author_or_laboratory_confirmation"
            and _valid_digest(digest)
        )
        core.require(
            structure_confirmation or laboratory_confirmation or risk_confirmation,
            f"{context}: F4 requires repository, laboratory, or risk-assessment confirmation",
            errors,
        )

    if level == "F5":
        core.require(external, f"{context}: F5 is reserved for external evidence objects", errors)
        core.require(
            role == "laboratory_confirmation"
            and derivation == "directly_reported"
            and artifact_kind in {"independent_replication_record", "risk_assessment_record"}
            and confirmation == "independent_laboratory_replication"
            and _valid_digest(digest),
            f"{context}: F5 requires a frozen independent-laboratory evidence artifact",
            errors,
        )


def _additional_semantic_checks(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    screening = record.get("screening_context", {})
    if isinstance(screening, dict) and screening.get("selected_count_status") == "positive_nonexact":
        for field in ("generated_count", "screened_count"):
            value = screening.get(field)
            if core.is_int(value):
                core.require(
                    value > 0,
                    f"positive_nonexact selection cannot follow known zero {field}",
                    errors,
                )

    assays = record.get("assays", [])
    if isinstance(assays, list):
        for index, assay in enumerate(assays):
            if not isinstance(assay, dict):
                continue
            system = assay.get("system")
            if system not in core.FUNCTIONAL_SYSTEMS:
                continue
            assay_id = str(assay.get("assay_id") or index)
            direction = assay.get("result_direction")
            endpoints = assay.get("endpoint_types", [])
            endpoint_set = {str(value) for value in endpoints} if isinstance(endpoints, list) else set()

            if direction == "retained_reference_activity":
                core.require(
                    endpoint_set == {"molecular_activity"},
                    f"assay {assay_id}: retained_reference_activity cannot assert comparator superiority",
                    errors,
                )
            elif direction == "exceeded_reference_activity":
                core.require(
                    "bounded_comparator_superiority" in endpoint_set,
                    f"assay {assay_id}: exceeded_reference_activity requires comparator-superiority endpoint",
                    errors,
                )
            elif direction == "mixed":
                core.require(
                    {"molecular_activity", "bounded_comparator_superiority"}.issubset(endpoint_set),
                    f"assay {assay_id}: mixed activity requires molecular and comparator-superiority endpoints",
                    errors,
                )

    return errors


def validate(record: dict[str, Any]) -> list[str]:
    return core.validate(
        record,
        provenance_rule=provenance_valid_for_level,
    ) + _additional_semantic_checks(record)


def load_json(path: Path) -> dict[str, Any]:
    return core.load_json(path)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate_ai_designed_molecule_claim_audit.py AUDIT.json [...]", file=sys.stderr)
        return 2

    failed = False
    for raw_path in argv[1:]:
        path = Path(raw_path)
        try:
            errors = validate(load_json(path))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            print(f"BLOCK {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"ACCEPT {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
