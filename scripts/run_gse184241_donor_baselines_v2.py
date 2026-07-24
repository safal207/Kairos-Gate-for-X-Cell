#!/usr/bin/env python3
"""Leakage-safe donor-held-out baselines for official GSE184241 counts.

No Geneformer model is executed. This establishes the frozen comparison floor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 20260723
DONORS = ["Donor1", "Donor2", "Donor3"]
PLATE_TO_DONOR = {"15": "Donor1", "17": "Donor2", "18": "Donor3"}
VISIT_TO_TIME = {"1": "day0", "2": "2wk", "3": "3mo"}
CELL_RE = re.compile(r"^Plate_(15|17|18)_v([123])_(LPS|RPMI)_(\d+)$")
PANEL = ["NFKBIA", "NFKB1", "RELA", "TNF", "IL1B", "CCL3", "CCL4", "CXCL8", "JUN", "FOS"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_identifier(value: object) -> str:
    return str(value).strip().strip('"').strip("'")


def load_counts(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        sep=r"\s+",
        compression="gzip",
        header=0,
        index_col=0,
        quotechar='"',
        engine="c",
    )
    frame = frame.apply(pd.to_numeric, errors="raise").astype(np.float32)
    frame.index = pd.Index([clean_identifier(value) for value in frame.index], dtype="object")
    frame.columns = pd.Index([clean_identifier(value) for value in frame.columns], dtype="object")
    if frame.index.has_duplicates:
        frame = frame.groupby(level=0, sort=False).sum()
    if frame.columns.has_duplicates:
        raise ValueError("duplicate cell identifiers after quote normalization")
    return frame


def parse_metadata(cell_names: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for cell in cell_names:
        match = CELL_RE.fullmatch(clean_identifier(cell))
        if not match:
            raise ValueError(f"unrecognized cell identifier after normalization: {cell!r}")
        plate, visit, condition, cell_number = match.groups()
        rows.append(
            {
                "cell_id": clean_identifier(cell),
                "plate": f"Plate_{plate}",
                "donor": PLATE_TO_DONOR[plate],
                "visit": f"v{visit}",
                "timepoint": VISIT_TO_TIME[visit],
                "condition": condition,
                "cell_number": int(cell_number),
            }
        )
    return pd.DataFrame(rows).set_index("cell_id")


def metric_bundle(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    prediction = (probability >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "log_loss": float(log_loss(y_true, probability, labels=[0, 1])),
    }


def fit_logistic(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train_x)
    test_scaled = scaler.transform(test_x)
    model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=2000,
        random_state=RANDOM_STATE,
        solver="liblinear",
    )
    model.fit(train_scaled, train_y)
    return model.predict_proba(test_scaled)[:, 1]


def pca_state(
    train_x: np.ndarray,
    test_x: np.ndarray,
    genes: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, list[str], int]:
    variance = train_x.var(axis=0)
    candidates = np.flatnonzero(variance > 0)
    if len(candidates) < 2:
        raise ValueError("insufficient nonzero-variance genes in training donors")
    selected = candidates[np.argsort(variance[candidates])[::-1]][: min(500, len(candidates))]
    scaler = StandardScaler()
    train_selected = scaler.fit_transform(train_x[:, selected])
    test_selected = scaler.transform(test_x[:, selected])
    components = min(20, train_selected.shape[0] - 1, train_selected.shape[1])
    reducer = PCA(n_components=components, svd_solver="randomized", random_state=RANDOM_STATE)
    return (
        reducer.fit_transform(train_selected),
        reducer.transform(test_selected),
        genes[selected].astype(str).tolist(),
        components,
    )


def macro_metrics(folds: list[dict[str, Any]], model: str) -> dict[str, float]:
    keys = ["roc_auc", "average_precision", "balanced_accuracy", "log_loss"]
    return {key: float(np.mean([fold["models"][model][key] for fold in folds])) for key in keys}


def report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# GSE184241 donor-held-out baseline benchmark",
        "",
        f"- Exact source revision: `{result['source_revision']}`",
        f"- Cells retained: **{result['dataset']['cells_retained']}**",
        f"- Genes: **{result['dataset']['genes']}**",
        "- Biological split: **leave one donor out**",
        f"- Geneformer: **{result['geneformer']['status']}**",
        "",
        "## Macro-average across held-out donors",
        "",
        "| Model | AUROC | AP | Balanced accuracy | Log loss |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, metrics in result["macro_metrics"].items():
        lines.append(
            f"| {model} | {metrics['roc_auc']:.4f} | {metrics['average_precision']:.4f} | "
            f"{metrics['balanced_accuracy']:.4f} | {metrics['log_loss']:.4f} |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "This is donor-held-out discrimination of LPS versus RPMI states in different cells.",
        "It does not establish same-cell future-response prediction, an NFKBIA-specific effect, causality, clinical utility, or therapeutic relevance.",
        "No Geneformer checkpoint was executed; exact runtime, input conversion, overlap assessment, embeddings, hashes, and a Model Evidence Passport remain required.",
        "",
    ]
    return "\n".join(lines)


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
    if "Sample_ID" not in barcode_table.columns:
        raise ValueError("barcode workbook lacks Sample_ID")
    barcode_ids = {clean_identifier(value) for value in barcode_table["Sample_ID"].dropna()}
    count_ids = set(counts.columns)
    if barcode_ids != count_ids:
        raise ValueError(
            "counts/workbook identity mismatch; "
            f"missing_in_workbook={sorted(count_ids - barcode_ids)[:10]}; "
            f"missing_in_counts={sorted(barcode_ids - count_ids)[:10]}"
        )

    cells_by_genes = counts.T
    library_size = cells_by_genes.sum(axis=1).to_numpy(dtype=np.float64)
    keep = library_size > 0
    dropped = int((~keep).sum())
    cells_by_genes = cells_by_genes.loc[keep]
    metadata = metadata.loc[cells_by_genes.index]
    raw = cells_by_genes.to_numpy(dtype=np.float32, copy=True)
    retained_library_size = raw.sum(axis=1)
    normalized = np.log1p((raw / retained_library_size[:, None]) * 10000.0).astype(np.float32)
    del raw

    genes = cells_by_genes.columns.to_numpy(dtype=str)
    gene_index = {gene: index for index, gene in enumerate(genes)}
    if "NFKBIA" not in gene_index:
        raise ValueError("NFKBIA is absent from official processed counts")
    available_panel = [gene for gene in PANEL if gene in gene_index]
    if len(available_panel) < 3:
        raise ValueError(f"too few frozen panel genes present: {available_panel}")

    y = (metadata["condition"] == "LPS").astype(int).to_numpy()
    folds: list[dict[str, Any]] = []
    for held_out in DONORS:
        test_mask = (metadata["donor"] == held_out).to_numpy()
        train_mask = ~test_mask
        train_x, test_x = normalized[train_mask], normalized[test_mask]
        train_y, test_y = y[train_mask], y[test_mask]
        train_meta, test_meta = metadata.loc[train_mask], metadata.loc[test_mask]

        train_pca, test_pca, selected_genes, components = pca_state(train_x, test_x, genes)
        visit_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        train_visit = visit_encoder.fit_transform(train_meta[["visit"]])
        test_visit = visit_encoder.transform(test_meta[["visit"]])
        prevalence = float(np.clip(train_y.mean(), 1e-6, 1 - 1e-6))

        probabilities = {
            "prevalence": np.full(len(test_y), prevalence),
            "metadata_visit": fit_logistic(train_visit, train_y, test_visit),
            "NFKBIA_only": fit_logistic(
                train_x[:, [gene_index["NFKBIA"]]], train_y, test_x[:, [gene_index["NFKBIA"]]]
            ),
            "inflammatory_panel": fit_logistic(
                train_x[:, [gene_index[gene] for gene in available_panel]],
                train_y,
                test_x[:, [gene_index[gene] for gene in available_panel]],
            ),
            "PCA_state": fit_logistic(train_pca, train_y, test_pca),
            "metadata_plus_PCA_state": fit_logistic(
                np.hstack([train_visit, train_pca]), train_y, np.hstack([test_visit, test_pca])
            ),
        }
        folds.append(
            {
                "held_out_donor": held_out,
                "training_donors": [donor for donor in DONORS if donor != held_out],
                "train_cells": int(train_mask.sum()),
                "test_cells": int(test_mask.sum()),
                "test_class_counts": {"LPS": int(test_y.sum()), "RPMI": int(len(test_y) - test_y.sum())},
                "pca": {
                    "selected_gene_count": len(selected_genes),
                    "component_count": components,
                    "selected_genes_sha256": hashlib.sha256("\n".join(selected_genes).encode()).hexdigest(),
                },
                "models": {name: metric_bundle(test_y, probability) for name, probability in probabilities.items()},
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
            "donors": DONORS,
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
            "folds": DONORS,
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
            "fixed_inflammatory_panel_requested": PANEL,
            "fixed_inflammatory_panel_available": available_panel,
        },
        "folds": folds,
        "macro_metrics": {model: macro_metrics(folds, model) for model in model_names},
        "geneformer": {
            "status": "GENEFORMER_RUNTIME_HOLD",
            "inference_executed": False,
            "embedding_generated": False,
            "checkpoint": None,
            "runtime": None,
            "training_overlap_status": "unknown",
            "required_next_evidence": [
                "exact checkpoint and runtime",
                "input conversion and cell-order hashes",
                "training-overlap assessment",
                "embedding artifact and SHA-256",
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

    output_json, output_report = Path(args.output_json), Path(args.output_report)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_report.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps({
        "cells": result["dataset"]["cells_retained"],
        "genes": result["dataset"]["genes"],
        "geneformer_status": result["geneformer"]["status"],
        "output_json": str(output_json),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
