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
metaphors are not admitted as biological variables.

## Research-only classifications

- `CANDIDATE_WINDOW` — current model-level criteria support further research;
- `WAIT` — timing or expected effectiveness is below the current threshold;
- `EXCLUDE` — a hard identity, toxicity, or reversibility boundary is violated;
- `INSUFFICIENT_EVIDENCE` — supported phase evidence or evidence quality is inadequate.

Hard exclusions take precedence over missing evidence. A known high-risk record
cannot be softened into `INSUFFICIENT_EVIDENCE`.

## Current v0.1 components

- strict Draft 2020-12 transition schema;
- complete date-time format validation;
- deterministic research-only validator;
- canonical synthetic example;
- regression tests for safety, schema, and authority boundaries;
- exact-head CI evidence artifact;
- installed-wheel smoke test outside the repository checkout;
- causal graph and minimal benchmark design;
- safety, ethics, non-claims, citation, and contribution documentation.

## Repository layout

```text
README.md
kairos_gate/                 deterministic reference validator
kairos_gate/schemas/         packaged runtime JSON Schema
schemas/                     public mirror of the transition schema
examples/                    canonical research records
tests/                       regression tests
scripts/                     exact-head CI evidence runner
docs/
  RESEARCH_QUESTION.md
  MINIMAL_EXPERIMENT.md
  HYPOTHESIS_MAP.md
  CAUSAL_GRAPH.md
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
```

Expected successful CLI shape:

```text
RESEARCH_ONLY ... classification=CANDIDATE_WINDOW; NOT EXPERIMENT AUTHORIZATION
```

To reproduce the exact-head evidence flow inside a Git checkout:

```bash
export KAIROS_EXACT_HEAD="$(git rev-parse HEAD)"
python scripts/run_ci_evidence.py
python scripts/run_ci_evidence.py --enforce
```

The project uses the third-party `jsonschema` package, declared in
`pyproject.toml`, to enforce the complete Draft 2020-12 contract and date-time
formats. The schema is packaged with the installed validator and checked against
the public repository mirror in regression tests.

## Relationship to the wider protocol family

The primary internal bridge is [Transition Intelligence Protocol](https://github.com/safal207/transition-intelligence-protocol):

```text
IFP: Is the initial state sufficiently known?
TIP: Which transition is justified next?
Kairos Gate: Is this a candidate phase window for that transition?
```

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
3. Preregister a synthetic phase-ablation and phase-shuffle benchmark.
4. Evaluate one suitable open perturbation-response dataset.
5. Test BioNeMo/Geneformer feasibility only after the benchmark contract is stable.
6. Approach X-Cell and NVIDIA with a narrow, reproducible technical question.

See [Roadmap](docs/ROADMAP.md) and [GitHub roadmap issue](https://github.com/safal207/Kairos-Gate-for-X-Cell/issues/11).

## License and citation

The repository is licensed under MIT. Citation metadata is provided in
`CITATION.cff`.
