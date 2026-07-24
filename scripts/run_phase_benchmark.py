"""Run the preregistered synthetic phase benchmark without external ML dependencies."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Hashable, Mapping, Sequence

DATASET_SCHEMA = "kairos.synthetic-phase-benchmark.v0.1"
RESULT_SCHEMA = "kairos.synthetic-phase-result.v0.1"


class BenchmarkError(ValueError):
    """Raised when the synthetic benchmark input or computation is invalid."""


def _reject_constant(value: str) -> None:
    """Reject non-standard JSON constants."""
    raise BenchmarkError(f"non-finite JSON constant: {value}")


def _require_finite(name: str, value: float) -> float:
    """Return a finite metric or fail closed before interpretation or serialization."""
    if not math.isfinite(value):
        raise BenchmarkError(f"{name} must be finite")
    return value


def _load(path: Path) -> Mapping[str, Any]:
    """Load and validate the minimal synthetic dataset contract."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            dataset = json.load(handle, parse_constant=_reject_constant)
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"unable to load dataset: {exc}") from exc

    if not isinstance(dataset, Mapping):
        raise BenchmarkError("dataset root must be an object")
    if dataset.get("schema") != DATASET_SCHEMA:
        raise BenchmarkError(f"unsupported dataset schema: {dataset.get('schema')}")
    if dataset.get("provenance_class") != "synthetic":
        raise BenchmarkError("v0.1 benchmark accepts synthetic fixtures only")
    for field in ("dataset_id", "version"):
        value = dataset.get(field)
        if not isinstance(value, str) or not value.strip():
            raise BenchmarkError(f"{field} must be a non-empty string")

    records = dataset.get("records")
    if not isinstance(records, list) or not records:
        raise BenchmarkError("records must be a non-empty list")

    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise BenchmarkError(f"record {index} must be an object")
        required = {"id", "split", "perturbation", "phase", "response"}
        if set(record) != required:
            raise BenchmarkError(f"record {index} must contain exactly {sorted(required)}")
        if not all(
            isinstance(record[field], str) and record[field]
            for field in required - {"response"}
        ):
            raise BenchmarkError(f"record {index} contains an invalid string field")
        if record["id"] in seen_ids:
            raise BenchmarkError(f"duplicate record id: {record['id']}")
        seen_ids.add(record["id"])
        if record["split"] not in {"train", "test"}:
            raise BenchmarkError(f"invalid split: {record['split']}")
        response = record["response"]
        if isinstance(response, bool) or not isinstance(response, (int, float)):
            raise BenchmarkError(f"record {index} response must be numeric")
        if not math.isfinite(float(response)):
            raise BenchmarkError(f"record {index} response must be finite")

    if not any(record["split"] == "train" for record in records):
        raise BenchmarkError("dataset has no training records")
    if not any(record["split"] == "test" for record in records):
        raise BenchmarkError("dataset has no test records")
    return dataset


def _means(
    records: Sequence[Mapping[str, Any]],
    key_fn: Callable[[Mapping[str, Any]], Hashable],
) -> dict[Hashable, float]:
    """Fit a deterministic group-mean estimator."""
    grouped: dict[Hashable, list[float]] = defaultdict(list)
    for record in records:
        grouped[key_fn(record)].append(float(record["response"]))

    means: dict[Hashable, float] = {}
    for key, values in grouped.items():
        mean = sum(values) / len(values)
        means[key] = _require_finite(f"fitted mean for group {key!r}", mean)
    return means


def _mse(
    test_records: Sequence[Mapping[str, Any]],
    model: Mapping[Hashable, float],
    key_fn: Callable[[Mapping[str, Any]], Hashable],
) -> float:
    """Calculate held-out mean squared error and fail on unseen or non-finite groups."""
    errors: list[float] = []
    for record in test_records:
        key = key_fn(record)
        if key not in model:
            raise BenchmarkError(f"test group absent from training data: {key}")
        error = _require_finite(
            f"prediction error for record {record['id']}",
            model[key] - float(record["response"]),
        )
        squared_error = _require_finite(
            f"squared error for record {record['id']}",
            error * error,
        )
        errors.append(squared_error)
    return _require_finite("mean squared error", sum(errors) / len(errors))


def run_benchmark(path: Path) -> dict[str, Any]:
    """Run baseline, phase-conditioned, ablation, and shuffle-control models."""
    dataset = _load(path)
    records = dataset["records"]
    train = [record for record in records if record["split"] == "train"]
    test = [record for record in records if record["split"] == "test"]

    phases = sorted({record["phase"] for record in train})
    if len(phases) < 2:
        raise BenchmarkError("phase shuffle requires at least two phases")
    shuffled_phase = {
        phase: phases[(index + 1) % len(phases)] for index, phase in enumerate(phases)
    }

    baseline = _means(train, lambda record: record["perturbation"])
    conditioned = _means(
        train, lambda record: (record["perturbation"], record["phase"])
    )
    shuffled = _means(
        train,
        lambda record: (record["perturbation"], shuffled_phase[record["phase"]]),
    )

    baseline_mse = _mse(test, baseline, lambda record: record["perturbation"])
    conditioned_mse = _mse(
        test, conditioned, lambda record: (record["perturbation"], record["phase"])
    )
    shuffled_mse = _mse(
        test, shuffled, lambda record: (record["perturbation"], record["phase"])
    )
    absolute_improvement = _require_finite(
        "absolute improvement", baseline_mse - conditioned_mse
    )

    if conditioned_mse < baseline_mse and shuffled_mse >= baseline_mse:
        interpretation = "SUPPORTED_SYNTHETIC_ONLY"
    elif conditioned_mse >= baseline_mse:
        interpretation = "UNSUPPORTED"
    else:
        interpretation = "CONTROL_FAILURE"

    return {
        "schema": RESULT_SCHEMA,
        "protocol_id": "kairos.cell-cycle-ablation.v0.1",
        "dataset_id": dataset["dataset_id"],
        "dataset_version": dataset["version"],
        "provenance_class": "synthetic",
        "authority": "RESEARCH_ONLY",
        "experiment_authorization": False,
        "metrics": {
            "baseline_mse": baseline_mse,
            "phase_conditioned_mse": conditioned_mse,
            "phase_ablation_mse": baseline_mse,
            "phase_shuffle_mse": shuffled_mse,
            "absolute_improvement": absolute_improvement,
        },
        "interpretation": interpretation,
        "limitations": [
            "This is a deterministic synthetic pipeline test, not biological evidence.",
            "The result does not establish causality, safety, or therapeutic efficacy.",
            "No wet-lab, animal, human, or clinical experiment is authorized.",
        ],
    }


def main() -> int:
    """Run the benchmark and print machine-readable JSON."""
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    try:
        result = run_benchmark(args.dataset)
        output = json.dumps(
            result,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    except (BenchmarkError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, allow_nan=False))
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
