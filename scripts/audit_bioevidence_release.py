#!/usr/bin/env python3
"""Fail-closed release audit for the bounded BioEvidence OS v0.1 scope."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/experimental-unit-audit-contract.yml"
README = ROOT / "README.md"

MODULES = [
    {
        "name": "bio-experimental-unit-auditor",
        "skill": ".agents/skills/bio-experimental-unit-auditor/SKILL.md",
        "gate": ".agents/skills/bio-experimental-unit-auditor/checklists/release-gate.md",
        "schema": "schemas/experimental-unit-audit.schema.json",
        "example": "examples/gse141064.experimental-unit-audit.json",
        "validator": "scripts/validate_experimental_unit_audit.py",
        "negative": "tests/fixtures/invalid_plate_as_biological_replicate.json",
    },
    {
        "name": "bio-provenance-confounder-graph",
        "skill": ".agents/skills/bio-provenance-confounder-graph/SKILL.md",
        "gate": ".agents/skills/bio-provenance-confounder-graph/checklists/release-gate.md",
        "schema": "schemas/bio-provenance-confounder-graph.schema.json",
        "example": "examples/gse141064.provenance-confounder-graph.json",
        "validator": "scripts/validate_provenance_confounder_graph.py",
        "negative": "tests/fixtures/invalid_hidden_batch_path.json",
    },
    {
        "name": "bio-independent-replication-finder",
        "skill": ".agents/skills/bio-independent-replication-finder/SKILL.md",
        "gate": ".agents/skills/bio-independent-replication-finder/checklists/release-gate.md",
        "schema": "schemas/independent-replication-search.schema.json",
        "example": "examples/gse141064.independent-replication-search.json",
        "validator": "scripts/validate_independent_replication_search.py",
        "negative": "tests/fixtures/invalid_same_study_as_replication.json",
    },
    {
        "name": "bio-causal-hypothesis-ranker",
        "skill": ".agents/skills/bio-causal-hypothesis-ranker/SKILL.md",
        "gate": ".agents/skills/bio-causal-hypothesis-ranker/checklists/release-gate.md",
        "schema": "schemas/causal-hypothesis-ranking.schema.json",
        "example": "examples/gse141064.nfkbia-causal-hypotheses.json",
        "validator": "scripts/validate_causal_hypothesis_ranking.py",
        "negative": "tests/fixtures/invalid_causal_winner_without_discriminator.json",
    },
    {
        "name": "bio-temporal-replication-gate",
        "skill": ".agents/skills/bio-temporal-replication-gate/SKILL.md",
        "gate": ".agents/skills/bio-temporal-replication-gate/checklists/release-gate.md",
        "schema": "schemas/temporal-replication-gate.schema.json",
        "example": "examples/gse141064.temporal-replication-gate.json",
        "validator": "scripts/validate_temporal_replication_gate.py",
        "negative": "tests/fixtures/invalid_poststim_as_direct_replication.json",
    },
    {
        "name": "bio-partner-lab-evidence-handoff",
        "skill": ".agents/skills/bio-partner-lab-evidence-handoff/SKILL.md",
        "gate": ".agents/skills/bio-partner-lab-evidence-handoff/checklists/release-gate.md",
        "schema": "schemas/partner-lab-evidence-handoff.schema.json",
        "example": "examples/gse141064.nfkbia-partner-lab-handoff.json",
        "validator": "scripts/validate_partner_lab_evidence_handoff.py",
        "negative": "tests/fixtures/invalid_partner_handoff_authorizes_execution.json",
    },
]

REQUIRED_RELEASE_FILES = [
    "MASTER_ROADMAP.md",
    "BACKLOG.md",
    "docs/architecture.md",
    "RELEASE_NOTES_v0.1.md",
    "reviews/biology-review-request.md",
    "reviews/statistics-review-request.md",
    "scripts/validate_bioevidence_contract.py",
    "scripts/check_gse94383_inference_boundary.py",
    "scripts/check_gse94383_claim_drift.py",
    "tests/fixtures/invalid_experimental_unit_extra_property.json",
]

PROHIBITED_TRUE_KEYS = {
    "execution_authorized",
    "physical_biology_authorized",
    "ai_authorizes_execution",
    "physical_protocol_included",
    "recipes_or_concentrations_included",
    "dosing_or_treatment_included",
    "biological_modification_instructions_included",
    "human_experimentation_instructions_included",
}
PROHIBITED_CLAIM_KEYS = {"causal", "tissue", "clinical_therapeutic"}
PROHIBITED_CLAIM_STATUSES = {"supported", "supported_with_limits"}


def walk(value: Any, path: str = "$") -> Iterator[tuple[str, Any, str]]:
    """Yield every dictionary key, child value, and JSON path recursively."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield key, child, child_path
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def load_json(relative: str, errors: list[str]) -> Any:
    """Load a repository-relative JSON file and accumulate parse errors."""
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load {relative}: {exc}")
        return None


