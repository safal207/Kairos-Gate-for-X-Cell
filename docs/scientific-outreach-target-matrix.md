# BioEvidence OS Scientific Outreach Target Matrix

## Purpose

This matrix records the first verified outreach wave for BioEvidence OS and Kairos Gate for X-Cell.

It is a coordination artifact, not evidence of endorsement, partnership, reviewer independence, institutional approval, or scientific acceptance.

Personal email addresses are intentionally not duplicated in this public document. Exact message recipients, thread history, timestamps, and delivery state remain in the project mailbox.

## Status vocabulary

```text
CONTACTED
DELIVERED_NO_IMMEDIATE_FAILURE
AWAITING_REPLY
REPLIED
DECLINED
VERDICT_RECEIVED
CONFLICT_CHECK_PENDING
FOLLOW_UP_DUE
CLOSED_NO_RESPONSE
```

`DELIVERED_NO_IMMEDIATE_FAILURE` means only that no immediate delivery failure was observed. It does not prove inbox placement, reading, or engagement.

## Verified outreach contacts

| # | Contact | Institution or organization | Primary relevance | Request type | Current status |
|---:|---|---|---|---|---|
| 1 | Alexander Hoffmann | UCLA | NF-kB signaling, macrophage biology, dynamic signaling interpretation | Biology and claim-boundary review | CONTACTED; AWAITING_REPLY; CONFLICT_CHECK_PENDING |
| 2 | Savas Tay | University of Chicago | Single-cell dynamics, immune signaling, temporal evidence | Biology and temporal-evidence review | CONTACTED; AWAITING_REPLY; CONFLICT_CHECK_PENDING |
| 3 | Kip D. Zimmerman | Wake Forest University School of Medicine | Experimental units, pseudoreplication, biomedical study design | Statistics and experimental-unit review | CONTACTED; AWAITING_REPLY; CONFLICT_CHECK_PENDING |
| 4 | Stanley E. Lazic | Independent statistical and machine-learning practice | Replication, effective N, inference boundaries, reproducibility | Statistics and replication review | CONTACTED; AWAITING_REPLY; CONFLICT_CHECK_PENDING |
| 5 | Stephanie C. Hicks | Johns Hopkins University | Biostatistics, single-cell data, reproducible computational biology | Statistics and reproducibility review | CONTACTED; AWAITING_REPLY; CONFLICT_CHECK_PENDING |
| 6 | Bart Deplancke | EPFL | Live-seq authorship and experimental provenance for GSE141064 | Author clarification on replicate semantics | CONTACTED; AWAITING_REPLY |
| 7 | Julia A. Vorholt | ETH Zurich | Live-seq authorship and experimental provenance for GSE141064 | Author clarification on replicate semantics | CONTACTED; AWAITING_REPLY |
| 8 | Ci Chu | Xaira Therapeutics | Virtual-cell modeling and timing-layer relevance | Technical feedback request | CONTACTED; AWAITING_REPLY |
| 9 | Bo Wang | Xaira Therapeutics | AI-enabled biological modeling and X-Cell relevance | Technical feedback request | CONTACTED; AWAITING_REPLY |
| 10 | Xaira general scientific contact route | Xaira Therapeutics | Organizational routing for the Kairos Gate timing-layer request | Technical routing and feedback request | CONTACTED; AWAITING_REPLY |

## Outreach groups

### A. Load-bearing external review gate

Contacts 1-5 were asked for bounded scientific verdicts on the BioEvidence OS release candidate.

The requested verdict vocabulary is:

```text
ACCEPT
ACCEPT_WITH_CHANGES
HOLD
BLOCK
```

Reviewers were also asked to identify:

- P0 critical validity errors;
- P1 required corrections;
- P2 improvements;
- conflicts of interest;
- claim boundaries that must remain blocked.

Current state:

```text
biology verdicts:    0 / 1 required
statistics verdicts: 0 / 1 required
human merge gate:    BLOCKED
```

The project must not describe these contacts as independent reviewers until conflict checks are completed.

### B. Source-author clarification

Contacts 6-7 were asked what `plate1`, `plate3`, and `plate4` physically represent in the selected GSE141064 cohort and what should count as the independent experimental unit.

Until source-backed clarification is received:

```text
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

Plate, well, library, index, or sequencing-run identifiers must not be promoted to biological replicates.

### C. AI-for-biology technical feedback

Contacts 8-10 received a research-only request concerning the relationship between X-Cell-style perturbation prediction and a separate timing/evidence-governance layer.

This request does not claim:

- endorsement by Xaira;
- technical integration;
- partnership;
- access to private models or data;
- validated biological performance;
- authorization for physical experiments.

## Current response state

Latest mailbox inspection found:

```text
human replies:                0
biology verdicts:             0
statistics verdicts:          0
author clarifications:        0
Xaira technical responses:    0
immediate delivery failures:  0 observed for the five reviewer threads
```

Silence is not interpreted as rejection, acceptance, review completion, or delivery confirmation.

## Follow-up policy

The first reviewer wave should not receive repeated immediate reminders.

Recommended sequence:

1. allow a reasonable professional response window;
2. send one concise follow-up that links the current exact review target;
3. do not send repeated reminders after that follow-up;
4. expand to a separately verified secondary pool if the required biology and statistics verdicts remain unavailable;
5. record every reply, decline, conflict, correction request, or verdict in the corresponding GitHub issue.

## Contact-specific decision routes

| Group | Useful reply | Project action |
|---|---|---|
| Biology reviewer | ACCEPT / CHANGES / HOLD / BLOCK with P0-P2 and conflicts | Update issue #31; preserve or change claim boundaries; keep merge blocked until complete disposition |
| Statistics reviewer | ACCEPT / CHANGES / HOLD / BLOCK with P0-P2 and conflicts | Update issue #32; correct inference contracts; keep merge blocked until complete disposition |
| Live-seq author | Source-backed explanation of experimental units and dependencies | Update issue #14 and PR #15; reassess replicate status without silently promoting technical groups |
| Xaira scientist or routing contact | Technical relevance, mismatch, decline, or suggested owner | Record feedback as non-authoritative product/scientific input; do not treat as validation or partnership |

## Evidence and governance boundary

This matrix demonstrates that focused international outreach has occurred. It does not demonstrate that:

- recipients read the messages;
- recipients agreed to review;
- recipients are independent;
- institutions endorse the work;
- a collaboration exists;
- any biological hypothesis is validated;
- the project is merge-authorized;
- physical or clinical work is authorized.

## Definition-of-done contribution

This matrix satisfies the backlog requirement that at least ten focused outreach contacts be prepared and recorded.

It does not satisfy the separate requirements for:

- one complete external biology verdict;
- one complete external statistics or bioinformatics verdict;
- correction or explicit disposition of every P0/P1 finding;
- source-backed replicate semantics for GSE141064;
- institutional partnership or governed validation work.
