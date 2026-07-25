#!/usr/bin/env python3
"""Fail closed when GSE94383 claim boundaries drift across repository artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REPLICATION = ROOT / "examples/gse141064.independent-replication-search.json"
TEMPORAL = ROOT / "examples/gse141064.temporal-replication-gate.json"
CAUSAL = ROOT / "examples/gse141064.nfkbia-causal-hypotheses.json"
HANDOFF = ROOT / "examples/gse141064.nfkbia-partner-lab-handoff.json"
REPORT = ROOT / "reports/gse94383-conceptual-replication-2026-07-23.json"
GSE94383_REPORT_MD = ROOT / "reports/gse94383-conceptual-replication-2026-07-23.md"
SUPERSESSION_HEADING = "## Supersession notice"
ALLOWED_SUPERSEDED_VERDICT = "`CONCEPTUAL_SIGNAL_SUPPORTED`"

TEXT_SURFACES = [
    ROOT / "README.md",
    ROOT / "docs/architecture.md",
    ROOT / "RELEASE_NOTES_v0.1.md",
    ROOT / "reports/gse141064-nfkbia-causal-ranking-2026-07-23.md",
    ROOT / "reports/gse141064-direct-temporal-replication-gap-2026-07-23.md",
    ROOT / "reports/gse141064-nfkbia-partner-lab-handoff-2026-07-23.md",
    ROOT / "reviews/biology-review-request.md",
    ROOT / "reviews/statistics-review-request.md",
]

FORBIDDEN_TEXT = (
    "GSE94383 independently supports",
    "independent GSE94383 data show",
    "independent dataset supports a weak",
    "independent conceptual signal",
    "independent conceptual pathway coupling",
    "independent conceptual NF-kB",
    "supplies independent conceptual pathway coupling",
    "conceptual pathway coupling: supported",
    "conceptual pathway signal: supported",
    "CONCEPTUAL_SIGNAL_SUPPORTED",
)


def load(path: Path) -> dict[str, Any]:
    """Load a JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append one error when a condition is false."""
    if not condition:
        errors.append(message)


def candidate(record: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    """Return one candidate by stable identifier."""
    for item in record.get("candidates", []):
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id:
            return item
    return {}


def hypothesis(record: dict[str, Any], hypothesis_id: str) -> dict[str, Any]:
    """Return one hypothesis by stable identifier."""
    for item in record.get("hypotheses", []):
        if isinstance(item, dict) and item.get("hypothesis_id") == hypothesis_id:
            return item
    return {}


def evidence_item(record: dict[str, Any], evidence_id: str) -> dict[str, Any]:
    """Return one handoff evidence item by stable identifier."""
    for item in record.get("current_evidence", []):
        if isinstance(item, dict) and item.get("evidence_id") == evidence_id:
            return item
    return {}


def scan_forbidden(path: Path, text: str, errors: list[str]) -> None:
    """Scan one named text surface for stale overclaim phrases."""
    for phrase in FORBIDDEN_TEXT:
        if phrase in text:
            errors.append(f"{path.relative_to(ROOT)} contains forbidden stale claim: {phrase}")


def scan_gse94383_markdown(errors: list[str]) -> None:
    """Scan the central report while allowing one explicit historical quote.

    The old verdict may appear exactly once inside the supersession notice as a
    historical value. The notice and every other report section remain scanned
    after replacing only that exact quoted token with a harmless sentinel.
    """
    path = GSE94383_REPORT_MD
    if not path.is_file():
        errors.append(f"missing text surface: {path.relative_to(ROOT)}")
        return

    text = path.read_text(encoding="utf-8")
    start = text.find(SUPERSESSION_HEADING)
    if start < 0:
        errors.append(f"{path.relative_to(ROOT)} lacks {SUPERSESSION_HEADING}")
        return
    next_heading = text.find("\n## ", start + len(SUPERSESSION_HEADING))
    if next_heading < 0:
        errors.append(f"{path.relative_to(ROOT)} supersession notice has no following section")
        return

    notice = text[start:next_heading]
    require(
        notice.count(ALLOWED_SUPERSEDED_VERDICT) == 1,
        f"{path.relative_to(ROOT)} must quote the superseded verdict exactly once in the notice",
        errors,
    )
    require(
        "supersedes" in notice.lower(),
        f"{path.relative_to(ROOT)} notice must explicitly state supersession",
        errors,
    )

    sanitized_notice = notice.replace(
        ALLOWED_SUPERSEDED_VERDICT,
        "`<ALLOWED_HISTORICAL_VERDICT>`",
        1,
    )
    text_for_scan = text[:start] + sanitized_notice + text[next_heading:]
    scan_forbidden(path, text_for_scan, errors)


def main() -> int:
    """Check machine-readable and human-readable claim boundaries."""
    errors: list[str] = []
    replication = load(REPLICATION)
    temporal = load(TEMPORAL)
    causal = load(CAUSAL)
    handoff = load(HANDOFF)
    report = load(REPORT)

    gse94383 = candidate(replication, "GSE94383")
    compatibility = gse94383.get("compatibility", {})
    test = replication.get("prespecified_test", {})

    require(replication.get("overall_verdict") == "HOLD", "replication overall verdict must be HOLD", errors)
    require(gse94383.get("candidate_verdict") == "HOLD", "GSE94383 candidate must remain HOLD", errors)
    require(gse94383.get("replication_type") == "undetermined", "GSE94383 replication type must remain undetermined", errors)
    require(
        isinstance(compatibility, dict) and compatibility.get("experimental_unit") == "unknown",
        "GSE94383 experimental unit must remain unknown",
        errors,
    )
    require(
        isinstance(test, dict) and test.get("status") == "run_incomplete",
        "GSE94383 test must remain run_incomplete until biological grouping is established",
        errors,
    )
    require(
        "No inferential replication success criterion" in str(test.get("success_criteria", "")),
        "replication success criterion must deny cell-level inference",
        errors,
    )

    temporal_candidate = candidate(temporal, "GSE94383")
    require(temporal.get("overall_verdict") == "DIRECT_REPLICATION_GAP", "temporal overall verdict drift", errors)
    require(temporal_candidate.get("verdict") == "HOLD", "temporal GSE94383 verdict must remain HOLD", errors)
    require(temporal_candidate.get("biological_unit_established") is False, "temporal gate must keep biological unit unresolved", errors)
    require(temporal_candidate.get("evidence_level") == "F2", "temporal GSE94383 evidence level must remain F2", errors)

    require(
        report.get("verdict") == "DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED",
        "GSE94383 report verdict must remain descriptive",
        errors,
    )
    inference = report.get("inference_boundary", {})
    claims = report.get("claim_boundary", {})
    require(
        isinstance(inference, dict) and inference.get("effective_biological_n") is None,
        "effective biological N must remain unresolved",
        errors,
    )
    require(
        isinstance(inference, dict) and inference.get("cell_level_resampling_can_promote_verdict") is False,
        "cell-level resampling must not promote the verdict",
        errors,
    )
    require(
        isinstance(claims, dict) and claims.get("conceptual_pathway_triangulation") is False,
        "conceptual pathway triangulation must remain false",
        errors,
    )

    expected = {
        "H1_SHARED_UPSTREAM_STATE": (1, 49, 1),
        "H2_DIRECT_NFKBIA_EFFECT": (2, 44, 1),
        "H5_STATE_MARKER_ONLY": (3, 40, 1),
        "H3_SMALL_CONTEXT_SPECIFIC_EFFECT": (4, 37, 1),
        "H4_TECHNICAL_CONFOUNDING": (5, 30, 0),
        "H6_CHANCE_OR_OVERFITTING": (6, 17, 0),
    }
    for hypothesis_id, (rank, score, cross_support) in expected.items():
        item = hypothesis(causal, hypothesis_id)
        scores = item.get("scores", {})
        require(item.get("rank") == rank, f"{hypothesis_id}: rank drift", errors)
        require(item.get("priority_score") == score, f"{hypothesis_id}: score drift", errors)
        require(
            isinstance(scores, dict) and scores.get("cross_dataset_support") == cross_support,
            f"{hypothesis_id}: unsupported cross-dataset score drift",
            errors,
        )
    identification = causal.get("causal_identification", {})
    require(
        isinstance(identification, dict) and identification.get("independent_validation_present") is False,
        "causal ranking must not claim independent validation",
        errors,
    )
    require(causal.get("overall_verdict") == "RANKED_NOT_IDENTIFIED", "causal verdict drift", errors)

    handoff_e4 = evidence_item(handoff, "E4")
    require(handoff_e4.get("evidence_level") == "F2", "handoff GSE94383 evidence must remain F2", errors)
    require(handoff_e4.get("role") == "limiting", "handoff GSE94383 role must remain limiting", errors)
    require(
        "does not establish independent validation" in str(handoff_e4.get("statement", "")),
        "handoff must deny GSE94383 independent validation",
        errors,
    )

    for path in TEXT_SURFACES:
        if not path.is_file():
            errors.append(f"missing text surface: {path.relative_to(ROOT)}")
            continue
        scan_forbidden(path, path.read_text(encoding="utf-8"), errors)
    scan_gse94383_markdown(errors)

    if errors:
        print("BLOCK GSE94383 claim-drift gate")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("ACCEPT GSE94383 claim-drift gate")
    print("  replication=HOLD")
    print("  temporal=HOLD")
    print("  effective_biological_n=unresolved")
    print("  report=DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED")
    print("  report_markdown_scanned=true")
    print("  causal=RANKED_NOT_IDENTIFIED")
    print("  partner_handoff_role=limiting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
