from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kairos_gate.trace_evidence_bridge import (
    TraceEvidenceBridgeError,
    build_trace_ecosystem_receipt,
    validate_ecosystem_receipt,
    validate_trace_package,
)
from scripts import derive_trace_ecosystem_receipt as receipt_cli


class TraceEvidenceBridgeTests(unittest.TestCase):
    def _manifest(self):
        roles = [
            ("claim_map", "claim-map.v0.1.json", "1" * 40, "kairos.trace-archaic-claim-map.v0.1"),
            ("causal_transition_map", "causal-transition-map.v0.1.json", "2" * 40, "kairos.trace-archaic-causal-transition-map.v0.1"),
            ("disposition", "disposition.v0.1.json", "3" * 40, "kairos.trace-archaic-disposition.v0.1"),
            ("source_manifest", "source-manifest.v0.1.json", "4" * 40, "kairos.trace-archaic-source-manifest.v0.1"),
            ("reproducibility_contract", "reproducibility-contract.v0.1.json", "5" * 40, "kairos.trace-archaic-reproducibility-contract.v0.1"),
            ("phase_compatibility", "phase-compatibility.v0.1.json", "6" * 40, "kairos.trace-archaic-phase-compatibility.v0.1"),
        ]
        return {
            "schema": "kairos.pinned-evidence-package.v0.1",
            "package_id": "trace-test-package",
            "case_id": "trace-archaic-introgression-2026",
            "repository": "safal207/Kairos-Gate-for-X-Cell",
            "pull_request": 55,
            "commit": "a" * 40,
            "base_engine_pull_request": 57,
            "files": [
                {
                    "role": role,
                    "path": f"evidence/trace-archaic-introgression-2026/{name}",
                    "git_blob_sha": blob,
                    "expected_schema": schema,
                }
                for role, name, blob, schema in roles
            ],
            "authority": {
                "classification": "RESEARCH_ONLY",
                "experiment_authorization": False,
                "merge_authorization": False,
            },
        }

    def _package(self):
        generated = "2026-07-31T04:10:00Z"
        source_ids = [
            "science_article",
            "biorxiv_preprint",
            "berkeley_news_release",
            "trace_code",
            "trace_paper_pipelines",
        ]
        statuses = {
            "C1": "SUPPORTED_METHOD_DESCRIPTION",
            "C2": "SUPPORTED_BY_AUTHOR_VALIDATION",
            "C3": "SUPPORTED_MODEL_BASED_INFERENCE",
            "C4": "SUPPORTED_AS_AUTHOR_REPORTED_ESTIMATE",
            "C5": "SUPPORTED_MODEL_DEPENDENT_TIME_ESTIMATE",
            "C6": "SUPPORTED_MODEL_BASED_INFERENCE",
            "C7": "REJECTED_DIRECT_OBSERVATION_CLAIM",
            "C8": "UNRESOLVED_TAXONOMIC_IDENTITY",
            "C9": "REJECTED_UNIVERSAL_SEGMENT_CLAIM",
            "C10": "REJECTED_CAUSAL_ADAPTATION_OVERCLAIM",
            "C11": "NOT_ESTABLISHED",
            "C12": "NOT_ESTABLISHED_UNIQUE_IDENTIFICATION",
        }
        claims = []
        for claim_id, status in statuses.items():
            basis = ["science_article"]
            if claim_id in {"C1", "C2", "C3", "C6", "C11", "C12"}:
                basis.append("biorxiv_preprint")
            if claim_id in {"C1", "C11"}:
                basis.append("trace_code")
            if claim_id in {"C2", "C11", "C12"}:
                basis.append("trace_paper_pipelines")
            claims.append(
                {
                    "id": claim_id,
                    "claim": f"Bounded TRACE claim {claim_id}",
                    "source_basis": basis,
                    "status": status,
                    "verification_level": f"LEVEL_{claim_id}",
                }
            )
        nodes = [
            {"id": node_id, "type": "node", "label": node_id}
            for node_id in ["N1", "N3", "N5", "N9", "N10", "N11", "N12", "N13"]
        ]
        edges = [
            {"from": "N1", "to": "N3", "relation": "INPUT"},
            {"from": "N3", "to": "N5", "relation": "INFERENCE"},
            {"from": "N5", "to": "N9", "relation": "SUPPORTS"},
            {"from": "N5", "to": "N10", "relation": "SUPPORTS"},
            {"from": "N11", "to": "N13", "relation": "DOES_NOT_PROVE"},
            {"from": "N9", "to": "N12", "relation": "DOES_NOT_IDENTIFY"},
        ]
        authority = {"classification": "RESEARCH_ONLY", "experiment_authorization": False}
        return {
            "claim_map": {
                "schema": "kairos.trace-archaic-claim-map.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "claims": claims,
                "rules": ["do not overclaim"],
                "authority": authority,
            },
            "causal_transition_map": {
                "schema": "kairos.trace-archaic-causal-transition-map.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "map_type": "COMPUTATIONAL_INFERENCE_GRAPH_NOT_BIOLOGICAL_CAUSAL_PROOF",
                "nodes": nodes,
                "edges": edges,
                "alternative_explanations_and_sensitivities": [
                    "ARG topology error",
                    "phasing error",
                    "ancestral allele error",
                    "recombination map error",
                    "mutation rate assumptions",
                    "demographic model misspecification",
                    "incomplete lineage sorting",
                    "background selection",
                    "sample bias",
                    "threshold choices",
                ],
                "required_robustness_checks": ["independent rerun"],
                "forbidden_causal_shortcuts": [
                    "deep genealogy implies a directly observed ancient individual",
                    "time overlap implies a named species",
                    "annotation enrichment implies adaptive benefit",
                    "positive-control recovery implies unique identification",
                    "population-wide signal implies identical ancestry",
                ],
                "authority": authority,
            },
            "disposition": {
                "schema": "kairos.trace-archaic-disposition.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "primary_status": "KAIROS_PARTIAL_COMPUTATIONAL_INFERENCE",
                "secondary_statuses": [
                    "NO_DIRECT_ARCHAIC_GENOME",
                    "NO_DIRECT_FOSSIL_ASSIGNMENT",
                    "TAXONOMIC_IDENTITY_UNRESOLVED",
                    "FUNCTIONAL_ADAPTATION_UNRESOLVED",
                    "REPRODUCTION_PENDING",
                    "PROCESSED_DATA_PENDING",
                    "OUTSIDE_CELLULAR_PHASE_DOMAIN",
                ],
                "supported_summary": "bounded",
                "evidence_ceiling": "association",
                "confidence_by_layer": {},
                "permitted_language": ["Functional enrichment is suggestive and does not establish adaptive causality."],
                "forbidden_language": ["Scientists found two species."],
                "next_actions": ["reproduce"],
                "authority": authority,
            },
            "source_manifest": {
                "schema": "kairos.trace-archaic-source-manifest.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "primary_citation": {"doi": "10.1126/science.aef8874"},
                "retrieval": {"retrieved_at": generated},
                "code_pins": {
                    "trace_repository": {"audited_commit": "b" * 40},
                    "trace_paper_repository": {"audited_commit": "c" * 40},
                },
                "sources": [
                    {"id": source_id, "role": "source", "url": f"https://example.test/{source_id}"}
                    for source_id in source_ids
                ],
                "availability_boundary": {
                    "full_independent_reproduction": "PENDING",
                    "direct_unknown_archaic_genome": False,
                    "direct_unknown_archaic_fossil_assignment": False,
                },
                "authority": authority,
            },
            "reproducibility_contract": {
                "schema": "kairos.trace-archaic-reproducibility-contract.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "status": "REPRODUCTION_PENDING",
                "blocking_components": [
                    {"id": f"B{index}", "requirement": "required", "status": "NOT_AUDITED"}
                    for index in range(1, 8)
                ],
                "authority": authority,
            },
            "phase_compatibility": {
                "schema": "kairos.trace-archaic-phase-compatibility.v0.1",
                "case_id": "trace-archaic-introgression-2026",
                "generated_at": generated,
                "assessment": {
                    "status": "KAIROS_EXTERNAL_METHOD_CASE_NO_CELLULAR_PHASE",
                    "candidate_window_unlocked": False,
                },
                "authority": authority,
            },
        }

    def _receipts(self, manifest):
        return [
            {
                "id": item["role"],
                "path": item["path"],
                "git_blob_sha": item["git_blob_sha"],
                "sha256": (str(index + 1) * 64)[:64],
                "bytes": 100 + index,
            }
            for index, item in enumerate(manifest["files"])
        ]

    def test_builds_deterministic_bounded_receipt(self):
        manifest = self._manifest()
        package = self._package()
        receipts = self._receipts(manifest)
        first = build_trace_ecosystem_receipt(manifest, package, receipts)
        second = build_trace_ecosystem_receipt(manifest, package, receipts)
        self.assertEqual(first, second)
        self.assertEqual(first["kairos_analysis"]["verdict"], "ACCEPT_WITH_LIMITS")
        self.assertEqual(first["proofpath_projection"]["decision"], "HOLD")
        self.assertFalse(first["proofpath_projection"]["execution_allowed"])
        self.assertFalse(
            first["liminaldb_projection"]["projection"]["adds_scientific_verdict"]
        )
        validate_ecosystem_receipt(first)

    def test_preserves_adaptive_causal_gap(self):
        result = build_trace_ecosystem_receipt(
            self._manifest(), self._package(), self._receipts(self._manifest())
        )
        gap_ids = {
            item["transition_id"] for item in result["kairos_analysis"]["causal_gaps"]
        }
        self.assertIn("modern_to_functional_signal", gap_ids)

    def test_rejects_claim_status_promotion(self):
        package = self._package()
        package["claim_map"]["claims"][9]["status"] = "SUPPORTED_CAUSAL_ADAPTATION"
        with self.assertRaises(TraceEvidenceBridgeError):
            validate_trace_package(self._manifest(), package)

    def test_rejects_cross_case_substitution(self):
        package = self._package()
        package["disposition"]["case_id"] = "different-case"
        with self.assertRaises(TraceEvidenceBridgeError):
            validate_trace_package(self._manifest(), package)

    def test_manifest_requires_package_and_pull_request_identity(self):
        for key, value, message in (
            ("package_id", None, "package_id"),
            ("pull_request", "59", "positive integer"),
            ("pull_request", True, "positive integer"),
        ):
            with self.subTest(key=key, value=value):
                manifest = self._manifest()
                if value is None:
                    manifest.pop(key)
                else:
                    manifest[key] = value
                with self.assertRaisesRegex(TraceEvidenceBridgeError, message):
                    validate_trace_package(manifest, self._package())

    def test_nested_package_fields_fail_with_bridge_error(self):
        mutations = (
            lambda package: package["source_manifest"].pop("primary_citation"),
            lambda package: package["source_manifest"].pop("retrieval"),
            lambda package: package["source_manifest"]["code_pins"].pop(
                "trace_repository"
            ),
            lambda package: package["claim_map"]["claims"][0].pop(
                "verification_level"
            ),
            lambda package: package["disposition"].update(
                {"permitted_language": []}
            ),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                package = self._package()
                mutate(package)
                with self.assertRaises(TraceEvidenceBridgeError):
                    validate_trace_package(self._manifest(), package)

    def test_alternative_explanation_boundary_requires_ten_entries(self):
        package = self._package()
        package["causal_transition_map"][
            "alternative_explanations_and_sensitivities"
        ] = ["one"] * 9
        with self.assertRaisesRegex(TraceEvidenceBridgeError, "at least 10"):
            validate_trace_package(self._manifest(), package)

    def test_file_receipt_path_is_validated_before_comparison(self):
        receipts = self._receipts(self._manifest())
        receipts[0]["path"] = None
        with self.assertRaisesRegex(TraceEvidenceBridgeError, "claim_map.path"):
            build_trace_ecosystem_receipt(
                self._manifest(), self._package(), receipts
            )

    def test_receipt_requires_source_package_object(self):
        receipt = build_trace_ecosystem_receipt(
            self._manifest(), self._package(), self._receipts(self._manifest())
        )
        receipt.pop("source_package")
        receipt["receipt_id"] = self._recompute_receipt_id(receipt)
        with self.assertRaisesRegex(TraceEvidenceBridgeError, "source_package"):
            validate_ecosystem_receipt(receipt)

    def test_enforcement_failure_does_not_write_receipt(self):
        result = {
            "kairos_analysis": {
                "verdict": "BLOCK",
                "temporal_conflicts": [],
                "claim_firewall": [],
            },
            "proofpath_projection": {"decision": "HOLD"},
            "liminaldb_projection": {
                "projection": {"adds_scientific_verdict": False}
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            with (
                patch.object(receipt_cli, "_load_json", return_value=self._manifest()),
                patch.object(receipt_cli, "validate_pinned_manifest"),
                patch.object(receipt_cli, "_load_package", return_value=({}, [])),
                patch.object(
                    receipt_cli,
                    "build_trace_ecosystem_receipt",
                    return_value=result,
                ),
                patch.object(
                    sys,
                    "argv",
                    [
                        "derive_trace_ecosystem_receipt.py",
                        "--manifest",
                        "manifest.json",
                        "--source-dir",
                        "source",
                        "--output",
                        str(output),
                        "--enforce",
                    ],
                ),
            ):
                self.assertEqual(receipt_cli.main(), 2)
            self.assertFalse(output.exists())

    def test_rejects_blob_identity_substitution(self):
        manifest = self._manifest()
        receipts = self._receipts(manifest)
        receipts[0]["git_blob_sha"] = "f" * 40
        with self.assertRaises(TraceEvidenceBridgeError):
            build_trace_ecosystem_receipt(manifest, self._package(), receipts)

    def test_rejects_authority_escalation(self):
        package = self._package()
        package["disposition"]["authority"]["experiment_authorization"] = True
        with self.assertRaises(TraceEvidenceBridgeError):
            validate_trace_package(self._manifest(), package)

    def test_rejects_tampered_proofpath_chain(self):
        receipt = build_trace_ecosystem_receipt(
            self._manifest(), self._package(), self._receipts(self._manifest())
        )
        tampered = copy.deepcopy(receipt)
        tampered["proofpath_projection"]["audit_chain"][2]["kairos_verdict"] = "BLOCK"
        tampered["receipt_id"] = self._recompute_receipt_id(tampered)
        with self.assertRaises(TraceEvidenceBridgeError):
            validate_ecosystem_receipt(tampered)

    @staticmethod
    def _recompute_receipt_id(receipt):
        import hashlib
        import json

        body = {key: value for key, value in receipt.items() if key != "receipt_id"}
        encoded = json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


if __name__ == "__main__":
    unittest.main()
