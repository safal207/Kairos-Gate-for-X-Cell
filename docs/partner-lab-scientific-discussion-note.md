# BioEvidence OS Partner-Lab Scientific Discussion Note

## Purpose

This note supports an initial scientific conversation with an authorized university, hospital, nonprofit, or contract research laboratory.

It is designed to help both sides decide whether a bounded validation collaboration is scientifically justified. It is not an experimental protocol, an authorization to perform physical work, a clinical recommendation, or a claim that NFKBIA is a validated target.

## Current evidence state

The reference case currently supports only the following bounded conclusions:

```text
GSE141064 cohort reconstruction: technically reproducible
GSE141064 biological replicate semantics: unresolved
GSE94383 pathway-related signal: supported with limits
out-of-sample biological prediction: not established
direct temporal replication: not established
NFKBIA unique causal driver: not identified
tissue, clinical, diagnostic, and therapeutic claims: blocked
physical biological execution: not authorized
```

The purpose of a partner discussion is therefore not to confirm a preferred story. It is to determine what evidence would be required to distinguish competing explanations and whether an authorized institution considers that question worth pursuing.

## What BioEvidence OS contributes

BioEvidence OS provides an evidence-governance layer rather than a wet-lab service. The current package includes:

- exact source and dataset identities;
- immutable repository commit and workflow references;
- experimental-unit audit records;
- provenance and confounder graphs;
- conceptual-versus-direct replication classification;
- deterministic causal-hypothesis ranking;
- machine-readable claim boundaries;
- fail-closed validation behavior;
- negative findings and unresolved unknowns;
- a review record for biology, statistics, and conflicts of interest.

## What the partner institution would contribute

A potential partner would retain authority over its own scientific, ethical, legal, safety, operational, and institutional decisions.

The initial contribution requested from a partner is scientific interpretation, not automatic execution. Useful input may include:

- whether the biological question is meaningful;
- whether the proposed independent unit is scientifically defensible;
- whether timing, lineage, and endpoint identity are sufficiently specified;
- whether the competing explanations are complete enough for review;
- what evidence would distinguish a driver from a state marker;
- whether any proposed validation concept is feasible under the institution's own governance;
- which claims must remain blocked even after a positive result;
- whether the institution has a conflict of interest relevant to the review.

## Reference question

The current reference question is bounded as follows:

> Does a pre-intervention cellular state contain reproducible information about a later inflammatory response, and can any observed NFKBIA-related signal be distinguished from shared upstream state, technical confounding, selection effects, or chance?

This question does not assume that:

- NFKBIA is causal;
- the current datasets establish biological replication;
- a cell-level association generalizes to tissue;
- pathway association implies a drug target;
- a computational result authorizes intervention.

## Competing explanations to preserve

The current inquiry keeps several explanations active:

1. shared upstream cellular state;
2. a direct NFKBIA-related effect;
3. NFKBIA acting only as a state marker;
4. a small context-specific real effect;
5. technical confounding;
6. chance or model instability.

A partner discussion should not collapse these alternatives into one preferred mechanism before appropriate evidence exists.

## Evidence questions for the first meeting

### Experimental unit

- What entity would be independently sampled, assigned, or repeated?
- Which dependencies may exist between cells, cultures, days, plates, imaging sessions, extractions, libraries, or runs?
- What grouping information must be recorded before analysis?
- What effective sample size would the institution consider interpretable for the proposed claim?

### Temporal identity

- Is the predictor measured before the biological transition relevant to the endpoint?
- Is the later endpoint linked to the same biological identity?
- Could a post-transition measurement be mistakenly represented as a basal predictor?
- What timing uncertainty would invalidate the intended interpretation?

### Replication

- Would the proposed evidence be direct replication, conceptual replication, or a technical sensitivity analysis?
- What source, lineage, protocol, or batch independence is required?
- Which similarities are necessary for the result to address the same claim?
- Which differences would make the evidence only conceptually related?

### Causal interpretation

