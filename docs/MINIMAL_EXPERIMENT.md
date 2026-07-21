# Minimal Phase-Conditioned Experiment

## Goal

Test whether one explicit phase variable improves prediction of a perturbation response without claiming therapeutic benefit.

## Recommended first variable

**Cell-cycle phase** is the preferred starting point because it is commonly inferred from single-cell RNA measurements and can be evaluated retrospectively.

## Dataset requirements

A suitable dataset should contain or permit reconstruction of:

- control and perturbed cells;
- perturbation identity;
- cell context;
- perturbation duration or collection time;
- cell-cycle phase or phase-score confidence;
- response measurements at one or more horizons;
- batch and replicate identifiers.

## Leakage-resistant split

1. held-out biological replicate;
2. held-out perturbation where feasible;
3. held-out cell context in a later benchmark;
4. no post-intervention measurement may enter pre-intervention phase features.

## Models

### Baseline

```text
current state + perturbation -> response
```

### Phase-conditioned

```text
current state + perturbation + phase token -> response
```

The architecture should remain as constant as possible so the comparison isolates the value of phase context.

## Primary endpoint

Improvement on a predeclared held-out response metric relative to the static-state baseline.

## Secondary endpoints

- calibration of phase-specific uncertainty;
- stability across replicates;
- target-state reachability;
- cell-identity preservation proxy;
- toxicity or stress-response proxy;
- ablation of individual phase features.

## Initial success criterion

A credible result requires:

1. predeclared split and metric;
2. reproduction across at least two seeds or folds;
3. no detected post-intervention leakage;
4. phase contribution surviving a matched ablation;
5. uncertainty and negative cases reported;
6. no therapeutic or clinical conclusion.

## Future sequence experiment

Only after the single-step benchmark should the project test sequences:

```text
prepare -> perturb -> observe -> recover -> reassess
```

A sequence model must distinguish elapsed time from state readiness and record every intervention and observation boundary.
