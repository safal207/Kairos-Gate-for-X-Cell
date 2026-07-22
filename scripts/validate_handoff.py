"""Validate a TIP-to-Kairos handoff as a research-only interoperability record."""

from __future__ import annotations

import argparse
from pathlib import Path

from kairos_gate import ValidationError, validate_handoff_path


def main() -> int:
    """Validate one handoff file and print the authority boundary."""
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff", type=Path)
    args = parser.parse_args()
    try:
        record = validate_handoff_path(args.handoff)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"FAIL {args.handoff}: {exc}")
        return 1
    print(
        f"RESEARCH_ONLY {args.handoff}: schema={record['schema']}; "
        "NOT BIOLOGICAL EXECUTION AUTHORIZATION"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
