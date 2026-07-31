import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "trace-archaic-introgression-2026"


class TraceArchaicEvidenceTests(unittest.TestCase):
    def read_json(self, filename):
        return json.loads((EVIDENCE / filename).read_text(encoding="utf-8"))

    def test_case_remains_computational_and_research_only(self):
        disposition = self.read_json("disposition.v0.1.json")
        self.assertEqual(
            disposition["primary_status"],
            "KAIROS_PARTIAL_COMPUTATIONAL_INFERENCE",
        )
        self.assertIn("NO_DIRECT_ARCHAIC_GENOME", disposition["secondary_statuses"])
        self.assertFalse(disposition["authority"]["experiment_authorization"])
        self.assertFalse(disposition["authority"]["clinical_authorization"])
        self.assertFalse(disposition["authority"]["ancestry_identity_authorization"])

    def test_direct_observation_and_adaptive_overclaims_are_rejected(self):
        claims = self.read_json("claim-map.v0.1.json")["claims"]
        status = {claim["id"]: claim["status"] for claim in claims}
        self.assertEqual(status["C7"], "REJECTED_DIRECT_OBSERVATION_CLAIM")
        self.assertEqual(status["C8"], "UNRESOLVED_TAXONOMIC_IDENTITY")
        self.assertEqual(status["C9"], "REJECTED_UNIVERSAL_SEGMENT_CLAIM")
        self.assertEqual(status["C10"], "REJECTED_CAUSAL_ADAPTATION_OVERCLAIM")
        self.assertEqual(status["C12"], "NOT_ESTABLISHED_UNIQUE_IDENTIFICATION")

    def test_phase_domain_does_not_unlock_candidate_window(self):
        phase = self.read_json("phase-compatibility.v0.1.json")
        self.assertEqual(
            phase["assessment"]["status"],
            "KAIROS_EXTERNAL_METHOD_CASE_NO_CELLULAR_PHASE",
        )
        self.assertFalse(phase["assessment"]["candidate_window_unlocked"])
        self.assertFalse(phase["phase_conditioned_preregistration"]["unlocked"])
        self.assertFalse(phase["authority"]["candidate_window_authorization"])

    def test_reproduction_remains_pending_and_code_is_pinned(self):
        contract = self.read_json("reproducibility-contract.v0.1.json")
        self.assertEqual(contract["status"], "REPRODUCTION_PENDING")
        self.assertEqual(len(contract["pinned_sources"]["trace_commit"]), 40)
        self.assertEqual(len(contract["pinned_sources"]["trace_paper_commit"]), 40)
        self.assertFalse(
            contract["authority"]["independent_replication_claim_authorized"]
        )

    def test_source_manifest_does_not_claim_direct_unknown_genome(self):
        manifest = self.read_json("source-manifest.v0.1.json")
        boundary = manifest["availability_boundary"]
        self.assertFalse(boundary["direct_unknown_archaic_genome"])
        self.assertFalse(boundary["direct_unknown_archaic_fossil_assignment"])
        self.assertEqual(boundary["full_independent_reproduction"], "PENDING")


if __name__ == "__main__":
    unittest.main()
