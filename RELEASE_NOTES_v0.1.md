# BioEvidence OS v0.1 — Release Notes

## Release status

```text
RELEASE_CANDIDATE_FOR_EXTERNAL_REVIEW
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
- a standard-library validator;
- a fail-closed misuse fixture;
- a release gate;
- authoritative CI coverage.

## Reference case

### GSE141064

The original discovery case is retained as an exploratory association with limits.

Key constraints:

- exact biological independence for Batch 8_8 is unresolved;
- plate and `exp8_*` labels are technical structures;
- collection day, extraction round, and imaging structure remain incompletely resolved;
- cells and technical containers are not treated as independent biological replication.

### GSE94383

Independent conceptual pathway analysis found weak but stable coupling between preceding NF-kB activity and post-LPS `Nfkbia` expression:

- Spearman rho: 0.178;
- bootstrap 95% CI: 0.110 to 0.243;
- stratified permutation p: 0.0002;
- leave-one-ID-prefix-out range: 0.153 to 0.200.

```text
CONCEPTUAL_SIGNAL_SUPPORTED
```

This is not direct temporal replication of basal `Nfkbia` predicting a later `Tnf-mCherry` response.

### Original model-ranking workbook

`Nfkbia` ranks first among 362 genes by nominal linear-model evidence, but no gene reaches bootstrap FDR at or below 0.20.

```text
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

### Causal interpretation

```text
RANKED_NOT_IDENTIFIED
```

The leading current explanation is a broader shared upstream cellular state. Direct `Nfkbia` action remains plausible but unidentified.

### Replication status

```text
DIRECT_REPLICATION_GAP
```

No independent public candidate currently satisfies the full pre-state, linked later phenotype, biological-unit, endpoint, and technical-lineage contract.

### Partner handoff

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

The handoff defines evidence requirements and governance questions. It is not a physical protocol.

## Validation

The authoritative workflow verifies:

- six accepted positive records;
- six blocked misuse cases;
- live GSE94383 source retrieval, checksum verification, structure probing, analysis, and artifact upload;
- original publisher workbook retrieval and diagnostic probing;
- release consistency and safety boundaries.

## Known limitations

- no direct independent temporal replication;
- incomplete biological-unit reconstruction for the target discovery cells;
- unresolved GSE94383 ID-prefix semantics;
- small original discovery sample and winner's-curse risk;
- no causal identification;
- no tissue, clinical, therapeutic, or treatment evidence;
- no external biology or statistics approval yet.

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
- safety and overclaim audit passes;
- biology and statistics review requests have been issued;
- resulting P0/P1 findings are resolved or explicitly documented.
