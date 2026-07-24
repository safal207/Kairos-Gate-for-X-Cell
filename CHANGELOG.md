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
- FAIR-oriented reproducibility, model-card, and data-card templates.

### Safety

- `CANDIDATE_WINDOW` is explicitly not experiment authorization;
- non-standard JSON constants such as `NaN` and `Infinity` are rejected;
- post-record phase evidence cannot qualify a candidate window;
- predictive usefulness is separated from causal evidence.

## 0.1.0 — planned

Initial reviewed research-protocol release. No biological efficacy, therapeutic, clinical, or safety claim is associated with this version.
