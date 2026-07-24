# Reproducibility

## Scope

This guide reproduces the repository's technical checks and synthetic demonstration. It does not reproduce a biological effect and does not authorize an experiment.

## Version identity

Record these independently for every result:

| Layer | Current development value |
|---|---|
| Software | `0.1.0-dev` |
| Transition schema | `kairos.transition.v0.1` |
| CI evidence schema | `kairos.ci-evidence.v0.1` |
| Synthetic protocol | `kairos.cell-cycle-ablation.v0.1` |
| Synthetic dataset | `kairos.synthetic-phase-benchmark.v0.1` |
| Biological model | not implemented |

## Environment

- Python 3.10 or newer;
- an isolated virtual environment is recommended;
- no GPU is required for the reference validator or synthetic benchmark.

## Reproduce the validator

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
python -m compileall -q kairos_gate tests scripts
```

Expected CLI boundary:

```text
RESEARCH_ONLY ... classification=CANDIDATE_WINDOW; NOT EXPERIMENT AUTHORIZATION
```

## Reproduce the synthetic benchmark

```bash
python scripts/run_phase_benchmark.py testdata/phase-window-tiny.json
```

The command emits machine-readable JSON. The dataset is deliberately synthetic and exists only to verify that the baseline, phase-conditioned, ablation, and shuffle-control pipeline behaves as declared.

## Exact-head CI evidence

In CI, `KAIROS_EXACT_HEAD` must equal `git rev-parse HEAD`. The evidence gate also checks:

- unit tests;
- canonical record validation;
- compilation;
- installed-wheel execution outside the checkout;
- synthetic benchmark execution;
- research-only authority fields.

A green technical verdict means only `TECHNICALLY_REPRODUCIBLE` for that exact commit.

## Randomness

The v0.1 synthetic benchmark contains no stochastic training. Any later model must record:

- random seeds;
- split identifiers;
- library and accelerator versions;
- deterministic settings where available;
- all deviations from the preregistered protocol.

## Data provenance classes

Every dataset and field must be identified as one of:

- `measured`;
- `inferred`;
- `synthetic`;
- `unavailable`.

Synthetic fixtures must never be described as X-Cell, X-Atlas, patient, clinical, or experimental data.

## Known limitations

Technical reproduction does not establish biological validity, generalization, causality, toxicity, clinical utility, or safety. Distribution shift and measurement error remain open research risks.