# External Biology Review Request — BioEvidence OS v0.1

## Supersession notice

This review packet supersedes the earlier packet tied to PR #23 head `936a58f91aef5fd6642770ac8930e9ab7b5f4bd5`.

The correction does not change the observed GSE94383 rho. It lowers the evidence interpretation because the independent biological unit and ID-prefix semantics for the analysed cells remain unresolved.

## Exact review-target binding

This committed packet deliberately does not name the commit that contains itself; embedding that value would create a self-referential stale-SHA loop after every packet edit.

The authoritative review target is instead the exact `head_sha` recorded by the latest successful, same-head pair of generated receipts for draft PR #46:

```text
workflow: BioEvidence P0 Contract Integrity
artifact: bioevidence-p0-contract-integrity-<head_sha>
receipt field: head_sha == checked_out_sha

workflow: BioEvidence P0 Scientific Inference Boundary
artifact: gse94383-p0-science-<head_sha>
receipt field: head_sha == checked_out_sha
```

Both receipts must name the same 40-character SHA. The correction email or review request must include that SHA plus both artifact IDs and SHA-256 digests. A verdict is not current unless the reviewer repeats the same exact SHA in the response.

```text
review_target_policy: GENERATED_EXACT_HEAD_RECEIPT_REQUIRED
pull_request: 46
branch: agent/p0-schema-science-hardening-v0-1
merge_authorization: false
```

Any later commit supersedes the prior receipts and requires a new same-head receipt pair and reviewer notice.

## Review purpose

Please review whether the biological interpretations and boundaries in the controlled P0-hardening successor PR are scientifically defensible for the GSE141064 / GSE94383 case.

This is a computational and documentary review. No physical biological work is requested or authorized.

## Primary review questions

1. Is the distinction between biological and technical units stated correctly?
2. Is it appropriate to treat plate, library, sequencing run, read, image frame, cell count, and unresolved ID prefixes as non-biological replication here?
3. Is GSE94383 correctly limited to descriptive pathway context while its effective biological N is unresolved?
4. Is it correct to keep replication and conceptual triangulation on `HOLD` rather than promoting cell-level intervals or permutation scores?
5. Are the shared-state, direct-effect, marker-only, technical-confounding, small-effect, and instability hypotheses biologically plausible and sufficiently distinct?
6. Does the current interpretation of `Nfkbia` avoid overstating a unique driver role?
7. Are important biological alternatives or context dependencies missing?
8. Are the proposed partner-laboratory evidence requirements biologically coherent without becoming an operational protocol?
9. Are any tissue, clinical, therapeutic, or translational implications stated too strongly?

## Current bounded conclusions

- GSE141064 exploratory association: supported with limits;
- GSE94383 within-table descriptive positive direction: observed;
- GSE94383 independent biological unit and effective biological N: unresolved;
- GSE94383 replication or inferential conceptual triangulation: `HOLD`;
- direct temporal replication: absent;
- direct causal effect: not identified;
- tissue, clinical, and therapeutic claims: blocked;
- partner evidence package: ready for scientific discussion only;
- physical execution: not authorized.

## Requested response format

```text
Exact head SHA reviewed:
Contract-integrity artifact ID and SHA-256:
Scientific-inference artifact ID and SHA-256:
Reviewer expertise:
Conflict of interest / independence statement:
Overall verdict: ACCEPT / ACCEPT_WITH_CHANGES / HOLD / BLOCK
P0 biological errors:
P1 required corrections:
P2 improvements:
Experimental-unit concerns:
Missing biological alternatives:
Claims that are too strong:
Claims that are too weak or unnecessarily blocked:
Partner-handoff concerns:
Recommended next evidence action:
```

## Evidence entry points

- `README.md`
- `docs/architecture.md`
- `RELEASE_NOTES_v0.1.md`
- `scripts/validate_bioevidence_contract.py`
- `scripts/analyze_gse94383_conceptual_replication.py`
- `scripts/check_gse94383_inference_boundary.py`
- `scripts/check_gse94383_claim_drift.py`
- `examples/gse141064.experimental-unit-audit.json`
- `examples/gse141064.provenance-confounder-graph.json`
- `examples/gse141064.independent-replication-search.json`
- `examples/gse141064.nfkbia-causal-hypotheses.json`
- `examples/gse141064.temporal-replication-gate.json`
- `examples/gse141064.nfkbia-partner-lab-handoff.json`
- `reports/gse94383-conceptual-replication-2026-07-23.md`
- `reports/gse141064-nfkbia-causal-ranking-2026-07-23.md`
- `reports/gse141064-direct-temporal-replication-gap-2026-07-23.md`

## Non-claims

This project does not claim that `Nfkbia` is a validated therapeutic target, that causality or independent replication has been established, or that any biological intervention should be performed.
