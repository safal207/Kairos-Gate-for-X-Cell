"""Command-line interface for validating Kairos Gate transition records."""

from __future__ import annotations

import argparse
from pathlib import Path

from .validator import ValidationError, validate_path


def main() -> int:
    """Validate one transition record and print a research-only classification."""
    parser = argparse.ArgumentParser(description="Validate a Kairos Gate transition record")
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

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


if __name__ == "__main__":
    raise SystemExit(main())
