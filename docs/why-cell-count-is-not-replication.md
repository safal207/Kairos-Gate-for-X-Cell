# Why Cell Count Is Not Replication

## An Executable Evidence Audit of Longitudinal Single-Cell Studies

**Status:** preprint-style technical draft for independent scientific review  
**Project:** BioEvidence OS v0.1 / Kairos Gate for X-Cell  
**Exact evidence head:** `936a58f91aef5fd6642770ac8930e9ab7b5f4bd5`  
**Review state:** biology verdict 0/1; statistics verdict 0/1; merge not authorized

> This report is computational and documentary only. It does not authorize physical biological work, genetic modification, human experimentation, clinical decisions, diagnosis, treatment, or therapeutic claims.

## Abstract

Single-cell studies can contain hundreds or thousands of measured cells while still providing only a small number of independently sampled biological units. Treating cells, wells, plates, sequencing indexes, libraries, or runs as independent replicates can make an analysis appear far more certain than the study design supports.

This report presents an executable evidence audit of two public single-cell resources, GSE141064 and GSE94383. The audit separates biological units from technical observations, traces provenance and confounders, distinguishes conceptual pathway triangulation from direct temporal replication, ranks competing causal explanations without identifying a causal mechanism, and enforces claim boundaries through machine-readable schemas and fail-closed validators.

The principal result is negative but useful. For the selected GSE141064 cohort, public materials recover 17 response-complete cells and several technical groupings, but do not establish an independent biological replicate unit. The correct current disposition is therefore `BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED`. GSE94383 provides bounded conceptual support for NF-kB/Nfkbia pathway coupling, but it does not directly replicate a pre-state-to-later-phenotype prediction claim. NFKBIA is not identified as a unique causal driver, and tissue, clinical, diagnostic, treatment, and therapeutic claims remain blocked.

## 1. The problem: measurement count is not experimental replication

A cell count answers how many cellular observations were measured. It does not automatically answer how many independent biological units were sampled, randomized, assigned, or repeated.

In a single-cell dataset, many cells may share:

- the same source culture;
- the same experimental day;
- the same intervention batch;
- the same imaging session;
- the same extraction event;
- the same plate or library;
- the same sequencing run;
- hidden upstream biological dependencies.

When those dependencies are ignored, uncertainty is underestimated. A model can then report stable-looking associations that are primarily supported by technical replication or repeated sampling from one biological source.

BioEvidence OS therefore applies a fail-closed rule:

> Cells, wells, plates, libraries, index pairs, reads, and sequencing runs cannot silently become biological replicates.

If the independent unit cannot be recovered from public evidence, confirmatory claims remain blocked.

## 2. Executable evidence architecture

The audit is organized as six contracts:

1. **Experimental Unit Auditor** — determines what was independently sampled or assigned.
2. **Provenance and Confounder Graph** — traces how observations became claims and exposes uncertain or missing links.
3. **Independent Replication Finder** — rejects same-study material, reruns, reprocessing, and shared biological sources as independent replication.
4. **Temporal Replication Gate** — prevents post-transition measurements from being represented as pre-state predictors.
5. **Causal Hypothesis Ranker** — compares explanations but does not equate rank with causal identification.
6. **Partner-Lab Evidence Handoff** — packages scientific questions for authorized institutional review without authorizing physical execution.

Every accepted evidence path preserves source identity, checksums where available, exact commit and workflow identity, validator and schema versions, model parameters, exclusions, missingness, transformations, negative evidence, unresolved unknowns, and claim boundaries.

## 3. GSE141064: what was recovered

The real-input audit reproduced the public metadata-to-count-matrix linkage:

```text
metadata IDs matching matrix columns: 1012 / 1012
selected response-complete cells:      17
plate1:                                7
plate3:                                4
plate4:                                6
shared original prefix exp8:           17 / 17
shared sequencing run NXT0590:         17 / 17
Date field present:                    0 / 17
Probe field present:                   0 / 17
unique index pairs:                    17
```

The cohort can therefore be reconstructed technically. That is not the same as proving biological independence.

Public evidence does not establish that `plate1`, `plate3`, and `plate4` correspond to independent cultures, independent experimental days, independent intervention batches, or independent imaging sessions. All 17 cells share the same original experiment prefix and sequencing run. Unique index pairs establish technical identity, not independent biological replication.

### Current disposition

