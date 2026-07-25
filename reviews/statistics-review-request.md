# External Statistics and Bioinformatics Review Request — BioEvidence OS v0.1

## Supersession notice

This packet supersedes the earlier statistics request tied to PR #23 head `936a58f91aef5fd6642770ac8930e9ab7b5f4bd5`.

The numerical GSE94383 within-table association is unchanged. The evidence interpretation is corrected because cell-level resampling cannot estimate independent biological uncertainty while the biological unit and ID-prefix semantics remain unresolved.

## Exact review-target binding

This committed packet deliberately does not embed the commit that contains itself; doing so would create a self-referential stale-SHA loop whenever the packet changed.

The authoritative statistics-review target is the exact `head_sha` recorded by the latest successful, same-head pair of generated receipts for draft PR #46:

```text
workflow: BioEvidence P0 Contract Integrity
artifact: bioevidence-p0-contract-integrity-<head_sha>
receipt field: head_sha == checked_out_sha

workflow: BioEvidence P0 Scientific Inference Boundary
artifact: gse94383-p0-science-<head_sha>
receipt field: head_sha == checked_out_sha
```

Both receipts must name the same 40-character SHA. The correction email or review request must provide that SHA plus both artifact IDs and SHA-256 digests. A verdict is not current unless the reviewer repeats the same exact SHA.

```text
review_target_policy: GENERATED_EXACT_HEAD_RECEIPT_REQUIRED
pull_request: 46
branch: agent/p0-schema-science-hardening-v0-1
merge_authorization: false
```

Any later commit supersedes the prior receipts and requires a new same-head receipt pair and reviewer notice.

## Review purpose

Please review whether the statistical, computational, and reproducibility boundaries in the controlled P0-hardening successor are defensible for the GSE141064 / GSE94383 case.

This review concerns evidence quality and analysis validity. It does not authorize physical biological work.

## Primary review questions

1. Is the experimental-unit and pseudoreplication logic correct?
2. Are uncertainty statements tied to biological rather than cell-level independence?
3. Is it correct to report the GSE94383 rho as within-table description while denying inferential use of its cell bootstrap, cell permutation, and prefix exclusion?
4. Does the `HOLD` verdict follow appropriately from unresolved effective biological N?
5. Is leave-one-ID-prefix-out correctly treated as technical sensitivity rather than replication?
6. Does the schema-first gateway correctly prevent semantic acceptance of schema-invalid records?
7. Is the Supplementary Table 4 interpretation of nominal p-values, FDR, bootstrap FDR, and winner's-curse risk appropriate?
8. Does the causal ranking make clear that scores prioritize inquiry rather than identify effects?
9. Are the corrected cross-dataset-support scores and ranks internally consistent?
10. Are model-comparison requirements sufficient to distinguish `Nfkbia`-only, broader-state, technical, combined, and negative-control explanations?
11. Are missingness, exclusions, transformations, multiplicity, calibration, and external validation sufficiently constrained?
12. Are any claims supported by weaker evidence than the stated F0–F5 level implies?

## Current key results

### GSE94383 descriptive analysis

- matched cell observations: 823;
- effective independent biological N: unresolved;
- Spearman rho: 0.178;
- cell-level bootstrap interval: 0.110 to 0.243, descriptive only;
- cell-level permutation score: 0.0002, non-inferential;
- leave-one-prefix-out rho range: 0.153 to 0.200, technical sensitivity only;
- verdict: `DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED`;
- replication / conceptual triangulation status: `HOLD`.

### Original GSE141064 Supplementary Table 4

- genes tested: 362;
- `Nfkbia` LM p-value: 0.0002735;
- LM FDR: 0.0996;
- R²: 0.5977;
- coefficient: -0.1239;
- bootstrap p-value: 0.01198;
- bootstrap FDR: 0.6056;
- genes with bootstrap FDR at or below 0.20: zero.

## Requested response format

```text
Exact head SHA reviewed:
Contract-integrity artifact ID and SHA-256:
Scientific-inference artifact ID and SHA-256:
Reviewer expertise:
Conflict of interest / independence statement:
Overall verdict: ACCEPT / ACCEPT_WITH_CHANGES / HOLD / BLOCK
P0 validity errors:
P1 required corrections:
P2 improvements:
Experimental-unit concerns:
Multiplicity or winner's-curse concerns:
Bootstrap/permutation concerns:
Schema/semantic authority concerns:
Model-comparison concerns:
Reproducibility concerns:
Claims that exceed statistical support:
Recommended next analysis:
```

## Evidence entry points

- `scripts/validate_bioevidence_contract.py`
- `scripts/analyze_gse94383_conceptual_replication.py`
- `scripts/check_gse94383_inference_boundary.py`
- `scripts/check_gse94383_claim_drift.py`
- `scripts/probe_gse94383_tables.py`
- `scripts/probe_live_seq_supplementary_table4.py`
- `reports/gse94383-conceptual-replication-2026-07-23.json`
- `reports/gse94383-conceptual-replication-2026-07-23.md`
- `reports/gse141064-supplementary-table4-probe-2026-07-23.json`
- `examples/gse141064.experimental-unit-audit.json`
- `examples/gse141064.independent-replication-search.json`
- `examples/gse141064.nfkbia-causal-hypotheses.json`

## Non-claims

The current analyses do not establish independent biological replication, generalization, prediction, causal identification, clinical utility, or therapeutic relevance.
