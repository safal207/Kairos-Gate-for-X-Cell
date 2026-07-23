from __future__ import annotations

import csv
import json
import tempfile
import unittest
from importlib.resources import files
from pathlib import Path

from kairos_gate.__main__ import main
from kairos_gate.dataset_readiness import (
    BLOCKED_DATA_INTEGRITY,
    BLOCKED_EFFECTIVE_SAMPLE_SIZE,
    BLOCKED_LICENSE_UNCLEAR,
    BLOCKED_MISSING_CELL_LINKAGE,
    BLOCKED_MISSING_RESPONSE_LABELS,
    BLOCKED_REPEATED_CELL_GROUP_LEAKAGE,
    BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED,
    DatasetReadinessError,
    EXPLORATORY,
    READY,
    audit_dataset_paths,
    evaluate_contract,
    load_manifest,
    validate_result_record,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
LIVE_MANIFEST = FIXTURES / "dataset-readiness-live-seq.manifest.json"
LIVE_META = FIXTURES / "live-seq-meta-tiny.csv"
LIVE_COUNTS = FIXTURES / "live-seq-count-tiny.csv"
SYN_MANIFEST = FIXTURES / "dataset-readiness-synthetic.manifest.json"
SYN_META = FIXTURES / "dataset-readiness-synthetic-meta.csv"
SYN_COUNTS = FIXTURES / "dataset-readiness-synthetic-counts.csv"
READY_EXAMPLE = ROOT / "examples" / "dataset-readiness-ready.result.v0.1.json"
BLOCKED_EXAMPLE = ROOT / "examples" / "dataset-readiness-blocked.result.v0.1.json"


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
            import hashlib

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
            import hashlib

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
        self.assertTrue(result["authority"]["preregistration_gate_passed"])
        self.assertFalse(result["authority"]["model_fitting_authorized"])
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

    def _canonical_manifest(
        self, *, reuse_status: str = "clear", minimum_units: int = 2
    ) -> dict[str, object]:
        return {
            "dataset_id": "contract-test",
            "dataset_version": "0.1",
            "adapter": {"name": "tabular-v0.1"},
            "reuse_status": reuse_status,
            "minimum_independent_units": minimum_units,
        }

    def _canonical_contract(
        self, *, semantics: str = "verified"
    ) -> dict[str, object]:
        return {
            "metadata_path": "metadata.csv",
            "matrix_path": "matrix.csv",
            "metadata_ids": ["s1", "s2"],
            "matrix_ids": ["s1", "s2"],
            "records": [
                {
                    "sample_id": "s1",
                    "selected": True,
                    "response_available": True,
                    "independent_unit": "u1",
                    "repeated_identity": None,
                },
                {
                    "sample_id": "s2",
                    "selected": True,
                    "response_available": True,
                    "independent_unit": "u2",
                    "repeated_identity": None,
                },
            ],
            "replicate_semantics": semantics,
        }

    def _evaluate(
        self,
        contract: dict[str, object],
        manifest: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return evaluate_contract(
            contract,
            manifest or self._canonical_manifest(),
            input_digests={
                "metadata": "sha256:" + "a" * 64,
                "matrix": "sha256:" + "b" * 64,
            },
        )

    def test_empty_selected_cohort_is_data_integrity_block(self) -> None:
        contract = self._canonical_contract()
        for record in contract["records"]:
            record["selected"] = False
        result = self._evaluate(contract)
        self.assertEqual(result["status"], BLOCKED_DATA_INTEGRITY)

    def test_selected_identifier_missing_from_matrix_blocks_linkage(self) -> None:
        contract = self._canonical_contract()
        contract["matrix_ids"] = ["s1"]
        result = self._evaluate(contract)
        self.assertEqual(result["status"], BLOCKED_MISSING_CELL_LINKAGE)
        self.assertEqual(result["cohort"]["missing_selected_sample_ids"], ["s2"])

    def test_verified_contract_with_too_few_units_blocks(self) -> None:
        contract = self._canonical_contract()
        contract["records"][1]["independent_unit"] = "u1"
        result = self._evaluate(contract)
        self.assertEqual(result["status"], BLOCKED_EFFECTIVE_SAMPLE_SIZE)

    def test_unclear_reuse_blocks_verified_contract(self) -> None:
        result = self._evaluate(
            self._canonical_contract(),
            self._canonical_manifest(reuse_status="unclear"),
        )
        self.assertEqual(result["status"], BLOCKED_LICENSE_UNCLEAR)

    def test_technical_grouping_is_exploratory_only(self) -> None:
        result = self._evaluate(self._canonical_contract(semantics="technical_only"))
        self.assertEqual(result["status"], EXPLORATORY)
        self.assertFalse(result["authority"]["preregistration_gate_passed"])

    def test_non_finite_canonical_value_is_rejected(self) -> None:
        contract = self._canonical_contract()
        contract["records"][0]["response_available"] = float("nan")
        with self.assertRaises(DatasetReadinessError):
            self._evaluate(contract)

    def test_malformed_tabular_adapter_config_is_rejected_by_schema(self) -> None:
        manifest = json.loads(SYN_MANIFEST.read_text(encoding="utf-8"))
        del manifest["adapter"]["config"]["response_field"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(DatasetReadinessError):
                load_manifest(path)

    def test_packaged_readiness_schemas_match_public_mirrors(self) -> None:
        for name in (
            "dataset-manifest.schema.json",
            "dataset-readiness-result.schema.json",
        ):
            packaged = json.loads(
                files("kairos_gate.schemas").joinpath(name).read_text(encoding="utf-8")
            )
            public = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(packaged, public)

    def test_committed_ready_and_blocked_examples_validate(self) -> None:
        for path in (READY_EXAMPLE, BLOCKED_EXAMPLE):
            result = json.loads(path.read_text(encoding="utf-8"))
            validate_result_record(result)

    def test_result_schema_rejects_ready_without_gate_pass(self) -> None:
        result = json.loads(READY_EXAMPLE.read_text(encoding="utf-8"))
        result["authority"]["preregistration_gate_passed"] = False
        with self.assertRaises(DatasetReadinessError):
            validate_result_record(result)

    def test_duplicate_selected_ids_remain_machine_readable(self) -> None:
        contract = self._canonical_contract()
        contract["metadata_ids"] = ["s1", "s1"]
        contract["matrix_ids"] = ["s1", "s1"]
        contract["records"][1]["sample_id"] = "s1"
        result = self._evaluate(contract)
        self.assertEqual(result["status"], BLOCKED_DATA_INTEGRITY)
        self.assertFalse(result["integrity"]["selected_ids_unique"])
        self.assertEqual(result["cohort"]["selected_sample_ids"], ["s1", "s1"])

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
