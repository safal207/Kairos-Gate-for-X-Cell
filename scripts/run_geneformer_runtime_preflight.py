#!/usr/bin/env python3
"""Observe Geneformer runtime readiness without claiming model inference."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

MODEL_REPO = "ctheodoris/Geneformer"
MODEL_TARGET = "Geneformer-V1-10M"
REQUIRED_MODULES = ["torch", "transformers", "datasets", "anndata", "huggingface_hub"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def module_observation(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", None)
        return {"module": name, "imported": True, "version": str(version) if version is not None else None, "error": None}
    except Exception as exc:  # noqa: BLE001 - exact preflight error is evidence
        return {"module": name, "imported": False, "version": None, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--captured-at-ms", required=True, type=int)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    modules = [module_observation(name) for name in REQUIRED_MODULES]
    imports_ready = all(item["imported"] for item in modules)

    git_remote = run(["git", "ls-remote", "https://huggingface.co/ctheodoris/Geneformer", "refs/heads/main"])
    resolved_revision = None
    if git_remote["returncode"] == 0 and git_remote["stdout"]:
        resolved_revision = git_remote["stdout"].split()[0]

    hf_info: dict[str, Any] = {
        "resolved": False,
        "sha": resolved_revision,
        "target_directory_present": False,
        "sibling_count": None,
        "error": None,
    }
    if imports_ready:
        try:
            from huggingface_hub import HfApi

            info = HfApi().model_info(MODEL_REPO, revision=resolved_revision or "main", files_metadata=True)
            siblings = [s.rfilename for s in (info.siblings or [])]
            hf_info.update(
                {
                    "resolved": True,
                    "sha": info.sha,
                    "target_directory_present": any(path.startswith(f"{MODEL_TARGET}/") for path in siblings),
                    "sibling_count": len(siblings),
                    "error": None,
                }
            )
        except Exception as exc:  # noqa: BLE001
            hf_info["error"] = f"{type(exc).__name__}: {exc}"

    torch_observation: dict[str, Any] = {
        "imported": False,
        "cuda_available": False,
        "cuda_device_count": 0,
        "cuda_device_names": [],
        "error": None,
    }
    try:
        import torch

        torch_observation["imported"] = True
        torch_observation["cuda_available"] = bool(torch.cuda.is_available())
        torch_observation["cuda_device_count"] = int(torch.cuda.device_count())
        torch_observation["cuda_device_names"] = [
            torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
        ]
    except Exception as exc:  # noqa: BLE001
        torch_observation["error"] = f"{type(exc).__name__}: {exc}"

    nvidia_smi = shutil.which("nvidia-smi")
    nvidia_smi_result = run([nvidia_smi, "--query-gpu=name,memory.total", "--format=csv,noheader"]) if nvidia_smi else None

    disk = shutil.disk_usage(output.parent)
    checkpoint_visible = bool(hf_info["resolved"] and hf_info["target_directory_present"])
    preflight_ready = bool(imports_ready and checkpoint_visible)

    if preflight_ready and torch_observation["cuda_available"]:
        status = "PREFLIGHT_READY_GPU"
        execution_state = "OBSERVED_EXECUTED"
    elif preflight_ready:
        status = "PREFLIGHT_READY_CPU_ONLY"
        execution_state = "OBSERVED_EXECUTED"
    else:
        status = "PREFLIGHT_BLOCKED"
        execution_state = "OBSERVED_BLOCKED"

    result = {
        "schema_version": "0.1.0",
        "artifact_type": "geneformer_runtime_preflight",
        "source_revision": args.source_revision,
        "captured_at_ms": args.captured_at_ms,
        "action": "GENEFORMER_RUNTIME_PREFLIGHT",
        "status": status,
        "execution_state": execution_state,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "github_actions": os.environ.get("GITHUB_ACTIONS") == "true",
            "runner_os": os.environ.get("RUNNER_OS"),
            "runner_arch": os.environ.get("RUNNER_ARCH"),
            "disk_total_bytes": disk.total,
            "disk_free_bytes": disk.free,
        },
        "modules": modules,
        "torch": torch_observation,
        "nvidia_smi": {
            "path": nvidia_smi,
            "result": nvidia_smi_result,
        },
        "model_source": {
            "repository": MODEL_REPO,
            "requested_revision": "main",
            "git_ls_remote": git_remote,
            "resolved_revision": hf_info["sha"],
            "target_checkpoint": MODEL_TARGET,
            "target_directory_present": hf_info["target_directory_present"],
            "repository_metadata_resolved": hf_info["resolved"],
            "sibling_count": hf_info["sibling_count"],
            "metadata_error": hf_info["error"],
        },
        "runtime_boundary": {
            "source_reachable": resolved_revision is not None,
            "required_modules_imported": imports_ready,
            "checkpoint_metadata_visible": checkpoint_visible,
            "checkpoint_downloaded": False,
            "geneformer_package_installed_from_pinned_source": False,
            "model_inference_executed": False,
            "embedding_generated": False,
            "full_dataset_tokenized": False,
            "incremental_value_tested": False,
        },
        "claim_boundary": {
            "environment_readiness_only": True,
            "same_cell_prediction_established": False,
            "causal_effect_established": False,
            "clinical_utility_established": False,
            "therapeutic_relevance_established": False,
            "physical_execution_authorized": False,
        },
    }

    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    result["content_sha256"] = sha256_bytes(canonical)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "resolved_revision": hf_info["sha"], "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
