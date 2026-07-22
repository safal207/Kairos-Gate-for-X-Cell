"""Build and enforce a compact exact-head Kairos CI evidence record."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / ".artifacts" / "kairos-validation.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _run(command: list[str]) -> dict[str, Any]:
    """Execute one bounded validation stage and capture its result."""
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def _git_head() -> str:
    """Return the checked-out Git commit SHA or an unavailable marker."""
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def _wheel_smoke() -> dict[str, Any]:
    """Build a wheel, install it outside the checkout, and run the packaged CLI."""
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        wheel_dir = temp / "wheel"
        target = temp / "target"
        wheel_dir.mkdir()
        target.mkdir()

        build = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                ".",
                "--no-deps",
                "--no-build-isolation",
                "-w",
                str(wheel_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        wheels = list(wheel_dir.glob("kairos_gate-*.whl"))
        if build.returncode != 0 or len(wheels) != 1:
            return {
                "command": ["pip", "wheel", "."],
                "status": "FAIL",
                "exit_code": build.returncode,
                "stdout": build.stdout[-8000:],
                "stderr": build.stderr[-8000:],
            }

        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--target",
                str(target),
                str(wheels[0]),
            ],
            cwd=temp,
            text=True,
            capture_output=True,
            check=False,
        )
        if install.returncode != 0:
            return {
                "command": ["pip", "install", "wheel"],
                "status": "FAIL",
                "exit_code": install.returncode,
                "stdout": install.stdout[-8000:],
                "stderr": install.stderr[-8000:],
            }

        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(target)
        smoke = subprocess.run(
            [
                sys.executable,
                "-m",
                "kairos_gate",
                str(ROOT / "examples" / "phase-conditioned-transition.json"),
            ],
            cwd=temp,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        passed = (
            smoke.returncode == 0
            and "classification=CANDIDATE_WINDOW" in smoke.stdout
            and "NOT EXPERIMENT AUTHORIZATION" in smoke.stdout
        )
        return {
            "command": ["wheel-install", "python -m kairos_gate"],
            "status": "PASS" if passed else "FAIL",
            "exit_code": smoke.returncode,
            "stdout": smoke.stdout[-8000:],
            "stderr": (build.stderr + install.stderr + smoke.stderr)[-8000:],
        }


def build_evidence() -> dict[str, Any]:
    """Run technical validation stages and write exact-head evidence."""
    requested = os.environ.get("KAIROS_EXACT_HEAD")
    checked_out = _git_head()
    exact_head_matches = (
        bool(requested)
        and bool(SHA_RE.fullmatch(requested))
        and bool(SHA_RE.fullmatch(checked_out))
        and requested.lower() == checked_out.lower()
    )

    stages = {
        "unit_tests": _run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        ),
        "canonical_example": _run(
            [sys.executable, "-m", "kairos_gate", "examples/phase-conditioned-transition.json"]
        ),
        "compile": _run(
            [sys.executable, "-m", "compileall", "-q", "kairos_gate", "tests", "scripts"]
        ),
        "installed_wheel": _wheel_smoke(),
    }

    all_stages_pass = all(stage["status"] == "PASS" for stage in stages.values())
    canonical_output = stages["canonical_example"]["stdout"]
    canonical_classification = (
        "CANDIDATE_WINDOW"
        if "classification=CANDIDATE_WINDOW" in canonical_output
        else None
    )

    evidence = {
        "schema": "kairos.ci-evidence.v0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_head_sha": requested,
        "checked_out_head_sha": checked_out,
        "exact_head_matches": exact_head_matches,
        "versions": {
            "software": "0.1.0",
            "transition_schema": "0.1.0",
            "protocol": "0.1.0",
            "dataset": "synthetic-demo-0.1",
            "model": "illustrative-0.0-demo",
        },
        "authority": {
            "classification": "RESEARCH_ONLY",
            "experiment_authorization": False,
            "clinical_authorization": False,
        },
        "canonical_classification": canonical_classification,
        "stages": stages,
        "verdict": (
            "TECHNICALLY_REPRODUCIBLE"
            if exact_head_matches and all_stages_pass and canonical_classification
            else "BLOCKED"
        ),
        "limitations": [
            "Technical CI evidence does not establish biological validity or causality.",
            "The canonical input is synthetic and illustrative.",
            "No wet-lab, animal, human, or clinical execution is authorized.",
        ],
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def enforce_evidence() -> int:
    """Fail closed unless stored evidence proves the expected technical state."""
    try:
        evidence = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Missing or malformed Kairos evidence: {exc}", file=sys.stderr)
        return 1

    checks = [
        evidence.get("verdict") == "TECHNICALLY_REPRODUCIBLE",
        evidence.get("exact_head_matches") is True,
        evidence.get("authority", {}).get("classification") == "RESEARCH_ONLY",
        evidence.get("authority", {}).get("experiment_authorization") is False,
        evidence.get("canonical_classification") == "CANDIDATE_WINDOW",
        evidence.get("stages", {}).get("installed_wheel", {}).get("status") == "PASS",
    ]
    if not all(checks):
        print(json.dumps(evidence, indent=2), file=sys.stderr)
        return 1

    print(
        "Kairos exact-head evidence accepted: TECHNICALLY_REPRODUCIBLE; "
        "RESEARCH_ONLY; NOT EXPERIMENT AUTHORIZATION"
    )
    return 0


def main() -> int:
    """Build or enforce the compact exact-head evidence artifact."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    if args.enforce:
        return enforce_evidence()

    evidence = build_evidence()
    print(
        f"Kairos evidence written: verdict={evidence['verdict']} "
        f"head={evidence['checked_out_head_sha']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
