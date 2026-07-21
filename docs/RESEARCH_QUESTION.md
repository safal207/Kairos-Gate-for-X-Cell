# Research Question

## Primary question

**Can X-Cell or another perturbation-response model learn phase-response curves and identify a measurable time window in which an intervention maximizes target-state reachability while minimizing identity loss, toxicity, and irreversible transition risk?**

## Narrow falsifiable claim

The project does not begin with aging reversal. It begins with a smaller proposition:

> Adding a measurable pre-intervention phase variable improves held-out prediction of cellular perturbation responses compared with a matched static-state baseline.

## Proposed conditional model

```text
P(next state | current state, perturbation)
```

becomes:

```text
P(next state at horizon h |
  current state,
  measurable phase,
  perturbation,
  recent intervention history)
```

## Candidate phase variables

1. cell-cycle phase;
2. collection timepoint and perturbation duration;
3. metabolic-state proxy;
4. calcium-signalling state, when measured;
5. membrane-potential state, when measured;
6. circadian phase, when experimentally controlled;
7. prior perturbation or recovery history.

A variable is admitted only when its measurement, inference method, confidence, and timestamp are recorded.

## Why this matters

An endpoint-only predictor can conflate biologically different interventions. A perturbation applied to cells with similar transcriptomes but different dynamic phases may lead to different trajectories. If phase conditioning improves prediction, timing is not merely metadata; it is part of the causal context.

## Required negative result

The project must accept that phase information may provide no useful improvement after controlling for state, batch, dose, duration, and leakage. That outcome falsifies or narrows the hypothesis rather than being reframed as success.
