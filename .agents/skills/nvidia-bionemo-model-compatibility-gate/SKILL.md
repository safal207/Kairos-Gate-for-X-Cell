# NVIDIA BioNeMo Model Compatibility Gate v0.2

## Purpose

Decide whether a biological model or agent tool is compatible with a dataset and scientific question before any model output is interpreted as evidence.

This gate separates:

1. **transport compatibility** — the input can technically be submitted;
2. **domain compatibility** — modality, organism, tissue/cell context and temporal design match the model's documented domain;
3. **question compatibility** — the model output can address the frozen scientific question;
4. **evidence contribution** — the run can support only the claim level explicitly allowed by the record.

A technically successful model call is never equivalent to biological validation.

## Required inputs

- frozen scientific question;
- dataset identity and hashes;
- organism/species;
- modality and input representation;
- biological and technical unit semantics;
- temporal design;
- exact model/checkpoint/runtime identity;
- official model-card or tool documentation;
- preprocessing and transformation lineage;
- training or benchmark overlap assessment;
- deployment, license and compute constraints;
- requested claim level.

## Verdicts

- `ACCEPT_WITH_LIMITS`
- `SPECIES_COMPATIBILITY_HOLD`
- `MODALITY_COMPATIBILITY_HOLD`
- `TEMPORAL_COMPATIBILITY_HOLD`
- `TRAINING_OVERLAP_HOLD`
- `QUESTION_NOT_APPLICABLE`
- `BLOCK`

`ACCEPT_WITH_LIMITS` permits a bounded computational run. It does not identify causality, establish biological-unit prediction, authorize physical biology, or support clinical/therapeutic claims.

## Fail-closed rules

- Human-trained single-cell checkpoints applied to mouse data require explicit transfer validation; ortholog mapping alone is insufficient.
- DNA models cannot be used to answer an expression-to-future-phenotype question without a separately frozen genomic hypothesis.
- Protein models cannot be treated as evidence about cell-state prediction without an explicit bridge and validation design.
- Agent orchestration toolkits contribute execution capability, not biological evidence by themselves.
- Unknown checkpoint, runtime, preprocessing, input hash, output hash, or training-overlap status blocks evidence promotion.
- Model confidence, embedding quality, token probability, docking score, or generated sequence plausibility is not biological truth.
- Any transformed species mapping must be recorded and sensitivity-tested.

## Current Nfkbia case

- BioNeMo Agent Toolkit: `ACCEPT_WITH_LIMITS` for orchestration only.
- Geneformer on RAW264.7 mouse cells: `SPECIES_COMPATIBILITY_HOLD`.
- Evo 2: `QUESTION_NOT_APPLICABLE` to the current basal-expression → later-response claim.
- ESM-2 / AMPLIFY: `QUESTION_NOT_APPLICABLE` unless a protein-level question and bridge are frozen.

## Required output

A machine-readable compatibility record plus a Model Evidence Passport for every executed run.

## Safety boundary

This skill is computational and documentary only. It does not provide or authorize physical biological procedures, genetic modification, pathogen work, dosing, implantation, treatment, human experimentation, or clinical decisions.
