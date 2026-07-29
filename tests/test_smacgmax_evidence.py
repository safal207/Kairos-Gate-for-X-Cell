import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "smacgmax-2026"


class SmacgmaxEvidenceTests(unittest.TestCase):
    def read_json(self, filename):
        return json.loads((EVIDENCE / filename).read_text(encoding="utf-8"))

    def test_phase_case_remains_research_only(self):
        phase = self.read_json("phase-compatibility.v0.1.json")
        self.assertEqual(
            phase["assessment"]["status"],
            "KAIROS_PARTIAL_NO_PREINTERVENTION_PHASE",
        )
        self.assertFalse(phase["phase_conditioned_preregistration"]["unlocked"])
        self.assertFalse(phase["authority"]["experiment_authorization"])

    def test_overclaims_are_rejected(self):
        claims = self.read_json("claim-map.v0.1.json")["claims"]
        status = {claim["id"]: claim["status"] for claim in claims}
        self.assertEqual(status["C6"], "REJECTED_PRIORITY_CLAIM")
        self.assertEqual(status["C7"], "REJECTED_OVERCLAIM")


if __name__ == "__main__":
    unittest.main()
