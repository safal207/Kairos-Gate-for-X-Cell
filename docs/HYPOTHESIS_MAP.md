# Hypothesis Map

| ID | Hypothesis | Test | Falsification condition | Status |
|---|---|---|---|---|
| H1 | The same perturbation has phase-dependent responses. | Compare conditional response distributions across pre-intervention phases. | Differences vanish after matched controls and correction. | Testable now |
| H2 | A phase token improves held-out response prediction. | Baseline versus phase-conditioned ablation. | No reproducible improvement or worsened calibration. | Primary v0.1 |
| H3 | A bounded candidate window can be estimated. | Estimate a phase-response curve with uncertainty. | The optimum is unstable across replicates or indistinguishable from noise. | After H2 |
| H4 | Small sequenced interventions can outperform one large intervention. | Match total intervention burden across sequential and single exposure. | No benefit, higher risk, or irreproducible trajectory. | Future |
| H5 | Identity-preserving constraints improve transition quality. | Add marker-based identity constraints and test trade-offs. | Constraints do not predict functional preservation or are circular. | Future |
| H6 | Acoustic or mechanical stimulation can be modeled as a phase-conditioned physical perturbation. | Control frequency, amplitude, duration, sham condition, and mechanistic readouts. | No dose-response, no mechanism, or effect fails sham controls. | Exploratory only |

## Evidence levels

- **Observed association** — variables co-vary.
- **Controlled intervention** — one factor is deliberately changed under a matched control.
- **Replicated causal evidence** — intervention effect repeats across independent experiments.
- **Generalized transition rule** — effect transfers to held-out contexts with calibrated uncertainty.

No causal edge should be promoted beyond its evidence level.
