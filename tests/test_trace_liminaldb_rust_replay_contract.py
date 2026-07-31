from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUST = ROOT / "tools/liminaldb_bridge/trace_ecosystem_replay.rs"
DOC = ROOT / "docs/TRACE_LIMINALDB_RUST_REPLAY.md"


class TraceLiminalDbRustReplayContractTests(unittest.TestCase):
    def test_rust_bridge_pins_exact_liminaldb_commit(self) -> None:
        text = RUST.read_text(encoding="utf-8")
        self.assertIn("b8cf0528187c6d3fac3b28dbb9e90f1a2fb740e7", text)
        self.assertIn("DOCUMENTARY_PROJECTION_NOT_RUST_REPLAY", text)
        self.assertIn("RUST_REPLAY_RECOVERED_REPORT_ONLY", text)

    def test_report_only_boundaries_are_executable(self) -> None:
        text = RUST.read_text(encoding="utf-8")
        self.assertIn("side_effect_committed: Some(false)", text)
        self.assertIn("adds_scientific_verdict: false", text)
        self.assertIn("ContinuityPosture::ReportOnly", text)
        self.assertNotIn("ContinueSideEffect", text)
        self.assertNotIn("RetrySideEffect", text)

    def test_documentation_does_not_overstate_replay(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("temporary LiminalDB WAL", text)
        self.assertIn("does not prove the TRACE scientific interpretation", text)


if __name__ == "__main__":
    unittest.main()
