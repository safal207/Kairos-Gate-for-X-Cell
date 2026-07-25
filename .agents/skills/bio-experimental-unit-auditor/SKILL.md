---
name: bio-experimental-unit-auditor
description: Audit biological repository studies for true experimental units, technical hierarchy, pseudoreplication, batch structure, missing provenance, and claim limits before causal or translational interpretation.
version: 0.1.0
status: experimental
---

# Bio Experimental Unit Auditor

## Purpose

Turn a biological repository record into a fail-closed evidence contract that distinguishes biological independence from technical repetition.

Use this skill before differential-expression, predictive, causal, tissue, clinical, or intervention claims are accepted.

This skill is computational and documentary only. It does not design or provide operational wet-lab procedures, human experimentation, pathogen work, genetic modification instructions, or treatment recommendations.

## Trigger

Use when the user provides or names:

- a GEO, SRA, ArrayExpress, Single Cell Expression Atlas, BioProject, or similar accession;
- sample sheets, sequencing metadata, supplementary tables, methods, or author correspondence;
- a claim that cells, wells, plates, batches, donors, animals, organoids, cultures, runs, or time points are independent replicates;
- a request to validate whether an analysis supports exploratory, predictive, causal, translational, or clinical conclusions.

## Core question

> What is the smallest unit that was independently assigned, sampled, or exposed to the condition of interest, and what evidence proves that independence?

Never infer independence from naming patterns alone.

## Inputs

Accept any subset of:

- repository accession and metadata;
- article and supplementary materials;
- raw and processed file manifests;
- sample annotations;
- author correspondence;
- analysis notebook or result tables;
- prior audit records.

Record unavailable inputs explicitly. Missing metadata is evidence of uncertainty, not permission to guess.

## Evidence levels

- **F0 — assertion:** unsupported statement or model guess.
- **F1 — repository label:** name, column, filename, or accession metadata without protocol confirmation.
- **F2 — documentary support:** methods, supplement, README, sample sheet, or repository description.
- **F3 — executable consistency:** machine-checkable agreement across files, identifiers, counts, and lineage.
- **F4 — author or laboratory confirmation:** direct clarification tied to the exact study and question.
- **F5 — independent replication:** separate biological material or experiment reproduces the result.

A technical label at F1 must not be promoted to biological independence. Author correspondence may clarify study structure at F4, but it does not create missing replication.

## Audit depth

- **L1 — labels:** parse entities and naming conventions.
- **L2 — structure:** reconstruct nesting and lineage.
- **L3 — analysis validity:** test independence assumptions, pseudoreplication, and confounding.
- **L4 — claim boundary:** determine which conclusions remain admissible.

## Entity taxonomy

Classify every entity as one of:

- `biological_source`: donor, animal, patient, organism, clone, tissue source;
- `biological_experimental_unit`: independently assigned or sampled unit;
- `derived_biological_unit`: cell, aliquot, organoid, culture, biopsy, sorted population;
- `technical_container`: well, plate, lane, chip, cartridge;
- `library_preparation_unit`: library, pool, amplification batch;
- `measurement_run`: sequencing run, flow cell, imaging session, instrument run;
- `analysis_unit`: row, cell barcode, spot, pseudobulk profile;
- `unknown_unit`: entity whose role cannot be proven.

## Required workflow

### 1. Freeze source identity

Record accession, article identifier, retrieval date, source URLs or repository paths, file hashes when available, and correspondence identifiers.

### 2. Extract entities

Build an entity table with:

- `entity_id`;
- `entity_type`;
- `parent_id`;
- `condition`;
- `timepoint`;
- `collection_event`;
- `operator`;
- `plate`;
- `library`;
- `run`;
- `evidence_level`;
- `source_ref`;
- `uncertainty`.

### 3. Reconstruct lineage

Produce a directed acyclic graph from biological source to analysis row:

`source -> collection -> derived unit -> container -> library -> run -> analysis unit`

Unknown edges must remain explicit. Do not silently connect entities by similar names.

### 4. Resolve the experimental unit

For each comparison, identify:

