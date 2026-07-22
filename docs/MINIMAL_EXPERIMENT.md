# Minimal Phase-Conditioned Experiment

## Goal

Test whether one explicit phase variable improves prediction of a perturbation
response without claiming therapeutic benefit or causal timing.

## Recommended first variable

**Cell-cycle phase** is the preferred starting point because it is commonly
inferred from single-cell RNA measurements and can be evaluated retrospectively.

## Dataset requirements

A suitable dataset should contain or permit reconstruction of:

- control and perturbed cells;
- perturbation identity;
- cell context;
- perturbation duration or collection time;
- cell-cycle phase or phase-score confidence;
- response measurements at one or more horizons;
- environment, donor, batch, and replicate identifiers.

## Leakage-resistant split

1. held-out biological replicate;
2. held-out perturbation where feasible;
3. held-out cell context in a later benchmark;
4. no post-intervention measurement may enter pre-intervention phase features;
5. preprocessing and phase inference must be fitted without test-set leakage.

## Models

### Baseline

```text
current state + perturbation -> response
```

### Phase-conditioned

```text
current state + perturbation + phase token -> response
```

The architecture should remain as constant as possible so the comparison
isolates the predictive value of phase context.

### Negative controls

```text
phase ablation:
current state + perturbation + removed phase -> response

phase shuffle:
current state + perturbation + randomly reassigned phase -> response
```

The phase-conditioned gain should disappear or materially weaken under a
properly constructed phase shuffle. A gain that survives shuffling is evidence
of leakage, proxy use, an invalid control, or another unresolved mechanism—not a
successful Kairos result.

## Primary endpoint

Improvement on a predeclared held-out response metric relative to the
static-state baseline.

## Secondary endpoints

- calibration of phase-specific uncertainty;
- stability across replicates;
- target-state reachability;
- cell-identity preservation proxy;
- toxicity or stress-response proxy;
- ablation of individual phase features;
- phase-stratified performance and failure cases.

## Initial success criterion

A credible predictive result requires:

1. predeclared split and metric;
2. reproduction across at least two seeds or folds;
3. no detected post-intervention leakage;
4. phase contribution surviving matched ablation;
5. phase contribution failing the phase-shuffle negative control;
6. environment, donor, batch, and replicate handled consistently with the causal graph;
7. uncertainty and negative cases reported;
8. no causal, therapeutic, or clinical conclusion.

A positive held-out result demonstrates predictive usefulness only. Causal
timing requires controlled or appropriately designed quasi-experimental
evidence.

## Future sequence experiment

Only after the single-step benchmark should the project test sequences:

```text
prepare -> perturb -> observe -> recover -> reassess
```

A sequence model must distinguish elapsed time from state readiness and record
every intervention and observation boundary.
