#!/usr/bin/env python3
"""Validate BioNeMo model compatibility records with fail-closed domain rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry/bionemo-model-registry.v0.2.json"
VERDICTS = {
    "ACCEPT_WITH_LIMITS",
    "SPECIES_COMPATIBILITY_HOLD",
    "MODALITY_COMPATIBILITY_HOLD",
    "TEMPORAL_COMPATIBILITY_HOLD",
    "TRAINING_OVERLAP_HOLD",
    "QUESTION_NOT_APPLICABLE",
    "BLOCK",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_bionemo_model_compatibility.py RECORD.json")
        return 2

    record_path = Path(sys.argv[1])
    try:
        record = load(record_path)
        registry = load(REGISTRY_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCK cannot load input: {exc}")
        return 1

    errors: list[str] = []
    require(record.get("schema_version") == "0.2.0", "schema_version must be 0.2.0", errors)
    require(bool(record.get("assessment_id")), "assessment_id is required", errors)

    for section in (
        "scientific_question", "dataset", "model", "compatibility", "transformations",
        "overlap_assessment", "evidence_contribution", "claim_boundary",
        "overall_verdict", "safety_status",
    ):
        require(section in record, f"missing section: {section}", errors)

    verdict = record.get("overall_verdict")
    require(verdict in VERDICTS, f"unknown verdict: {verdict}", errors)

    model = record.get("model", {})
    dataset = record.get("dataset", {})
    compatibility = record.get("compatibility", {})
    claims = record.get("claim_boundary", {})
    safety = record.get("safety_status", {})
    overlap = record.get("overlap_assessment", {})

    registry_entries = {entry.get("registry_id"): entry for entry in registry.get("entries", [])}
    registry_id = model.get("registry_id")
    require(registry_id in registry_entries, f"model registry_id is not frozen in registry: {registry_id}", errors)
    require(bool(model.get("checkpoint_or_version")), "exact checkpoint_or_version is required", errors)
    require(bool(model.get("source_urls")), "at least one official source URL is required", errors)
    require(bool(model.get("retrieved_at")), "model documentation retrieval date is required", errors)

    require(dataset.get("modality") is not None, "dataset modality is required", errors)
    require(dataset.get("species") is not None, "dataset species is required", errors)
    require(dataset.get("biological_unit_status") is not None, "biological unit status is required", errors)

    for key in ("transport", "modality", "species", "cell_context", "temporal", "question"):
        require(key in compatibility, f"compatibility.{key} is required", errors)

    for transformation in record.get("transformations", []):
        require(transformation.get("provenance_recorded") is True,
                f"transformation provenance missing: {transformation.get('name')}", errors)
        if transformation.get("status") == "applied":
            require(transformation.get("validation_status") == "validated",
                    f"applied transformation is not validated: {transformation.get('name')}", errors)

    require(overlap.get("training_overlap_status") is not None,
            "training overlap status is required", errors)
    require(overlap.get("benchmark_overlap_status") is not None,
            "benchmark overlap status is required", errors)

    family = str(model.get("model_family", "")).lower()
    species = dataset.get("species")
    modality = dataset.get("modality")

    if "geneformer" in family and species != "Homo sapiens":
        require(verdict == "SPECIES_COMPATIBILITY_HOLD",
                "non-human Geneformer use must remain SPECIES_COMPATIBILITY_HOLD", errors)
        require(compatibility.get("species") == "transfer_unvalidated",
                "non-human Geneformer use must expose unvalidated transfer", errors)
        require(record.get("evidence_contribution") == "none",
                "held non-human Geneformer run cannot contribute evidence", errors)

    if "evo 2" in family or "evo2" in family:
        if modality != "dna":
            require(verdict in {"QUESTION_NOT_APPLICABLE", "MODALITY_COMPATIBILITY_HOLD", "BLOCK"},
                    "Evo 2 cannot be accepted for a non-DNA input question", errors)

    registry_entry = registry_entries.get(registry_id, {})
    if registry_entry.get("kind") == "agent_toolkit":
        require(record.get("evidence_contribution") == "orchestration_only",
                "agent toolkit must contribute orchestration_only", errors)

    if verdict == "ACCEPT_WITH_LIMITS":
        require(compatibility.get("transport") == "compatible", "accepted record needs transport compatibility", errors)
        require(compatibility.get("modality") == "compatible", "accepted record needs modality compatibility", errors)
        require(compatibility.get("species") in {"compatible", "not_applicable"},
                "accepted record cannot have unvalidated species transfer", errors)
        require(compatibility.get("question") in {"compatible", "partial"},
                "accepted record needs a compatible scientific question", errors)

    require(claims.get("causal") == "blocked", "causal claims must remain blocked", errors)
    require(claims.get("tissue") == "blocked", "tissue claims must remain blocked", errors)
    require(claims.get("clinical_therapeutic") == "blocked",
            "clinical/therapeutic claims must remain blocked", errors)
    require(safety.get("mode") == "computational_documentary_only",
            "safety mode must be computational_documentary_only", errors)
    require(safety.get("physical_biology_authorized") is False,
            "physical biology cannot be authorized", errors)
    require(safety.get("clinical_use_authorized") is False,
            "clinical use cannot be authorized", errors)

    if errors:
        print("BLOCK BioNeMo model compatibility")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("ACCEPT BioNeMo model compatibility record")
    print(f"  assessment_id={record['assessment_id']}")
    print(f"  verdict={verdict}")
    print(f"  evidence_contribution={record.get('evidence_contribution')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
