#!/usr/bin/env python3
"""Regression checks for semantic-subprocess verdict handling in the gateway."""

from __future__ import annotations

import tempfile
from pathlib import Path

from validate_bioevidence_contract import validate_semantics


def write_script(directory: Path, name: str, body: str) -> Path:
    """Write one temporary Python semantic-validator double."""
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def require_error(errors: list[str], needle: str) -> None:
    """Require a bounded error containing the expected diagnostic."""
    assert errors, "expected fail-closed errors"
    assert any(needle in error for error in errors), errors
    assert not any("Traceback" in error for error in errors), errors


def main() -> int:
    """Prove exit code alone cannot unlock semantic acceptance."""
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        record = (directory / "record.json").resolve()
        record.write_text("{}\n", encoding="utf-8")

        valid = write_script(
            directory,
            "valid.py",
            "import sys\nprint(f'ACCEPT {sys.argv[1]}')\n",
        )
        assert validate_semantics(record, valid) == []

        silent_zero = write_script(directory, "silent_zero.py", "pass\n")
        require_error(
            validate_semantics(record, silent_zero),
            "without exactly one matching ACCEPT verdict",
        )

        block_zero = write_script(
            directory,
            "block_zero.py",
            "import sys\nprint(f'BLOCK {sys.argv[1]}')\n",
        )
        errors = validate_semantics(record, block_zero)
        require_error(errors, "without exactly one matching ACCEPT verdict")
        require_error(errors, "emitted BLOCK with a zero exit status")

        wrong_path = write_script(
            directory,
            "wrong_path.py",
            "print('ACCEPT /wrong/record.json')\n",
        )
        require_error(
            validate_semantics(record, wrong_path),
            "without exactly one matching ACCEPT verdict",
        )

        duplicate_accept = write_script(
            directory,
            "duplicate_accept.py",
            "import sys\nprint(f'ACCEPT {sys.argv[1]}')\nprint(f'ACCEPT {sys.argv[1]}')\n",
        )
        require_error(
            validate_semantics(record, duplicate_accept),
            "without exactly one matching ACCEPT verdict",
        )

        traceback = write_script(
            directory,
            "traceback.py",
            "raise RuntimeError('synthetic semantic failure')\n",
        )
        require_error(
            validate_semantics(record, traceback),
            "unexpected exception",
        )

        bounded_failure = write_script(
            directory,
            "bounded_failure.py",
            "import sys\nprint(f'BLOCK {sys.argv[1]}')\nprint('  - synthetic bounded failure')\nraise SystemExit(1)\n",
        )
        require_error(
            validate_semantics(record, bounded_failure),
            "synthetic bounded failure",
        )

    print("ACCEPT schema-gateway subprocess boundary")
    print("  exit_code_alone_is_authority=false")
    print("  exact_accept_path_required=true")
    print("  zero_exit_block_rejected=true")
    print("  traceback_leakage=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
