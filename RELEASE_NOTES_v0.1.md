# BioEvidence OS v0.1 — Release Notes

## Release status

```text
P0_HARDENING_FOR_EXTERNAL_REVIEW
NOT_MERGED
NOT_CLINICAL
NOT_AN_EXECUTION_AUTHORIZATION
```

## Purpose

BioEvidence OS v0.1 is a computational evidence and governance stack for auditing biological claims before expensive or physical validation is considered.

It focuses on experimental-unit semantics, provenance, confounding, independent replication, temporal identity, causal alternatives, claim boundaries, and non-operational partner-laboratory handoff.

## Included contracts

1. `bio-experimental-unit-auditor`
2. `bio-provenance-confounder-graph`
3. `bio-independent-replication-finder`
4. `bio-causal-hypothesis-ranker`
5. `bio-temporal-replication-gate`
6. `bio-partner-lab-evidence-handoff`

Each contract has:

- a skill specification;
- a machine-readable schema;
- a positive reference record;
- a semantic validator;
- a fail-closed misuse fixture;
- a release gate;
- authoritative CI coverage.

Acceptance is schema-first:

```text
public Draft 2020-12 schema
  -> format checks
  -> semantic validator
  -> ACCEPT / BLOCK
```

A semantic validator cannot override schema invalidity.

## Reference case

### GSE141064

The original discovery case is retained as an exploratory association with limits.

Key constraints:

- exact biological independence for Batch 8_8 is unresolved;
- plate and `exp8_*` labels are technical structures;
- collection day, extraction round, and imaging structure remain incompletely resolved;
- cells and technical containers are not treated as independent biological replication.

### GSE94383

A weak positive direction is visible within the matched 823-cell table:

- Spearman rho: 0.178;
- cell-level bootstrap interval: 0.110 to 0.243;
- cell-level permutation score: 0.0002;
- leave-one-ID-prefix-out rho range: 0.153 to 0.200.

```text
DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED
INDEPENDENT_BIOLOGICAL_UNIT_UNRESOLVED
REPLICATION_STATUS_HOLD
```

The bootstrap, permutation, and prefix-exclusion outputs are within-table sensitivity summaries only. The 823 cells are not treated as 823 independent biological units. Effective biological N and ID-prefix semantics remain unresolved, so the result does not establish independent biological support, conceptual triangulation, replication, or generalization.

It is also not direct temporal replication of basal `Nfkbia` predicting a later `Tnf-mCherry` response.

### Original model-ranking workbook

`Nfkbia` ranks first among 362 genes by nominal linear-model evidence, but no gene reaches bootstrap FDR at or below 0.20.

```text
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

### Causal interpretation

```text
RANKED_NOT_IDENTIFIED
```

The leading current explanation is a broader shared upstream cellular state. Direct `Nfkbia` action remains plausible but unidentified. The GSE94383 table contributes descriptive pathway context, not an accepted independent-validation signal.

### Replication status

```text
DIRECT_REPLICATION_GAP
```

No public candidate currently satisfies the full pre-state, linked later phenotype, biological-unit, endpoint, and technical-lineage contract. GSE94383 remains `HOLD` until source-backed independent-unit semantics are available.

### Partner handoff

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

The handoff defines evidence requirements and governance questions. It is not a physical protocol.

## P0 hardening

The controlled successor PR adds:

- a canonical schema-first gateway for all six records;
- a negative fixture that proves schema-invalid evidence cannot receive final acceptance;
- deterministic no-traceback failure output;
- exact pull-request-head checkout and receipt binding;
- a GSE94383 regression proving that even 100,000 cell observations cannot promote a verdict when the independent unit is unresolved;
- a cross-artifact drift gate covering machine-readable records, reports, architecture, release notes, and review packets.

## Validation

The authoritative workflows verify:

- six accepted positive records through schema and semantic validation;
- all blocked misuse cases without traceback;
- exact-head checkout identity;
- GSE94383 source retrieval and SHA-256 verification;
- descriptive-only GSE94383 verdict enforcement;
- claim consistency across records and public text;
- original publisher workbook retrieval and diagnostic probing;
- release consistency and safety boundaries.

## Known limitations

- no direct independent temporal replication;
- incomplete biological-unit reconstruction for the target discovery cells;
- unresolved GSE94383 biological grouping and ID-prefix semantics;
- small original discovery sample and winner's-curse risk;
- no causal identification;
- no tissue, clinical, therapeutic, or treatment evidence;
- no completed external biology or statistics verdict yet.

## Deferred to v0.2

- NVIDIA BioNeMo model-compatibility gate;
- Model Evidence Passport;
- species and domain-shift checks;
- human macrophage temporal-data search expansion;
- accession-to-evidence web MVP;
- automated negative-result and supersession memory.

## Merge gate

Do not merge until:

- exact-head CI is green;
- review threads are clear;
- documentation and executable behavior agree;
- schema-first and independent-unit P0 gates pass;
- safety and overclaim audit passes;
- external biology and statistics reviewers receive the superseding exact head;
- resulting P0/P1 findings are resolved or explicitly documented.