- What observations could distinguish a driver from a correlated state marker?
- Which upstream variables remain plausible common causes?
- Which negative result would weaken the direct-effect hypothesis?
- Which positive result would still be insufficient for a causal claim?

### Statistical integrity

- What is the correct analysis unit?
- Which criteria must be frozen before outcomes are inspected?
- How should missingness, exclusions, multiple comparisons, and selection history be recorded?
- What sensitivity analyses are necessary without being misrepresented as confirmatory evidence?

### Claim boundary

- What conclusion would a positive result actually support?
- What conclusion would remain blocked?
- What language would overstate the evidence?
- What additional review would be required before any downstream decision?

## Proposed evidence handoff

A partner-facing review package should include:

1. **Question contract** — exact claim being evaluated and forbidden stronger claims.
2. **Experimental-unit contract** — independent unit, dependencies, grouping fields, and unresolved semantics.
3. **Temporal contract** — predictor time, endpoint time, identity linkage, and acceptable mismatch.
4. **Provenance contract** — source, transformations, exclusions, versions, and checksums.
5. **Analysis contract** — preregistered or otherwise frozen criteria, models, uncertainty, and stopping rules.
6. **Replication contract** — what counts as direct, conceptual, technical, or failed replication.
7. **Claim contract** — allowed, blocked, and superseded conclusions.
8. **Review contract** — named reviewers, conflicts, verdict, P0/P1/P2 findings, and disposition.

## Expected outputs from an initial collaboration discussion

The first scientific discussion should produce one of the following bounded outcomes:

```text
SCIENTIFIC_QUESTION_RELEVANT
SCIENTIFIC_QUESTION_REQUIRES_REVISION
PUBLIC_EVIDENCE_INSUFFICIENT
PARTNER_REVIEW_NOT_FEASIBLE
CONCEPT_VALIDATION_POSSIBLE_UNDER_INSTITUTIONAL_GOVERNANCE
BLOCKED_BY_EXPERIMENTAL_UNIT
BLOCKED_BY_TEMPORAL_IDENTITY
BLOCKED_BY_CAUSAL_IDENTIFICATION
BLOCKED_BY_ETHICS_SAFETY_OR_POLICY
```

A positive discussion outcome does not authorize physical execution. It only indicates that the institution may consider developing its own governed study plan.

## Suggested 30-minute discussion agenda

1. **5 minutes — Evidence boundary**  
   What is known, unknown, and explicitly blocked.

2. **7 minutes — Experimental-unit and temporal risks**  
   Why the current public datasets cannot support a confirmatory claim.

3. **7 minutes — Competing explanations**  
   Which biological and technical alternatives must remain active.

4. **6 minutes — Minimum discriminating evidence**  
   What kind of evidence could separate the leading explanations, without discussing operational procedures in this note.

5. **5 minutes — Decision and ownership**  
   Whether to stop, revise the question, continue documentary review, or let the institution consider a governed validation concept.

## Collaboration principles

- Negative findings are valid outputs.
- Unknown experimental-unit semantics remain visible.
- Technical replication is not promoted to biological replication.
- Conceptual pathway support is not promoted to direct replication.
- Rank is not probability and is not causal identification.
- AI-generated hypotheses do not bypass human scientific review.
- BioEvidence OS does not authorize physical work.
- The partner institution owns its approvals, procedures, safety systems, and execution decisions.
- No clinical, diagnostic, treatment, or therapeutic language is permitted without evidence and authorization appropriate to that claim.

## Current merge and release boundary

This note belongs to the docs-only outreach package stacked on the BioEvidence OS v0.1 release candidate.

The underlying release candidate remains blocked pending:

- one complete biology verdict;
- one complete statistics or bioinformatics verdict;
- conflict-of-interest review;
- correction or explicit disposition of every P0 and P1 finding.

The note may be used for scientific discussion and critique. It must not be represented as proof of biological discovery, validated drug-target infrastructure, institutional partnership, or authorization for wet-lab execution.