def claim_status(value: Any) -> str | None:
    """Normalize flat and nested claim-boundary representations."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        nested = value.get("status")
        return nested if isinstance(nested, str) else None
    return None


def main() -> int:
    """Run the release audit and return a fail-closed process exit code."""
    errors: list[str] = []

    for module in MODULES:
        for role in ("skill", "gate", "schema", "example", "validator", "negative"):
            relative = module[role]
            if not (ROOT / relative).is_file():
                errors.append(f"{module['name']}: missing {role} file {relative}")

    for relative in REQUIRED_RELEASE_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing release file {relative}")

    workflow_text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""
    readme_text = README.read_text(encoding="utf-8") if README.is_file() else ""

    if "permissions:\n  contents: read" not in workflow_text:
        errors.append("workflow permissions must remain contents: read")

    for module in MODULES:
        for role in ("validator", "example", "negative"):
            if module[role] not in workflow_text:
                errors.append(f"workflow does not reference {module[role]}")
        if module["name"] not in readme_text:
            errors.append(f"README does not name module {module['name']}")

        record = load_json(module["example"], errors)
        if record is None:
            continue
        for key, value, json_path in walk(record):
            if key in PROHIBITED_TRUE_KEYS and value is True:
                errors.append(
                    f"unsafe true flag in accepted example {module['example']} at {json_path}"
                )
            if key not in PROHIBITED_CLAIM_KEYS:
                continue
            normalized = claim_status(value)
            if normalized in PROHIBITED_CLAIM_STATUSES:
                errors.append(
                    f"overclaimed boundary in {module['example']} at {json_path}: {normalized}"
                )

    required_workflow_fragments = [
        "BIOEVIDENCE_HEAD_SHA",
        "ref: ${{ env.BIOEVIDENCE_HEAD_SHA }}",
        "scripts/validate_bioevidence_contract.py",
        "scripts/check_gse94383_claim_drift.py",
        "actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "jsonschema==4.23.0",
        "numpy==2.1.3",
        "pandas==2.2.3",
        "scipy==1.14.1",
        "openpyxl==3.1.5",
        "curl --fail --location --retry 3 --retry-all-errors",
        "8be1e148d47762fd148584469a6179a6",
        "60a8bc62e5c49692fce8c79fdf0bf530",
        "c43d0b54ed4b245b1690e9675630682c0843cda63f14a3e51dbf13b8f87c070e",
        "e264565c72f06ed98ee10914c0350486dd2daa2460cd19ec8071d756bf982200",
        "ffb1f233d7cd0c40d79086d92f3cf335fc6cbf0de14f64538bf063974784e925",
        "authors.library.caltech.edu",
        "static-content.springer.com",
        "retention-days: 30",
    ]
    for fragment in required_workflow_fragments:
        if fragment not in workflow_text:
            errors.append(f"workflow evidence-integrity fragment missing: {fragment}")

    handoff_negative_path = "tests/fixtures/invalid_partner_handoff_authorizes_execution.json"
    handoff_negative = load_json(handoff_negative_path, errors)
    if isinstance(handoff_negative, dict):
        unsafe_signals = [
            handoff_negative.get("governance_gates", {}).get("execution_authorized") is True,
            handoff_negative.get("operational_content", {}).get("physical_protocol_included") is True,
            handoff_negative.get("safety_status", {}).get("ai_authorizes_execution") is True,
        ]
        if not all(unsafe_signals):
            errors.append(
                "false-authorization fixture no longer exercises all required unsafe signals"
            )

    replication = load_json("examples/gse141064.independent-replication-search.json", errors)
    temporal = load_json("examples/gse141064.temporal-replication-gate.json", errors)
    descriptive = load_json("reports/gse94383-conceptual-replication-2026-07-23.json", errors)
    if isinstance(replication, dict) and replication.get("overall_verdict") != "HOLD":
        errors.append("GSE94383 replication search must remain HOLD")
    if isinstance(temporal, dict) and temporal.get("overall_verdict") != "DIRECT_REPLICATION_GAP":
        errors.append("temporal replication gap must remain active")
    if isinstance(descriptive, dict):
        if descriptive.get("verdict") != "DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED":
            errors.append("GSE94383 report must remain descriptive")
        boundary = descriptive.get("inference_boundary", {})
        if not isinstance(boundary, dict) or boundary.get("effective_biological_n") is not None:
            errors.append("GSE94383 effective biological N must remain unresolved")

    release_notes = (ROOT / "RELEASE_NOTES_v0.1.md").read_text(encoding="utf-8")
    combined = readme_text + "\n" + release_notes
    for required_statement in (
        "DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED",
        "REPLICATION_STATUS_HOLD",
        "RANKED_NOT_IDENTIFIED",
        "DIRECT_REPLICATION_GAP",
        "PHYSICAL_EXECUTION_NOT_AUTHORIZED",
        "AI_DOES_NOT_AUTHORIZE_EXECUTION",
    ):
        if required_statement not in combined:
            errors.append(
                f"release documentation missing boundary statement: {required_statement}"
            )

    if errors:
        print("BLOCK BioEvidence OS v0.1 release audit")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("ACCEPT BioEvidence OS v0.1 release audit")
    print(f"  modules={len(MODULES)}")
    print("  positive_records=6")
    print("  negative_fixtures=7")
    print("  acceptance_authority=schema_then_semantics")
    print("  gse94383=descriptive_hold")
    print("  safety_boundary=fail_closed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        if os.environ.get("BIOEVIDENCE_DEBUG") == "1":
            raise
        print("BLOCK BioEvidence OS v0.1 release audit")
        print(f"  - unexpected audit failure: {type(exc).__name__}")
        raise SystemExit(1)
