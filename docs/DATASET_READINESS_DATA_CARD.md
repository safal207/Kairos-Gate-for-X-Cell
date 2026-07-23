# Dataset Readiness Scanner Data Card

## Scope

This card describes the data contracts consumed by `kairos.dataset-readiness.v0.1` and the evidence the scanner can produce.

## Intended use

- pre-model data linkage checks;
- cohort-selection leakage checks;
- downstream-label availability checks;
- repeated-measurement split checks;
- replicate-semantics and effective-unit gates;
- provenance and reuse-term checks;
- machine-readable blocked or ready evidence.

## Out of scope

- estimating biological effects;
- validating biological ground truth;
- selecting treatments or molecules;
- safety or toxicity assessment;
- clinical decisions;
- experiment design or authorization.

## Required inputs

### Manifest

A Draft 2020-12 JSON document containing:

- dataset identifier and version;
- declared adapter;
- one metadata source and one matrix source;
- immutable or digest-bound source references;
- reuse status;
- minimum independent-unit threshold.

### Metadata

A CSV or gzip-compressed CSV readable by the declared adapter.

### Matrix

A CSV or gzip-compressed CSV whose first column is the feature identifier and remaining header columns are sample identifiers.

## Canonical record

Each adapter emits, for every metadata row:

- `sample_id`;
- `selected`;
- `response_available`;
- `independent_unit`;
- `repeated_identity`.

The readiness engine also receives complete metadata and matrix identifier lists and one replicate-semantics classification.

## Sensitive attributes

The v0.1 canonical contract contains no required demographic, clinical, or directly identifying human fields. Dataset-specific adapters must not add such fields to evidence unless a future reviewed schema explicitly requires them.

## Known limitations

- adapter correctness remains dataset-specific;
- a verified label in a manifest is not sufficient by itself to establish biological replicate semantics;
- exact identifier linkage cannot prove source data correctness;
- effective-unit counts cannot prove statistical power;
- a ready result is a technical preregistration gate, not biological validation;
- source availability may change even when downloaded bytes remain digest-verifiable.

## Current fixtures

### Live-seq tiny fixture

Exercises response-independent cohort selection and repeated-cell leakage detection. Its expected result is blocked.

### Generic synthetic fixture

Exercises the manifest-configured tabular adapter with two verified independent units. Its expected result is `READY_FOR_PREREGISTRATION` and is not biological evidence.

## Evidence retention

The dedicated GitHub Actions workflow stores ready, blocked, and attestation JSON files for 30 days. The attestation binds the exact head, Git tree, stack base, and SHA-256 digests of both results.
