#!/usr/bin/env python3
"""Execute bounded Geneformer V1 inference on frozen GSE184241 donor folds."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
import torch
from huggingface_hub import snapshot_download
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler
from transformers import BertForMaskedLM, __version__ as transformers_version

from run_gse184241_donor_baselines_v2 import DONORS, load_counts, parse_metadata, sha256_file

MODEL_REPOSITORY = "ctheodoris/Geneformer"
MODEL_REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
MODEL_CHECKPOINT = "Geneformer-V1-10M"
MODEL_INPUT_SIZE = 2048
TARGET_SUM = 10_000.0
RANDOM_STATE = 20260723
PREDECESSOR_TRANSITION_ID = "gse184241-geneformer-runtime-preflight-v0-1"
PREDECESSOR_AUTHORIZATION_REF = "sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665"
ALLOWED_MODEL_FILES = [
    "Geneformer-V1-10M/config.json",
    "Geneformer-V1-10M/model.safetensors",
    "geneformer/gene_dictionaries_30m/gene_median_dictionary_gc30M.pkl",
    "geneformer/gene_dictionaries_30m/token_dictionary_gc30M.pkl",
    "geneformer/gene_dictionaries_30m/gene_name_id_dict_gc30M.pkl",
    "geneformer/gene_dictionaries_30m/ensembl_mapping_dict_gc30M.pkl",
]


class ContractHold(RuntimeError):
    """Represent one expected fail-closed evidence hold."""

    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class Assets:
    """Exact local paths for the pinned Geneformer V1 execution assets."""

    root: Path
    checkpoint: Path
    median: Path
    tokens: Path
    names: Path
    mapping: Path


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 digest of exact bytes."""
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> str:
    """Write stable pretty JSON and return its exact file digest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return sha256_file(path)


def load_pickle(path: Path) -> Any:
    """Load one trusted pickle from the exact pinned model repository."""
    with path.open("rb") as handle:
        return pickle.load(handle)


def download_assets(cache_dir: Path) -> Assets:
    """Download only the exact V1 checkpoint and 30M dictionaries at the pinned revision."""
    try:
        root = Path(
            snapshot_download(
                repo_id=MODEL_REPOSITORY,
                revision=MODEL_REVISION,
                allow_patterns=ALLOWED_MODEL_FILES,
                local_dir=cache_dir,
            )
        )
    except Exception as exc:  # noqa: BLE001 - network/resource failure is evidence
        raise ContractHold("HOLD_RUNTIME_RESOURCE", f"model asset download failed: {type(exc).__name__}: {exc}") from exc
    assets = Assets(
        root=root,
        checkpoint=root / MODEL_CHECKPOINT,
        median=root / "geneformer/gene_dictionaries_30m/gene_median_dictionary_gc30M.pkl",
        tokens=root / "geneformer/gene_dictionaries_30m/token_dictionary_gc30M.pkl",
        names=root / "geneformer/gene_dictionaries_30m/gene_name_id_dict_gc30M.pkl",
        mapping=root / "geneformer/gene_dictionaries_30m/ensembl_mapping_dict_gc30M.pkl",
    )
    required = [assets.checkpoint / "config.json", assets.checkpoint / "model.safetensors", assets.median, assets.tokens, assets.names, assets.mapping]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise ContractHold("HOLD_CHECKPOINT_IDENTITY", f"pinned model assets missing: {missing}")
    return assets


def map_and_collapse_genes(
    counts: pd.DataFrame,
    gene_name_to_id: dict[Any, Any],
    ensembl_mapping: dict[Any, Any],
    token_dict: dict[Any, Any],
    median_dict: dict[Any, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    """Map symbols to canonical V1 Ensembl IDs and sum duplicate mapped rows."""
    grouped: dict[str, list[int]] = {}
    unmapped = 0
    missing_vocab = 0
    genes = counts.index.astype(str).tolist()
    for index, symbol in enumerate(genes):
        candidate = gene_name_to_id.get(symbol)
        if candidate is None:
            candidate = gene_name_to_id.get(symbol.upper())
        if candidate is None:
            unmapped += 1
            continue
        candidate = str(candidate).split(".")[0]
        candidate = str(ensembl_mapping.get(candidate, candidate))
        if candidate not in token_dict or candidate not in median_dict:
            missing_vocab += 1
            continue
        grouped.setdefault(candidate, []).append(index)
    canonical_ids = np.array(sorted(grouped), dtype=object)
    if len(canonical_ids) < 500:
        raise ContractHold("HOLD_INPUT_CONTRACT", f"only {len(canonical_ids)} genes mapped into V1 vocabulary")
    cells_by_original = counts.to_numpy(dtype=np.float32, copy=False).T
    collapsed = np.empty((cells_by_original.shape[0], len(canonical_ids)), dtype=np.float32)
    for output_index, gene in enumerate(canonical_ids):
        source = grouped[str(gene)]
        collapsed[:, output_index] = (
            cells_by_original[:, source[0]]
            if len(source) == 1
            else cells_by_original[:, source].sum(axis=1, dtype=np.float32)
        )
    tokens = np.array([int(token_dict[str(gene)]) for gene in canonical_ids], dtype=np.int64)
    medians = np.array([float(median_dict[str(gene)]) for gene in canonical_ids], dtype=np.float64)
    if np.any(~np.isfinite(medians)) or np.any(medians <= 0):
        raise ContractHold("HOLD_TOKENIZATION", "V1 median dictionary contains non-positive or non-finite factors")
    summary = {
        "input_gene_count": len(genes),
        "mapped_canonical_gene_count": int(len(canonical_ids)),
        "unmapped_symbol_count": int(unmapped),
        "mapped_but_missing_v1_vocab_count": int(missing_vocab),
        "duplicate_canonical_groups": int(sum(len(indices) > 1 for indices in grouped.values())),
        "canonical_gene_order_sha256": sha256_bytes("\n".join(canonical_ids.tolist()).encode("utf-8")),
    }
    return collapsed, tokens, medians, summary


def tokenize_raw_counts(
    collapsed_counts: np.ndarray,
    total_counts: np.ndarray,
    gene_tokens: np.ndarray,
    medians: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Reproduce V1 median-scaled rank tokenization without feature selection."""
    if np.any(total_counts <= 0):
        raise ContractHold("HOLD_INPUT_CONTRACT", "zero-library cells reached tokenization")
    input_ids = np.zeros((collapsed_counts.shape[0], MODEL_INPUT_SIZE), dtype=np.int32)
    lengths = np.zeros(collapsed_counts.shape[0], dtype=np.int32)
    detected: list[int] = []
    for cell_index, row in enumerate(collapsed_counts):
        nonzero = np.flatnonzero(row > 0)
        detected.append(int(len(nonzero)))
        if len(nonzero) == 0:
            raise ContractHold("HOLD_TOKENIZATION", f"cell {cell_index} has no V1-vocabulary genes")
        normalized = row[nonzero].astype(np.float64) / float(total_counts[cell_index]) * TARGET_SUM / medians[nonzero]
        order = np.argsort(-normalized, kind="stable")[:MODEL_INPUT_SIZE]
        ranked = gene_tokens[nonzero][order]
        lengths[cell_index] = len(ranked)
        input_ids[cell_index, : len(ranked)] = ranked.astype(np.int32, copy=False)
    if np.any(lengths <= 0) or np.any(lengths > MODEL_INPUT_SIZE):
        raise ContractHold("HOLD_TOKENIZATION", "invalid V1 token sequence length")
    return input_ids, lengths, {
        "cells_tokenized": int(len(lengths)),
        "model_input_size": MODEL_INPUT_SIZE,
        "special_tokens_added": False,
        "target_sum": int(TARGET_SUM),
        "length_min": int(lengths.min()),
        "length_median": float(np.median(lengths)),
        "length_max": int(lengths.max()),
        "cells_truncated_to_2048": int(sum(value > MODEL_INPUT_SIZE for value in detected)),
        "detected_v1_genes_before_truncation_max": int(max(detected)),
    }


