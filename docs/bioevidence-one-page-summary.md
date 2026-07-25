# BioEvidence OS — One-Page Scientific Summary

## The problem

AI can generate biological hypotheses much faster than researchers can verify whether the underlying evidence is independent, reproducible, temporally matched, and causally informative. In single-cell studies, hundreds of cells may come from only one or a few true biological units. Treating cells, plates, wells, libraries, or sequencing runs as independent replicates can create false certainty.

## The system

BioEvidence OS is a computational evidence-governance layer that audits:

- experimental units and pseudoreplication;
- provenance and confounders;
- independent replication;
- temporal and identity matching;
- competing causal explanations;
- claim boundaries;
- scientific handoff to authorized institutions.

It produces both machine-readable evidence records and human-readable reports. The system is fail-closed: unresolved load-bearing evidence prevents claim escalation.

## Reference case

### GSE141064

- 1012 metadata identifiers match 1012 count-matrix columns.
- 17 response-complete cells were recovered.
- Technical groups: plate1 = 7, plate3 = 4, plate4 = 6.
- All 17 share original prefix `exp8` and sequencing run `NXT0590`.
- Public evidence does not establish independent biological replicate semantics.

**Verdict:** `BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED`.

### GSE94383

- 823 identity-matched cells.
- Spearman rho = 0.178.
- Bootstrap 95% CI = 0.110–0.243.
- Stratified permutation p = 0.0002.

**Interpretation:** bounded conceptual NF-kB/Nfkbia pathway triangulation, not direct temporal replication of the GSE141064 target claim.

## Claim boundary

```text
Exploratory association: supported with limits
Out-of-sample prediction: not established
NFKBIA unique causal driver: not identified
Direct temporal replication: gap remains
Tissue, clinical, diagnostic, treatment, therapeutic claims: blocked
Physical biological execution: not authorized
```

## Why it matters

BioEvidence OS is intended to sit between AI hypothesis generation and expensive downstream research. It helps laboratories, funders, reviewers, and AI-for-science teams identify when a promising-looking result is actually limited by pseudoreplication, provenance gaps, temporal mismatch, winner's curse, or causal overreach.

## Current status

- Exact evidence head: `936a58f91aef5fd6642770ac8930e9ab7b5f4bd5`
- Exact-head CI: successful.
- Eleven major automated-review findings: fixed and regression-tested.
- Open inline review threads: 0.
- Independent human verdicts: biology 0/1; statistics 0/1.
- Merge authorization: blocked pending independent scientific review.

This is a computational and documentary research artifact. It does not authorize physical experiments or clinical use.
