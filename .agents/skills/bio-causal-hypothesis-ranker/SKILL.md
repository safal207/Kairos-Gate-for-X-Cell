---
name: bio-causal-hypothesis-ranker
description: Rank competing causal explanations for a biological association without promoting correlation, pathway plausibility, or model preference to causal identification.
version: 0.1.0
status: experimental
---

# Bio Causal Hypothesis Ranker

## Purpose

Convert a biological association into an explicit competition among causal, non-causal, technical, and null explanations.

The skill ranks hypotheses by current evidence and information value. It does not declare a causal winner unless the evidence identifies the effect under a documented design.

This skill is computational and documentary only. It does not provide operational wet-lab procedures, treatment instructions, human experimentation guidance, pathogen work, or genetic-modification protocols.

## Trigger

Use when:

- a gene, pathway, cell state, image feature, or molecular measurement is associated with a later phenotype;
- a replication or conceptual-replication result has been obtained;
- the user asks what may cause a biological observation;
- several plausible mechanisms or confounders compete;
- a proposed next experiment must distinguish explanations rather than merely generate another correlation.

## Core rule

> A hypothesis can be ranked first without being causally identified.

Never translate `rank = 1` into `cause established`.

## Inputs

Accept any subset of:

- frozen target claim;
- experimental-unit audit;
- provenance and confounder graph;
- independent-replication search;
- executed analysis results;
- methods and supplementary information;
- author correspondence;
- prior hypotheses and negative results.

Missing evidence must remain explicit.

## Hypothesis classes

Every ranking must consider, where applicable:

- `direct_causal_effect`: the candidate variable changes the later phenotype;
- `mediated_causal_effect`: the candidate acts through one or more intermediates;
- `shared_upstream_state`: a common cause drives both candidate and phenotype;
- `state_marker_only`: the candidate marks a broader cell state without being load-bearing;
- `reverse_or_contemporaneous_coupling`: the measured phenotype or stimulation history influences the candidate measurement;
- `technical_confounding`: batch, day, plate, library, imaging, processing, or identity structure explains the association;
- `selection_or_measurement_bias`: filtering, missingness, normalization, or outcome-dependent measurement creates the association;
- `chance_or_overfitting`: the apparent result is sampling noise or analysis flexibility;
- `small_real_effect`: the association is real but too small or context-specific to support the intended biological interpretation.

Do not omit a serious alternative merely because it is less interesting.

## Evidence levels

Use the shared F0–F5 scale:

- **F0:** assertion or model preference;
- **F1:** label or repository metadata;
- **F2:** methods, supplement, or documented analysis;
- **F3:** machine-checkable result, executable consistency, or independent public-data computation;
- **F4:** author or laboratory confirmation tied to the exact question;
- **F5:** independent biological replication or an identifying intervention/design.

Mechanistic plausibility does not increase causal-identification level by itself.

## Required workflow

### 1. Freeze the target claim

Record:

- candidate variable;
- phenotype;
- temporal order;
- biological system;
- intended claim level;
- exact scope of observed evidence.

### 2. Import upstream constraints

Carry forward without weakening:

- unresolved experimental-unit semantics;
- provenance gaps;
- high-risk or aliased confounders;
- replication type and temporal mismatch;
- effect size and uncertainty;
- blocked claim levels.

### 3. Generate competing hypotheses

Create a bounded hypothesis set. Each item must contain:

- exact statement;
- mechanism class;
- evidence for;
- evidence against;
- unresolved assumptions;
- predicted observations;
- at least one falsifier;
- one discriminating test or evidence request;
- current evidence level;
- rank and priority score.

### 4. Score evidence dimensions

Score each hypothesis from 0 to 4 on:

- `temporal_fit`;
- `experimental_unit_fit`;
- `cross_dataset_support`;
- `confounder_resilience`;
- `mechanistic_coherence`;
- `intervention_support`;
- `falsifiability`;
- `effect_relevance`.

Also score `uncertainty_penalty` from 0 to 4. The machine-readable record must explain every non-zero score.

Scores prioritize inquiry; they do not mathematically prove causality.

### 5. Compare hypotheses pairwise

For every load-bearing pair, state the observation that would favor one over the other.

Example:

`direct causal effect` versus `state marker only` requires evidence that changing the candidate while holding the broader state comparable changes the phenotype. The record may describe this distinction conceptually but must not provide operational biological manipulation instructions.

### 6. Apply causal-identification gate

A hypothesis may be marked `causally_identified_with_limits` only when all are true:

- temporal order matches the target claim;
- the experimental unit is established;
- an identifying intervention, natural experiment, or defensible causal design is documented;
- major confounders are separable or controlled;
- evidence level is F4 or F5;
- the result is independently reproduced or has equivalent strong validation;
- the claimed scope does not exceed the design.

Otherwise use:

- `supported_explanation`;
- `plausible`;
- `weakened`;
- `not_identified`;
- `blocked`.

### 7. Select the next evidence action

Rank actions by expected information gain and feasibility. Favor the smallest action that distinguishes the top competing hypotheses.

Examples include:

- resolve missing metadata;
- analyse an independent temporally compatible dataset;
- test a prespecified negative control computationally;
- obtain author clarification;
- prepare a non-operational validation brief for an authorized laboratory;
- stop when no safe or informative action exists.

## Fail-closed rules

Return `BLOCK` when:

- a correlation is labelled as an established cause;
- the top-ranked hypothesis has no falsifier or discriminator;
- a pathway diagram is treated as intervention evidence;
- cells, reads, wells, plates, libraries, or runs substitute for biological replication;
- a temporally reversed dataset is represented as direct replication;
- unresolved aliased confounding is ignored;
- a tissue, clinical, or therapeutic claim is derived from cell-level association alone;
- operational biological manipulation is proposed without an authorized institutional pathway.

Return `RANKED_NOT_IDENTIFIED` when hypotheses can be prioritized but no causal effect is identified.

Return `IDENTIFIED_WITH_LIMITS` only when the causal-identification gate is fully satisfied.

## Required output

Produce a record conforming to `schemas/causal-hypothesis-ranking.schema.json` and a human-readable summary containing:

1. frozen target claim;
2. inherited evidence constraints;
3. ranked hypothesis table;
4. evidence for and against each hypothesis;
5. pairwise discriminators;
6. causal-identification status;
7. blocked claims;
8. next highest-information action;
9. safety boundary.

## Current GSE141064 / GSE94383 expectation

For the current `Nfkbia` case:

- GSE141064 provides a limited exploratory association between basal expression and later `Tnf-mCherry` response;
- exact biological independence for Batch 8_8 is not established;
- GSE94383 provides F3 conceptual pathway triangulation between prior NF-kB activity and post-LPS `Nfkbia` expression;
- GSE94383 does not match the original temporal predictor claim;
- no intervention identifying a direct `Nfkbia` effect is present;
- technical and latent-state explanations remain live.

Expected overall verdict: `RANKED_NOT_IDENTIFIED`.

Causal, tissue, clinical, and therapeutic claims remain blocked.
