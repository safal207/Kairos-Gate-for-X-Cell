#!/usr/bin/env python3
"""Fail closed unless full MLM and encoder-only Geneformer forwards are equivalent."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
from transformers import BertForMaskedLM

from run_gse184241_donor_baselines_v2 import parse_metadata, sha256_file
from run_gse184241_geneformer_v1_inference import embedding_benchmark

EXPECTED_CELLS = 1710
EXPECTED_TOKENS = 2048
EXPECTED_DIMENSIONS = 256
CANONICAL_EMBEDDING_ATOL = 2e-6
CANONICAL_METRIC_ATOL = 1e-6


def array_sha256(value: np.ndarray) -> str:
    """Hash a contiguous array including dtype and shape identity."""
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode("utf-8"))
    digest.update(json.dumps(list(value.shape), separators=(",", ":")).encode("utf-8"))
    digest.update(np.ascontiguousarray(value).tobytes(order="C"))
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    """Serialize metrics deterministically for exact comparison."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def structures_close(left: Any, right: Any, tolerance: float) -> tuple[bool, float]:
    """Compare nested metric structures while preserving non-numeric identity."""
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right, 0.0
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if not math.isfinite(float(left)) or not math.isfinite(float(right)):
            return False, math.inf
        difference = abs(float(left) - float(right))
        return difference <= tolerance, difference
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False, math.inf
        valid = True
        maximum = 0.0
        for key in sorted(left):
            child_valid, child_maximum = structures_close(left[key], right[key], tolerance)
            valid = valid and child_valid
            maximum = max(maximum, child_maximum)
        return valid, maximum
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False, math.inf
        valid = True
        maximum = 0.0
        for left_item, right_item in zip(left, right, strict=True):
            child_valid, child_maximum = structures_close(left_item, right_item, tolerance)
            valid = valid and child_valid
            maximum = max(maximum, child_maximum)
        return valid, maximum
    return left == right, 0.0


def extract_embeddings(
    model: BertForMaskedLM,
    input_ids: np.ndarray,
    lengths: np.ndarray,
    batch_size: int,
    forward: Callable[[torch.Tensor, torch.Tensor], Any],
) -> tuple[np.ndarray, float]:
    """Run one exact forward path and mean-pool the second-to-last hidden state."""
    output = np.empty((len(lengths), EXPECTED_DIMENSIONS), dtype=np.float32)
    sorted_indices = np.argsort(lengths, kind="stable")
    started = time.monotonic()
    with torch.inference_mode():
        for start in range(0, len(sorted_indices), batch_size):
            indices = sorted_indices[start : start + batch_size]
            max_len = int(lengths[indices].max())
            ids = torch.from_numpy(input_ids[indices, :max_len].astype(np.int64, copy=False))
            mask = torch.arange(max_len).unsqueeze(0) < torch.from_numpy(
                lengths[indices].astype(np.int64, copy=False)
            ).unsqueeze(1)
            hidden = forward(ids, mask).hidden_states[-2]
            pooled = (hidden * mask.unsqueeze(-1)).sum(dim=1) / mask.sum(dim=1, keepdim=True)
            output[indices] = pooled.numpy().astype(np.float32, copy=False)
    if not np.all(np.isfinite(output)):
        raise ValueError("non-finite embeddings produced during equivalence check")
    return output, float(time.monotonic() - started)


