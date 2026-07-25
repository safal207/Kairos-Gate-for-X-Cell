---
name: bio-independent-replication-finder
description: Find and rank genuinely independent biological datasets for replication while rejecting same-study reuse, shared biological sources, technical reprocessing, incompatible units, and hidden batch dependence.
version: 0.1.0
status: experimental
---

# Bio Independent Replication Finder

## Purpose

Identify whether an observed biological signal has a credible path to independent replication.

The skill must distinguish:

- an independent biological replication dataset;
- a technical remeasurement or reprocessing of the same material;
- another accession derived from the same study or donor pool;
- a biologically related but non-equivalent dataset;
- a candidate that is too poorly documented to classify.

Similarity is not independence. Reanalysis is not replication. A new accession is not automatically a new biological experiment.

This skill is computational and documentary only. It does not provide operational wet-lab procedures or authorize physical biological work.

## Trigger

Use when the user asks to:

- find another GEO, SRA, ArrayExpress, BioProject, or Single Cell Expression Atlas dataset;
- validate a model or marker on independent biological material;
- determine whether a paper or accession reproduces an earlier result;
- build external validation, replication, holdout, or transfer-learning evidence;
- compare datasets across laboratories, donors, organisms, tissues, cell types, assays, or perturbations.

## Required upstream inputs

Prefer outputs from:

1. `bio-experimental-unit-auditor`;
2. `bio-provenance-confounder-graph`.

Minimum required query contract:

- target study/accession;
- target observation or claim;
- biological source and experimental unit, if known;
- species;
- tissue/cell type or system;
- phenotype, perturbation, condition, or outcome;
- assay modality;
- known confounders and blocked claims.

Unknown fields must stay unknown. Do not silently broaden the biological question.

## Evidence levels

- **F0 — unverified mention:** keyword or model-generated candidate.
- **F1 — repository-level match:** title, abstract, tags, accession, or indexed metadata.
- **F2 — documentary compatibility:** methods and sample annotations support the match.
- **F3 — executable compatibility:** files, identifiers, unit counts, and analysis inputs are machine-checkable.
- **F4 — source/laboratory confirmation:** authors or repository curators confirm independence and semantics.
- **F5 — completed independent replication:** prespecified analysis reproduces the load-bearing result on independent biological material.

A candidate cannot be called replicated before F5.

## Candidate independence classes

Classify each candidate as exactly one:

- `independent_biological_experiment`;
- `independent_biological_source_uncertain_protocol`;
- `same_study_new_accession`;
- `shared_biological_source`;
- `technical_remeasurement`;
- `derived_or_reprocessed_data`;
- `related_non_equivalent_system`;
- `insufficient_metadata`;
- `excluded`.

## Required workflow

### 1. Freeze the replication target

Record the exact target claim, outcome, comparison, direction, biological scope, and claim level.

Example:

> In the observed Live-seq cells, expression features are associated with `mCherry.log.slope`.

Do not broaden this into tissue restoration, therapeutic response, or causal control.

### 2. Build a search fingerprint

Create explicit fields for:

- species;
- biological source;
- tissue/cell type;
- cell state;
- perturbation or condition;
- phenotype/outcome;
- assay;
- time structure;
- required biological unit;
- excluded accessions, papers, labs, donors, or sample identifiers;
- acceptable biological substitutions;
- unacceptable substitutions.

### 3. Search broadly, classify narrowly

Candidate discovery may use:

- accessions and repository metadata;
- article methods and supplements;
- citation and related-record links;
- sample identifiers and BioProject relationships;
- author and laboratory names;
- raw-file and checksum overlaps;
- donor, animal, clone, cell-line, or culture identifiers.

Every candidate must be independently classified after discovery.

### 4. Detect independence leakage

Raise a blocking finding when a candidate shares any load-bearing biological source with the target, including:

