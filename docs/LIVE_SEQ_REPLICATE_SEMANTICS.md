# Live-seq replicate semantics overlay

This note records a model correction for the 17-cell GSE141064 `Raw264.7_G9` / Batch `8_8` cohort.

The correction comes from private researcher correspondence received on 2026-08-12. No direct quote or public attribution is included here. The correspondence is therefore treated as an **external semantic evidence layer**, not as a publicly reproducible primary source.

## What changed

The previous state was intentionally conservative:

```text
cell != independent experimental unit by default
plate label != biological replicate
replicate semantics unresolved
```

The external clarification splits that single blocker into two different questions.

### 1. Cell heterogeneity

For an analysis whose target is **cell heterogeneity**, the clarified working semantics are:

```text
cell = biological replicate
plate = sub-batch
```

This resolves the narrow question of what unit may represent biological replication for cell-level heterogeneity analysis.

### 2. Generalization / held-out evaluation

The clarification does **not** establish plate as an independent biological replicate and does not establish a separate independent culture, day, animal, donor, or other held-out biological unit.

Therefore:

```text
plate holdout != demonstrated biological generalization
held-out generalization unit = unresolved
```

No confirmatory generalization claim is unlocked by this clarification alone.

## Plate-effect gate

The clarified default is to treat plate as a sub-batch and not promote it to an experimental unit unless the data show a non-negligible plate-associated effect.

The next discriminating analysis is therefore:

```text
quantify plate-associated variation
        ↓
negligible? ── yes → cell-level heterogeneity analysis may ignore plate as a major nuisance factor
        │
        no
        ↓
model / stratify / sensitivity-check plate explicitly
```

This is a sensitivity and nuisance-structure question, not evidence that plates are independent biological replicates.

## Evidence separation

Two evidence layers remain distinct:

1. `technical-groups.real.v0.1.json` — what the pinned public metadata directly expose;
2. `replicate-semantics.external.v0.1.json` — contextual semantics learned from external researcher correspondence.

The second layer must never be rewritten as if it were derivable from the CSV itself.

## Current decision

```text
cell heterogeneity replicate semantics: RESOLVED
plate semantics: SUB_BATCH
plate-as-biological-replicate: REJECTED
plate effect: MUST BE CHECKED IF MATERIAL
held-out biological generalization unit: UNRESOLVED
confirmatory preregistration: NOT UNLOCKED
```

## Authority

Research-only. This note authorizes no biological experiment, clinical use, deployment, or causal claim.
