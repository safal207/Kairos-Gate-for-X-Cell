#!/usr/bin/env python3
"""Computational-only analysis of public GSE94383 tables.

Tests a bounded question: whether post-LPS Nfkbia expression is associated
with the same cell's preceding NF-kB trajectory. This is not a direct test of
the GSE141064 basal-expression-to-future-response claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SEED = 94383
N_BOOT = 2000
N_PERM = 5000


def digest(path: Path, name: str) -> str:
    h = hashlib.new(name)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rho(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    keep = np.isfinite(x) & np.isfinite(y)
    if keep.sum() < 3 or np.unique(x[keep]).size < 2 or np.unique(y[keep]).size < 2:
        return math.nan, math.nan, int(keep.sum())
    result = spearmanr(x[keep], y[keep])
    return float(result.statistic), float(result.pvalue), int(keep.sum())


def rank_within_time(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.groupby("time")[column].rank(method="average", pct=True)


def endpoint(frame: pd.DataFrame, feature: str, expected: str | None) -> dict:
    x, y = "nfkbia_rank", f"{feature}_rank"
    observed, asymptotic_p, count = rho(frame[x], frame[y])
    rng = np.random.default_rng(SEED)
    groups = [g.index.to_numpy() for _, g in frame.groupby("time")]

    boot = []
    for _ in range(N_BOOT):
        indexes = np.concatenate([rng.choice(ids, len(ids), replace=True) for ids in groups])
        value, _, _ = rho(frame.loc[indexes, x], frame.loc[indexes, y])
        if math.isfinite(value):
            boot.append(value)
    ci = list(np.quantile(boot, [0.025, 0.975])) if boot else [math.nan, math.nan]

    exceed = 0
    rng = np.random.default_rng(SEED + 1)
    for _ in range(N_PERM):
        shuffled = frame[x].copy()
        for _, group in frame.groupby("time"):
            values = shuffled.loc[group.index].to_numpy(copy=True)
            rng.shuffle(values)
            shuffled.loc[group.index] = values
        value, _, _ = rho(shuffled, frame[y])
        if math.isfinite(value) and abs(value) >= abs(observed):
            exceed += 1

    per_time = []
    for time, group in frame.groupby("time"):
        value, pvalue, n = rho(group["log_nfkbia"], group[feature])
        per_time.append({"time": float(time), "rho": value, "p_descriptive": pvalue, "n": n})

    leave_one_prefix_out = []
    for prefix in sorted(frame["prefix"].unique()):
        subset = frame[frame["prefix"] != prefix]
        value, pvalue, n = rho(subset[x], subset[y])
        leave_one_prefix_out.append(
            {"excluded_prefix": str(prefix), "rho": value, "p_descriptive": pvalue, "n": n}
        )

    direction_met = None
    if expected == "positive":
        direction_met = bool(math.isfinite(observed) and observed > 0)
    elif expected == "negative":
        direction_met = bool(math.isfinite(observed) and observed < 0)

    return {
        "feature": feature,
        "expected_direction": expected,
        "direction_met": direction_met,
        "rho": observed,
        "asymptotic_p_descriptive": asymptotic_p,
        "stratified_permutation_p": (exceed + 1) / (N_PERM + 1),
        "bootstrap_95_ci": ci,
        "n": count,
        "per_time": per_time,
        "leave_one_prefix_out": leave_one_prefix_out,
    }


def strict_json(value):
    if isinstance(value, dict):
        return {str(k): strict_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [strict_json(v) for v in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (float, np.floating)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def analyse(dynamics_path: Path, expression_path: Path) -> dict:
    dyn = pd.read_csv(dynamics_path)
    expr = pd.read_csv(expression_path)
    dyn_id = "id" if "id" in dyn.columns else dyn.columns[0]
    expr_id = "id" if "id" in expr.columns else expr.columns[0]
    required = {expr_id, "time", "Nfkbia"}
    if required - set(expr.columns):
        raise ValueError(f"missing expression columns: {sorted(required - set(expr.columns))}")

    trajectory_columns = sorted(
        [c for c in dyn.columns if str(c).isdigit()], key=lambda c: int(str(c))
    )
    if not trajectory_columns:
        raise ValueError("no trajectory columns")

    dyn = dyn.rename(columns={dyn_id: "id"})
    expr = expr.rename(columns={expr_id: "id"})
    dyn["id"], expr["id"] = dyn["id"].astype(str), expr["id"].astype(str)
    duplicates = int(dyn["id"].duplicated().sum() + expr["id"].duplicated().sum())
    if duplicates:
        raise ValueError(f"duplicate IDs: {duplicates}")
    if set(dyn["id"]) != set(expr["id"]):
        raise ValueError("dynamics and expression cell-ID sets differ")

    values = dyn[trajectory_columns].apply(pd.to_numeric, errors="coerce")
    feature_rows = []
    for _, row in values.iterrows():
        observed = row.dropna().to_numpy(float)
        if not len(observed):
            feature_rows.append((0, math.nan, math.nan, math.nan))
            continue
        recent = observed[-min(3, len(observed)):]
        feature_rows.append(
            (len(observed), float(observed.mean()), float(recent.mean()), float(observed.max() - recent.mean()))
        )
    features = pd.DataFrame(
        feature_rows, columns=["points", "mean_activity", "recent_activity", "attenuation"]
    )
    features.insert(0, "id", dyn["id"].to_numpy())

    frame = expr[["id", "time", "Nfkbia"]].merge(features, on="id", validate="one_to_one")
    frame["time"] = pd.to_numeric(frame["time"], errors="raise")
    frame["Nfkbia"] = pd.to_numeric(frame["Nfkbia"], errors="coerce")
    frame["log_nfkbia"] = np.log1p(frame["Nfkbia"].clip(lower=0))
    frame["prefix"] = frame["id"].str.split("-", n=1).str[0]
    frame = frame.dropna(subset=["log_nfkbia", "recent_activity", "attenuation", "mean_activity"])
    if len(frame) < 30:
        raise ValueError(f"too few complete cells: {len(frame)}")

    frame["nfkbia_rank"] = rank_within_time(frame, "log_nfkbia")
    for feature in ["recent_activity", "attenuation", "mean_activity"]:
        frame[f"{feature}_rank"] = rank_within_time(frame, feature)

    primary = endpoint(frame, "recent_activity", "positive")
    secondary = endpoint(frame, "attenuation", None)
    mean_activity = endpoint(frame, "mean_activity", "positive")
    low = primary["bootstrap_95_ci"][0]
    if primary["direction_met"] and math.isfinite(low) and low > 0:
        verdict = "CONCEPTUAL_SIGNAL_SUPPORTED"
    elif primary["direction_met"]:
        verdict = "DIRECTIONALLY_CONSISTENT_BUT_UNCERTAIN"
    else:
        verdict = "CONCEPTUAL_SIGNAL_NOT_REPRODUCED"

    return strict_json({
        "schema_version": "0.1.0",
        "analysis_id": "GSE94383_NFKBIA_CONCEPTUAL_REPLICATION",
        "commit": os.environ.get("GITHUB_SHA"),
        "analysis_type": "conceptual_replication_only",
        "source_hashes": {
            "dynamics_md5": digest(dynamics_path, "md5"),
            "expression_md5": digest(expression_path, "md5"),
            "dynamics_sha256": digest(dynamics_path, "sha256"),
            "expression_sha256": digest(expression_path, "sha256"),
        },
        "integrity": {
            "dynamics_rows": len(dyn),
            "expression_rows": len(expr),
            "cell_id_sets_match": True,
            "duplicates": duplicates,
            "complete_cells": len(frame),
            "trajectory_columns": len(trajectory_columns),
            "time_counts": {str(k): int(v) for k, v in frame["time"].value_counts().sort_index().items()},
            "point_counts": {str(k): int(v) for k, v in frame["points"].value_counts().sort_index().items()},
            "prefix_count": int(frame["prefix"].nunique()),
        },
        "endpoints": {"primary": primary, "attenuation": secondary, "mean_activity": mean_activity},
        "verdict": verdict,
        "claim_boundary": {
            "direct_replication": False,
            "conceptual_triangulation": True,
            "causal": False,
            "tissue": False,
            "clinical": False,
        },
        "next_valid_action": "Document ID-prefix semantics and continue searching for pre-stimulation RNA linked to a later TNF-promoter phenotype.",
        "safety": {"mode": "computational_only", "physical_biology_authorized": False},
    })


def markdown(result: dict) -> str:
    p, s = result["endpoints"]["primary"], result["endpoints"]["attenuation"]
    def f(value, digits=3):
        return "NA" if value is None else f"{value:.{digits}f}"
    return "\n".join([
        "# GSE94383 conceptual replication",
        "",
        "This tests post-LPS `Nfkbia` against preceding same-cell NF-kB dynamics; it is not direct replication of the basal predictor claim.",
        "",
        f"- Exact ID sets match: {result['integrity']['cell_id_sets_match']}",
        f"- Complete cells: {result['integrity']['complete_cells']}",
        f"- Harvest-time counts: {result['integrity']['time_counts']}",
        f"- Trajectory-point counts: {result['integrity']['point_counts']}",
        "",
        "| Endpoint | rho | 95% bootstrap CI | stratified permutation p |",
        "|---|---:|---:|---:|",
        f"| Recent activity (primary, positive) | {f(p['rho'])} | [{f(p['bootstrap_95_ci'][0])}, {f(p['bootstrap_95_ci'][1])}] | {f(p['stratified_permutation_p'], 4)} |",
        f"| Attenuation (exploratory) | {f(s['rho'])} | [{f(s['bootstrap_95_ci'][0])}, {f(s['bootstrap_95_ci'][1])}] | {f(s['stratified_permutation_p'], 4)} |",
        "",
        f"**Verdict: {result['verdict']}**",
        "",
        "Cells remain nested observations. ID-prefix leave-one-out is technical sensitivity only. No causal, tissue, clinical, or therapeutic claim is supported.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dynamics", type=Path, required=True)
    parser.add_argument("--expression", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    result = analyse(args.dynamics, args.expression)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
