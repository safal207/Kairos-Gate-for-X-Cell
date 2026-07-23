---
name: bio-temporal-replication-gate
description: Determine whether a candidate dataset directly tests a frozen pre-state-to-later-phenotype claim, only offers conceptual triangulation, or is ineligible because temporal order, same-cell linkage, or biological independence is missing.
version: 0.1.0
status: experimental
---

# Bio Temporal Replication Gate

## Purpose

Separate true temporal replication from datasets that are merely biologically similar.

This skill is used after a causal-hypothesis ranking identifies a high-information contrast such as:

`pre-stimulation molecular state -> later phenotype in the same cell`

It evaluates whether a public or partner dataset can distinguish competing explanations without changing the target claim after inspecting results.

This skill is computational and documentary only. It does not provide operational biological procedures or authorize physical experimentation.

## Core rule

> Similar cells, the same stimulus, and the same pathway do not constitute direct replication when temporal order or same-cell linkage differs.

## Required direct-replication structure

A candidate may be classified as `direct_temporal_replication_candidate` only when all are established:

1. the molecular state is measured before the phenotype-generating stimulus or transition;
2. the later phenotype is measured after that molecular state;
3. the pre-state and later phenotype are linked to the same cell or to an explicitly defensible longitudinal biological unit;
4. the candidate is biologically independent of the target study;
5. technical containers and repeated measurements are not substituted for biological units;
6. the target candidate variable and phenotype are measured directly or through a frozen compatible mapping;
7. sample lineage and exclusions are machine-checkable at F3 or stronger;
8. the analysis plan is frozen before outcome inspection.

Failure of any item prevents direct-replication classification.

## Candidate classes

- `direct_temporal_replication_candidate`: all direct-replication gates pass;
- `partial_temporal_candidate`: pre-state and later phenotype exist, but same-cell linkage, biological independence, grouping, or endpoint compatibility is incomplete;
- `conceptual_replication`: related pathway or cell biology, but temporal direction or endpoint differs;
- `cross_sectional_support`: same pathway or condition measured at one time or in different cells;
- `method_transfer_only`: useful technology or analytical method without compatible biological evidence;
- `same_study_internal_validation`: additional evidence inside the original study;
- `ineligible`: cannot test the frozen claim.

## Inputs

- frozen target claim;
- experimental-unit audit;
- provenance/confounder graph;
- independent-replication search;
- causal-hypothesis ranking;
- public repository records;
- methods, supplements, metadata, and correspondence;
- candidate analysis files.

## Required workflow

### 1. Freeze the target contrast

Record:

- pre-state measurement;
- stimulus or transition;
- later phenotype;
- required same-cell or longitudinal linkage;
- required biological unit;
- acceptable endpoint substitutions;
- forbidden substitutions;
- competing models the dataset must distinguish.

### 2. Build a temporal lineage

For every candidate, reconstruct:

`biological source -> pre-state measurement -> stimulus/transition -> later phenotype -> analysis row`

Every edge must be marked `verified`, `documented`, `inferred`, or `unknown`.

### 3. Apply temporal-order gates

Check separately:

- pre-state truly precedes the stimulus;
- phenotype follows the stimulus;
- molecular measurement is not collected after the phenotype or after substantial pathway activation;
- destructive assays do not break same-cell continuity unless an explicit longitudinal design exists.

### 4. Apply identity gates

Require:

- one-to-one cell identity or a defensible biological-unit mapping;
- no duplicate or ambiguous identifiers;
- no undocumented merge across cells, plates, libraries, or runs;
- no reprocessed target-study material presented as external evidence.

### 5. Apply model-discrimination gate

The candidate must support a frozen comparison of at least:

- candidate-only model;
- broader biological-state model;
- technical-confounder model.

A dataset that can estimate only one model may support association but cannot distinguish the top causal hypotheses.

### 6. Record the gap

If no direct candidate exists, return a machine-readable `direct_replication_gap` rather than lowering the eligibility standard.

The gap must identify which field is missing:

- pre-state measurement;
- later phenotype;
- same-cell linkage;
- independent biological units;
- endpoint compatibility;
- technical lineage;
- sample size;
- public availability.

### 7. Choose the next action

Possible actions:

- obtain missing metadata or author clarification;
- inspect supplementary files;
- execute a frozen diagnostic reanalysis of the original study without calling it validation;
- continue repository surveillance;
- prepare a non-operational evidence brief for an authorized partner laboratory.

## Fail-closed rules

Return `BLOCK` when:

- post-stimulation RNA is described as a pre-stimulation predictor;
- measurements from different cells are presented as same-cell longitudinal data;
- a same-study replicate is called independent external replication;
- a cell count is presented as the number of biological replicates;
- endpoint selection changes after outcome inspection;
- a conceptual candidate is promoted to direct replication;
- a direct-effect conclusion is drawn from a dataset unable to compare broader-state and technical explanations;
- operational biological instructions are included.

## Verdicts

- `DIRECT_CANDIDATE_AVAILABLE`
- `PARTIAL_CANDIDATE_AVAILABLE`
- `DIRECT_REPLICATION_GAP`
- `BLOCK`

## Current Nfkbia case expectation

The frozen target is:

`basal pre-LPS transcriptome -> later same-cell Tnf-promoter response`

Current public candidates:

- GSE141064 directly instantiates the temporal structure but is the target study and has unresolved biological independence;
- GSE94383 links prior NF-kB dynamics to post-LPS RNA in the same cells and is conceptual, not direct;
- GSE162992 contains stimulated macrophage imaging/transcriptomics but does not establish the frozen pre-state-to-later-TNF same-cell mapping;
- GSE65528 and GSE65529 pair inflammatory phenotypes with single-cell expression after exposure, not a pre-stimulation transcriptome predicting a later phenotype;
- GSE161125 links macrophage transcriptional states and secretion programs but does not provide the required same-cell pre-state-to-later-response mapping;
- nondestructive transcriptome-inference methods may be useful for future method transfer but do not themselves replicate the claim.

Expected verdict: `DIRECT_REPLICATION_GAP`.
