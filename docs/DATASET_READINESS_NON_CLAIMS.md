# Dataset Readiness Scanner: Safety and Non-Claims

## Meaning of a ready result

`READY_FOR_PREREGISTRATION` means only that the declared files, cohort, labels, independent-unit contract, provenance, and reuse status passed the v0.1 technical gate.

It does **not** mean that:

- the dataset is biologically correct;
- the dataset is unbiased or representative;
- the sample size has adequate statistical power;
- a model will generalize;
- an observed association is causal;
- a perturbation is effective or safe;
- a therapeutic or clinical claim is supported;
- a wet-lab, animal, or human experiment is authorized;
- deployment or merge is authorized.

## Meaning of an exploratory result

`EXPLORATORY_ONLY` permits only explicitly labelled technical sensitivity analysis. It must not be presented as confirmatory generalization, verified biological replication, or model readiness.

## Meaning of a blocked result

A blocked result is a positive safety outcome of the scanner: it records the earliest enforced contract boundary that prevents preregistered modelling.

Blocked datasets must not be silently repaired by:

- random cell-level splits;
- treating wells, indexes, plates, runs, or filenames as biological replicates;
- dropping rows because the downstream response is missing;
- allowing repeated measurements of one identity across train and test;
- replacing pinned evidence with mutable branch or `latest` URLs;
- fitting a larger model to compensate for missing experimental units.

## Human authority

All scanner results are `RESEARCH_ONLY`. Human review remains responsible for dataset interpretation, preregistration, statistical design, biological claims, and any decision to conduct experiments.