def extract_embeddings(
    checkpoint_dir: Path,
    input_ids: np.ndarray,
    lengths: np.ndarray,
    batch_size: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Mean-pool the second-to-last hidden layer over non-padding V1 gene tokens."""
    try:
        model = BertForMaskedLM.from_pretrained(checkpoint_dir, local_files_only=True, output_hidden_states=True)
    except Exception as exc:  # noqa: BLE001 - exact checkpoint-load failure is evidence
        raise ContractHold("HOLD_CHECKPOINT_IDENTITY", f"checkpoint load failed: {type(exc).__name__}: {exc}") from exc
    config = model.config
    if (int(config.max_position_embeddings), int(config.hidden_size), int(config.num_hidden_layers)) != (2048, 256, 6):
        raise ContractHold("HOLD_CHECKPOINT_IDENTITY", "V1 config mismatch: expected positions=2048 hidden=256 layers=6")
    model.eval().to(torch.device("cpu"))
    output = np.empty((len(lengths), 256), dtype=np.float32)
    sorted_indices = np.argsort(lengths, kind="stable")
    started = time.monotonic()
    try:
        with torch.inference_mode():
            for start in range(0, len(sorted_indices), batch_size):
                indices = sorted_indices[start : start + batch_size]
                max_len = int(lengths[indices].max())
                ids = torch.from_numpy(input_ids[indices, :max_len].astype(np.int64, copy=False))
                mask = torch.arange(max_len).unsqueeze(0) < torch.from_numpy(lengths[indices].astype(np.int64, copy=False)).unsqueeze(1)
                hidden = model(input_ids=ids, attention_mask=mask).hidden_states[-2]
                pooled = (hidden * mask.unsqueeze(-1)).sum(dim=1) / mask.sum(dim=1, keepdim=True)
                output[indices] = pooled.numpy().astype(np.float32, copy=False)
    except (RuntimeError, MemoryError) as exc:
        raise ContractHold("HOLD_RUNTIME_RESOURCE", f"Geneformer CPU inference failed: {type(exc).__name__}: {exc}") from exc
    if not np.all(np.isfinite(output)):
        raise ContractHold("HOLD_RUNTIME_RESOURCE", "non-finite values in Geneformer embeddings")
    return output, {
        "device": "cpu",
        "batch_size": batch_size,
        "hidden_layer": "second_to_last",
        "hidden_state_index": -2,
        "pooling": "mean_nonpadding_gene_tokens",
        "embedding_dimensions": 256,
        "elapsed_seconds": float(time.monotonic() - started),
    }


def metric_bundle(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    """Compute the frozen binary benchmark metric bundle."""
    prediction = (probability >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "log_loss": float(log_loss(y_true, probability, labels=[0, 1])),
    }


def embedding_benchmark(embeddings: np.ndarray, metadata: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """Evaluate frozen leave-one-donor-out logistic probes on fixed embeddings."""
    y = (metadata["condition"] == "LPS").astype(int).to_numpy()
    folds: list[dict[str, Any]] = []
    for held_out in DONORS:
        test_mask = (metadata["donor"] == held_out).to_numpy()
        train_mask = ~test_mask
        scaler = StandardScaler()
        train_x = scaler.fit_transform(embeddings[train_mask])
        test_x = scaler.transform(embeddings[test_mask])
        model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE, solver="liblinear")
        model.fit(train_x, y[train_mask])
        probability = model.predict_proba(test_x)[:, 1]
        folds.append({
            "held_out_donor": held_out,
            "training_donors": [donor for donor in DONORS if donor != held_out],
            "train_cells": int(train_mask.sum()),
            "test_cells": int(test_mask.sum()),
            "models": {"Geneformer_V1_embedding": metric_bundle(y[test_mask], probability)},
        })
    keys = ["roc_auc", "average_precision", "balanced_accuracy", "log_loss"]
    macro = {key: float(np.mean([fold["models"]["Geneformer_V1_embedding"][key] for fold in folds])) for key in keys}
    return folds, macro


def model_file_manifest(assets: Assets) -> dict[str, Any]:
    """Return exact file identities for every model asset used by execution."""
    files = [assets.checkpoint / "config.json", assets.checkpoint / "model.safetensors", assets.median, assets.tokens, assets.names, assets.mapping]
    return {str(path.relative_to(assets.root)): {"sha256": sha256_file(path), "size_bytes": path.stat().st_size} for path in files}


def claim_boundary() -> dict[str, bool]:
    """Return the immutable scientific and physical claim boundary."""
    return {
        "same_cell_future_response_prediction": False,
        "incremental_value_established": False,
        "causal_effect_established": False,
        "clinical_utility_established": False,
        "physical_execution_authorized": False,
    }


def hold_outputs(output_dir: Path, source_revision: str, status: str, error: str, counts_path: Path, barcodes_path: Path) -> int:
    """Persist an expected fail-closed HOLD without fabricating inference evidence."""
    result = {
        "schema_version": "0.1.0",
        "run_id": f"gse184241-geneformer-v1-{source_revision[:12]}",
        "status": status,
        "source_revision": source_revision,
        "predecessor": {"transition_id": PREDECESSOR_TRANSITION_ID, "authorization_ref": PREDECESSOR_AUTHORIZATION_REF},
        "dataset": {
            "accession": "GSE184241",
            "counts_sha256": sha256_file(counts_path) if counts_path.is_file() else None,
            "barcodes_sha256": sha256_file(barcodes_path) if barcodes_path.is_file() else None,
        },
        "execution": {"completed": False, "model_inference_executed": False, "embedding_generated": False, "error": error},
        "compatibility_verdict": status,
        "claim_boundary": claim_boundary(),
    }
    write_json(output_dir / "geneformer-v1-inference.json", result)
    passport = {
        "schema_version": "0.2.0",
        "passport_id": f"gse184241-geneformer-v1-{source_revision[:12]}-hold",
        "run_identity": {"run_id": result["run_id"], "created_at": "2026-07-23T00:00:00Z", "code_revision": source_revision, "execution_mode": "framework_local"},
        "model_identity": {"provider": "ctheodoris", "registry_id": MODEL_REPOSITORY, "model_family": "Geneformer-V1", "checkpoint_or_version": f"{MODEL_CHECKPOINT}@{MODEL_REVISION}", "runtime_or_container": "GitHub Actions ubuntu-latest CPU", "source_url": "https://huggingface.co/ctheodoris/Geneformer"},
        "data_identity": {"dataset_id": "GSE184241", "input_artifact": counts_path.name, "input_sha256": result["dataset"]["counts_sha256"] or "0" * 64, "output_artifact": "geneformer-v1-inference.json", "output_sha256": sha256_file(output_dir / "geneformer-v1-inference.json")},
        "execution": {"parameters": {"model_input_size": 2048, "special_tokens": False}, "random_seeds": [RANDOM_STATE], "hardware": {"device": "cpu"}, "software": {"python": platform.python_version()}, "status": "failed"},
        "transformations": [],
        "compatibility_verdict": status,
        "uncertainty": {"domain_shift_risks": ["execution hold prevented complete model evidence"], "training_overlap_status": "unknown", "limitations": [error]},
        "claim_boundary": {"evidence_contribution": "No model evidence; durable fail-closed HOLD only.", "causal": "blocked", "clinical_therapeutic": "blocked"},
        "safety_status": {"physical_biology_authorized": False, "clinical_use_authorized": False},
    }
    write_json(output_dir / "model-evidence-passport.json", passport)
    return 0


def main() -> int:
    """Run exact V1 tokenization, embedding extraction and donor-held-out comparison."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", required=True)
    parser.add_argument("--barcodes", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-cache", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    counts_path, barcodes_path, benchmark_path = Path(args.counts), Path(args.barcodes), Path(args.benchmark)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        counts = load_counts(counts_path)
        metadata = parse_metadata(counts.columns.tolist())
        barcode_table = pd.read_excel(barcodes_path, sheet_name=0)
        if "Sample_ID" not in barcode_table.columns:
            raise ContractHold("HOLD_INPUT_CONTRACT", "barcode workbook lacks Sample_ID")
        barcode_ids = {str(value).strip().strip('"').strip("'") for value in barcode_table["Sample_ID"].dropna()}
        if barcode_ids != set(counts.columns):
            raise ContractHold("HOLD_INPUT_CONTRACT", "counts and barcode workbook cell identity differ")
        if sha256_file(counts_path) != benchmark["dataset"]["counts_sha256"] or sha256_file(barcodes_path) != benchmark["dataset"]["barcodes_sha256"]:
            raise ContractHold("HOLD_INPUT_CONTRACT", "official input digest differs from frozen benchmark")
        total_counts = counts.sum(axis=0).to_numpy(dtype=np.float64)
        keep = total_counts > 0
        counts, metadata, total_counts = counts.loc[:, keep], metadata.loc[counts.columns[keep]], total_counts[keep]
        cell_ids = counts.columns.astype(str).tolist()
        if len(cell_ids) != int(benchmark["dataset"]["cells_retained"]):
            raise ContractHold("HOLD_INPUT_CONTRACT", "retained cell count differs from frozen benchmark")
        cell_order_sha = sha256_bytes("\n".join(cell_ids).encode("utf-8"))

        assets = download_assets(Path(args.model_cache))
        collapsed, gene_tokens, medians, mapping_summary = map_and_collapse_genes(
            counts, load_pickle(assets.names), load_pickle(assets.mapping), load_pickle(assets.tokens), load_pickle(assets.median)
        )
        input_ids, lengths, token_summary = tokenize_raw_counts(collapsed, total_counts, gene_tokens, medians)
        del collapsed
        token_path = output_dir / "geneformer-v1-tokenized-inputs.npz"
        np.savez_compressed(token_path, input_ids=input_ids, lengths=lengths, cell_ids=np.array(cell_ids, dtype="U64"))
        token_sha = sha256_file(token_path)
        embeddings, runtime = extract_embeddings(assets.checkpoint, input_ids, lengths, args.batch_size)
        embedding_path = output_dir / "geneformer-v1-cell-embeddings.npz"
        np.savez_compressed(embedding_path, embeddings=embeddings, cell_ids=np.array(cell_ids, dtype="U64"), token_lengths=lengths)
        embedding_sha = sha256_file(embedding_path)
        folds, macro = embedding_benchmark(embeddings, metadata)
        baseline_macro = benchmark["macro_metrics"]
        model_files = model_file_manifest(assets)
        input_manifest = {
            "schema_version": "0.1.0", "dataset": "GSE184241", "counts_sha256": sha256_file(counts_path),
            "barcodes_sha256": sha256_file(barcodes_path), "cell_order_sha256": cell_order_sha,
            "cells": len(cell_ids), "input_genes": int(counts.shape[0]), "model_repository": MODEL_REPOSITORY,
            "model_revision": MODEL_REVISION, "checkpoint": MODEL_CHECKPOINT, "model_files": model_files,
            "mapping": mapping_summary, "tokenization": token_summary,
        }
        input_manifest_sha = write_json(output_dir / "geneformer-v1-input-manifest.json", input_manifest)
        run_id = f"gse184241-geneformer-v1-{args.source_revision[:12]}"
        passport = {
            "schema_version": "0.2.0", "passport_id": run_id,
            "run_identity": {"run_id": run_id, "created_at": "2026-07-23T00:00:00Z", "code_revision": args.source_revision, "execution_mode": "framework_local"},
            "model_identity": {"provider": "ctheodoris", "registry_id": MODEL_REPOSITORY, "model_family": "Geneformer-V1", "checkpoint_or_version": f"{MODEL_CHECKPOINT}@{MODEL_REVISION}", "runtime_or_container": "GitHub Actions ubuntu-latest CPU; pinned Python dependencies", "source_url": "https://huggingface.co/ctheodoris/Geneformer"},
            "data_identity": {"dataset_id": "GSE184241", "input_artifact": "geneformer-v1-input-manifest.json", "input_sha256": input_manifest_sha, "output_artifact": embedding_path.name, "output_sha256": embedding_sha},
            "execution": {"parameters": {"model_input_size": 2048, "special_tokens": False, "target_sum": 10000, "embedding_layer": "second_to_last", "pooling": "mean_nonpadding_gene_tokens", "batch_size": args.batch_size, "probe": "fixed_C1_balanced_liblinear_leave_one_donor_out"}, "random_seeds": [RANDOM_STATE], "hardware": {"device": "cpu", "machine": platform.machine(), "processor": platform.processor(), "torch_threads": torch.get_num_threads()}, "software": {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers_version, "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__}, "status": "completed"},
            "transformations": [
                {"name": "symbol_to_v1_ensembl_mapping_and_duplicate_sum", "version": MODEL_REVISION, "parameters": mapping_summary, "status": "applied"},
                {"name": "geneformer_v1_median_scaled_rank_tokenization", "version": MODEL_REVISION, "parameters": token_summary, "status": "applied"},
                {"name": "geneformer_v1_second_to_last_layer_mean_pool", "version": MODEL_REVISION, "parameters": runtime, "status": "applied"},
            ],
            "compatibility_verdict": "HOLD_TRAINING_OVERLAP",
            "uncertainty": {"domain_shift_risks": ["three-donor post-response monocyte dataset", "possible pretraining-corpus overlap cannot be excluded", "cell predictions are evaluated only through donor-held-out folds"], "training_overlap_status": "unknown", "limitations": ["No same-cell longitudinal response identity exists.", "Only three independent donors are available.", "Embedding probe performance is descriptive, not causal or clinical evidence.", "Training overlap was not independently excluded."]},
            "claim_boundary": {"evidence_contribution": "Executed foundation-model embedding comparison on frozen donor-held-out post-response state task; report-only with training-overlap hold.", "causal": "blocked", "clinical_therapeutic": "blocked"},
            "safety_status": {"physical_biology_authorized": False, "clinical_use_authorized": False},
        }
        passport_sha = write_json(output_dir / "model-evidence-passport.json", passport)
        result = {
            "schema_version": "0.1.0", "run_id": run_id, "status": "GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY",
            "compatibility_verdict": "HOLD_TRAINING_OVERLAP", "source_revision": args.source_revision,
            "predecessor": {"transition_id": PREDECESSOR_TRANSITION_ID, "authorization_ref": PREDECESSOR_AUTHORIZATION_REF},
            "dataset": {"accession": "GSE184241", "organism": "Homo sapiens", "cells": len(cell_ids), "independent_donors": 3, "counts_sha256": sha256_file(counts_path), "barcodes_sha256": sha256_file(barcodes_path), "cell_order_sha256": cell_order_sha, "same_cell_longitudinal_identity": False},
            "model": {"repository": MODEL_REPOSITORY, "revision": MODEL_REVISION, "checkpoint": MODEL_CHECKPOINT, "files": model_files},
            "tokenization": {**token_summary, **mapping_summary, "artifact": token_path.name, "artifact_sha256": token_sha, "raw_counts_without_feature_selection": True},
            "inference": {"completed": True, "model_inference_executed": True, "embedding_generated": True, "runtime": runtime, "artifact": embedding_path.name, "artifact_sha256": embedding_sha, "shape": [int(value) for value in embeddings.shape], "dtype": str(embeddings.dtype)},
            "benchmark": {"biological_unit": "donor", "split_strategy": "leave_one_donor_out", "cell_random_split_allowed": False, "folds": folds, "geneformer_macro_metrics": macro, "frozen_baseline_macro_metrics": baseline_macro, "descriptive_delta_vs_PCA_state": {key: float(macro[key] - baseline_macro["PCA_state"][key]) for key in macro}, "incremental_value_established": False, "interpretation": "DESCRIPTIVE_COMPARISON_ONLY_TRAINING_OVERLAP_HOLD"},
            "evidence": {"input_manifest": "geneformer-v1-input-manifest.json", "input_manifest_sha256": input_manifest_sha, "model_evidence_passport": "model-evidence-passport.json", "model_evidence_passport_sha256": passport_sha},
            "execution": {"completed": True, "model_inference_executed": True, "embedding_generated": True, "error": None},
            "claim_boundary": claim_boundary(),
        }
        result_sha = write_json(output_dir / "geneformer-v1-inference.json", result)
        report = ["# GSE184241 Geneformer V1 inference", "", f"- Status: **{result['status']}**", f"- Compatibility: **{result['compatibility_verdict']}**", f"- Cells: **{len(cell_ids)}** across **3 donors**", f"- Embeddings: **{embeddings.shape[0]} × {embeddings.shape[1]}**", f"- Result SHA-256: `{result_sha}`", "", "## Donor-held-out macro metrics", "", "| Model | AUROC | AP | Balanced accuracy | Log loss |", "|---|---:|---:|---:|---:|"]
        for name in ["NFKBIA_only", "inflammatory_panel", "PCA_state"]:
            value = baseline_macro[name]
            report.append(f"| {name} | {value['roc_auc']:.4f} | {value['average_precision']:.4f} | {value['balanced_accuracy']:.4f} | {value['log_loss']:.4f} |")
        report.append(f"| Geneformer_V1_embedding | {macro['roc_auc']:.4f} | {macro['average_precision']:.4f} | {macro['balanced_accuracy']:.4f} | {macro['log_loss']:.4f} |")
        report += ["", "## Boundary", "", "Checkpoint execution and embeddings are report-only because training overlap was not independently excluded, only three donors exist, and this is post-response state discrimination rather than same-cell future-response prediction.", "", "No causal, clinical, therapeutic, physical-experiment, production-write, deployment, submission or merge authority is granted.", ""]
        (output_dir / "geneformer-v1-inference.md").write_text("\n".join(report), encoding="utf-8")
        print(json.dumps({"status": result["status"], "compatibility_verdict": result["compatibility_verdict"], "result_sha256": result_sha, "macro_metrics": macro}, sort_keys=True))
        return 0
    except ContractHold as hold:
        print(json.dumps({"status": hold.status, "error": str(hold)}, sort_keys=True), file=sys.stderr)
        return hold_outputs(output_dir, args.source_revision, hold.status, str(hold), counts_path, barcodes_path)


if __name__ == "__main__":
    raise SystemExit(main())
