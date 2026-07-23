from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from kairos_gate.__main__ import main
from kairos_gate.dataset_readiness import (
    BLOCKED_MISSING_RESPONSE_LABELS,
    BLOCKED_REPEATED_CELL_GROUP_LEAKAGE,
    BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED,
    DatasetReadinessError,
    READY,
    audit_dataset_paths,
    load_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
LIVE_MANIFEST = FIXTURES / "dataset-readiness-live-seq.manifest.json"
LIVE_META = FIXTURES / "live-seq-meta-tiny.csv"
LIVE_COUNTS = FIXTURES / "live-seq-count-tiny.csv"
SYN_MANIFEST = FIXTURES / "dataset-readiness-synthetic.manifest.json"
SYN_META = FIXTURES / "dataset-readiness-synthetic-meta.csv"
SYN_COUNTS = FIXTURES / "dataset-readiness-synthetic-counts.csv"


class DatasetReadinessTests(unittest.TestCase):
    def test_live_seq_repeated_identity_crossing_groups_blocks(self) -> None:
        result = audit_dataset_paths(LIVE_MANIFEST, LIVE_META, LIVE_COUNTS)
        self.assertEqual(result["status"], BLOCKED_REPEATED_CELL_GROUP_LEAKAGE)
        self.assertEqual(
            result["replicates"]["cross_group_repeated_identity_ids"], ["pair-1"]
        )
        self.assertFalse(result["authority"]["model_fitting_authorized"])

    def test_live_seq_grouped_repeat_remains_semantics_blocked(self) -> None:
        with LIVE_META.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
        source_pair = next(row for row in rows if row["sample_ID"] == "sampleC")
        target_pair = next(row for row in rows if row["sample_ID"] == "sampleD")
        target_pair["Date"] = source_pair["Date"]
        target_pair["Probe"] = source_pair["Probe"]

        with tempfile.TemporaryDirectory() as directory:
            metadata = Path(directory) / "metadata.csv"
            with metadata.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            manifest = json.loads(LIVE_MANIFEST.read_text(encoding="utf-8"))
            manifest["sources"][0]["sha256"] = (
                "sha256:" + hashlib.sha256(metadata.read_bytes()).hexdigest()
            )
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = audit_dataset_paths(manifest_path, metadata, LIVE_COUNTS)

        self.assertEqual(result["status"], BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED)
        self.assertEqual(
            result["replicates"]["cross_group_repeated_identity_ids"], []
        )

    def test_missing_response_does_not_change_cohort(self) -> None:
        with LIVE_META.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
        next(row for row in rows if row["sample_ID"] == "sampleD")[
            "mCherry.log.slope"
        ] = ""

        with tempfile.TemporaryDirectory() as directory:
            metadata = Path(directory) / "metadata.csv"
            with metadata.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            manifest = json.loads(LIVE_MANIFEST.read_text(encoding="utf-8"))
            manifest["sources"][0]["sha256"] = (
                "sha256:" + hashlib.sha256(metadata.read_bytes()).hexdigest()
            )
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = audit_dataset_paths(manifest_path, metadata, LIVE_COUNTS)

        self.assertEqual(result["status"], BLOCKED_MISSING_RESPONSE_LABELS)
        self.assertEqual(result["cohort"]["selected_records"], 4)
        self.assertEqual(
            result["cohort"]["missing_response_sample_ids"], ["sampleD"]
        )

    def test_generic_tabular_adapter_can_reach_ready(self) -> None:
        result = audit_dataset_paths(SYN_MANIFEST, SYN_META, SYN_COUNTS)
        self.assertEqual(result["status"], READY)
        self.assertTrue(result["authority"]["model_fitting_authorized"])
        self.assertEqual(result["replicates"]["effective_independent_units"], 2)

    def test_mutable_github_source_is_rejected(self) -> None:
        manifest = json.loads(SYN_MANIFEST.read_text(encoding="utf-8"))
        manifest["sources"][0]["url"] = (
            "https://github.com/example/project/blob/main/metadata.csv"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(DatasetReadinessError):
                load_manifest(path)

    def test_cli_returns_blocked_exit_code_for_live_seq_fixture(self) -> None:
        code = main(
            [
                "audit-dataset",
                "--manifest",
                str(LIVE_MANIFEST),
                "--metadata",
                str(LIVE_META),
                "--matrix",
                str(LIVE_COUNTS),
            ]
        )
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