- intervention or exposure;
- assignment mechanism;
- unit assigned independently;
- unit sampled independently;
- number of independent units per condition;
- whether repeated measurements are nested within the same unit.

### 5. Detect pseudoreplication

Raise a blocking warning when multiple cells, wells, images, reads, spots, aliquots, or runs from the same biological unit are counted as independent biological replicates.

### 6. Build the confounder graph

Evaluate candidate paths involving:

- collection day;
- donor or source;
- operator;
- plate or well;
- library-preparation batch;
- flow cell or sequencing run;
- imaging session;
- processing order;
- storage time;
- condition assignment.

Mark each relationship as `observed`, `documented`, `inferred`, or `unknown`.

### 7. Evaluate admissible analyses

Classify analyses as:

- `allowed`;
- `allowed_with_warning`;
- `exploratory_only`;
- `blocked`.

Common rules:

- cell-level descriptive summaries may be allowed when clearly labelled;
- cell-level inferential tests are blocked when cells are nested within too few biological units;
- pseudobulk requires a defensible biological grouping key;
- leave-one-plate-out tests technical sensitivity, not biological generalization, unless plates are proven independent biological units;
- sequencing runs are technical repeats unless proven otherwise;
- causal, tissue, clinical, and therapeutic claims require stronger evidence than repository association.

### 8. Apply the Biological Claim Firewall

Return separate verdicts for:

- descriptive observation;
- association;
- prediction within the observed dataset;
- generalization to new biological units;
- causal effect;
- tissue-level effect;
- clinical or therapeutic relevance.

Default to the weakest supported claim.

### 9. Define the next valid action

Choose the smallest action that can reduce the dominant uncertainty, such as:

- obtain author clarification;
- recover a missing sample sheet;
- locate an independent dataset;
- reanalyse using a valid grouping key;
- collect additional independent biological replicates through an authorized partner laboratory;
- stop because the requested claim is not supportable.

## Fail-closed rules

Return `HOLD` or `BLOCK` when:

- biological independence is not established;
- the grouping key mixes technical and biological units;
- condition is perfectly or near-perfectly confounded with batch;
- sample lineage contains unresolved identity collisions;
- the requested causal or translational claim exceeds the evidence level;
- data protection, consent, ethics, or biosafety status is unknown for a proposed real-world intervention.

Never convert `unknown` to `no issue`.

## Verdicts

- **ACCEPT:** the requested analysis and claim are supported at the stated scope.
- **ACCEPT_WITH_LIMITS:** valid only with explicit restrictions.
- **HOLD:** potentially resolvable missing evidence prevents a conclusion.
- **BLOCK:** the requested interpretation is invalid or unsafe under current evidence.

## Required output

Produce a machine-readable record conforming to `schemas/experimental-unit-audit.schema.json` and a human summary containing:

1. study identity;
2. resolved biological experimental unit;
3. technical hierarchy;
4. independent-unit counts by condition;
5. unresolved metadata;
6. pseudoreplication findings;
7. confounder graph summary;
8. admissible analyses;
9. claim firewall;
10. overall verdict;
11. next valid action.

## Safety boundary

The skill may recommend that an authorized professional laboratory evaluate or perform an experiment. It must not provide operational instructions for culturing, modifying, infecting, dosing, implanting, or otherwise manipulating biological material.

Any transition from computational analysis to physical biological work requires:

- named responsible institution;
- competent scientific supervision;
- applicable ethics approval;
- biosafety review;
- documented consent and data governance where relevant;
- predefined stop, containment, and incident-response criteria.

## GSE141064 reference expectation

For the current Batch 8_8 case, the auditor should preserve these author-confirmed facts:

- plate labels are library-preparation containers, not independent biological experiments;
- cells were collected over multiple days;
- `exp8_*` represents sequencing runs or flow cells associated with the exp8 library preparation;
- exact collection-day or batch identity per cell was not retained;
- leave-one-plate-out can test sensitivity but cannot demonstrate biological replication;
- the current result remains exploratory and requires independent biological validation.

Expected overall verdict: `ACCEPT_WITH_LIMITS` for exploratory analysis and `BLOCK` for causal, tissue, clinical, or therapeutic claims.
