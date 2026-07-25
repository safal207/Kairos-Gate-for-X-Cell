#!/usr/bin/env python3
"""Regression checks for the GSE94383 independent-unit inference boundary."""

from __future__ import annotations

from analyze_gse94383_conceptual_replication import verdict_from_primary


def main() -> int:
    """Prove cell-level uncertainty cannot promote a scientific support verdict."""
    apparently_strong_cell_result = {
        "direction_met": True,
        "rho": 0.95,
        "bootstrap_95_ci": [0.94, 0.96],
        "stratified_permutation_p": 1e-12,
        "n": 100000,
        "independent_unit_status": "unresolved",
        "inferential_use_authorized": False,
    }
    verdict = verdict_from_primary(apparently_strong_cell_result)
    assert verdict == "DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED"
    assert "SUPPORTED" not in verdict
    assert "REPLICATION" not in verdict

    reversed_result = dict(apparently_strong_cell_result, direction_met=False)
    assert (
        verdict_from_primary(reversed_result)
        == "DESCRIPTIVE_WITHIN_DATASET_SIGNAL_NOT_OBSERVED"
    )

    print("ACCEPT GSE94383 inference-boundary regression")
    print("  cell_level_resampling_can_promote_verdict=false")
    print("  independent_biological_unit_status=unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
