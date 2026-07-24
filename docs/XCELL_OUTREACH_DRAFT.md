# Draft X-Cell Research Discussion

## Suggested issue title

**Research question: could intervention timing be modeled as a causal context variable?**

## Suggested body

Hello X-Cell team,

Thank you for releasing the X-Cell research direction and the X-Atlas/Pisces dataset.

I am exploring a small, falsifiable extension question:

> Could X-Cell be evaluated not only as `cell state + perturbation -> response`, but as a phase-conditioned transition model in which measurable pre-intervention timing or phase is part of the causal context?

The hypothesis is that an identical perturbation may represent a different causal intervention when applied during a different measurable state, initially using a bounded variable such as cell-cycle phase.

A minimal benchmark would compare:

```text
baseline: current state + perturbation -> response
phase-conditioned: current state + perturbation + phase -> response
```

The immediate goal would only be to test whether the phase token improves held-out response prediction and calibration. Longer-term questions about target-state reachability, identity preservation, and sequence design would be deferred until that result is established.

I drafted an independent research protocol here:

https://github.com/safal207/Kairos-Gate-for-X-Cell

The repository explicitly makes no therapeutic, aging-reversal, or safety claims and treats all gate outputs as research-only classifications.

Two questions would help determine whether this is useful:

1. Does X-Atlas/Pisces include cell-cycle, collection-time, perturbation-duration, or longitudinal metadata suitable for a retrospective phase-conditioned benchmark?
2. Would a small ablation or adapter exploring phase/context tokens be aligned with the intended X-Cell contribution surface once the inference code and weights are available?

I would be happy to narrow the proposal to a reproducible benchmark or documentation contribution that fits your roadmap.
