#!/usr/bin/env python3
"""Validate the GSE184241 donor-held-out benchmark contract fail-closed."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

DONORS = {"Donor1", "Donor2", "Donor3"}
MODELS = {
    "prevalence",
    "metadata_visit",
    "NFKBIA_only",
    "inflammatory_panel",
    "PCA_state",
    "metadata_plus_PCA_state",
}
METRICS = {"roc_auc", "average_precision", "balanced_accuracy", "log_loss"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def valid_metrics(value: Any, prefix: str, errors: list[str]) -> None:
    require(isinstance(value, dict), f"{prefix} must be an object", errors)
    if not isinstance(value, dict):
        return
    require(METRICS <= set(value), f"{prefix} missing metrics {sorted(METRICS - set(value))}", errors)
    for key in METRICS & set(value):
        metric = value[key]
        require(isinstance(metric, (int, float)) and math.isfinite(metric), f"{prefix}.{key} must be finite", errors)
        if isinstance(metric, (int, float)) and math.isfinite(metric):
            if key != "log_loss":
                require(0 <= metric <= 1, f"{prefix}.{key} must be in [0, 1]", errors)
            else:
                require(metric >= 0, f"{prefix}.log_loss must be nonnegative", errors)


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(data.get("schema_version") == "0.2.0", "schema_version must be 0.2.0", errors)
    require(data.get("benchmark_id") == "GSE184241-donor-held-out-response-state-v0.1", "benchmark_id mismatch", errors)

    dataset = data.get("dataset", {})
    require(dataset.get("accession") == "GSE184241", "dataset accession must be GSE184241", errors)
    require(dataset.get("organism") == "Homo sapiens", "organism must be Homo sapiens", errors)
    require(set(dataset.get("donors", [])) == DONORS, "dataset donors must be Donor1-3", errors)
    require(dataset.get("counts_workbook_identity_exact") is True, "count/workbook cell identity must match exactly", errors)
    require(dataset.get("same_cell_longitudinal_identity") is False, "same-cell longitudinal identity must remain false", errors)
    for key in ("counts_sha256", "barcodes_sha256"):
        value = dataset.get(key)
        require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value), f"{key} must be lowercase SHA-256", errors)

    split = data.get("split_contract", {})
    require(split.get("biological_unit") == "donor", "biological unit must be donor", errors)
    require(split.get("strategy") == "leave_one_donor_out", "split strategy must be leave_one_donor_out", errors)
    require(split.get("cell_random_split_allowed") is False, "cell-random split must be prohibited", errors)
    for key in (
        "feature_selection_fit_on_training_donors_only",
        "scaling_fit_on_training_donors_only",
        "pca_fit_on_training_donors_only",
    ):
        require(split.get(key) is True, f"{key} must be true", errors)
    require(set(split.get("folds", [])) == DONORS, "split folds must hold out each donor exactly once", errors)

    task = data.get("task", {})
    require(task.get("primary_target") == "LPS_vs_RPMI_response_state", "primary target mismatch", errors)
    require(task.get("unit_of_prediction") == "cell", "unit of prediction must be cell", errors)
    require(task.get("unit_of_generalization") == "held_out_donor", "unit of generalization must be held_out_donor", errors)

    folds = data.get("folds")
    require(isinstance(folds, list) and len(folds) == 3, "exactly three donor folds required", errors)
    seen: set[str] = set()
    if isinstance(folds, list):
        for index, fold in enumerate(folds):
            prefix = f"folds[{index}]"
            require(isinstance(fold, dict), f"{prefix} must be object", errors)
            if not isinstance(fold, dict):
                continue
            held = fold.get("held_out_donor")
            training = set(fold.get("training_donors", []))
            require(held in DONORS, f"{prefix}.held_out_donor invalid", errors)
            if held in DONORS:
                seen.add(held)
            require(training == DONORS - {held}, f"{prefix}.training_donors must exclude held-out donor", errors)
            require(held not in training, f"{prefix} leaks held-out donor into training", errors)
            require(isinstance(fold.get("train_cells"), int) and fold["train_cells"] > 0, f"{prefix}.train_cells invalid", errors)
            require(isinstance(fold.get("test_cells"), int) and fold["test_cells"] > 0, f"{prefix}.test_cells invalid", errors)
            models = fold.get("models", {})
            require(isinstance(models, dict) and MODELS <= set(models), f"{prefix}.models missing required baselines", errors)
            if isinstance(models, dict):
                for name in MODELS & set(models):
                    valid_metrics(models[name], f"{prefix}.models.{name}", errors)
    require(seen == DONORS, "every donor must be held out exactly once", errors)

    macro = data.get("macro_metrics", {})
    require(isinstance(macro, dict) and MODELS <= set(macro), "macro_metrics missing required baselines", errors)
    if isinstance(macro, dict):
        for name in MODELS & set(macro):
            valid_metrics(macro[name], f"macro_metrics.{name}", errors)

    geneformer = data.get("geneformer", {})
    status = geneformer.get("status")
    require(status in {"GENEFORMER_RUNTIME_HOLD", "EXECUTED_WITH_PASSPORT"}, "invalid Geneformer status", errors)
    if status == "GENEFORMER_RUNTIME_HOLD":
        require(geneformer.get("inference_executed") is False, "runtime HOLD cannot claim inference", errors)
        require(geneformer.get("embedding_generated") is False, "runtime HOLD cannot claim embeddings", errors)
        require(geneformer.get("checkpoint") in {None, ""}, "runtime HOLD must not invent checkpoint", errors)
        require(geneformer.get("runtime") in {None, ""}, "runtime HOLD must not invent runtime", errors)
    else:
        require(geneformer.get("inference_executed") is True, "executed status requires inference", errors)
        require(geneformer.get("embedding_generated") is True, "executed status requires embeddings", errors)
        require(bool(geneformer.get("checkpoint")), "executed status requires checkpoint", errors)
        require(bool(geneformer.get("runtime")), "executed status requires runtime", errors)
        require(bool(geneformer.get("model_evidence_passport")), "executed status requires Model Evidence Passport", errors)
    require(geneformer.get("training_overlap_status") in {"unknown", "excluded", "possible", "confirmed"}, "training overlap status invalid", errors)

    claims = data.get("claim_boundary", {})
    require(claims.get("same_cell_future_response_prediction") == "blocked", "same-cell prediction must be blocked", errors)
    require(claims.get("NFKBIA_specific_predictive_effect") in {"not_established", "blocked"}, "NFKBIA-specific effect must not be established", errors)
    require(claims.get("causal") == "blocked", "causal claim must be blocked", errors)
    require(claims.get("clinical") == "blocked", "clinical claim must be blocked", errors)
    require(claims.get("therapeutic") == "blocked", "therapeutic claim must be blocked", errors)

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_gse184241_donor_benchmark.py <record.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("BLOCK")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ACCEPT_WITH_LIMITS")
    print(f"benchmark_id={data['benchmark_id']}")
    print(f"geneformer_status={data['geneformer']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
