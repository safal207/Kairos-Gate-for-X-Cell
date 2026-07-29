# Scientific outreach playbook

## Objective

Turn the Kairos Gate evidence package into a small, testable scientific usability pilot.

The campaign does **not** ask for endorsement, partnership, publicity, funding, or scientific validation. It asks whether a scientist or scientific agent can use the evidence structure correctly and what must change before real workflow integration.

## Message architecture

Every outreach message should follow this order:

1. **Problem** — scientific AI systems can blur reported, recalculated, replicated, predictive, associative, and causal evidence.
2. **Mechanism** — Kairos Gate records claims, exact sources, evidence levels, state, intervention, timing, replicate semantics, confounders, uncertainty, and non-claim boundaries.
3. **Concrete example** — the smACGmax evidence case converts one recent triple-base-editing paper into an auditable evidence graph.
4. **One default action** — spend ten minutes checking whether the 60-second demo and claim map are understandable.
5. **Boundary** — research-only; no guide design, wet-lab instruction, safety approval, clinical claim, or experiment authorization.

## Default call to action

> Would one person on your team be willing to spend ten minutes reviewing the smACGmax 60-second demo and return one of the response codes below?

Response codes:

- `A_CLEAR` — the evidence levels and boundaries are understandable;
- `B_MISSING_FIELD` — an important scientific field or state is missing;
- `C_WRONG_CLASSIFICATION` — at least one claim is classified incorrectly;
- `D_PILOT_PAPER` — the team is willing to nominate one public paper for a second evidence case;
- `E_ROUTE` — please contact another named person or team.

A recipient may reply with only the code and one sentence.

## Pilot offer

When a team shows interest, offer one bounded pilot:

> Nominate one recent public biological paper from your team. We will convert it into a machine-readable Kairos evidence case and return it for critique. This is a usability exercise, not independent replication or scientific endorsement.

## Contact ladder

For a large organization, do not rely on one generic inbox. Seek separate, relevant roles without duplicating the same message:

- research lead;
- principal scientist;
- research engineer;
- scientific product or program manager;
- open-source or developer-relations lead;
- benchmark or evaluation owner;
- author of a directly relevant paper.

Each contact must receive a role-specific reason for the message.

## Cadence

### Day 0 — initial outreach

Introduce the problem, link the evidence case, and ask for the ten-minute review.

### Day 3 — value-adding follow-up

Send the 60-second demo, state one concrete finding, and repeat only the default CTA.

Example value:

- `41%` is a reported maximum, not a typical editing rate;
- the paper's rebuttal reports a `5.5%` mean across 71 sites, still pending independent recalculation;
- a valid pre-intervention phase remains unresolved.

### Day 7 — routing or pilot follow-up

Ask for one of two actions:

1. route the material to the correct scientist; or
2. nominate one public paper for a bounded pilot.

### Day 14 — polite close

State that no further follow-up will be sent unless requested. Keep the public materials available.

## Stop rules

Stop outreach to a contact immediately when:

- they reply;
- they ask not to be contacted;
- the address bounces;
- they identify a better contact;
- they state that the topic is outside their scope;
- the Day 14 close has been sent.

Do not interpret silence as endorsement, rejection, adoption, scientific validation, or partnership.

## CRM states

```text
CONTACT_IDENTIFIED
MESSAGE_SENT
ROUTING_REQUEST_SENT
RESPONSE_RECEIVED
ROUTED_INTERNALLY
TEN_MINUTE_REVIEW_ACCEPTED
FEEDBACK_RECEIVED
PILOT_PAPER_NOMINATED
PILOT_STARTED
CLOSED_NO_RESPONSE
CLOSED_OUT_OF_SCOPE
DO_NOT_CONTACT
```

## Metrics

Track only observable events:

- distinct organizations contacted;
- distinct relevant roles contacted;
- messages sent;
- replies received;
- internal routes received;
- scientific corrections;
- missing fields identified;
- pilot papers nominated;
- pilots started.

Do not use email opens as evidence of scientific interest unless a reliable source explicitly provides that signal.

## Personalization rule

Every message must name one concrete connection between the recipient's work and the evidence case.

Examples:

- genomic prediction → prediction-to-evidence boundary;
- virtual cell → pre-intervention state and perturbation response;
- scientific agent → provenance and claim-state transitions;
- workflow platform → sample linkage and replicate semantics;
- benchmark team → reviewer-agent evaluation case.

## Shared authority boundary

```text
RESEARCH_ONLY
NO INDEPENDENT_REPLICATION_CLAIM
NO GUIDE_DESIGN
NO WET_LAB_INSTRUCTIONS
NO CLINICAL_CLAIM
NO SAFETY_APPROVAL
NO EXPERIMENT_AUTHORIZATION
```
