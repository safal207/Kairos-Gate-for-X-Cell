---
name: bio-provenance-confounder-graph
description: Reconstruct biological source-to-claim provenance, expose missing lineage, detect condition-batch confounding, and block claims whose causal path is unsupported.
version: 0.1.0
status: experimental
---

# Bio Provenance Confounder Graph

## Purpose

Build a machine-checkable directed graph from biological source to scientific claim so that every transformation, grouping decision, measurement, model output, and interpretation has an explicit provenance path.

The skill must reveal where lineage is complete, where it is uncertain, where batch variables can explain the observed result, and which claims depend on unsupported edges.

This skill is computational and documentary only. It does not provide operational wet-lab procedures, human experimentation instructions, pathogen work, genetic modification instructions, or treatment recommendations.

## Trigger

Use this skill when a study contains any of the following:

- multiple donors, collection days, extraction rounds, plates, wells, libraries, chips, lanes, flow cells, imaging sessions, operators, or processing orders;
- missing or ambiguous sample lineage;
- claims derived from merged metadata, transformed matrices, model scores, embeddings, clusters, or differential expression;
- possible condition-batch confounding;
- a request to explain whether a biological result is caused by the condition or by technical structure;
- author correspondence that changes the interpretation of repository labels.

## Core questions

1. Can every claim be traced back to exact biological sources and exact processing events?
2. Which graph edges are directly observed, documented, inferred, or unknown?
3. Is the condition separable from collection day, operator, plate, library, run, imaging session, storage time, or processing order?
4. Which unsupported or high-risk edges are load-bearing for the final claim?
5. What smallest new evidence would most reduce uncertainty?

## Inputs

Accept any subset of:

- repository accession and metadata;
- article and supplementary methods;
- sample sheets and manifests;
- raw and processed filenames;
- notebooks, scripts, workflow manifests, and model outputs;
- author correspondence;
- prior `bio-experimental-unit-auditor` output;
- hashes, commit SHAs, workflow run IDs, or container identifiers.

Unavailable inputs must be recorded. Do not invent lineage from filename similarity.

## Evidence levels

Use the same F0–F5 contract as the experimental-unit auditor:

- **F0 — assertion:** unsupported statement or model guess.
- **F1 — label:** filename, column, identifier, or repository tag.
- **F2 — documentary support:** methods, supplement, README, sample sheet.
- **F3 — executable consistency:** hashes, joins, counts, manifests, deterministic transformations.
- **F4 — author or laboratory confirmation:** clarification tied to the exact study.
- **F5 — independent replication:** separate biological material or experiment reproduces the result.

An F4 clarification can correct semantics but cannot replace F5 replication.

## Graph model

The graph is a directed acyclic graph for provenance and a directed risk graph for possible confounding.

### Node classes

- `biological_source`
- `collection_event`
- `derived_biological_unit`
- `technical_container`
- `library_preparation`
- `measurement_run`
- `raw_data_artifact`
- `processed_data_artifact`
- `analysis_transformation`
- `model_output`
- `scientific_claim`
- `unknown_event`

### Provenance edge classes

- `derived_from`
- `contained_in`
- `pooled_into`
- `measured_by`
- `generated`
- `transformed_into`
- `grouped_by`
- `trained_on`
- `validated_on`
- `supports`
- `contradicts`
- `supersedes`

### Confounder edge classes

- `may_influence`
- `coincides_with`
- `determines_assignment`
- `partially_determines_assignment`
- `unknown_relationship`

### Edge status

Every edge must have one status:

- `observed`
- `documented`
- `executable`
- `author_confirmed`
- `inferred`
- `unknown`

## Required workflow

### 1. Freeze source identity

Record accession, article identifier, retrieval time, file hashes where available, correspondence identifiers, code commit, workflow version, and environment identity.

### 2. Import the experimental-unit audit

Use the output of `bio-experimental-unit-auditor` when available. Experimental-unit uncertainty must propagate into the provenance graph and claim gates.

### 3. Construct node inventory

Create one node per biological source, collection event, cell or derived unit, plate or well, library, run, raw file, processed artifact, transformation, model output, and claim.

Nodes with unresolved identity must remain separate until evidence proves equivalence.

### 4. Construct provenance edges

Connect source to claim through exact transformations:

`source -> collection -> derived unit -> container -> library -> run -> raw artifact -> processed artifact -> analysis -> model output -> claim`

