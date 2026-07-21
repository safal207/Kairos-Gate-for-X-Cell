# Causal Transition Graph

```mermaid
flowchart LR
    S[Pre-intervention cellular state] --> P[Measured dynamic phase]
    E[Environment and batch] --> P
    H[Recent intervention history] --> S
    P --> I[Intervention at phase t]
    S --> I
    I --> R1[Early response]
    R1 --> R2[Later response]
    R2 --> T[Target-state reachability]
    R2 --> ID[Identity preservation]
    R2 --> TX[Toxicity or stress proxy]
    R2 --> RV[Recovery or reversibility]
    T --> G[Kairos research assessment]
    ID --> G
    TX --> G
    RV --> G
    Q[Evidence quality and uncertainty] --> G
```

## Important confounders

- dose and duration;
- cell type and donor;
- batch and replicate;
- baseline viability;
- phase-inference error;
- selection effects after perturbation;
- measurement timepoint;
- post-treatment variables accidentally used as baseline features.

## Counterfactual question

For a cell or matched population in state `S`, what response would be expected under the same perturbation if the measurable phase were different while relevant confounders remained controlled?

This counterfactual cannot be established by a diagram alone. It requires controlled or appropriately designed quasi-experimental data.
