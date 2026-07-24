#!/usr/bin/env python3
"""Fail-closed validator for GSE184241 Geneformer V1 inference evidence."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[a-f0-9]{64}$")
SHA_REF = re.compile(r"^sha256:[a-f0-9]{64}$")
COMPLETED = "GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY"
HOLDS = {
    "HOLD_INPUT_CONTRACT",
    "HOLD_CHECKPOINT_IDENTITY",
    "HOLD_TOKENIZATION",
    "HOLD_RUNTIME_RESOURCE",
    "HOLD_TRAINING_OVERLAP",
}
EXPECTED_MODEL_REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
EXPECTED_PREDECESSOR = "gse184241-geneformer-runtime-preflight-v0-1"
EXPECTED_PREDECESSOR_AUTH = "sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665"
METRICS = ["roc_auc", "average_precision", "balanced_accuracy", "log_loss"]


def require(condition: bool, message: str, errors: list[str]) -> None:
    """Append one stable validation error when a condition is false."""
    if not condition:
        errors.append(message)


def valid_sha(value: Any) -> bool:
    """Return whether a value is an exact lowercase SHA-256 hex digest."""
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def numeric(value: Any) -> bool:
    """Return whether a value is a finite non-boolean number."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def main() -> int:
    """Validate completed or expected-HOLD evidence without upgrading claims."""
    if len(sys.argv) != 2:
        print("usage: validate_gse184241_geneformer_v1_inference.py RESULT.json")
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"verdict": "BLOCK", "errors": [f"cannot load result: {exc}"]}, indent=2))
        return 1

    errors: list[str] = []
    status = data.get("status")
    require(data.get("schema_version") == "0.1.0", "schema_version must be 0.1.0", errors)
    require(status == COMPLETED or status in HOLDS, "status is not an allowed completed/HOLD outcome", errors)
    require(data.get("source_revision"), "source_revision is required", errors)
    predecessor = data.get("predecessor", {})
    require(predecessor.get("transition_id") == EXPECTED_PREDECESSOR, "predecessor transition mismatch", errors)
    require(predecessor.get("authorization_ref") == EXPECTED_PREDECESSOR_AUTH, "predecessor authorization mismatch", errors)
    require(bool(SHA_REF.fullmatch(str(predecessor.get("authorization_ref", "")))), "predecessor authorization must be a sha256 reference", errors)

    dataset = data.get("dataset", {})
    require(dataset.get("accession") == "GSE184241", "dataset must remain GSE184241", errors)
    require(valid_sha(dataset.get("counts_sha256")), "counts_sha256 must be exact", errors)
    require(valid_sha(dataset.get("barcodes_sha256")), "barcodes_sha256 must be exact", errors)

    execution = data.get("execution", {})
    claims = data.get("claim_boundary", {})
    for key in [
        "same_cell_future_response_prediction",
        "incremental_value_established",
        "causal_effect_established",
        "clinical_utility_established",
        "physical_execution_authorized",
    ]:
        require(claims.get(key) is False, f"claim boundary {key} must remain false", errors)

    if status == COMPLETED:
        require(data.get("compatibility_verdict") == "HOLD_TRAINING_OVERLAP", "completed execution must retain training-overlap hold", errors)
        require(dataset.get("organism") == "Homo sapiens", "completed run organism mismatch", errors)
        require(dataset.get("cells") == 1710, "completed run must preserve 1710 cells", errors)
        require(dataset.get("independent_donors") == 3, "completed run must preserve three donors", errors)
        require(dataset.get("same_cell_longitudinal_identity") is False, "same-cell longitudinal identity must remain false", errors)
        require(valid_sha(dataset.get("cell_order_sha256")), "cell_order_sha256 must be exact", errors)

        model = data.get("model", {})
        require(model.get("repository") == "ctheodoris/Geneformer", "model repository mismatch", errors)
        require(model.get("revision") == EXPECTED_MODEL_REVISION, "model revision mismatch", errors)
        require(model.get("checkpoint") == "Geneformer-V1-10M", "checkpoint mismatch", errors)
        files = model.get("files", {})
        required_files = {
            "Geneformer-V1-10M/config.json",
            "Geneformer-V1-10M/model.safetensors",
            "geneformer/gene_dictionaries_30m/gene_median_dictionary_gc30M.pkl",
            "geneformer/gene_dictionaries_30m/token_dictionary_gc30M.pkl",
            "geneformer/gene_dictionaries_30m/gene_name_id_dict_gc30M.pkl",
            "geneformer/gene_dictionaries_30m/ensembl_mapping_dict_gc30M.pkl",
        }
        require(set(files) == required_files, "exact V1 model file set mismatch", errors)
        for name, identity in files.items():
            require(valid_sha(identity.get("sha256")), f"model file {name} sha256 missing", errors)
            require(isinstance(identity.get("size_bytes"), int) and identity.get("size_bytes") > 0, f"model file {name} size invalid", errors)

        tokenization = data.get("tokenization", {})
        require(tokenization.get("raw_counts_without_feature_selection") is True, "Geneformer input must use raw counts without feature selection", errors)
        require(tokenization.get("model_input_size") == 2048, "V1 model_input_size must be 2048", errors)
        require(tokenization.get("special_tokens_added") is False, "V1 special tokens must be false", errors)
        require(tokenization.get("cells_tokenized") == 1710, "all retained cells must be tokenized", errors)
        require(tokenization.get("mapped_canonical_gene_count", 0) >= 500, "too few V1 vocabulary genes", errors)
        require(valid_sha(tokenization.get("artifact_sha256")), "token artifact sha256 missing", errors)
        require(valid_sha(tokenization.get("canonical_gene_order_sha256")), "canonical gene order sha256 missing", errors)

        inference = data.get("inference", {})
        require(execution.get("completed") is True, "completed result execution flag must be true", errors)
        require(execution.get("model_inference_executed") is True, "completed result must record inference", errors)
        require(execution.get("embedding_generated") is True, "completed result must record embeddings", errors)
        require(inference.get("completed") is True, "inference.completed must be true", errors)
        require(inference.get("model_inference_executed") is True, "inference flag must be true", errors)
        require(inference.get("embedding_generated") is True, "embedding flag must be true", errors)
        require(inference.get("shape") == [1710, 256], "embedding shape must be 1710x256", errors)
        require(inference.get("dtype") == "float32", "embedding dtype must be float32", errors)
        require(valid_sha(inference.get("artifact_sha256")), "embedding artifact sha256 missing", errors)
        runtime = inference.get("runtime", {})
        require(runtime.get("hidden_layer") == "second_to_last", "embedding layer mismatch", errors)
        require(runtime.get("hidden_state_index") == -2, "hidden state index must be -2", errors)
        require(runtime.get("pooling") == "mean_nonpadding_gene_tokens", "embedding pooling mismatch", errors)

        benchmark = data.get("benchmark", {})
        require(benchmark.get("biological_unit") == "donor", "biological unit must be donor", errors)
        require(benchmark.get("split_strategy") == "leave_one_donor_out", "split strategy mismatch", errors)
        require(benchmark.get("cell_random_split_allowed") is False, "cell-random split must remain forbidden", errors)
        require(len(benchmark.get("folds", [])) == 3, "exactly three donor folds are required", errors)
        require(benchmark.get("incremental_value_established") is False, "three-donor comparison cannot establish incremental value", errors)
        require(benchmark.get("interpretation") == "DESCRIPTIVE_COMPARISON_ONLY_TRAINING_OVERLAP_HOLD", "benchmark interpretation must remain held", errors)
        geneformer_metrics = benchmark.get("geneformer_macro_metrics", {})
        pca_metrics = benchmark.get("frozen_baseline_macro_metrics", {}).get("PCA_state", {})
        deltas = benchmark.get("descriptive_delta_vs_PCA_state", {})
        for metric in METRICS:
            require(numeric(geneformer_metrics.get(metric)), f"Geneformer metric {metric} missing", errors)
            require(numeric(pca_metrics.get(metric)), f"PCA_state metric {metric} missing", errors)
            require(numeric(deltas.get(metric)), f"Geneformer-vs-PCA delta {metric} missing", errors)
            if numeric(geneformer_metrics.get(metric)) and numeric(pca_metrics.get(metric)) and numeric(deltas.get(metric)):
                expected_delta = float(geneformer_metrics[metric]) - float(pca_metrics[metric])
                require(abs(float(deltas[metric]) - expected_delta) <= 1e-12, f"Geneformer-vs-PCA delta {metric} mismatch", errors)

        evidence = data.get("evidence", {})
        require(valid_sha(evidence.get("input_manifest_sha256")), "input manifest sha256 missing", errors)
        require(valid_sha(evidence.get("model_evidence_passport_sha256")), "passport sha256 missing", errors)
    else:
        require(execution.get("completed") is False, "HOLD execution must not be completed", errors)
        require(execution.get("model_inference_executed") is False, "HOLD cannot claim inference", errors)
        require(execution.get("embedding_generated") is False, "HOLD cannot claim embeddings", errors)
        require(bool(execution.get("error")), "HOLD must preserve exact error evidence", errors)

    verdict = "ACCEPT" if not errors else "BLOCK"
    print(json.dumps({"verdict": verdict, "status": status, "errors": errors}, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
