# BioEvidence OS — Master Roadmap

Canonical planning epic: #24

## North star

Build an evidence and governance layer for agentic biology. Scientific models may generate candidate conclusions; Kairos Gate determines which conclusions are supported, limited, unresolved, or blocked.

## Operating principles

1. Biological and technical units remain distinct.
2. New accessions are not automatically independent evidence.
3. Temporal order and identity linkage must match the claim.
4. Association, prediction, and causality are separate levels.
5. Unknown provenance remains explicit.
6. Negative and inconclusive results are retained.
7. Model outputs receive compatibility and evidence boundaries.
8. Scientific review and execution authorization remain separate.
9. Every module has a schema, validator, positive case, negative case, and CI gate.
10. Every accepted conclusion is tied to exact evidence and versioned artifacts.

## Milestone 1 — BioEvidence OS v0.1

Completed:

- [x] Experimental-unit auditor
- [x] Provenance and confounder graph
- [x] Independent-replication finder
- [x] Causal-hypothesis ranker
- [x] Temporal-replication gate
- [x] GSE141064 evidence audit
- [x] GSE94383 conceptual-replication analysis
- [x] Supplementary Table 4 diagnostic
- [x] Direct-replication gap record

In progress:

- [ ] Complete partner-laboratory evidence handoff — #25
- [ ] Freeze and externally review PR #23 — #26

v0.1 release gate:

- final exact-head CI is green;
- no unresolved P0/P1 review findings;
- documentation matches executable behavior;
- every positive contract has a fail-closed misuse case;
- the partner handoff is complete;
- external biology and statistics reviews are requested;
- deferred v0.2 scope is explicit.

After the freeze, PR #23 receives no new major modules.

## Milestone 2 — Model governance v0.2

Tracking: #27

Deliverables:

- NVIDIA BioNeMo model-compatibility gate;
- registry for Geneformer, Evo 2, ESM-2, AMPLIFY, and relevant alternatives;
- species, modality, context, timing, format, license, compute, and domain-shift checks;
- training-overlap assessment;
- Model Evidence Passport;
- reproducible positive and negative examples.

Current boundary:

- BioNeMo Agent Toolkit is an orchestration candidate;
- Geneformer on current mouse data remains on species-compatibility hold;
- sequence models are not evidence for the current expression-to-response claim unless a separate question is frozen.

## Milestone 3 — Independent temporal evidence

Tracking: #28

Target structure:

```text
pre-state measurement
        ↓ linked unit
transition or exposure
        ↓
later response phenotype
```

Deliverables:

- search human macrophage and monocyte datasets;
- require independent biological grouping and technical lineage;
- resolve GSE94383 ID-prefix semantics;
- retain rejected candidates and reasons;
- refresh the direct-replication gap when evidence changes.

Success means either an eligible external dataset with a frozen analysis contract or a complete updated gap record. Eligibility is never weakened to obtain a positive candidate.

## Milestone 4 — Product MVP

Tracking: #29

User flow:

1. Enter an accession, DOI, or evidence package.
2. Resolve study identity and source files.
3. Run evidence contracts.
4. Display experimental units, provenance, timing, replication, causal hypotheses, model compatibility, and claim boundaries.
5. Export machine-readable and human-readable evidence reports.

Reference demo: GSE141064 and GSE94383.

## Milestone 5 — Publication and partnerships

Tracking: #30

Working report:

**Why Cell Count Is Not Replication: An Executable Evidence Audit of Longitudinal Single-Cell Studies**

Deliverables:

- manuscript and methods;
- schemas, validators, fixtures, and reproducibility instructions;
- exact evidence hashes;
- limitations and negative findings;
- architecture diagram and demo;
- biology review and statistics review;
- outreach to study authors, scientific advisers, partner laboratories, and AI-for-science teams;
- NVIDIA BioNeMo and NVIDIA Inception positioning.

## Milestone 6 — Business modes

Potential products:

- biotech evidence audit before expensive validation;
- academic study and supplement audit;
- journal-review evidence package;
- investor and funder scientific due diligence.

## Personal learning track

Learn only what strengthens current decisions:

- cell biology and inflammatory signaling;
- single-cell and live-cell measurement;
- experimental design and replication;
- causal reasoning, bootstrap, multiple testing, and external validation;
- biological foundation models, embeddings, domain shift, and training overlap.

Cadence:

```text
30 minutes theory
+ 60 minutes applied to a live project decision
```

## Working rhythm

Daily:

- one evidence gap;
- one testable artifact;
- no unrelated feature expansion.

Weekly:

- what became supported;
- what weakened or became blocked;
- what remains unknown;
- which action has highest information gain;
- which issue must close before new work starts.

Monthly:

- refresh roadmap, backlog, risk register, dataset registry, and model registry;
- request at least one external expert interaction;
- publish one public artifact or documented negative result.

## Immediate sequence

1. Complete #25.
2. Freeze and review PR #23 through #26.
3. Start v0.2 in a separate branch through #27.
4. Continue dataset discovery through #28.
5. Build the MVP through #29 after contracts stabilize.
6. Prepare publication and outreach through #30.
