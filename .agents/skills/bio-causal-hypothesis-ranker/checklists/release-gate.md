# Bio Causal Hypothesis Ranker — Release Gate v0.1

A causal-hypothesis ranking may be published only when every applicable gate is satisfied.

## Frozen claim

- [ ] Candidate variable is explicit.
- [ ] Phenotype is explicit.
- [ ] Temporal order is explicit.
- [ ] Biological system and intended claim level are explicit.
- [ ] The claim is not strengthened after inspecting candidate outcomes.

## Inherited constraints

- [ ] Experimental-unit findings are carried forward unchanged.
- [ ] Provenance gaps and confounders remain visible.
- [ ] Replication type and temporal mismatch are recorded.
- [ ] Effect size and uncertainty are recorded.
- [ ] Existing blocked claims remain blocked unless new evidence resolves them.

## Competing explanations

- [ ] At least three serious hypotheses are included.
- [ ] Direct causation is not the only biological hypothesis.
- [ ] Shared-state or marker-only explanations are considered.
- [ ] Technical confounding is considered.
- [ ] Chance, overfitting, selection, or small-effect explanations are considered where applicable.
- [ ] No hypothesis is omitted because it is inconvenient.

## Falsifiability

- [ ] Every hypothesis has at least one predicted observation.
- [ ] Every hypothesis has at least one falsifier.
- [ ] Every hypothesis has a discriminating evidence request.
- [ ] Load-bearing hypothesis pairs have explicit distinguishing observations.
- [ ] A rank is not presented as causal identification.

## Identification gate

- [ ] Temporal order matches the target claim.
- [ ] Experimental unit is established.
- [ ] An identifying intervention, natural experiment, or defensible causal design is documented.
- [ ] Major confounders are separable or controlled.
- [ ] Evidence level is at least F4.
- [ ] Independent validation is present.
- [ ] Claimed scope does not exceed the design.

If any identification item is false:

- [ ] `identified` is false.
- [ ] No hypothesis is `causally_identified_with_limits`.
- [ ] Overall verdict is not `IDENTIFIED_WITH_LIMITS`.
- [ ] Causal claim remains `not_established` or `blocked`.

## Safety boundary

- [ ] Mode is `computational_only`.
- [ ] `physical_biology_authorized` is false.
- [ ] Discriminating tests are described as evidence questions, not operational procedures.
- [ ] No culturing, modification, dosing, infection, implantation, treatment, or human-experiment instructions are included.
- [ ] Any physical validation is routed to an authorized institution.

## Reproducibility

- [ ] Ranking conforms to the machine-readable schema.
- [ ] Positive reference ranking validates.
- [ ] False causal-winner fixture fails closed.
- [ ] Exact commit and CI result are recorded.

## Verdict

- [ ] `RANKED_NOT_IDENTIFIED`
- [ ] `IDENTIFIED_WITH_LIMITS`
- [ ] `BLOCK`

Reviewer note:

```text
Top-ranked explanation:
Why it is not yet identified:
Closest competing explanation:
Highest-information discriminator:
Claims still blocked:
```
