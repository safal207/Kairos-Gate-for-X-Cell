#!/usr/bin/env python3
"""Run deterministic donor-held-out expression baselines on GSE184241.

This script does not execute Geneformer. It establishes the comparison floor and
records an explicit runtime hold for any foundation-model claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 20260723
PLATE_TO_DONOR = {"15": "Donor1", "17": "Donor2", "18": "Donor3"}
VISIT_TO_TIME = {"1": "day0", "2": "2wk", "3": "3mo"}
CELL_RE = re.compile(r"^Plate_(15|17|18)_v([123])_(LPS|RPMI)_(\d+)$")
INFLAMMATORY_PANEL = [
    "NFKBIA",
    "NFKB1",
    "RELA",
    "TNF",
    "IL1B",
    "CCL3",
    "CCL4",
    "CXCL8",
    "JUN",
    "FOS",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_counts(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=r"\s+", compression="gzip", header=0, index_col=0, engine="python")
    frame.index = frame.index.astype(str)
    frame.columns = frame.columns.astype(str)
    if frame.index.has_duplicates:
        frame = frame.groupby(level=0, sort=False).sum()
    return frame


def parse_metadata(cell_names: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for cell in cell_names:
        match = CELL_RE.match(cell)
        if not match:
            raise ValueError(f"unrecognized cell identifier: {cell}")
        plate, visit, condition, cell_number = match.groups()
        rows.append(
            {
                "cell_id": cell,
                "plate": f"Plate_{plate}",
                "donor": PLATE_TO_DONOR[plate],
                "visit": f"v{visit}",
                "timepoint": VISIT_TO_TIME[visit],
                "condition": condition,
                "cell_number": int(cell_number),
            }
        )
    return pd.DataFrame(rows).set_index("cell_id")


def normalize_log_cpm(counts_cells_by_genes: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    raw = counts_cells_by_genes.to_numpy(dtype=np.float32, copy=True)
    library_size = raw.sum(axis=1)
    if np.any(library_size <= 0):
        raise ValueError("zero-library cells must be handled before normalization")
    normalized = np.log1p((raw / library_size[:, None]) * 10000.0).astype(np.float32)
    return normalized, library_size


def metric_bundle(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    prediction = (probability >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "log_loss": float(log_loss(y_true, probability, labels=[0, 1])),
    }


def constant_probability(y_train: np.ndarray, n_test: int) -> np.ndarray:
    prevalence = float(np.clip(y_train.mean(), 1e-6, 1 - 1e-6))
    return np.full(n_test, prevalence, dtype=float)


def fit_logistic(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "logistic",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                    solver="liblinear",
                ),
            ),
        ]
    )
    model.fit(train_x, train_y)
    return model.predict_proba(test_x)[:, 1]


def fit_metadata(train_meta: pd.DataFrame, train_y: np.ndarray, test_meta: pd.DataFrame) -> np.ndarray:
    transformer = ColumnTransformer(
        [("visit", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["visit"])],
        remainder="drop",
    )
    model = Pipeline(
        [
            ("metadata", transformer),
            (
                "logistic",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                    solver="liblinear",
                ),
            ),
        ]
    )
    model.fit(train_meta, train_y)
    return model.predict_proba(test_meta)[:, 1]


def pca_features(
    train_x: np.ndarray,
    test_x: np.ndarray,
    gene_names: np.ndarray,
    top_variable_genes: int = 500,
    components: int = 20,
) -> tuple[np.ndarray, np.ndarray, list[str], int]:
    variance = train_x.var(axis=0)
    nonzero = np.flatnonzero(variance > 0)
    if len(nonzero) < 2:
        raise ValueError("insufficient nonzero-variance genes in training donors")
    order = nonzero[np.argsort(variance[nonzero])[::-1]]
    selected = order[: min(top_variable_genes, len(order))]
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train_x[:, selected])
    test_scaled = scaler.transform(test_x[:, selected])
    n_components = min(components, train_scaled.shape[0] - 1, train_scaled.shape[1])
    reducer = PCA(n_components=n_components, svd_solver="full", random_state=RANDOM_STATE)
    return (
        reducer.fit_transform(train_scaled),
        reducer.transform(test_scaled),
        gene_names[selected].astype(str).tolist(),
        n_components,
    )


def macro_average(folds: list[dict[str, Any]], model_name: str) -> dict[str, float]:
    keys = ["roc_auc", "average_precision", "balanced_accuracy", "log_loss"]
    return {key: float(np.mean([fold["models"][model_name][key] for fold in folds])) for key in keys}


def write_report(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# GSE184241 donor-held-out baseline benchmark",
        "",
        f"- Exact source revision: `{result['source_revision']}`",
        f"- Cells retained: **{result['dataset']['cells_retained']}**",
        f"- Genes: **{result['dataset']['genes']}**",
        f"- Biological split unit: **{result['split_contract']['biological_unit']}**",
        f"- Geneformer status: **{result['geneformer']['status']}**",
        "",
        "## Primary task",
        "",
        "LPS versus RPMI response-state discrimination with each donor held out in turn.",
        "",
        "| Model | AUROC | Average precision | Balanced accuracy | Log loss |",
        "|---|---:|---:|---:|---:|",
    ]
    for model_name, metrics in result["macro_metrics"].items():
        lines.append(
            f"| {model_name} | {metrics['roc_auc']:.4f} | {metrics['average_precision']:.4f} | "
            f"{metrics['balanced_accuracy']:.4f} | {metrics['log_loss']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "These are descriptive donor-held-out response-state baselines on different cells sampled across conditions and visits.",
            "They do not establish same-cell future-response prediction, an NFKBIA-specific effect, causality, clinical utility, or therapeutic relevance.",
            "",
            "## Foundation-model status",
            "",
            "No Geneformer checkpoint was executed in this workflow. The benchmark records `GENEFORMER_RUNTIME_HOLD`;",
            "training-data overlap with GSE184241 remains unknown and an exact Model Evidence Passport is required before comparison.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", required=True)
    parser.add_argument("--barcodes", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()

    counts_path = Path(args.counts)
    barcodes_path = Path(args.barcodes)
    counts = load_counts(counts_path)
    metadata = parse_metadata(counts.columns.tolist())

    barcode_table = pd.read_excel(barcodes_path, sheet_name=0)
    barcode_ids = set(barcode_table["Sample_ID"].astype(str))
    count_ids = set(counts.columns.astype(str))
    if barcode_ids != count_ids:
        missing_in_workbook = sorted(count_ids - barcode_ids)[:10]
        missing_in_counts = sorted(barcode_ids - count_ids)[:10]
        raise ValueError(
            f"counts/workbook identity mismatch; missing_in_workbook={missing_in_workbook}; "
            f"missing_in_counts={missing_in_counts}"
        )

    cells_by_genes = counts.T
    library_size = cells_by_genes.sum(axis=1).to_numpy(dtype=float)
    keep = library_size > 0
    dropped = int((~keep).sum())
    cells_by_genes = cells_by_genes.loc[keep]
    metadata = metadata.loc[cells_by_genes.index]
    normalized, retained_library_size = normalize_log_cpm(cells_by_genes)
    genes = cells_by_genes.columns.to_numpy(dtype=str)
    gene_to_index = {gene: idx for idx, gene in enumerate(genes)}
    available_panel = [gene for gene in INFLAMMATORY_PANEL if gene in gene_to_index]
    if "NFKBIA" not in gene_to_index:
        raise ValueError("NFKBIA is absent from the official processed matrix")
    if len(available_panel) < 3:
        raise ValueError(f"too few inflammatory-panel genes available: {available_panel}")

    y = (metadata["condition"] == "LPS").astype(int).to_numpy()
    folds: list[dict[str, Any]] = []
    donors = ["Donor1", "Donor2", "Donor3"]

    for held_out in donors:
        test_mask = (metadata["donor"] == held_out).to_numpy()
        train_mask = ~test_mask
        train_x = normalized[train_mask]
        test_x = normalized[test_mask]
        train_y = y[train_mask]
        test_y = y[test_mask]
        train_meta = metadata.iloc[np.flatnonzero(train_mask)].copy()
        test_meta = metadata.iloc[np.flatnonzero(test_mask)].copy()

        train_pca, test_pca, selected_genes, n_components = pca_features(train_x, test_x, genes)
        metadata_probability = fit_metadata(train_meta, train_y, test_meta)
        metadata_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        train_visit = metadata_encoder.fit_transform(train_meta[["visit"]])
        test_visit = metadata_encoder.transform(test_meta[["visit"]])

        model_probabilities: dict[str, np.ndarray] = {
            "prevalence": constant_probability(train_y, len(test_y)),
            "metadata_visit": metadata_probability,
            "NFKBIA_only": fit_logistic(
                train_x[:, [gene_to_index["NFKBIA"]]], train_y, test_x[:, [gene_to_index["NFKBIA"]]]
            ),
            "inflammatory_panel": fit_logistic(
                train_x[:, [gene_to_index[g] for g in available_panel]],
                train_y,
                test_x[:, [gene_to_index[g] for g in available_panel]],
            ),
            "PCA_state": fit_logistic(train_pca, train_y, test_pca),
            "metadata_plus_PCA_state": fit_logistic(
                np.hstack([train_visit, train_pca]), train_y, np.hstack([test_visit, test_pca])
            ),
        }

        fold_models = {name: metric_bundle(test_y, probability) for name, probability in model_probabilities.items()}
        folds.append(
            {
                "held_out_donor": held_out,
                "training_donors": [donor for donor in donors if donor != held_out],
                "train_cells": int(train_mask.sum()),
                "test_cells": int(test_mask.sum()),
                "test_class_counts": {
                    "LPS": int(test_y.sum()),
                    "RPMI": int(len(test_y) - test_y.sum()),
                },
                "pca": {
                    "selected_gene_count": len(selected_genes),
                    "component_count": n_components,
                    "selected_genes_sha256": hashlib.sha256("\n".join(selected_genes).encode("utf-8")).hexdigest(),
                },
                "models": fold_models,
            }
        )

    model_names = list(folds[0]["models"])
    result: dict[str, Any] = {
        "schema_version": "0.2.0",
        "benchmark_id": "GSE184241-donor-held-out-response-state-v0.1",
        "source_revision": args.source_revision,
        "dataset": {
            "accession": "GSE184241",
            "organism": "Homo sapiens",
            "cells_in_matrix": int(counts.shape[1]),
            "cells_retained": int(cells_by_genes.shape[0]),
            "zero_library_cells_dropped": dropped,
            "genes": int(cells_by_genes.shape[1]),
            "donors": donors,
            "visits": ["v1", "v2", "v3"],
            "conditions": ["LPS", "RPMI"],
            "counts_sha256": sha256_file(counts_path),
            "barcodes_sha256": sha256_file(barcodes_path),
            "counts_workbook_identity_exact": True,
            "same_cell_longitudinal_identity": False,
        },
        "split_contract": {
            "biological_unit": "donor",
            "strategy": "leave_one_donor_out",
            "folds": donors,
            "cell_random_split_allowed": False,
            "feature_selection_fit_on_training_donors_only": True,
            "scaling_fit_on_training_donors_only": True,
            "pca_fit_on_training_donors_only": True,
            "hyperparameter_tuning": "none_fixed_parameters",
        },
        "task": {
            "primary_target": "LPS_vs_RPMI_response_state",
            "unit_of_prediction": "cell",
            "unit_of_generalization": "held_out_donor",
            "secondary_timepoint_task": "deferred_exploratory",
        },
        "preprocessing": {
            "normalization": "per_cell_log1p_CPM_10000",
            "zero_library_policy": "drop_and_count",
            "top_variable_genes": 500,
            "pca_components_max": 20,
            "fixed_inflammatory_panel_requested": INFLAMMATORY_PANEL,
            "fixed_inflammatory_panel_available": available_panel,
        },
        "folds": folds,
        "macro_metrics": {name: macro_average(folds, name) for name in model_names},
        "geneformer": {
            "status": "GENEFORMER_RUNTIME_HOLD",
            "inference_executed": False,
            "embedding_generated": False,
            "checkpoint": None,
            "runtime": None,
            "training_overlap_status": "unknown",
            "required_next_evidence": [
                "exact Geneformer checkpoint and BioNeMo runtime",
                "input conversion artifact and hashes",
                "exact cell-order binding",
                "training-overlap assessment",
                "Model Evidence Passport",
            ],
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "random_state": RANDOM_STATE,
        },
        "claim_boundary": {
            "human_domain_response_state_discrimination": "descriptive_with_limits",
            "donor_generalization": "three_donor_descriptive_only",
            "geneformer_incremental_value": "not_tested",
            "same_cell_future_response_prediction": "blocked",
            "NFKBIA_specific_predictive_effect": "not_established",
            "causal": "blocked",
            "clinical": "blocked",
            "therapeutic": "blocked",
        },
    }

    output_json = Path(args.output_json)
    output_report = Path(args.output_report)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result, output_report)
    print(json.dumps({"output_json": str(output_json), "output_report": str(output_report), "cells": result["dataset"]["cells_retained"], "genes": result["dataset"]["genes"], "geneformer_status": result["geneformer"]["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
