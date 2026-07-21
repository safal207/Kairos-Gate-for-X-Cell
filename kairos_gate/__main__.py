from __future__ import annotations

import argparse
from pathlib import Path

from .validator import ValidationError, validate_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Kairos Gate transition record")
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

    try:
        record = validate_path(args.record)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"FAIL {args.record}: {exc}")
        return 1

    print(f"PASS {args.record}: {record['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