```text
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

A leave-one-plate-out analysis may be described as a technical sensitivity analysis. It cannot be presented as confirmatory held-out biological generalization unless source-backed semantics establish that the plates correspond to independent biological units.

An author clarification request remains open. Until an authoritative source resolves the experimental-unit meaning, the block is intentional.

## 4. GSE94383: conceptual triangulation, not direct replication

GSE94383 was evaluated as an independent source of pathway-related evidence. The bounded analysis linked 823 cells with both recent NF-kB activity information and post-LPS Nfkbia expression.

Observed result:

```text
identity-matched cells:                 823
Spearman rho:                           0.178
bootstrap 95% confidence interval:      0.110 to 0.243
stratified permutation p-value:         0.0002
leave-one-ID-prefix-out rho range:      0.153 to 0.200
```

This supports a modest association between recent NF-kB activity and post-stimulation Nfkbia expression in that dataset. It does not directly test whether a pre-intervention transcriptomic state predicts a later phenotype in GSE141064.

The endpoint criterion is explicitly recorded as `not_commit_bound`: the repository does not claim that the success threshold was demonstrably frozen in a commit before outcome inspection. Observed results are stored separately from success criteria to prevent retrospective rewriting of the target.

### Correct interpretation

```text
conceptual pathway coupling: supported with limits
out-of-sample biological prediction: not established
direct temporal replication: gap remains
```

Post-stimulation expression cannot be represented as a basal predictor. A related pathway signal is not the same as direct replication of timing, identity linkage, biological unit, endpoint, and intervention structure.

## 5. Competing causal explanations

The system ranks explanations as inquiry priorities using a published deterministic formula. Scores are not probabilities and do not establish causality.

Current ordering:

| Rank | Explanation | Priority score | Bounded interpretation |
|---:|---|---:|---|
| 1 | Shared upstream cellular state | 53 | Strong competing explanation |
| 2 | Direct NFKBIA-related effect | 46 | Plausible but not identified |
| 3 | NFKBIA as a state marker only | 44 | Plausible competing explanation |
| 4 | Small context-specific real effect | 41 | Plausible, not established |
| 5 | Technical confounding | 32 | Remains possible |
| 6 | Chance or model instability | 19 | Weakened but not eliminated |

The direct-effect hypothesis is not promoted to a causal conclusion because the identification gates are not satisfied. In particular, the analysis lacks verified biological replication, direct temporal replication, and intervention evidence capable of distinguishing a driver from a correlated state marker.

### Current causal boundary

```text
NFKBIA unique causal driver: not identified
direct causal effect: blocked
tissue-level claim: blocked
clinical or therapeutic claim: blocked
```

## 6. Winner's-curse and selection risk

The reference case began with a discovery-stage candidate selected from a small effective evidence base. Such settings are vulnerable to winner's curse: the most favorable observed feature may overestimate the underlying effect because it was selected after comparing many candidates.

The audit therefore requires explicit reporting of:

- candidate-selection history;
- raw and multiple-testing-adjusted statistics;
- bootstrap stability;
- sensitivity to grouping assumptions;
- negative and contradictory evidence;
- whether eligibility or success criteria were frozen before outcome inspection;
- whether the target was switched after viewing results.

A nominally attractive candidate is not considered externally validated merely because it shows a related association in another dataset.

## 7. Provenance and confounder controls

The provenance graph records each transformation from source data to claim, including:

- evidence level;
- confidence;
- whether an edge is load-bearing;
- transformation reversibility;
- missing-input impact;
- observed, documented, executable, author-confirmed, inferred, or unknown status;
- confounder edge class;
- unknown and inferred edge counts;
- reproducibility from frozen inputs.

This makes uncertainty inspectable rather than hiding it inside prose. A broken or unknown load-bearing path limits the claim even when the downstream computation succeeds.

## 8. Claim firewall

The release audit rejects unsafe claim promotion in accepted records. It scans both flat and nested claim structures and blocks causal, tissue, clinical, or therapeutic support states that exceed the evidence contract.

The current accepted boundary is:

```text
exploratory association: supported with limits
conceptual pathway evidence: supported with limits
out-of-sample prediction: not established
causal identification: blocked
tissue generalization: blocked
clinical utility: blocked
diagnostic use: blocked
treatment or therapeutic relevance: blocked
physical execution: not authorized
```

## 9. Fail-closed validation

A scientific evidence gate must not silently pass malformed data and should not crash in a way that obscures the verdict.

The validators therefore accumulate bounded validation errors and emit `BLOCK` for invalid evidence records. A dedicated regression verifies that malformed or null causal score components:

- exit non-zero;
- emit `BLOCK`;
- report the malformed component;
- produce no Python traceback.

Eleven major automated-review findings were corrected and regression-tested. Final exact-head CI and the final incremental automated review succeeded with zero unresolved inline threads.

## 10. Negative findings are part of the result

The audit did not establish:

- a verified independent replicate unit for the 17-cell GSE141064 cohort;
- confirmatory held-out biological prediction;
- direct temporal replication;
- a uniquely causal role for NFKBIA;
- tissue generalization;
- diagnostic, clinical, treatment, or therapeutic utility;
- authorization for a physical experiment.

These are not missing marketing claims. They are the principal evidence boundaries produced by the system.

## 11. Why this matters for AI-enabled biology

AI systems can generate and rank biological hypotheses faster than laboratories and reviewers can validate them. Without an evidence-governance layer, weak assumptions can propagate from public data into model outputs, experiment plans, investment decisions, and medical language.

BioEvidence OS is designed as a control layer between hypothesis generation and expensive downstream action. Its purpose is not to replace scientists or statistical reviewers. Its purpose is to make the evidence path explicit, reproducible, reviewable, and fail-closed.

A useful system should be able to say not only:

> This hypothesis is interesting.

It should also be able to say:

> The independent unit is unresolved, the external dataset is only conceptually related, causality is not identified, and this claim must not advance yet.

## 12. Limitations

- The report depends on public data and public documentation; hidden experimental dependencies may remain unknown.
- GSE141064 replicate semantics require author clarification or another authoritative source.
- GSE94383 provides conceptual rather than direct temporal replication.
- The GSE94383 criterion is not claimed to have been demonstrably commit-bound before outcome inspection.
- The causal ranking formula organizes inquiry priorities; it is not a causal estimator.
- Automated validation cannot replace independent biology and statistics review.
- The report is a technical draft pending one independent biology verdict and one independent statistics/bioinformatics verdict.

## 13. Independent review gate

Five independent reviewers have been contacted across single-cell biology, NF-kB signaling, experimental design, pseudoreplication, biostatistics, and reproducibility.

Requested verdicts:

```text
ACCEPT
ACCEPT_WITH_CHANGES
HOLD
BLOCK
```

Each reviewer is asked to identify:

- P0 critical scientific or validity errors;
- P1 required corrections;
- P2 improvements;
- conflicts of interest;
- claim boundaries that must remain blocked.

The BioEvidence OS release candidate must not merge until both independent human verdicts are received and every P0/P1 finding is corrected or explicitly dispositioned.

## 14. Reproducibility appendix

### Exact head

```text
936a58f91aef5fd6642770ac8930e9ab7b5f4bd5
```

### Exact-head workflows

```text
Kairos Gate validation:          30135562019 — SUCCESS
Live-seq feasibility:            30135562028 — SUCCESS
Biological Evidence Contracts:   30135562030 — SUCCESS
```

### Evidence artifacts

```text
Kairos evidence
ID 8612645474
sha256:0097aaa3a7b5bf1d36d4af4c0cbb09d0d93dbb50b3abce17037df424cbc3e3da

Live-seq exact-head audit
ID 8612643386
sha256:a9d7394538226ce280445d8c91e0366f1325e6150280c328cc9ca70c50920228

BioEvidence release audit
ID 8612642679
sha256:50cd053d458f1c70c9248898bd8a47ea88d45fa2258b271351c97481b8c5787b

GSE141064 Supplementary Table 4 probe
ID 8612643702
sha256:8fd2b891d12897e4f4b0b6dce862161727f9e08fd15fa15be7fa2036a9b9fff2

GSE94383 live analysis
ID 8612658485
sha256:1612074e8351d49403b8e6037a70cd23632df0a3dd97a7b1d35401a70457d620
```

## 15. Release boundary

This document is a review artifact, not a completed biological discovery claim. It is suitable for scientific critique, reproducibility review, research-integrity discussion, and bounded infrastructure evaluation.

It is not authorization for wet-lab execution, clinical translation, treatment, diagnosis, deployment, or investment claims based on a validated drug target.
