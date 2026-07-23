#!/usr/bin/env python3
"""Generate a deterministic metadata-only Model Evidence Passport demo.

No biological model is executed. The script proves identity, hashing, runtime,
transformation, uncertainty, and claim-boundary contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-artifact", required=True)
    parser.add_argument("--passport", required=True)
    parser.add_argument("--created-at", default="2026-07-23T12:00:00Z")
    parser.add_argument("--code-revision", default="demo-fixed-revision")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output_artifact)
    passport_path = Path(args.passport)

    input_raw = input_path.read_bytes()
    manifest = json.loads(input_raw.decode("utf-8"))
    input_sha = sha256_bytes(input_raw)

    output_record = {
        "schema_version": "0.2.0",
        "artifact_type": "metadata_only_demo_output",
        "dataset_id": manifest["dataset_id"],
        "registry_id": "nvidia-geneformer-v2-104m",
        "model_inference_executed": False,
        "embedding_generated": False,
        "input_sha256": input_sha,
        "result": "CONTRACT_TRACEABILITY_DEMONSTRATED",
        "scientific_interpretation": "none"
    }
    output_raw = canonical_bytes(output_record)
    output_sha = sha256_bytes(output_raw)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(output_raw)

    passport = {
        "schema_version": "0.2.0",
        "passport_id": f"MEP-DEMO-{input_sha[:12]}",
        "run_identity": {
            "run_id": f"metadata-demo-{input_sha[:12]}",
            "created_at": args.created_at,
            "code_revision": args.code_revision,
            "execution_mode": "metadata_only_no_model_inference"
        },
        "model_identity": {
            "provider": "NVIDIA",
            "registry_id": "nvidia-geneformer-v2-104m",
            "model_family": "Geneformer",
            "checkpoint_or_version": "Geneformer-V2-104M",
            "runtime_or_container": "not_started; governance demo only",
            "source_url": "https://docs.nvidia.com/bionemo-framework/latest/main/recipes/models/geneformer/geneformer/index.html"
        },
        "data_identity": {
            "dataset_id": manifest["dataset_id"],
            "input_artifact": input_path.as_posix(),
            "input_sha256": input_sha,
            "output_artifact": output_path.as_posix(),
            "output_sha256": output_sha
        },
        "execution": {
            "parameters": {
                "model_inference": False,
                "purpose": "governance contract demonstration"
            },
            "random_seeds": [0],
            "hardware": {
                "accelerator": "none",
                "machine": platform.machine()
            },
            "software": {
                "python": platform.python_version(),
                "generator": "generate_model_evidence_passport_demo.py"
            },
            "status": "not_executed"
        },
        "transformations": [
            {
                "name": "AnnData to rank-ordered gene tokens",
                "version": "not_started",
                "parameters": {},
                "status": "not_applied"
            }
        ],
        "compatibility_verdict": "ACCEPT_WITH_LIMITS",
        "uncertainty": {
            "domain_shift_risks": [
                "Synthetic manifest contains no expression values and cannot establish model performance.",
                "Cell context and benchmark validity require a real frozen dataset."
            ],
            "training_overlap_status": "unknown",
            "limitations": [
                "No model inference was executed.",
                "No biological, predictive, causal, tissue, clinical, or therapeutic conclusion is supported."
            ]
        },
        "claim_boundary": {
            "evidence_contribution": "traceability_contract_only",
            "causal": "blocked",
            "clinical_therapeutic": "blocked"
        },
        "safety_status": {
            "physical_biology_authorized": False,
            "clinical_use_authorized": False
        }
    }

    passport_path.parent.mkdir(parents=True, exist_ok=True)
    passport_path.write_bytes(canonical_bytes(passport))
    print(json.dumps({
        "passport": passport_path.as_posix(),
        "input_sha256": input_sha,
        "output_sha256": output_sha,
        "model_inference_executed": False
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
