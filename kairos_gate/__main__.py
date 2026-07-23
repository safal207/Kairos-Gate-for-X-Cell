"""Command-line interface for Kairos Gate research-only validators."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .dataset_readiness import DatasetReadinessError, audit_dataset_paths
from .evidence_planner import EvidencePlannerError, plan_evidence_path
from .validator import ValidationError, validate_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kairos Gate research-only validation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate-record", help="Validate one Kairos transition record"
    )
    validate.add_argument("record", type=Path)

    audit = subparsers.add_parser(
        "audit-dataset", help="Audit dataset readiness before any model fitting"
    )
    audit.add_argument("--manifest", type=Path, required=True)
    audit.add_argument("--metadata", type=Path, required=True)
    audit.add_argument("--matrix", type=Path, required=True)

    plan = subparsers.add_parser(
        "plan-next-evidence",
        help="Generate a bounded evidence request from a readiness result",
    )
    plan.add_argument("--result", type=Path, required=True)
    return parser


def _normalize_legacy_args(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    commands = {
        "validate-record",
        "audit-dataset",
        "plan-next-evidence",
        "-h",
        "--help",
    }
    if values and values[0] not in commands:
        return ["validate-record", *values]
    return values


def main(argv: Sequence[str] | None = None) -> int:
    """Run transition validation, dataset audit, or evidence planning."""
    parsed_argv = _normalize_legacy_args(sys.argv[1:] if argv is None else argv)
    args = _parser().parse_args(parsed_argv)

    if args.command == "validate-record":
        try:
            record = validate_path(args.record)
        except (OSError, ValueError, ValidationError) as exc:
            print(f"FAIL {args.record}: {exc}")
            return 1
        print(
            f"RESEARCH_ONLY {args.record}: classification={record['decision']}; "
            "NOT EXPERIMENT AUTHORIZATION"
        )
        return 0

    if args.command == "plan-next-evidence":
        try:
            plan = plan_evidence_path(args.result)
        except (OSError, ValueError, EvidencePlannerError) as exc:
            print(
                json.dumps(
                    {
                        "schema": "kairos.evidence-request-plan-error.v0.1",
                        "status": "BLOCKED_INVALID_READINESS_RESULT",
                        "authority": {
                            "classification": "RESEARCH_ONLY",
                            "readiness_verdict_changed": False,
                            "model_fitting_authorized": False,
                            "author_contact_authorized": False,
                            "experiment_authorization": False,
                            "clinical_authorization": False,
                            "merge_authorization": False,
                        },
                        "error": str(exc),
                    },
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
            )
            return 1
        print(json.dumps(plan, indent=2, sort_keys=True, allow_nan=False))
        return 0

    try:
        result = audit_dataset_paths(args.manifest, args.metadata, args.matrix)
    except (OSError, ValueError, DatasetReadinessError) as exc:
        print(
            json.dumps(
                {
                    "schema": "kairos.dataset-readiness-result.v0.1",
                    "status": "BLOCKED_DATA_INTEGRITY",
                    "authority": {
                        "classification": "RESEARCH_ONLY",
                        "model_fitting_authorized": False,
                        "experiment_authorization": False,
                        "clinical_authorization": False,
                        "merge_authorization": False,
                    },
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
        )
        return 1

    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "READY_FOR_PREREGISTRATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
