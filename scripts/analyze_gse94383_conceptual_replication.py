#!/usr/bin/env python3
"""Run a frozen, claim-bounded conceptual replication analysis on GSE94383.

The analysis asks whether post-LPS Nfkbia expression is associated with the
same cell's preceding NF-kB trajectory. It does NOT test the stronger GSE141064
claim that basal Nfkbia predicts a future Tnf-mCherry response, because the
GSE94383 transcriptome was collected after stimulation.

Structural/provenance failures raise an error. A null biological result is a
valid result and does not fail the process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


RNG_SEED = 94383
BOOTSTRAP_ITERATIONS = 2000
PERMUTATION_ITERATIONS = 5000


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def finite_spearman(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> tuple[float, float, int]:
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    mask = np.isfinite(x_values) & np.isfinite(y_values)
    count = int(mask.sum())
    if count < 3 or np.unique(x_values[mask]).size < 2 or np.unique(y_values[mask]).size < 2:
        return math.nan, math.nan, count
    result = spearmanr(x_values[mask], y_values[mask])
    return float(result.statistic), float(result.pvalue), count


def within_stratum_ranks(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.groupby("harvest_time", observed=True)[column].rank(method="average", pct=True)


def stratified_bootstrap_ci(
    frame: pd.DataFrame,
    x_column: str,
    y_column: str,
    iterations: int = BOOTSTRAP_ITERATIONS,
) -> tuple[float, float, int]:
    rng = np.random.default_rng(RNG_SEED)
    groups = [group.index.to_numpy() for _, group in frame.groupby("harvest_time", observed=True)]
    estimates: list[float] = []
    for _ in range(iterations):
        sampled_parts = [rng.choice(indexes, size=len(indexes), replace=True) for indexes in groups]
        sampled = frame.loc[np.concatenate(sampled_parts)]
        rho, _, _ = finite_spearman(sampled[x_column], sampled[y_column])
        if np.isfinite(rho):
            estimates.append(rho)
    if not estimates:
        return math.nan, math.nan, 0
    lower, upper = np.quantile(np.asarray(estimates), [0.025, 0.975])
    return float(lower), float(upper), len(estimates)


def stratified_permutation_pvalue(
    frame: pd.DataFrame,
    x_column: str,
    y_column: str,
    observed_rho: float,
    iterations: int = PERMUTATION_ITERATIONS,
) -> float:
    if not np.isfinite(observed_rho):
        return math.nan
    rng = np.random.default_rng(RNG_SEED + 1)
    exceedances = 0
    for _ in range(iterations):
        permuted = frame[x_column].copy()
        for _, group in frame.groupby("harvest_time", observed=True):
            values = permuted.loc[group.index].to_numpy(copy=True)
            rng.shuffle(values)
            permuted.loc[group.index] = values
        rho, _, _ = finite_spearman(permuted, frame[y_column])
        if np.isfinite(rho) and abs(rho) >= abs(observed_rho):
            exceedances += 1
    return float((exceedances + 1) / (iterations + 1))


def leave_one_prefix_out(frame: pd.DataFrame, x_column: str, y_column: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for prefix in sorted(frame["id_prefix"].dropna().astype(str).unique()):
        subset = frame.loc[frame["id_prefix"] != prefix]
        rho, pvalue, count = finite_spearman(subset[x_column], subset[y_column])
        results.append(
            {
                "excluded_prefix": prefix,
                "rho": rho,
                "pvalue_descriptive": pvalue,
                "n_cells": count,
            }
        )
    return results


def trajectory_features(row: pd.Series, trajectory_columns: list[str]) -> pd.Series:
    values = pd.to_numeric(row[trajectory_columns], errors="coerce").to_numpy(dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return pd.Series(
            {
                "trajectory_points": 0,
                "nfkb_mean_all": math.nan,
                "nfkb_recent_mean": math.nan,
                "nfkb_peak": math.nan,
                "nfkb_attenuation": math.nan,
                "nfkb_peak_position": math.nan,
            }
        )
    recent = values[-min(3, values.size) :]
    peak_position = int(np.argmax(values))
    return pd.Series(
        {
            "trajectory_points": int(values.size),
            "nfkb_mean_all": float(np.mean(values)),
            "nfkb_recent_mean": float(np.mean(recent)),
            "nfkb_peak": float(np.max(values)),
            "nfkb_attenuation": float(np.max(values) - np.mean(recent)),
            "nfkb_peak_position": peak_position,
        }
    )


def endpoint_result(frame: pd.DataFrame, feature: str, expected_direction: str | None) -> dict[str, Any]:
    x_column = "nfkbia_rank_within_time"
    y_column = f"{feature}_rank_within_time"
    rho, asymptotic_pvalue, count = finite_spearman(frame[x_column], frame[y_column])
    ci_low, ci_high, bootstrap_count = stratified_bootstrap_ci(frame, x_column, y_column)
    permutation_pvalue = stratified_permutation_pvalue(frame, x_column, y_column, rho)
    per_time: list[dict[str, Any]] = []
    for harvest_time, group in frame.groupby("harvest_time", observed=True):
        time_rho, time_pvalue, time_count = finite_spearman(group["log1p_nfkbia"], group[feature])
        per_time.append(
            {
                "harvest_time": float(harvest_time),
                "rho": time_rho,
                "pvalue_descriptive": time_pvalue,
                "n_cells": time_count,
            }
        )

    direction_met: bool | None
    if expected_direction == "positive":
        direction_met = bool(np.isfinite(rho) and rho > 0)
    elif expected_direction == "negative":
        direction_met = bool(np.isfinite(rho) and rho < 0)
    else:
        direction_met = None

    return {
        "feature": feature,
        "expected_direction": expected_direction,
        "direction_met": direction_met,
        "pooled_within_time_spearman_rho": rho,
        "asymptotic_pvalue_descriptive": asymptotic_pvalue,
        "stratified_permutation_pvalue": permutation_pvalue,
        "bootstrap_95_percent_ci": [ci_low, ci_high],
        "bootstrap_estimates": bootstrap_count,
        "n_cells": count,
        "per_harvest_time": per_time,
        "leave_one_id_prefix_out": leave_one_prefix_out(frame, x_column, y_column),
    }


def format_number(value: Any, digits: int = 3) -> str:
    if value is None or not isinstance(value, (int, float, np.integer, np.floating)) or not np.isfinite(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def write_markdown(result: dict[str, Any], output_path: Path) -> None:
    primary = result["endpoints"]["primary"]
    secondary = result["endpoints"]["secondary_attenuation"]
    lines = [
        "# GSE94383 conceptual replication result",
        "",
        "## Claim boundary",
        "",
        "This analysis tests whether **post-LPS `Nfkbia` expression** is associated with the same cell's preceding NF-kB trajectory. It does **not** test whether basal `Nfkbia` predicts a future `Tnf-mCherry` response.",
        "",
        "## Data integrity",
        "",
        f"- Dynamics rows: {result['data_integrity']['dynamics_rows']}",
        f"- Transcriptome rows: {result['data_integrity']['transcriptome_rows']}",
        f"- Exact matched cell IDs: {result['data_integrity']['matched_cell_ids']}",
        f"- Duplicate IDs: {result['data_integrity']['duplicate_ids']}",
        f"- Harvest times: {result['data_integrity']['harvest_time_counts']}",
        f"- Trajectory point counts: {result['data_integrity']['trajectory_point_count_distribution']}",
        "",
        "## Frozen endpoints",
        "",
        "| Endpoint | Direction | rho | bootstrap 95% CI | stratified permutation p | n cells |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Primary: recent NF-kB activity vs `Nfkbia` | positive | {format_number(primary['pooled_within_time_spearman_rho'])} | [{format_number(primary['bootstrap_95_percent_ci'][0])}, {format_number(primary['bootstrap_95_percent_ci'][1])}] | {format_number(primary['stratified_permutation_pvalue'], 4)} | {primary['n_cells']} |",
        f"| Secondary: attenuation index vs `Nfkbia` | exploratory | {format_number(secondary['pooled_within_time_spearman_rho'])} | [{format_number(secondary['bootstrap_95_percent_ci'][0])}, {format_number(secondary['bootstrap_95_percent_ci'][1])}] | {format_number(secondary['stratified_permutation_pvalue'], 4)} | {secondary['n_cells']} |",
        "",
        "## Verdict",
        "",
        f"**{result['verdict']}** — {result['interpretation']}",
        "",
        "## Non-negotiable limitations",
        "",
        "- The transcriptome was measured after LPS stimulation; temporal direction differs from GSE141064.",
        "- Individual cells are nested observations, not automatically independent biological replicates.",
        "- The ID prefix sensitivity analysis is technical robustness only unless its biological meaning is independently documented.",
        "- No causal, tissue, clinical, or therapeutic claim is supported.",
        "",
        "## Next valid action",
        "",
        result["next_valid_action"],
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def analyse(dynamics_path: Path, transcriptomes_path: Path) -> dict[str, Any]:
    dynamics = pd.read_csv(dynamics_path)
    transcriptomes = pd.read_csv(transcriptomes_path)

    dynamics_id_column = "id" if "id" in dynamics.columns else str(dynamics.columns[0])
    transcriptome_id_column = "id" if "id" in transcriptomes.columns else str(transcriptomes.columns[0])
    required_expression_columns = {transcriptome_id_column, "time", "Nfkbia"}
    missing_expression_columns = sorted(required_expression_columns - set(transcriptomes.columns))
    if missing_expression_columns:
        raise ValueError(f"missing transcriptome columns: {missing_expression_columns}")

    trajectory_columns = sorted(
        [str(column) for column in dynamics.columns if str(column).isdigit()],
        key=lambda value: int(value),
    )
    if not trajectory_columns:
        raise ValueError("no numeric NF-kB trajectory columns found")

    dynamics = dynamics.rename(columns={dynamics_id_column: "cell_id"})
    transcriptomes = transcriptomes.rename(columns={transcriptome_id_column: "cell_id", "time": "harvest_time"})
    dynamics["cell_id"] = dynamics["cell_id"].astype(str)
    transcriptomes["cell_id"] = transcriptomes["cell_id"].astype(str)

    dynamics_duplicates = int(dynamics["cell_id"].duplicated().sum())
    transcriptome_duplicates = int(transcriptomes["cell_id"].duplicated().sum())
    if dynamics_duplicates or transcriptome_duplicates:
        raise ValueError(
            f"duplicate cell IDs: dynamics={dynamics_duplicates}, transcriptomes={transcriptome_duplicates}"
        )

    dynamics_ids = set(dynamics["cell_id"])
    transcriptome_ids = set(transcriptomes["cell_id"])
    if dynamics_ids != transcriptome_ids:
        missing_in_dynamics = sorted(transcriptome_ids - dynamics_ids)[:20]
        missing_in_transcriptomes = sorted(dynamics_ids - transcriptome_ids)[:20]
        raise ValueError(
            "cell identity mismatch; "
            f"missing_in_dynamics={missing_in_dynamics}, "
            f"missing_in_transcriptomes={missing_in_transcriptomes}"
        )

    features = dynamics.apply(trajectory_features, axis=1, trajectory_columns=trajectory_columns)
    dynamics = pd.concat([dynamics[["cell_id"]], features], axis=1)
    expression_columns = ["cell_id", "harvest_time", "Nfkbia"]
    matched = transcriptomes[expression_columns].merge(dynamics, on="cell_id", how="inner", validate="one_to_one")
    matched["harvest_time"] = pd.to_numeric(matched["harvest_time"], errors="raise")
    matched["Nfkbia"] = pd.to_numeric(matched["Nfkbia"], errors="coerce")
    matched["log1p_nfkbia"] = np.log1p(matched["Nfkbia"].clip(lower=0))
    matched["id_prefix"] = matched["cell_id"].str.split("-", n=1).str[0]

    analysis_columns = ["log1p_nfkbia", "nfkb_recent_mean", "nfkb_attenuation", "nfkb_mean_all"]
    matched = matched.dropna(subset=analysis_columns).copy()
    if len(matched) < 30:
        raise ValueError(f"too few matched complete cells: {len(matched)}")

    matched["nfkbia_rank_within_time"] = within_stratum_ranks(matched, "log1p_nfkbia")
    for feature in ["nfkb_recent_mean", "nfkb_attenuation", "nfkb_mean_all"]:
        matched[f"{feature}_rank_within_time"] = within_stratum_ranks(matched, feature)

    primary = endpoint_result(matched, "nfkb_recent_mean", expected_direction="positive")
    attenuation = endpoint_result(matched, "nfkb_attenuation", expected_direction=None)
    mean_all = endpoint_result(matched, "nfkb_mean_all", expected_direction="positive")

    primary_ci = primary["bootstrap_95_percent_ci"]
    if primary["direction_met"] and np.isfinite(primary_ci[0]) and primary_ci[0] > 0:
        verdict = "CONCEPTUAL_SIGNAL_SUPPORTED"
        interpretation = (
            "Post-LPS Nfkbia expression is positively associated with recent preceding NF-kB activity "
            "after harvest-time stratification. This supports pathway coupling, not the stronger basal-predictor claim."
        )
    elif primary["direction_met"]:
        verdict = "DIRECTIONALLY_CONSISTENT_BUT_UNCERTAIN"
        interpretation = (
            "The primary effect has the prespecified positive direction, but uncertainty includes a null or opposite effect."
        )
    else:
        verdict = "CONCEPTUAL_SIGNAL_NOT_REPRODUCED"
        interpretation = (
            "The primary endpoint does not show the prespecified positive association. The null or contrary result is retained."
        )

    trajectory_distribution = {
        str(int(key)): int(value)
        for key, value in matched["trajectory_points"].value_counts().sort_index().items()
    }
    harvest_counts = {
        str(float(key)): int(value)
        for key, value in matched["harvest_time"].value_counts().sort_index().items()
    }

    return {
        "schema_version": "0.1.0",
        "analysis_id": "GSE94383_NFKBIA_CONCEPTUAL_REPLICATION",
        "generated_at_commit": os.environ.get("GITHUB_SHA"),
        "analysis_type": "conceptual_replication_only",
        "frozen_question": (
            "Is post-LPS Nfkbia expression positively associated with the same cell's recent preceding "
            "NF-kB activity, after stratifying by transcriptome harvest time?"
        ),
        "source_files": {
            "dynamics": {
                "path": dynamics_path.name,
                "md5": digest(dynamics_path, "md5"),
                "sha256": digest(dynamics_path, "sha256"),
            },
            "transcriptomes": {
                "path": transcriptomes_path.name,
                "md5": digest(transcriptomes_path, "md5"),
                "sha256": digest(transcriptomes_path, "sha256"),
            },
        },
        "data_integrity": {
            "dynamics_rows": int(len(dynamics_ids)),
            "transcriptome_rows": int(len(transcriptome_ids)),
            "matched_cell_ids": int(len(matched)),
            "duplicate_ids": dynamics_duplicates + transcriptome_duplicates,
            "trajectory_columns": len(trajectory_columns),
            "harvest_time_counts": harvest_counts,
            "trajectory_point_count_distribution": trajectory_distribution,
            "id_prefix_count": int(matched["id_prefix"].nunique()),
        },
        "endpoints": {
            "primary": primary,
            "secondary_attenuation": attenuation,
            "secondary_mean_activity": mean_all,
        },
        "verdict": verdict,
        "interpretation": interpretation,
        "claim_boundary": {
            "direct_replication_of_gse141064": false,
            "conceptual_pathway_triangulation": true,
            "biological_generalization": false,
            "causal_inference": false,
            "tissue_claim": false,
            "clinical_or_therapeutic_claim": false
        },
        "next_valid_action": (
            "Verify the biological meaning of GSE94383 ID prefixes and collection batches, then seek a dataset "
            "with a pre-stimulation transcriptome linked to a later TNF-promoter phenotype for direct replication."
        ),
        "safety_status": {
            "mode": "computational_only",
            "physical_biology_authorized": false
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dynamics", required=True, type=Path)
    parser.add_argument("--transcriptomes", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    args = parser.parse_args()

    result = analyse(args.dynamics, args.transcriptomes)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(result, args.markdown_output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
