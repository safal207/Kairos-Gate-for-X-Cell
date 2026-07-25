---
name: bio-partner-lab-evidence-handoff
description: Convert a validated computational evidence gap into a non-operational handoff for scientific review by an authorized partner laboratory.
version: 0.1.0
status: experimental
---

# Bio Partner Laboratory Evidence Handoff

## Purpose

Prepare a bounded evidence contract that an authorized scientific institution can review when public data cannot resolve a biological question.

The handoff defines **what evidence is needed**, not **how to physically perform biological work**.

It must never include culturing conditions, reagent recipes, concentrations, dosing, timings for physical manipulation, genetic-modification steps, infection procedures, implantation, treatment instructions, or human experimentation procedures.

## Trigger

Use when:

- a direct-replication gap has been established;
- competing hypotheses remain distinguishable in principle;
- public data are insufficient;
- a partner laboratory, scientific advisor, or institutional review is the next valid step;
- the evidence question can be stated without operational wet-lab instructions.

## Required inputs

Import without weakening:

- frozen target claim;
- experimental-unit audit;
- provenance and confounder graph;
- independent-replication classification;
- temporal-replication gate;
- causal-hypothesis ranking;
- effect sizes, uncertainty, negative findings, and blocked claims;
- governance and safety constraints.

## Core rule

> The handoff specifies an evidence contract, not an execution protocol.

A laboratory must independently design and approve any physical methods under its own scientific, ethical, biosafety, legal, and quality systems.

## Required handoff sections

### 1. Evidence question

State:

- the candidate variable;
- the later phenotype;
- the required temporal order;
- the biological system;
- the exact hypotheses to distinguish;
- the decision that the evidence could change.

### 2. Experimental-unit contract

Define the smallest independently assigned or sampled biological unit.

Require:

- biological-source identifiers;
- unit-to-cell lineage;
- condition assignment at the biological-unit level;
- separation of cells, wells, plates, libraries, and runs from biological replication;
- enough independent units to estimate uncertainty at the biological-unit level;
- a documented rationale from the partner's statistician or methodologist.

The handoff must not prescribe a numeric sample size as an operational instruction. It may require a prospective power or precision justification by the authorized partner.

### 3. Temporal and identity contract

Require a machine-auditable chain:

```text
biological source
  -> independent experimental unit
  -> cell or longitudinal unit identity
  -> pre-transition molecular state
  -> transition exposure record
  -> later phenotype
  -> assay and analysis outputs
```

Pre-state must precede the transition. Later phenotype must link to the same cell or defensible longitudinal unit.

### 4. Competing-model contract

Freeze model families before outcome inspection:

1. candidate-only model;
2. broader baseline-state model;
3. technical-confounder model;
4. combined model;
5. prespecified negative controls.

The partner may propose scientifically justified changes, but every change must be versioned before outcome analysis.

### 5. Data-return contract

Require de-identified, lawful, machine-readable outputs sufficient to reconstruct:

- biological and technical lineage;
- exclusions and missingness;
- exact timestamps or ordered phases;
- raw or minimally processed measurements where permitted;
- normalization and transformation provenance;
- model inputs, outputs, uncertainty, and diagnostics;
- deviations and superseding decisions;
- checksums and immutable source references.

### 6. Decision matrix

State observations that would:

- strengthen shared-upstream-state explanation;
- strengthen direct candidate effect;
- strengthen marker-only interpretation;
- strengthen technical-confounding interpretation;
- support a small context-specific effect;
- support null, instability, or overfitting.

Do not turn a single positive result into a tissue, clinical, or therapeutic claim.

### 7. Stop and hold rules

The handoff must require `HOLD` when:

- biological independence cannot be reconstructed;
- pre-state is measured after the transition;
- identity linkage breaks;
- condition is aliased with batch or operator;
- exclusions are outcome-dependent or undocumented;
- the frozen analysis is changed after outcome inspection without a superseding record;
- approvals, competence, containment, consent, or data-governance requirements are unresolved;
- adverse or unexpected conditions activate the partner institution's stop criteria.

### 8. Governance

Require review by the appropriate authorized institution, including as applicable:

- principal investigator;
- domain biologist;
- statistician or quantitative methodologist;
- biosafety authority;
- ethics or human/animal research authority;
- data-protection and governance authority;
- quality or reproducibility reviewer.

The handoff does not determine which approvals apply; the partner institution must determine and document them before execution.

## Verdicts

- `READY_FOR_PARTNER_SCIENTIFIC_REVIEW`: computational package is coherent enough for an authorized institution to review, but physical work is not authorized.
- `HOLD`: information, governance, unit, timing, identity, or analysis requirements remain incomplete.
- `BLOCK`: the request contains unsafe operational instructions, bypasses institutional oversight, or claims physical/clinical authorization.

## Fail-closed rules

Return `BLOCK` when:

- physical methods, recipes, doses, concentrations, biological modification, infection, implantation, treatment, or human experimentation instructions are included;
- the package states or implies that AI approval authorizes laboratory execution;
- institutional approvals or qualified supervision are bypassed;
- the biological unit is replaced with cells, wells, plates, libraries, reads, or runs;
- post-transition measurements are accepted as pre-state;
- clinical or therapeutic claims are allowed from the proposed cell-level evidence.

Return `HOLD` when the handoff is scientifically incomplete but not unsafe.

## Required output

Produce a record conforming to `schemas/partner-lab-evidence-handoff.schema.json` and a human-readable evidence brief containing:

1. frozen question;
2. current evidence and uncertainty;
3. competing hypotheses;
4. biological-unit contract;
5. temporal and identity contract;
6. frozen model comparison;
7. data-return requirements;
8. decision matrix;
9. stop/hold rules;
10. governance gates;
11. prohibited claims;
12. safety boundary.

## Current `Nfkbia` case expectation

The package may be `READY_FOR_PARTNER_SCIENTIFIC_REVIEW` because:

- a direct temporal replication gap is documented;
- the target and competing hypotheses are frozen;
- `Nfkbia` is a strong discovery candidate but not a stable unique driver;
- causal identification remains absent;
- the handoff can request distinguishing evidence without prescribing physical procedures.

Physical execution remains unauthorized until a competent institution independently designs, approves, and owns the study.
