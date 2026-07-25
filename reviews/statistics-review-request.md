# External Statistics and Bioinformatics Review Request — BioEvidence OS v0.1

## Review purpose

Please review whether the statistical, computational, and reproducibility boundaries in PR #23 are defensible for the GSE141064 / GSE94383 case.

This review concerns evidence quality and analysis validity. It does not authorize physical biological work.

## Primary review questions

1. Is the experimental-unit and pseudoreplication logic correct?
2. Are uncertainty statements appropriately tied to biological rather than cell-level independence?
3. Is the GSE94383 endpoint adequately frozen and described?
4. Are stratified bootstrap and permutation procedures represented accurately?
5. Is the leave-one-ID-prefix-out analysis correctly treated as technical sensitivity rather than biological replication?
6. Is the Supplementary Table 4 interpretation of nominal p-values, FDR, bootstrap FDR, and winner's-curse risk appropriate?
7. Does the causal ranking make clear that scores prioritize inquiry rather than identify effects?
8. Are model-comparison requirements sufficient to distinguish `Nfkbia`-only, broader-state, technical, combined, and negative-control explanations?
9. Are missingness, exclusions, transformations, multiplicity, calibration, and external validation sufficiently constrained?
10. Are any claims supported by weaker evidence than the stated F0–F5 level implies?

## Current key results

### GSE94383 conceptual analysis

- matched cell identities: 823;
- Spearman rho: 0.178;
- bootstrap 95% CI: 0.110 to 0.243;
- stratified permutation p: 0.0002;
- leave-one-prefix-out rho range: 0.153 to 0.200.

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
Reviewer expertise:
Overall verdict: ACCEPT / ACCEPT_WITH_CHANGES / HOLD / BLOCK
P0 validity errors:
P1 required corrections:
P2 improvements:
Experimental-unit concerns:
Multiplicity or winner's-curse concerns:
Bootstrap/permutation concerns:
Model-comparison concerns:
Reproducibility concerns:
Claims that exceed statistical support:
Recommended next analysis:
```

## Evidence entry points

- `scripts/analyze_gse94383_conceptual_replication.py`
- `scripts/probe_gse94383_tables.py`
- `scripts/probe_live_seq_supplementary_table4.py`
- `scripts/audit_bioevidence_release.py`
- `reports/gse94383-conceptual-replication-2026-07-23.json`
- `reports/gse94383-conceptual-replication-2026-07-23.md`
- `reports/gse141064-supplementary-table4-probe-2026-07-23.json`
- `examples/gse141064.experimental-unit-audit.json`
- `examples/gse141064.nfkbia-causal-hypotheses.json`
- `examples/gse141064.nfkbia-partner-lab-handoff.json`

## Non-claims

The current analyses do not establish independent biological prediction, causal identification, clinical utility, or therapeutic relevance.