def main() -> int:
    """Run both paths on one token artifact and reject any forward divergence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", required=True)
    parser.add_argument("--canonical-embeddings", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=2)
    args = parser.parse_args()

    token_path = Path(args.tokens)
    canonical_path = Path(args.canonical_embeddings)
    checkpoint_path = Path(args.checkpoint)
    output_path = Path(args.output)

    with np.load(token_path, allow_pickle=False) as token_artifact:
        input_ids = token_artifact["input_ids"]
        lengths = token_artifact["lengths"]
        cell_ids = token_artifact["cell_ids"].astype(str)
    with np.load(canonical_path, allow_pickle=False) as canonical_artifact:
        canonical_embeddings = canonical_artifact["embeddings"]
        canonical_cell_ids = canonical_artifact["cell_ids"].astype(str)
        canonical_lengths = canonical_artifact["token_lengths"]

    if input_ids.shape != (EXPECTED_CELLS, EXPECTED_TOKENS):
        raise ValueError(f"unexpected token shape: {input_ids.shape}")
    if lengths.shape != (EXPECTED_CELLS,):
        raise ValueError(f"unexpected token-length shape: {lengths.shape}")
    if canonical_embeddings.shape != (EXPECTED_CELLS, EXPECTED_DIMENSIONS):
        raise ValueError(f"unexpected canonical embedding shape: {canonical_embeddings.shape}")
    if not np.array_equal(cell_ids, canonical_cell_ids):
        raise ValueError("token and canonical embedding cell order differ")
    if not np.array_equal(lengths, canonical_lengths):
        raise ValueError("token and canonical embedding lengths differ")

    model = BertForMaskedLM.from_pretrained(
        checkpoint_path,
        local_files_only=True,
        output_hidden_states=True,
    )
    config = model.config
    if (
        int(config.max_position_embeddings),
        int(config.hidden_size),
        int(config.num_hidden_layers),
    ) != (EXPECTED_TOKENS, EXPECTED_DIMENSIONS, 6):
        raise ValueError("Geneformer V1 checkpoint configuration mismatch")
    model.eval().to(torch.device("cpu"))

    def full_forward(ids: torch.Tensor, mask: torch.Tensor) -> Any:
        return model(
            input_ids=ids,
            attention_mask=mask,
            output_hidden_states=True,
            return_dict=True,
        )

    def encoder_forward(ids: torch.Tensor, mask: torch.Tensor) -> Any:
        return model.bert(
            input_ids=ids,
            attention_mask=mask,
            output_hidden_states=True,
            return_dict=True,
        )

    full_embeddings, full_seconds = extract_embeddings(
        model, input_ids, lengths, args.batch_size, full_forward
    )
    encoder_embeddings, encoder_seconds = extract_embeddings(
        model, input_ids, lengths, args.batch_size, encoder_forward
    )

    metadata = parse_metadata(cell_ids.tolist())
    full_folds, full_macro = embedding_benchmark(full_embeddings, metadata)
    encoder_folds, encoder_macro = embedding_benchmark(encoder_embeddings, metadata)
    canonical_folds, canonical_macro = embedding_benchmark(canonical_embeddings, metadata)

    full_vs_canonical_fold_close, full_vs_canonical_fold_max = structures_close(
        full_folds, canonical_folds, CANONICAL_METRIC_ATOL
    )
    encoder_vs_canonical_fold_close, encoder_vs_canonical_fold_max = structures_close(
        encoder_folds, canonical_folds, CANONICAL_METRIC_ATOL
    )
    full_vs_canonical_macro_close, full_vs_canonical_macro_max = structures_close(
        full_macro, canonical_macro, CANONICAL_METRIC_ATOL
    )
    encoder_vs_canonical_macro_close, encoder_vs_canonical_macro_max = structures_close(
        encoder_macro, canonical_macro, CANONICAL_METRIC_ATOL
    )

    full_vs_encoder_max = float(np.max(np.abs(full_embeddings - encoder_embeddings)))
    full_vs_canonical_max = float(np.max(np.abs(full_embeddings - canonical_embeddings)))
    encoder_vs_canonical_max = float(np.max(np.abs(encoder_embeddings - canonical_embeddings)))
    checks = {
        "identical_token_artifact_for_both_paths": True,
        "token_and_canonical_cell_order_equal": bool(np.array_equal(cell_ids, canonical_cell_ids)),
        "token_and_canonical_lengths_equal": bool(np.array_equal(lengths, canonical_lengths)),
        "full_vs_encoder_embeddings_exact_equal": bool(np.array_equal(full_embeddings, encoder_embeddings)),
        "full_vs_encoder_fold_metrics_exact_equal": canonical_json(full_folds) == canonical_json(encoder_folds),
        "full_vs_encoder_macro_metrics_exact_equal": canonical_json(full_macro) == canonical_json(encoder_macro),
        "full_vs_canonical_embeddings_within_float32_tolerance": full_vs_canonical_max <= CANONICAL_EMBEDDING_ATOL,
        "encoder_vs_canonical_embeddings_within_float32_tolerance": encoder_vs_canonical_max <= CANONICAL_EMBEDDING_ATOL,
        "full_vs_canonical_fold_metrics_within_tolerance": full_vs_canonical_fold_close,
        "encoder_vs_canonical_fold_metrics_within_tolerance": encoder_vs_canonical_fold_close,
        "full_vs_canonical_macro_metrics_within_tolerance": full_vs_canonical_macro_close,
        "encoder_vs_canonical_macro_metrics_within_tolerance": encoder_vs_canonical_macro_close,
    }
    exact_forward_differences = {"full_vs_encoder": full_vs_encoder_max}
    canonical_reference_differences = {
        "full_vs_canonical_embeddings": full_vs_canonical_max,
        "encoder_vs_canonical_embeddings": encoder_vs_canonical_max,
        "full_vs_canonical_fold_metrics": full_vs_canonical_fold_max,
        "encoder_vs_canonical_fold_metrics": encoder_vs_canonical_fold_max,
        "full_vs_canonical_macro_metrics": full_vs_canonical_macro_max,
        "encoder_vs_canonical_macro_metrics": encoder_vs_canonical_macro_max,
    }
    valid = all(checks.values()) and full_vs_encoder_max == 0.0
    receipt = {
        "schema_version": "0.2.0",
        "artifact_type": "geneformer_v1_forward_equivalence_receipt",
        "status": "EXACT_FORWARD_EQUIVALENCE_VERIFIED" if valid else "BLOCK_FORWARD_DIVERGENCE",
        "contract": {
            "full_vs_encoder": "bit_exact_same_tokens_same_batch",
            "canonical_reference": "float32_numerical_consistency_across_batch_partitioning",
            "canonical_embedding_absolute_tolerance": CANONICAL_EMBEDDING_ATOL,
            "canonical_metric_absolute_tolerance": CANONICAL_METRIC_ATOL,
        },
        "inputs": {
            "token_artifact": token_path.name,
            "token_artifact_sha256": sha256_file(token_path),
            "canonical_embedding_artifact": canonical_path.name,
            "canonical_embedding_artifact_sha256": sha256_file(canonical_path),
            "checkpoint": checkpoint_path.name,
            "cells": EXPECTED_CELLS,
            "tokens": EXPECTED_TOKENS,
            "dimensions": EXPECTED_DIMENSIONS,
            "equivalence_batch_size": args.batch_size,
        },
        "array_sha256": {
            "input_ids": array_sha256(input_ids),
            "lengths": array_sha256(lengths),
            "cell_ids": hashlib.sha256("\n".join(cell_ids.tolist()).encode("utf-8")).hexdigest(),
            "full_embeddings": array_sha256(full_embeddings),
            "encoder_embeddings": array_sha256(encoder_embeddings),
            "canonical_embeddings": array_sha256(canonical_embeddings),
        },
        "runtime_seconds": {
            "full_masked_language_model": full_seconds,
            "encoder_only": encoder_seconds,
        },
        "checks": checks,
        "maximum_absolute_difference": exact_forward_differences,
        "canonical_reference_maximum_absolute_difference": canonical_reference_differences,
        "macro_metrics": {
            "full": full_macro,
            "encoder": encoder_macro,
            "canonical": canonical_macro,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "checks": checks,
        "maximum_absolute_difference": exact_forward_differences,
        "canonical_reference_maximum_absolute_difference": canonical_reference_differences,
    }, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