Each edge must include:

- source reference;
- evidence level;
- status;
- confidence;
- timestamp or ordering when known;
- reversible or irreversible transformation flag;
- missing-input impact.

### 5. Validate graph integrity

Check for:

- orphan claim nodes;
- orphan model outputs;
- cycles in provenance;
- identity collisions;
- many-to-one pooling without membership records;
- joins performed on non-unique keys;
- processed artifacts with no raw ancestor;
- claims that depend only on inferred or unknown edges;
- source or code versions that do not match the reported result.

### 6. Build the confounder graph

Evaluate paths from candidate confounders to both condition assignment and outcome:

- donor or biological source;
- collection day or extraction round;
- operator;
- plate, well, chip, lane;
- library preparation;
- sequencing or imaging run;
- storage time;
- processing order;
- instrument;
- software version;
- normalization or filtering choice.

### 7. Score confounding risk

For each candidate confounder, classify:

- `separable`: represented across conditions with usable overlap;
- `partially_separable`: some overlap but imbalance remains;
- `aliased`: condition and confounder cannot be distinguished;
- `unknown`: metadata is insufficient.

Risk levels:

- `low`
- `medium`
- `high`
- `blocking`
- `unknown`

A confounder is load-bearing when removing or changing its edge could reverse the claim or when condition assignment is aliased with it.

### 8. Compute claim reachability

For each claim, identify all source-to-claim paths and report:

- weakest evidence level on each path;
- unknown edges;
- inferred edges;
- high-risk confounders intersecting the path;
- whether an independent validation path exists;
- whether the path is reproducible from frozen inputs.

### 9. Apply fail-closed claim gates

Return `HOLD` or `BLOCK` when:

- a claim has no complete source-to-claim path;
- the only complete path contains an unknown load-bearing edge;
- condition is aliased with a high-risk batch factor;
- independent validation uses the same biological source or technical batch;
- a processed artifact cannot be tied to raw input and exact code;
- a causal, tissue, clinical, or therapeutic claim depends on observational or technically confounded evidence;
- the graph relies on hidden, private, or unavailable data that reviewers cannot inspect.

### 10. Select the next evidence action

Rank possible next actions by expected uncertainty reduction:

- obtain missing sample sheet or extraction log;
- obtain author clarification;
- recover exact raw-to-processed manifest;
- rerun analysis from frozen source and code;
- stratify or block by a documented confounder;
- locate an independent dataset;
- collect independent biological replicates through an authorized partner laboratory;
- stop the claim because the confounding is structurally unresolvable.

## Required outputs

Produce a machine-readable record conforming to `schemas/bio-provenance-confounder-graph.schema.json` and a human summary containing:

1. graph identity and source freeze;
2. node and edge counts by class;
3. orphaned or unresolved nodes;
4. missing provenance edges;
5. high-risk confounders;
6. condition-confounder separability;
7. claim reachability table;
8. weakest evidence per claim;
9. independent validation status;
10. verdict per claim;
11. overall verdict;
12. ranked next evidence action.

## GSE141064 reference expectation

For Batch 8_8, preserve these facts:

- individual cells are observed, but exact per-cell collection day or extraction round is unavailable;
- plate labels are technical library-preparation containers;
- `exp8` is a library-preparation experiment containing cells accumulated across multiple rounds;
- `exp8_*` labels sequencing runs or flow cells;
- the lineage edge from each cell to exact collection event is unknown;
- collection day and imaging session remain possible high-risk confounders;
- leave-one-plate-out does not create an independent biological validation path;
- any claim beyond within-dataset exploratory association must be blocked or held.

Expected graph verdict:

- provenance completeness: partial;
- condition-batch separability: unknown or aliased for unresolved collection factors;
- exploratory descriptive claim: `ACCEPT_WITH_LIMITS`;
- biological generalization: `BLOCK`;
- causal tissue or therapeutic claim: `BLOCK`.

## Safety boundary

The graph may recommend an authorized professional laboratory as the destination for a validation study. It must not provide operational instructions for culturing, modifying, infecting, dosing, implanting, or otherwise manipulating biological material.

Any transition to physical biological work requires a named responsible institution, qualified scientific supervision, applicable ethics approval, biosafety review, consent and data governance where relevant, containment, incident response, and predefined stop criteria.