- the same donor, animal, patient, clone, culture, organoid, tissue aliquot, or extraction event;
- the same parent BioProject or experiment with split accessions;
- the same raw files, checksums, sample IDs, barcodes, or library IDs;
- a processed or normalized derivative of the target data;
- another sequencing run or flow cell from the same biological material.

Shared authors or institutions alone do not disqualify a candidate, but require stronger provenance review.

### 5. Evaluate compatibility

Score and document these dimensions separately:

- biological-source independence;
- experimental-unit independence;
- species compatibility;
- tissue/cell-type compatibility;
- phenotype/outcome compatibility;
- perturbation/condition compatibility;
- assay compatibility;
- temporal compatibility;
- covariate availability;
- provenance completeness;
- sample-size adequacy;
- availability of raw or sufficiently processed data.

Never collapse all dimensions into one opaque similarity score.

### 6. Separate replication from extension

Return one of:

- `direct_replication` — same load-bearing biological question and compatible units;
- `conceptual_replication` — same mechanism or directional relationship in a meaningfully different system;
- `external_validation` — same prediction task on independent biological units;
- `method_transfer_only` — workflow can be tested but biological claim cannot;
- `not_a_replication`.

### 7. Prespecify the replication test

Before inspecting the candidate outcome, define:

- primary endpoint;
- expected direction or effect;
- biological grouping key;
- exclusion criteria;
- covariates;
- minimum evidence threshold;
- robustness checks;
- success, mixed, and failure criteria.

The skill must not rewrite the target after seeing candidate results.

### 8. Apply claim gates

- Candidate discovery alone: `HOLD`.
- Repository-level match without proven independence: `HOLD`.
- Shared biological source or reprocessed data: `BLOCK` as independent replication.
- Independent but biologically incompatible system: `related_non_equivalent_system`.
- Independent and compatible dataset ready for prespecified analysis: `ACCEPT_WITH_LIMITS` as a replication candidate.
- Completed, prespecified, reproducible confirmation: eligible for F5, but claim scope remains bounded to the matched biological question.

## Ranking model

Rank candidates lexicographically, not by a single blended score:

1. independence status;
2. biological-question compatibility;
3. experimental-unit validity;
4. provenance completeness;
5. raw-data availability;
6. sample-size adequacy;
7. assay and temporal compatibility.

A highly similar but non-independent dataset must rank below a less similar but truly independent candidate.

## Required output

Produce a record conforming to `schemas/independent-replication-search.schema.json` with:

1. target study and claim;
2. search fingerprint;
3. sources searched;
4. candidate records;
5. independence-leakage findings;
6. compatibility matrix;
7. replication type;
8. prespecified test status;
9. overall verdict;
10. next valid action;
11. computational-only safety status.

## Fail-closed rules

Return `BLOCK` for an individual candidate as independent replication when:

- its accession differs but biological material is shared;
- it reuses target raw or processed data;
- its only independence evidence is naming, publication date, or repository separation;
- the biological experimental unit remains unresolved;
- it uses technical containers as replication units;
- target and candidate conditions are inseparable from incompatible batch structures.

Return overall `HOLD` when no accepted candidate exists but the search remains incomplete or promising.

## GSE141064 reference expectation

For the current GSE141064 Batch 8_8 case:

- the target claim is exploratory association with `mCherry.log.slope` in observed Live-seq cells;
- a candidate must use independently collected biological material;
- plate, library, flow-cell, or alternate-run splits from exp8 are not independent replication;
- exact per-cell collection grouping in the target is unavailable, so candidate comparison must not pretend to validate target biological folds;
- until an independent compatible dataset is verified and analysed, prediction, generalization, causal, tissue, clinical, and therapeutic claims remain blocked.

Expected current overall verdict: `HOLD` — search contract defined, no verified independent candidate accepted yet.

## Safety boundary

The skill may recommend an authorized partner laboratory when no suitable public dataset exists. It must not provide step-by-step biological manipulation instructions.

Any new physical study requires competent scientific supervision, ethics and biosafety review, documented biological units, prespecified analysis, and independent replication planning before data collection.
