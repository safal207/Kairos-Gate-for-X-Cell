#!/usr/bin/env python3
"""Regression checks for semantic-subprocess and resource handling."""

from __future__ import annotations

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import validate_bioevidence_contract as gateway


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


def require_main_block(contract: str, record: Path, needle: str) -> None:
    """Require main() to emit BLOCK without traceback for a broken resource."""
    output = io.StringIO()
    with redirect_stdout(output):
        code = gateway.main(["validate_bioevidence_contract.py", contract, str(record)])
    text = output.getvalue()
    assert code == 1, (code, text)
    assert text.startswith(f"BLOCK {contract}\n"), text
    assert needle in text, text
    assert "Traceback" not in text, text


def main() -> int:
    """Prove exit code and missing resources cannot unlock acceptance."""
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        record = (directory / "record.json").resolve()
        record.write_text("{}\n", encoding="utf-8")

        valid = write_script(
            directory,
            "valid.py",
            "import sys\nprint(f'ACCEPT {sys.argv[1]}')\n",
        )
        assert gateway.validate_semantics(record, valid) == []

        silent_zero = write_script(directory, "silent_zero.py", "pass\n")
        require_error(
            gateway.validate_semantics(record, silent_zero),
            "without exactly one matching ACCEPT verdict",
        )

        block_zero = write_script(
            directory,
            "block_zero.py",
            "import sys\nprint(f'BLOCK {sys.argv[1]}')\n",
        )
        errors = gateway.validate_semantics(record, block_zero)
        require_error(errors, "without exactly one matching ACCEPT verdict")
        require_error(errors, "emitted BLOCK with a zero exit status")

        wrong_path = write_script(
            directory,
            "wrong_path.py",
            "print('ACCEPT /wrong/record.json')\n",
        )
        require_error(
            gateway.validate_semantics(record, wrong_path),
            "without exactly one matching ACCEPT verdict",
        )

        duplicate_accept = write_script(
            directory,
            "duplicate_accept.py",
            "import sys\nprint(f'ACCEPT {sys.argv[1]}')\nprint(f'ACCEPT {sys.argv[1]}')\n",
        )
        require_error(
            gateway.validate_semantics(record, duplicate_accept),
            "without exactly one matching ACCEPT verdict",
        )

        traceback = write_script(
            directory,
            "traceback.py",
            "raise RuntimeError('synthetic semantic failure')\n",
        )
        require_error(
            gateway.validate_semantics(record, traceback),
            "unexpected exception",
        )

        bounded_failure = write_script(
            directory,
            "bounded_failure.py",
            "import sys\nprint(f'BLOCK {sys.argv[1]}')\nprint('  - synthetic bounded failure')\nraise SystemExit(1)\n",
        )
        require_error(
            gateway.validate_semantics(record, bounded_failure),
            "synthetic bounded failure",
        )

        missing_schema = directory / "missing-schema.json"
        missing_validator = directory / "missing-validator.py"
        minimal_schema = directory / "minimal-schema.json"
        minimal_schema.write_text('{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object"}\n', encoding="utf-8")

        gateway.CONTRACTS["missing-schema-test"] = (str(missing_schema), str(valid))
        try:
            require_main_block("missing-schema-test", record, "cannot read contract schema")
        finally:
            gateway.CONTRACTS.pop("missing-schema-test", None)

        gateway.CONTRACTS["missing-validator-test"] = (
            str(minimal_schema),
            str(missing_validator),
        )
        try:
            require_main_block("missing-validator-test", record, "cannot read contract schema or semantic validator")
        finally:
            gateway.CONTRACTS.pop("missing-validator-test", None)

    print("ACCEPT schema-gateway subprocess boundary")
    print("  exit_code_alone_is_authority=false")
    print("  exact_accept_path_required=true")
    print("  zero_exit_block_rejected=true")
    print("  missing_contract_resources_block=true")
    print("  traceback_leakage=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
