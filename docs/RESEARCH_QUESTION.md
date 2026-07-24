# Research Question

## Primary question

**Can X-Cell or another perturbation-response model learn phase-response curves
and identify a measurable time window in which an intervention maximizes
target-state reachability while minimizing identity loss, toxicity, and
irreversible transition risk?**

## Narrow falsifiable claim

The project does not begin with aging reversal. It begins with a smaller proposition:

> Adding a measurable pre-intervention phase variable improves held-out
> prediction of cellular perturbation responses compared with a matched
> static-state baseline.

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

## Supported phase variables in v0.1

1. cell-cycle phase;
2. metabolic-state proxy;
3. calcium-signalling state, when measured;
4. membrane-potential state, when measured;
5. circadian phase, when experimentally controlled.

Collection timepoint, perturbation duration, donor, batch, and prior
perturbation or recovery history are important covariates, but they are not
candidate-qualifying phase keys in the v0.1 transition record.

A phase variable is admitted only when its `status`, `label`, measurement or
inference `method`, `confidence`, and per-variable `observed_at` timestamp are
recorded. The top-level `observed_at` records the transition-record observation
time and does not replace the per-phase timestamp.

## Why this matters

An endpoint-only predictor can conflate biologically different interventions. A
perturbation applied to cells with similar transcriptomes but different dynamic
phases may lead to different trajectories. If phase conditioning improves
held-out prediction, it shows that phase provides useful predictive context in
the tested setting.

Predictive improvement alone does not establish that timing is causal.
Confounding, proxy variables, or leakage can produce the same pattern. Causal
interpretation requires controlled intervention or an appropriately designed
quasi-experimental study consistent with the causal graph.

## Required negative result

The project must accept that phase information may provide no useful improvement
after controlling for state, batch, dose, duration, and leakage. That outcome
falsifies or narrows the hypothesis rather than being reframed as success.
