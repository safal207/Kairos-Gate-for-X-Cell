# Kairos Gate for X-Cell

**Research-only protocol for phase-conditioned cellular transition assessment.**

X-Cell asks what a perturbation may cause. Kairos Gate asks **when** that
perturbation becomes a justified candidate transition window while preserving
identity, limiting risk, and exposing uncertainty.

> `CANDIDATE_WINDOW` is a research classification, not biological authorization.

## Research question

Does adding a measurable pre-intervention phase variable improve held-out
cellular perturbation-response prediction relative to a matched static-state
baseline?

The first proposed comparison is:

```text
static baseline:
cell state + perturbation -> response

phase-conditioned:
cell state + perturbation + measurable phase -> response
```

A positive predictive result does not establish causality. Controlled or valid
quasi-experimental evidence is required before making a causal timing claim.

## Why Kairos

The same perturbation may have different consequences in different measurable
biological phases. Candidate examples include:

- cell-cycle phase;
- calcium-signalling state;
- membrane-potential state;
- metabolic-state proxy;
- experimentally controlled circadian phase.

The v0.1 record accepts only versioned supported phase keys. Philosophical
metaphors are not admitted as biological variables. Qualifying phase evidence
must be timestamped at or before the transition record time.

## Research-only classifications

- `CANDIDATE_WINDOW` — current model-level criteria support further research;
- `WAIT` — timing or expected effectiveness is below the current threshold;
- `EXCLUDE` — a hard identity, toxicity, or reversibility boundary is violated;
- `INSUFFICIENT_EVIDENCE` — supported phase evidence or evidence quality is inadequate.

Hard exclusions take precedence over missing evidence. A known high-risk record
cannot be softened into `INSUFFICIENT_EVIDENCE`.

## Current v0.1 components

- strict Draft 2020-12 transition schema;
- complete date-time format and pre-intervention timestamp validation;
- strict JSON loading that rejects `NaN` and `Infinity`;
- deterministic research-only validator;
- canonical synthetic transition example;
- FAIR-oriented reproducibility, Model Card, and Data Card templates;
- preregistered synthetic phase-ablation and shuffle-control benchmark;
- versioned TIP-to-Kairos handoff schema, example, negative fixtures, and validator;
- regression tests for safety, schema, provenance, and authority boundaries;
- exact-head CI evidence artifact;
- installed-wheel smoke tests outside the repository checkout;
- causal graph, safety, non-claims, citation, and contribution documentation.

## Repository layout

```text
README.md
CHANGELOG.md
kairos_gate/                 deterministic validators
kairos_gate/schemas/         packaged runtime JSON Schemas
schemas/                     public schema mirrors
examples/                    canonical research records
protocols/                   preregistered research protocols
testdata/                    synthetic and negative fixtures
tests/                       regression tests
scripts/                     benchmark, handoff, and exact-head evidence runners
docs/
  RESEARCH_QUESTION.md
  MINIMAL_EXPERIMENT.md
  HYPOTHESIS_MAP.md
  CAUSAL_GRAPH.md
  REPRODUCIBILITY.md
  MODEL_CARD_TEMPLATE.md
  DATA_CARD_TEMPLATE.md
  TIP_HANDOFF.md
  SAFETY_AND_NON_CLAIMS.md
  PHILOSOPHICAL_ORIGIN.md
  ECOSYSTEM_BRIDGE.md
  XCELL_OUTREACH_DRAFT.md
  ROADMAP.md
```

## Quick start

Install the package and its runtime dependency first:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
python scripts/validate_handoff.py examples/tip-kairos-handoff.json
python scripts/run_phase_benchmark.py testdata/phase-window-tiny.json
```

Expected transition CLI shape:

```text
RESEARCH_ONLY ... classification=CANDIDATE_WINDOW; NOT EXPERIMENT AUTHORIZATION
```

The synthetic benchmark must label itself `SUPPORTED_SYNTHETIC_ONLY`; this is a
pipeline-control result and not evidence of a biological phase effect.

To reproduce the exact-head evidence flow inside a Git checkout:

```bash
export KAIROS_EXACT_HEAD="$(git rev-parse HEAD)"
python scripts/run_ci_evidence.py
python scripts/run_ci_evidence.py --enforce
```

The project uses the third-party `jsonschema` package, declared in
`pyproject.toml`, to enforce complete Draft 2020-12 contracts and date-time
formats. Schemas are packaged with the installed validators and checked against
the public repository mirrors in regression tests.

See [Reproducibility](docs/REPRODUCIBILITY.md) for version and provenance rules.

## Relationship to the wider protocol family

The primary internal bridge is [Transition Intelligence Protocol](https://github.com/safal207/transition-intelligence-protocol):

```text
IFP: Is the initial state sufficiently known?
TIP: Which transition is justified next?
Kairos Gate: Is this a candidate phase window for that transition?
```

The versioned bridge is documented in [TIP → Kairos Handoff](docs/TIP_HANDOFF.md).
Additional roles are documented in [Ecosystem Bridge](docs/ECOSYSTEM_BRIDGE.md),
including T-Trace, CML, LiminalDB, PythiaLabs, ProofPath, LRI, SOMA, and Lifetra.

## Scope boundary

Kairos Gate does **not** claim to:

- reverse aging;
- provide medical advice or treatment;
- establish that meditation, sound, music, intention, or an undefined information field directly reprograms cells;
- prove biological safety from transcriptomic prediction;
- authorize wet-lab, animal, or human experimentation;
- represent or speak for Xaira Therapeutics or the X-Cell authors.

See [Safety, Ethics, and Non-Claims](docs/SAFETY_AND_NON_CLAIMS.md).

## Roadmap

1. Stabilize and review the v0.1 protocol contract.
2. Publish FAIR model/data-card and reproducibility templates.
3. Preregister and execute the synthetic phase-ablation and phase-shuffle pipeline test.
4. Stabilize the reciprocal TIP-to-Kairos interoperability profile.
5. Evaluate one suitable open perturbation-response dataset.
6. Test BioNeMo/Geneformer feasibility only after the open-data benchmark is specified.
7. Approach X-Cell and NVIDIA with a narrow, reproducible technical question.

See [Roadmap](docs/ROADMAP.md) and [GitHub roadmap issue](https://github.com/safal207/Kairos-Gate-for-X-Cell/issues/11).

## License and citation

The repository is licensed under MIT. Citation metadata is provided in
`CITATION.cff`.
