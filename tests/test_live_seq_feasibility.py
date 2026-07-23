from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_live_seq_gse141064.py"
METADATA = ROOT / "tests" / "fixtures" / "live-seq-meta-tiny.csv"
COUNTS = ROOT / "tests" / "fixtures" / "live-seq-count-tiny.csv"


class LiveSeqFeasibilityTests(unittest.TestCase):
    """Verify the open-data auditor fails closed before any model is fitted."""

    def _run(
        self,
        metadata: Path = METADATA,
        counts: Path = COUNTS,
        reuse_status: str = "unclear",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(metadata),
                str(counts),
                "--data-reuse-status",
                reuse_status,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_grouped_repeat_metadata(self, directory: Path) -> Path:
        """Keep pair-1 inside one Date|Probe group while preserving two groups."""
        with METADATA.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]

        source_pair = next(row for row in rows if row["sample_ID"] == "sampleC")
        target_pair = next(row for row in rows if row["sample_ID"] == "sampleD")
        target_pair["Date"] = source_pair["Date"]
        target_pair["Probe"] = source_pair["Probe"]

        metadata_path = directory / "grouped-repeat-metadata.csv"
        with metadata_path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return metadata_path

    def test_clear_linkage_is_ready_for_preregistration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata_path = self._write_grouped_repeat_metadata(Path(directory))
            completed = self._run(metadata=metadata_path, reuse_status="clear")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "READY_FOR_PREREGISTRATION")
        self.assertEqual(result["authority"]["classification"], "RESEARCH_ONLY")
        self.assertFalse(result["authority"]["experiment_authorization"])
        self.assertFalse(result["cohort"]["selection_uses_response_label"])
        self.assertEqual(result["cohort"]["selected_recorded_cells"], 4)
        self.assertEqual(result["cohort"]["response_complete_cells"], 4)
        self.assertEqual(result["cohort"]["missing_response_sample_ids"], [])
        self.assertEqual(len(result["cohort"]["replicate_groups"]), 2)
        self.assertEqual(result["cohort"]["repeated_measurement_rows"], 2)
        self.assertEqual(
            result["cohort"]["cross_group_repeated_measurement_ids"], []
        )
        self.assertTrue(result["integrity"]["full_id_sets_match"])

    def test_repeated_cell_pair_crossing_groups_blocks_readiness(self) -> None:
        completed = self._run(reuse_status="clear")
        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED_REPEATED_CELL_GROUP_LEAKAGE")
        self.assertEqual(
            result["cohort"]["cross_group_repeated_measurement_ids"], ["pair-1"]
        )
        self.assertEqual(
            result["cohort"]["repeated_measurement_groups"]["pair-1"],
            ["2020-01-01|probe1", "2020-01-02|probe2"],
        )
        self.assertIn("one split group", result["next_action"])

    def test_unclear_reuse_terms_block_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metadata_path = self._write_grouped_repeat_metadata(Path(directory))
            completed = self._run(metadata=metadata_path)

        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED_LICENSE_UNCLEAR")
        self.assertIn("reuse terms", result["next_action"])

    def test_missing_response_does_not_change_selected_cohort(self) -> None:
        with METADATA.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]

        target = next(row for row in rows if row["sample_ID"] == "sampleD")
        target["mCherry.log.slope"] = ""

        with tempfile.TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "metadata.csv"
            with metadata_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            completed = self._run(metadata=metadata_path, reuse_status="clear")

        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED_MISSING_RESPONSE_LABELS")
        self.assertFalse(result["cohort"]["selection_uses_response_label"])
        self.assertEqual(result["cohort"]["selected_recorded_cells"], 4)
        self.assertEqual(result["cohort"]["response_complete_cells"], 3)
        self.assertEqual(result["cohort"]["missing_response_sample_ids"], ["sampleD"])

    def test_missing_selected_count_column_blocks_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            count_path = Path(directory) / "counts.csv"
            count_path.write_text(
                "gene_id,sampleA,sampleB,sampleC,sampleE\n"
                "ENSMUSG00000000001,1,2,3,5\n",
                encoding="utf-8",
            )
            completed = self._run(counts=count_path, reuse_status="clear")

        self.assertEqual(completed.returncode, 2, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED_MISSING_CELL_LINKAGE")
        self.assertEqual(result["cohort"]["missing_selected_sample_ids"], ["sampleD"])

    def test_missing_required_metadata_column_is_machine_readable(self) -> None:
        with METADATA.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        fieldnames = [field for field in rows[0] if field != "mCherry.log.slope"]

        with tempfile.TemporaryDirectory() as directory:
            metadata_path = Path(directory) / "metadata.csv"
            with metadata_path.open("w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(target, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(
                    {field: row[field] for field in fieldnames} for row in rows
                )
            completed = self._run(metadata=metadata_path, reuse_status="clear")

        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "BLOCKED_DATA_INTEGRITY")
        self.assertIn("mCherry.log.slope", result["error"])
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
