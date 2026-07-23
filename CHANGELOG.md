# Changelog

All notable changes to Kairos Gate are recorded here. The project follows semantic versioning for software releases, while schemas, protocols, datasets, and models keep independent versions.

## Unreleased

### Added

- strict Draft 2020-12 transition-record validation;
- supported phase allowlist and pre-intervention timestamp checks;
- research-only deterministic classifications;
- hard safety-exclusion precedence;
- exact-head CI evidence with installed-wheel smoke testing;
- synthetic phase benchmark protocol and negative controls;
- FAIR-oriented reproducibility, model-card, and data-card templates;
- dataset-agnostic readiness manifests, adapters, result schema, and exact-head evidence;
- pinned GSE141064 scanner evidence with historical cohort-equivalence checks;
- deterministic Next Evidence Planner, strict plan schema, CLI, result-digest binding, Live-seq example, and exact-head evidence.

### Changed

- the Dataset Readiness Scanner is now the only implementation of invariant Live-seq readiness rules;
- the canonical Live-seq status is refined from `BLOCKED_INSUFFICIENT_REPLICATES` to `BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED` without changing cohort membership or biological readiness;
- the canonical real-input workflow invokes `kairos audit-dataset` and validates `kairos.dataset-readiness-result.v0.1`;
- historical evidence is preserved and superseded by an additive evidence record rather than rewritten.

### Deprecated

- `scripts/audit_live_seq_gse141064.py` remains only as a positional CLI compatibility shim and emits a deprecation notice;
- direct consumers should migrate to `kairos audit-dataset` with `examples/live-seq-gse141064.dataset-manifest.v0.1.json`.

### Safety

- `CANDIDATE_WINDOW` is explicitly not experiment authorization;
- non-standard JSON constants such as `NaN` and `Infinity` are rejected;
- post-record phase evidence cannot qualify a candidate window;
- predictive usefulness is separated from causal evidence;
- technical plate, index, run, `Date`, and `Probe` labels cannot verify biological replicate semantics;
- scanner readiness never authorizes model fitting, experiments, clinical use, deployment, or merge actions;
- evidence planning never changes the source verdict, accepts evidence automatically, contacts authors, or authorizes downstream actions.

## 0.1.0 — planned

Initial reviewed research-protocol release. No biological efficacy, therapeutic, clinical, or safety claim is associated with this version.
